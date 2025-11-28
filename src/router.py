import secrets
from http import HTTPStatus
from json.decoder import JSONDecodeError
from urllib.parse import urljoin
from contextlib import asynccontextmanager
from typing import Optional

import httpx
from fastapi import FastAPI, HTTPException, Depends
from fastapi.requests import Request
from fastapi.responses import RedirectResponse
from fastapi.routing import APIRouter

from src.config import settings, logger
from src.bot.processor import serialize_message, serialize_callback_query
from src.tunnel import start_ngrok_tunnel, stop_ngrok_tunnel, get_current_ngrok_url
from src.bot.webhook import set_webhook, delete_webhook
from src.utils.price import calculate_prices
from src.clients.telegram_client import (
    telegram_answer_callback_query,
    telegram_edit_messages_text,
    telegram_send_message,
)

from sqlalchemy.orm import Session
from src.db import get_db

router = APIRouter()


# ---------- Public docs redirect ----------
@router.get(path="/", response_class=RedirectResponse, include_in_schema=False)
async def redirect_index():
    """Redirect root to read-only docs."""
    return "/redoc"


# ---------- Lifespan: startup + shutdown ----------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup:
      - create shared httpx AsyncClient
      - discover or start public URL (webhook or ngrok)
      - set Telegram webhook
    Shutdown:
      - delete Telegram webhook
      - stop ngrok if we started it
      - close AsyncClient
    """
    # 1) shared HTTP client
    app.state.http = httpx.AsyncClient()

    # 2) get public URL
    public_url: Optional[str] = None
    using_ngrok = False

    if settings.webhook:
        public_url = str(settings.webhook)
    else:
        using_ngrok = True
        public_url = start_ngrok_tunnel()
        if not public_url:
            # try to read the running ngrok url if the tunnel is already up
            public_url = get_current_ngrok_url()

    if not public_url:
        # can't serve webhooks at all
        await app.state.http.aclose()
        raise RuntimeError("Failed to acquire a public HTTPS URL (webhook or ngrok).")

    logger.info(
        "Local http://%s:%s  →  %s", settings.host, settings.port.value, public_url
    )

    # 3) set telegram webhook
    target_url = urljoin(public_url.rstrip("/") + "/", settings.endpoint.lstrip("/"))
    try:
        await set_webhook(target_url)
        logger.info("Webhook registered at: %s", target_url)
    except Exception as e:
        await app.state.http.aclose()
        if using_ngrok:
            stop_ngrok_tunnel()
        raise RuntimeError(f"Failed to set Telegram webhook: {e}") from e

    # ---- hand control to the app ----
    try:
        yield
    finally:
        # ---- graceful shutdown ----
        try:
            await delete_webhook(drop_pending=True)
            logger.info("Webhook deleted.")
        except Exception as e:
            logger.warning("Failed to delete webhook: %s", e)

        if using_ngrok:
            try:
                stop_ngrok_tunnel()
            except Exception as e:
                logger.warning("Failed to stop ngrok: %s", e)

        try:
            await app.state.http.aclose()
        except Exception:
            pass


# ---------- Security helper ----------
def verify_secret_token(request: Request) -> bool:
    """
    Verifies Telegram's X-Telegram-Bot-Api-Secret-Token header when SECRET_TOKEN is set.
    Returns True if header matches (or if no secret is configured).
    """
    if not settings.secret_token:
        return True
    header_val = request.headers.get("X-Telegram-Bot-Api-Secret-Token", "")
    return secrets.compare_digest(header_val, settings.secret_token)


# helper function for sending messages in telegram


# ---------- Webhook endpoint ----------
@router.post(settings.endpoint)
async def telegram_webhook(request: Request, db: Session = Depends(get_db)):
    """Main webhook: receives updates, routes them, replies with sendMessage."""
    try:

        logger.debug(
            "Incoming connection from %s via host %s",
            request.client.host,
            request.headers.get("host"),
        )

        # 1) parse JSON
        try:
            update = await request.json()
        except JSONDecodeError as error:
            logger.error("Invalid JSON: %s", error)
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST.value,
                detail=HTTPStatus.BAD_REQUEST.phrase,
            )

        # 2) verify webhook secret (if enabled)
        if not verify_secret_token(request):
            logger.error("Forbidden: secret token mismatch")
            raise HTTPException(
                status_code=HTTPStatus.FORBIDDEN.value,
                detail=HTTPStatus.FORBIDDEN.phrase,
            )

        # 3) pick a supported message container
        message = (
            update.get("message")
            or update.get("edited_message")
            or update.get("channel_post")
        )

        callback_query = update.get("callback_query")

        # 4) route + build reply for message update
        if message is not None:
            try:
                response_params = serialize_message(message, db)
            except Exception as e:
                logger.error("Serialize_message/route failed: %s", e)
                return {"ok": False, "error": "serializing message failed"}

            if "method" not in response_params:
                return await telegram_send_message(
                    request=request, payload=response_params
                )
            method = response_params.get("method")
        if callback_query is not None:
            try:
                response_params = serialize_callback_query(
                    payload=callback_query, db=db
                )
            except Exception as e:
                logger.error("seraializing_callback_query failed: %s", e)
                return {"ok": False, "error": "serializing callback failed"}
            if "method" not in response_params:
                return await telegram_send_message(
                    request=request, payload=response_params
                )
            method = response_params.get("method")
            if method == "answerCallback":
                return await telegram_answer_callback_query(
                    request=request, payload=response_params.get("params")
                )
            if method == "editMessageText":
                return await telegram_edit_messages_text(
                    request=request, payload=response_params.get("params")
                )
            if method == "show_menu":
                await telegram_send_message(
                    request, payload=response_params.get("params")
                )
                chat_id = response_params.get("params").get("chat_id")
                custom_payload = {"custom": "show_menu", "chat_id": chat_id}
                try:
                    response_params = serialize_callback_query(custom_payload, db)
                except Exception as e:
                    logger.error("seraializing_callback_query failed: %s", e)
                    return {"ok": False, "error": "serializing callback failed"}
                return await telegram_send_message(request, response_params)
            if method == "calculatePrices":
                try:
                    chat_id = response_params.get("loading_message").get("chat_id")
                    loading_message_payload = response_params.get("loading_message")
                    await telegram_send_message(
                        request=request, payload=loading_message_payload
                    )
                    prices = await calculate_prices()
                    custom_message_payload = {
                        "chat_id": chat_id,
                        "prices": prices,
                        "custom": "show_prices",
                    }

                    response_params = serialize_callback_query(
                        payload=custom_message_payload, db=db
                    )

                    return await telegram_send_message(request, response_params)
                except Exception as e:
                    logger.error("calculatePrices failed:%s", e)
                    return {"ok": False, "error": "calculating prices failed"}
        if message is None and callback_query is None:
            logger.info("Unsupported update type: %s", update.keys())
            return {"ok": True, "ignored": True}  # 200 OK, no retry
    except Exception as e:
        logger.exception("Unhandled error in telegram_webhook: %s", e)
        return {"ok": False, "error": "internal error"}
