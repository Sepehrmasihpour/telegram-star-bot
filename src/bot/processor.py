from typing import Dict, Any, Union
from src.bot.models import Chat, Text
from src.crud.chat import get_chat_by_chat_id, create_chat, update_chat_by_chat_id
from sqlalchemy.orm import Session
from src.config import logger
from src.config import settings
import re


class NotPrivateChat(ValueError):
    pass


class CallbackQueryFromNonUser(LookupError):
    pass


class UserAlreadyAcceptedTerms(KeyError):
    pass


class BotFound(PermissionError):
    pass


class UnsuportedTextInput(ValueError):
    pass


def serialize_message(payload: Dict[str, Any], db: Session) -> Dict[str, Any]:
    try:
        chat_data = payload.get("chat") or {}
        from_data = payload.get("from") or {}
        if chat_data.get("type") != "private":
            raise NotPrivateChat("Only private chats are supported.")
        if chat_data.get("id") != from_data.get("id"):
            raise NotPrivateChat("chat.id and from.id must match for private messages.")
        chat = Chat(**chat_data)
        data = Text(**payload)
        return process_text(chat, data, db)
    except Exception as e:
        logger.error(f"serialize_message failed:{e}")


def serialize_callback_query(payload: Dict[str, Any], db: Session) -> Dict[str, Any]:
    try:
        from_data = payload.get("from") or {}
        if from_data.get("is_bot"):
            raise BotFound("the callback query is from a bot")
        chat_id = from_data.get("id")
        message = payload.get("message")
        message_id = message.get("message_id")
        query_data = payload.get("data")
        query_id = payload.get("id")
        return process_callback_query(query_id, chat_id, query_data, message_id, db)
    except Exception as e:
        logger.error(f"serialize_callback_query failed:{e}")


def process_callback_query(
    query_id: str, chat_id: str, query_data: str, message_id: str, db: Session
):
    try:

        if query_data == "show_terms_for_acceptance":
            chat = get_chat_by_chat_id(db, chat_id)
            if chat.accepted_terms is True:
                return settings.telegram_process_callback_query_outputs.empty_answer_callback(
                    query_id
                )
            return (
                settings.telegram_process_callback_query_outputs.show_terms_condititons(
                    chat_id, message_id
                )
            )

        if query_data == "read_the_terms":
            return (
                settings.telegram_process_callback_query_outputs.terms_and_conditions(
                    chat_id, message_id
                )
            )

        if query_data == "accepted_terms":
            update_chat_by_chat_id(db, chat_id, accepted_terms=True)
            return settings.telegram_process_callback_query_outputs.welcome_message(
                chat_id
            )

        else:
            ...
    except Exception as e:
        logger.error(f"proccess_callback_query failed:{e}")


def process_text(chat: Chat, data: Text, db: Session) -> Dict[str, Any]:
    try:
        chat_data = get_chat_by_chat_id(db, chat.id)
        if chat_data is None or chat_data.pending_action is None:
            if data.text == "/start":
                output = settings.telegram_process_text_outputs.shop_options(chat.id)
                return ultimate_authntication(db, chat, output)
            if data.text == "/buy":
                output = settings.telegram_process_text_outputs.shop_options(chat.id)
                ultimate_authntication(db, chat, output)
            if data == "/prices":
                return settings.telegram_process_text_outputs.prices(chat.id)
            if data == "/support":
                return settings.telegram_process_text_outputs.support(chat.id)
            else:
                raise UnsuportedTextInput("unsupported command or text input")
        if chat_data.pending_action == "waiting_for_phone_number":
            valid_phone_number = phone_number_authenticator(data)
            if not valid_phone_number:
                attempts = chat_data.phone_input_attempt
                if attempts >= 3:
                    update_chat_by_chat_id(
                        db, chat.id, phone_input_attempt=0, pending_action=None
                    )
                    return settings.telegram_process_text_outputs.phone_max_attempt(
                        chat.id
                    )
                update_chat_by_chat_id(db, chat.id, phone_input_attempt=attempts + 1)
                return settings.telegram_process_text_outputs.invalid_phone_number(
                    chat.id
                )
            update_chat_by_chat_id(
                db,
                chat.id,
                phone_input_attempt=0,
                phone_number=data,
                pending_action="waiting_for_otp",
            )
            return settings.telegram_process_text_outputs.phone_numebr_verification(
                chat.id
            )
        if chat_data.pending_action == "waiting_for_otp":
            if data != "1111":
                return settings.telegram_process_text_outputs.invalid_otp(chat.id)
            return settings.telegram_process_text_outputs.phone_number_verified(chat.id)

    except Exception as e:
        logger.error(f"procces_text failed:{e}")


def chat_first_level_authentication(db: Session, data: Chat) -> Dict[str, Any] | bool:
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
        return True
    except Exception as e:
        logger.error(f"chat_first_level_authentication failed: {e}")


def chat_second_lvl_authentication(db: Session, data: Chat) -> Dict[str, Any] | bool:
    try:
        first_auth_resutlt = chat_first_level_authentication(db, data)
        if first_auth_resutlt is True:
            chat = get_chat_by_chat_id(db, chat_id=data.id)
            if not chat.phone_number:
                update_chat_by_chat_id(
                    db, data.id, pending_action="waiting_for_phone_number"
                )
                return settings.telegram_process_text_outputs.phone_number_input(
                    chat.chat_id
                )
            if not chat.phone_number_validated:
                settings.telegram_process_text_outputs.phone_number_verfication_needed(
                    chat.chat_id
                )
            return True
        return first_auth_resutlt
    except Exception as e:
        logger.error(f"chat_second_level_authentication failed: {e}")


def ultimate_authntication(db: Session, data: Chat, output: Dict) -> Union[Dict, bool]:
    first_lvl_authentication_response = chat_first_level_authentication(
        db=db, data=data
    )
    if first_lvl_authentication_response is True:
        second_lvl_authectication_response = chat_second_lvl_authentication(db, data)
        if second_lvl_authectication_response is True:
            return output
        else:
            return second_lvl_authectication_response
    else:
        return first_lvl_authentication_response


def phone_number_authenticator(phone: str) -> bool:
    pattern = r"^09\d{9}$"
    return bool(re.match(pattern, phone))
