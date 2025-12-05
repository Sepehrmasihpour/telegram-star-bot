from typing import Dict, Any
from fastapi.requests import Request
import httpx
from src.config import logger, settings


async def _post_to_telegram(
    request: Request, method: str, payload: Dict[str, Any]
) -> Dict[str, Any]:
    url = f"https://api.telegram.org/bot{settings.bot_token}/{method}"

    try:
        resp: httpx.Response = await request.app.state.http.post(url, json=payload)
        resp.raise_for_status()
    except httpx.HTTPError as e:
        logger.error(
            "%s failed: %s | body=%s | payload=%s",
            method,
            e,
            getattr(e, "response", None) and e.response.text,
            payload,
        )
        raise

    return {"ok": True}


async def send_message(request: Request, payload: Dict[str, Any]) -> Dict[str, Any]:
    return await _post_to_telegram(request, "sendMessage", payload)


async def answer_callback_query(
    request: Request, payload: Dict[str, Any]
) -> Dict[str, Any]:
    return await _post_to_telegram(request, "answerCallbackQuery", payload)


async def edit_messages_text(
    request: Request, payload: Dict[str, Any]
) -> Dict[str, Any]:
    return await _post_to_telegram(request, "editMessageText", payload)


async def delete_message(request: Request, payload: Dict[str, Any]) -> Dict[str, Any]:
    return await _post_to_telegram(request, "deleteMessage", payload)
