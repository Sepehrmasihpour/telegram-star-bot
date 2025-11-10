from typing import Dict, Union, Any
from bot.telegram_models import Chat, Text


class NotPrivateChat(ValueError):
    pass


def serialize(payload: Dict[str, Any]) -> Dict[str, Union[str, int]]:
    # 1) Hard gate: only private chats and matching IDs
    chat_data = payload.get("chat") or {}
    from_data = payload.get("from") or {}

    if chat_data.get("type") != "private":
        raise NotPrivateChat("Only private chats are supported.")

    if chat_data.get("id") != from_data.get("id"):
        # In true private DMs these are equal. If not, reject.
        raise NotPrivateChat("chat.id and from.id must match for private messages.")

    # 2) Build Chat from chat block only (avoid silent overwrites)
    chat = Chat(**chat_data)

    # 3) Enforce that the payload is a valid Text message (your Text model already narrows commands)
    try:
        data = Text(**payload)  # Will fail fast if command is invalid
    except Exception:
        raise ValueError("Payload is not a valid Text message.")

    # 4) Delegate to command logic
    return process_text(chat, data)


def process_text(chat: Chat, data: Text) -> Dict[str, Union[str, int]]:
    # With Literal-enforced commands, you can branch exhaustively.
    if data.text == "/start":
        return {"chat_id": chat.id, "text": "hello"}

    # If you add more commands to Text later, extend here.
    raise ValueError(f"Unsupported command: {data.text}")
