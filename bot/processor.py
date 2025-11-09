from typing import Dict, Tuple, Union
from bot.telegram_models import Chat, Text


def serialize(payload: Dict[str, Union[str, int, dict]]) -> Tuple[str, int]:
    chat = Chat(**{**payload, **payload["chat"], **payload["from"]})
    print(chat)
    if payload.get("text"):
        return process_text(chat, Text(**payload))
    raise ValueError("Payload type is not allowed.")


def process_text(chat: Chat, data: Text) -> Tuple[str, int]:
    try:

        if "/start" in data.text:
            response_text = "hello"
        return {"chat_id": chat.id, "text": response_text}
    except ValueError as e:
        raise ValueError(e)
