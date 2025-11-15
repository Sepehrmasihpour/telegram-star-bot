from typing import Dict, Union, Any
from src.bot.models import Chat, Text
from src.crud.chat import get_chat_by_chat_id, create_chat
from sqlalchemy.orm import Session
from src.config import logger


class NotPrivateChat(ValueError):
    pass


def serialize(payload: Dict[str, Any], db: Session) -> Dict[str, Union[str, int]]:
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
    return process_text(chat, data, db)


def process_text(chat: Chat, data: Text, db: Session) -> Dict[str, Union[str, int]]:
    if data.text == "/start":
        authentication_response = chat_authentication(db=db, data=chat)
        if authentication_response:
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
    logger.error("unsupported command")


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
            }
        return True
    except Exception as e:
        logger.error(f"chat authentication failed: {e}")
        return False
