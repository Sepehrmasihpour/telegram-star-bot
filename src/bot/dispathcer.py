from src.config import logger
from fastapi.requests import Request
from typing import Any, Dict
from sqlalchemy.orm import Session
from src.bot.chat_flow import get_prices
from src.bot.chat_output import telegram_process_bot_outputs
from src.clients.telegram import (
    send_message,
    edit_messages_text,
    answer_callback_query,
    # delete_message,
)


async def dispatch_response(
    request: Request, db: Session, payload: Dict[str, Any]
) -> Dict:
    try:

        if "method" not in payload:
            return await send_message(request=request, payload=payload)
        method = payload.get("method")
        if method == "answerCallback":
            return await answer_callback_query(
                request=request, payload=payload.get("params")
            )
        if method == "editMessageText":
            return await edit_messages_text(
                request=request, payload=payload.get("params")
            )
        if method == "custom":
            data = payload.get("payload")
            return await custom_handler(request, db, data)

    except Exception as e:
        logger.error(f"diapatch_response failed:{e}")
        raise


async def custom_handler(request: Request, db: Session, payload: Dict[str, Any]):
    try:

        custom = payload.get("custom")
        if custom == "get_prices":
            await send_message(request, payload=payload.get("message"))
            prices = await get_prices(db)
            logger.debug(f"prices at custom_handler for get_peices : {prices}")
            chat_id = payload.get("chat_id")
            resp = telegram_process_bot_outputs.get_prices(
                chat_id=chat_id, prices=prices
            )
            return await send_message(request, payload=resp)
    except Exception as e:
        logger.error(f"custom_handler at dispathcer failed:{e}")
        raise
