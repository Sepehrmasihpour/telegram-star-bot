from typing import Dict, Any
from src.bot.models import Chat, Text
from src.crud.chat import get_chat_by_chat_id, create_chat
from sqlalchemy.orm import Session
from src.config import logger
from pydantic import ValidationError


class NotPrivateChat(ValueError):
    pass


def serialize(payload: Dict[str, Any], db: Session) -> Dict[str, Any]:
    chat_data = payload.get("chat") or {}
    from_data = payload.get("from") or {}

    if chat_data.get("type") != "private":
        raise NotPrivateChat("Only private chats are supported.")

    if chat_data.get("id") != from_data.get("id"):
        raise NotPrivateChat("chat.id and from.id must match for private messages.")

    chat = Chat(**chat_data)

    try:
        data = Text(**payload)
    except ValidationError:
        return {"chat_id": chat_data.get("id"), "text": "un supported command"}
    return process_text(chat, data, db)


def process_text(chat: Chat, data: Text, db: Session) -> Dict[str, Any]:
    if data.text == "/start":
        authentication_response = chat_authentication(db=db, data=chat)
        if authentication_response is False:
            return {
                "chat_id": chat.id,
                "text": "authentication failed",
            }
        if authentication_response is True:
            return {
                "chat_id": chat.id,
                "text": "به ربات تست خوش آمدید",
                "reply_markup": {
                    "inline_keyboard": [
                        [{"text": "خرید جنس 1", "callback_data": "buy product 1"}],
                        [{"text": "خرید جنس 2", "callback_data": "buy product 2"}],
                        [{"text": "خرید جنس 3", "callback_data": "buy product 3"}],
                        [{"text": "قیمت های محصولات", "callback_data": "show prices"}],
                        [{"text": "مشاهده قوانین", "callback_data": "show terms"}],
                        [{"text": "پشتیبانی", "callback_data": "support"}],
                    ]
                },
            }
        else:
            return authentication_response
    logger.error("unsupported command")

    return {
        "chat_id": chat.id,
        "text": "دستور پشتیبانی نمی‌شود.",
    }


def chat_authentication(db: Session, data: Chat) -> Dict[str, Any] | bool:
    try:

        chat = get_chat_by_chat_id(db, chat_id=data.id)
        if chat is None:
            new_chat = create_chat(
                db, chat_id=data.id, first_name=data.first_name, username=data.username
            )

            if new_chat is None:
                logger.error("failed to create chat during authentication")
                return False

            return {
                "chat_id": data.id,
                "text": f"{new_chat.first_name}, {new_chat.username} sign in",
                "reply_markup": {
                    "inline_keyboard": [
                        [{"text": "موافقم", "callback_data": "accepted terms"}],
                        [{"text": "مشاهده قوانین", "callback_data": "show terms"}],
                    ]
                },
            }
        if not chat.accepted_terms:
            return {
                "chat_id": chat.chat_id,
                "text": f"{chat.first_name}, {chat.username} in the data base",
                "reply_markup": {
                    "inline_keyboard": [
                        [{"text": "موافقم", "callback_data": "accepted terms"}],
                        [{"text": "مشاهده قوانین", "callback_data": "show terms"}],
                    ]
                },
            }
        if not chat.phone_number:
            return {
                "chat_id": chat.chat_id,
                "text": (
                    """
                         به ربات تست خوش آمدید\n
                          برای شروع، لطفا شماره تلفن خود را وارد کنید\n
                          • شماره را با فرمت 09123456789 وارد کنید
                         """
                ),
                "reply_markup": {
                    "force_reply": True,
                    "input_field_placeholder": "09121753528",
                },
            }
        if not chat.phone_number_validated:
            return {
                "chat_id": chat.chat_id,
                "text": (
                    """
                         شماره تلفن تایید نشده\n
                          برای ادامه باید شماره تایید بشه\n
                          آیا میخواهید کد تایید بفرستیم یا شمارتونو عوض کنید؟
                         """
                ),
                "reply_markup": {
                    "inline_keyboard": [
                        [
                            {
                                "text": "کد تایید بفرست",
                                "callback_data": "send validation code",
                            }
                        ],
                        [
                            {
                                "text": "ویرایش شماره تلفن",
                                "callback_data": "edit phone number",
                            }
                        ],
                    ]
                },
            }
        return True
    except Exception as e:
        logger.error(f"chat authentication failed: {e}")
        return False
