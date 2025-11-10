from typing import Dict, Union, Any
from bot.telegram_models import Chat, Text


class NotPrivateChat(ValueError):
    pass


def serialize(payload: Dict[str, Any]) -> Dict[str, Union[str, int]]:
    chat_data = payload.get("chat") or {}
    from_data = payload.get("from") or {}

    if chat_data.get("type") != "private":
        raise NotPrivateChat("Only private chats are supported.")

    if chat_data.get("id") != from_data.get("id"):
        raise NotPrivateChat("chat.id and from.id must match for private messages.")

    chat = Chat(**chat_data)

    try:
        data = Text(**payload)
    except Exception:
        raise ValueError("Payload is not a valid Text message.")
    return process_text(chat, data)


def process_text(chat: Chat, data: Text) -> Dict[str, Union[str, int]]:
    if data.text == "/start":
        return {"chat_id": chat.id, "text": "hello"}
    raise ValueError(f"Unsupported command: {data.text}")
