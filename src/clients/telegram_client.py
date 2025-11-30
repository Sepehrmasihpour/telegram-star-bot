from typing import Dict, Union
from fastapi.requests import Request
import httpx
from src.config import logger, settings


async def telegram_send_message(request: Request, payload: Dict) -> Union[Dict, None]:
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
        return {"ok": False, "error": "sendMessage failed"}

    return {"ok": True}


async def telegram_answer_callback_query(
    request: Request, payload: Dict
) -> Union[Dict, None]:
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
        return {"ok": False, "error": "answerCallbackQuery failed"}

    return {"ok": True}


async def telegram_edit_messages_text(
    request: Request, payload: Dict
) -> Union[Dict, None]:
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
        return {"ok": False, "error": "editMessageText failed"}

    return {"ok": True}
