from typing import Dict, Any
from src.bot.models import Chat, Text
from src.crud.chat import get_chat_by_chat_id, create_chat, update_chat_by_chat_id
from sqlalchemy.orm import Session
from src.config import logger
from pydantic import ValidationError
from src.config import settings


class NotPrivateChat(ValueError):
    pass


class CallbackQueryFromNonUser(LookupError):
    pass


class UserAlreadyAcceptedTerms(KeyError):
    pass


class BotFound(PermissionError):
    pass


def serialize_message(payload: Dict[str, Any], db: Session) -> Dict[str, Any]:

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


#! this looks iffy to me find out if needs more error handling
def serialize_callback_query(payload: Dict[str, Any], db: Session) -> Dict[str, Any]:
    from_data = payload.get("from") or {}
    if from_data.get("is_bot"):
        raise BotFound("the callback query is from a bot")
    chat_id = from_data.get("id")
    message = payload.get("message")
    message_id = message.get("message_id")
    query_data = payload.get("data")
    query_id = payload.get("id")
    return process_callback_query(query_id, chat_id, query_data, message_id, db)


def process_callback_query(
    query_id: str, chat_id: str, query_data: str, message_id: str, db: Session
):
    if query_data == "show terms for acceptance":
        chat = get_chat_by_chat_id(db, chat_id)
        if chat.accepted_terms:
            return (
                settings.telegram_process_callback_query_outputs.empty_answer_callback(
                    query_id
                )
            )
        return settings.telegram_process_callback_query_outputs.show_terms_condititons(
            chat_id, message_id
        )

    if query_data == "read the terms":
        return settings.telegram_process_callback_query_outputs.terms_and_conditions(
            chat_id, message_id
        )

    if query_data == "accepted terms":
        update_chat_by_chat_id(db, chat_id, accepted_terms=True)
        return {
            "chat_id": chat_id,
            "text": "text",
        }  #! this should go to the commands help guide . go to the blue bot for guidance

    else:
        ...


def process_text(chat: Chat, data: Text, db: Session) -> Dict[str, Any]:
    if data.text == "/start":
        authentication_response = chat_authentication(db=db, data=chat)
        if authentication_response is False:
            return settings.telegram_process_text_outputs.authentication_failed(chat.id)
        if authentication_response is True:
            return settings.telegram_process_text_outputs.shop_options(chat.id)
        else:
            return authentication_response
    logger.error("unsupported command")

    return settings.telegram_process_text_outputs.unsupported_command(chat.id)


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

            return settings.telegram_process_text_outputs.terms_and_conditions(data.id)
        if not chat.accepted_terms:
            return settings.telegram_process_text_outputs.terms_and_conditions(
                chat.chat_id
            )
        if not chat.phone_number:
            return settings.telegram_process_text_outputs.phone_number_input(
                chat.chat_id
            )
        if not chat.phone_number_validated:
            settings.telegram_process_text_outputs.phone_number_verfication(
                chat.chat_id
            )
        return True
    except Exception as e:
        logger.error(f"chat authentication failed: {e}")
        return False
