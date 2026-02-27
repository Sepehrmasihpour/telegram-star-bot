import secrets
from http import HTTPStatus
from json.decoder import JSONDecodeError

from fastapi import HTTPException, Depends
from fastapi.requests import Request
from fastapi.routing import APIRouter

from src.config import settings, logger
from src.bot.processor import serialize_message, serialize_callback_query
from src.bot.dispathcer import dispatch_response
from src.db import get_db

from sqlalchemy.orm import Session

router = APIRouter()


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
            outputs = request.app.state.outputs
            try:
                response_params = serialize_message(
                    payload=message, db=db, outputs=outputs
                )
            except Exception as e:
                logger.error("Serialize_message/route failed: %s", e)
                return {"ok": False, "error": "serializing message failed"}
            resp = await dispatch_response(
                request=request, db=db, payload=response_params
            )
            return resp
        if callback_query is not None:
            try:
                response_params = serialize_callback_query(
                    payload=callback_query, db=db, outputs=outputs
                )
            except Exception as e:
                logger.error("seraializing_callback_query failed: %s", e)
                return {"ok": False, "error": "serializing callback failed"}
            resp = await dispatch_response(
                request=request, db=db, payload=response_params
            )
            return resp

        if message is None and callback_query is None:
            logger.info("Unsupported update type: %s", update.keys())
            return {"ok": True, "ignored": True}  # 200 OK, no retry
    except Exception as e:
        logger.exception("Unhandled error in telegram_webhook: %s", e)
        return {"ok": False, "error": "internal error"}
