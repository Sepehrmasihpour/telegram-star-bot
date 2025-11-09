from typing import Dict, Tuple, Union
from bot.telegram_models import Message, Text

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
    msg = Message(**{**payload, **payload["chat"], **payload["from"]})
    print(msg)
    if payload.get("text"):
        return process_text(msg, Text(**payload))
    raise ValueError("Payload type is not allowed.")


def process_text(msg: Message, data: Text) -> Tuple[str, int]:
    try:

        if "/start" in data.text:
            response_text = "hello"
        return {"chat_id": msg.id, "text": response_text}
    except ValueError as e:
        raise ValueError(e)
