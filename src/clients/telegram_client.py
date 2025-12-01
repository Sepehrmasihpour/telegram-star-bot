from typing import Dict, Union
from fastapi.requests import Request
import httpx
from src.config import logger, settings


async def send_message(request: Request, payload: Dict) -> Union[Dict, None]:
    send_url = f"https://api.telegram.org/bot{settings.bot_token}/sendMessage"
    params = payload

    try:
        resp = await request.app.state.http.post(send_url, json=params)
        resp.raise_for_status()
    except httpx.HTTPError as e:
        logger.error(
            "sendMessage failed:%s | body=%s | payload:%s",
            e,
            getattr(e, "response", None) and e.response.text,
            payload,
        )
        # Return 200 to avoid Telegram retry storms; log the error for us
        raise

    return {"ok": True}


async def answer_callback_query(request: Request, payload: Dict) -> Union[Dict, None]:
    send_url = f"https://api.telegram.org/bot{settings.bot_token}/answerCallbackQuery"
    params = payload

    try:
        resp = await request.app.state.http.post(send_url, json=params)
        resp.raise_for_status()
    except httpx.HTTPError as e:
        logger.error(
            "callback query answer failed: %s | body=%s",
            e,
            getattr(e, "response", None) and e.response.text,
        )
        raise

    return {"ok": True}


async def edit_messages_text(request: Request, payload: Dict) -> Union[Dict, None]:
    send_url = f"https://api.telegram.org/bot{settings.bot_token}/editMessageText"
    params = payload

    try:
        resp = await request.app.state.http.post(send_url, json=params)
        resp.raise_for_status()
    except httpx.HTTPError as e:
        logger.error(
            "telgram edit message text failed: %s | body=%s",
            e,
            getattr(e, "response", None) and e.response.text,
        )
        raise

    return {"ok": True}


async def delete_message(request: Request, payload: Dict) -> Union[Dict, None]:
    send_url = f"https://api.telegram.org/bot{settings.bot_token}/deleteMessage"
    params = payload
    try:
        resp = await request.app.state.http.post(send_url, json=params)
        resp.raise_for_status()
    except Exception as e:
        logger.error(
            "telgram delete_message failed: %s | body=%s",
            e,
            getattr(e, "response", None) and e.response.text,
        )
        raise
    return {"ok": True}
