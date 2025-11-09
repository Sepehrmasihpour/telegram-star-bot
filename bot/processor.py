from typing import Dict, Tuple, Union
from telegram_models import Chat, Text

# def serialize(payload: Dict) -> Dict:
#     text = payload.get("text")
#     user = payload.get("from")
#     chat = payload.get("chat")
#     if user.get("is_bot"):
#         raise ValueError()
#     if text == "/start":
#         response_params = {"text": "hellp", "chat_id": chat.get("id")}
#     return response_params


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
