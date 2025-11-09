from pydantic import ValidationError
from typing import Dict, Tuple

from bot.telegram_models import Message


def serialize_message(payload: Dict) -> Tuple[str, int]:
    try:
        validated_message = Message.model_validate(payload)
        text = validated_message.text
        chat = validated_message.chat
        chat_id = chat.id
        if text is not None:
            if text == "/start":
                response = "hello"
            return response, chat_id

    except ValidationError as e:
        # Classify common failure modes so your API/logs are actually useful.
        errors = e.errors()  # list[dict]: {'type','loc','msg','input','ctx'?}
        extras = [err["loc"][-1] for err in errors if err["type"] == "extra_forbidden"]
        missing = [err["loc"][-1] for err in errors if err["type"] == "missing"]
        type_mismatches = [
            err for err in errors if err["type"] not in {"extra_forbidden", "missing"}
        ]

        return None, {
            "message": "Invalid payload",
            "extra_fields": extras or None,
            "missing_fields": missing or None,
            "type_errors": [
                {"loc": err["loc"], "type": err["type"], "msg": err["msg"]}
                for err in type_mismatches
            ]
            or None,
            # Original Pydantic detail if you want the raw thing
            "raw": errors,
        }


# def serialize(payload: Dict[str, Union[str, int, dict]]) -> Tuple[str, int]:
#     chat = Chat(**{**payload, **payload["chat"], **payload["from"]})
#     if payload.get("video"):
#         return process_video(chat, Video(**payload["video"]))
#     if payload.get("text"):
#         return process_text(chat, Text(**payload))
#     if payload.get("voice"):
#         return process_voice(chat, Voice(**payload["voice"]))
#     if payload.get("audio"):
#         return process_audio(chat, Audio(**payload["audio"]))
#     if payload.get("document"):
#         return process_document(chat, Document(**payload["document"]))
#     if payload.get("photo"):
#         # Matches for compressed images
#         return process_photo(chat, [PhotoFragment(**d) for d in payload["photo"]])
#     raise ValueError("Payload type is not allowed.")


# def process_video(chat, data) -> Tuple[str, int]:
#     return "Received a video", chat.id


# def process_text(chat: Chat, data: Text) -> Tuple[str, int]:
#     if "stop" in data.text or "exit" in data.text or "kill" in data.text:
#         response = "Stopping webhook server"
#         os.kill(
#             os.getpid(), 15
#         )  # Send a terminate signal for the current process ID triggering shutdown event
#     else:
#         response = f"Received {data.text}"
#     return response, chat.id


# def process_voice(chat, data) -> Tuple[str, int]:
#     return "Received a voice memo", chat.id


# def process_audio(chat, data) -> Tuple[str, int]:
#     return "Received an audio file", chat.id


# def process_document(chat, data) -> Tuple[str, int]:
#     return "Received a document", chat.id


# def process_photo(chat, data) -> Tuple[str, int]:
#     return "Received a photo", chat.id
