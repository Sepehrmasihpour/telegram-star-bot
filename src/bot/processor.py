from typing import Dict, Any, Optional
from src.bot.models import TgChat, Text
from src.crud.chat import get_chat_by_chat_id, create_chat, update_chat_by_chat_id
from sqlalchemy.orm import Session
from src.config import logger
from src.config import settings
from src.models import Chat
from bot.process_output import (
    telegram_process_callback_query_outputs,
    telegram_process_text_outputs,
)
import re


class NotPrivateChat(ValueError):
    pass


class UnsuportedTextInput(ValueError):
    pass


class ChatNotCreated(SystemError):
    pass


def serialize_message(payload: Dict[str, Any], db: Session) -> Dict[str, Any]:
    try:
        chat_data = payload.get("chat") or {}
        from_data = payload.get("from") or {}
        if chat_data.get("type") != "private":
            raise NotPrivateChat("Only private chats are supported.")
        if chat_data.get("id") != from_data.get("id"):
            raise NotPrivateChat("chat.id and from.id must match for private messages.")
        chat = TgChat(**chat_data)
        data = Text(**payload)
        return process_text(chat, data, db)
    except Exception as e:
        logger.error(f"serialize_message failed:{e}")
        raise


def serialize_callback_query(payload: Dict[str, Any], db: Session) -> Dict[str, Any]:
    try:
        from_data = payload.get("from") or {}
        chat_id = from_data.get("id")
        message = payload.get("message")
        message_id = message.get("message_id")
        query_data = payload.get("data")
        query_id = payload.get("id")
        return process_callback_query(query_id, chat_id, query_data, message_id, db)
    except Exception as e:
        logger.error(f"serialize_callback_query failed:{e}")
        raise


def process_callback_query(
    query_id: str, chat_id: str, query_data: str, message_id: str, db: Session
):
    try:

        if query_data == "show_terms_for_acceptance":
            chat = get_chat_by_chat_id(db, chat_id)
            if chat.accepted_terms is True:
                return telegram_process_callback_query_outputs.empty_answer_callback(
                    query_id
                )
            return telegram_process_callback_query_outputs.show_terms_condititons(
                chat_id, message_id
            )

        if query_data == "read_the_terms":
            return telegram_process_callback_query_outputs.terms_and_conditions(
                chat_id, message_id
            )

        if query_data == "accepted_terms":
            update_chat_by_chat_id(db, chat_id, accepted_terms=True)
            return telegram_process_callback_query_outputs.welcome_message(chat_id)

        else:
            ...
    except Exception as e:
        logger.error(f"proccess_callback_query failed:{e}")
        raise


def process_text(chat: TgChat, data: Text, db: Session) -> Dict[str, Any]:
    try:
        chat_data = get_chat_by_chat_id(db, chat.id)
        if chat_data is None or chat_data.pending_action is None:
            auth_result = chat_first_level_authentication(db, chat, chat_data)
            if data.text == "/start":
                return (
                    telegram_process_text_outputs.shop_options(chat.id)
                    if auth_result is True
                    else auth_result
                )
            if data.text == "/buy":
                return (
                    telegram_process_text_outputs.shop_options(chat.id)
                    if auth_result is True
                    else auth_result
                )
            if data.text == "/prices":
                return (
                    telegram_process_text_outputs.prices(chat.id)
                    if auth_result is True
                    else auth_result
                )
            if data.text == "/support":
                return (
                    telegram_process_text_outputs.support(chat.id)
                    if auth_result is True
                    else auth_result
                )
            else:
                raise UnsuportedTextInput("unsupported command or text input")
        if chat_data.pending_action == "waiting_for_phone_number":
            valid_phone_number = phone_number_authenticator(data.text)
            if not valid_phone_number:
                attempts = chat_data.phone_input_attempt
                if attempts >= 3:
                    update_chat_by_chat_id(
                        db, chat.id, phone_input_attempt=0, pending_action=None
                    )
                    return telegram_process_text_outputs.phone_max_attempt(chat.id)
                update_chat_by_chat_id(db, chat.id, phone_input_attempt=attempts + 1)
                return telegram_process_text_outputs.invalid_phone_number(chat.id)
            update_chat_by_chat_id(
                db,
                chat.id,
                phone_input_attempt=0,
                phone_number=data.text,
                pending_action="waiting_for_otp",
            )
            return telegram_process_text_outputs.phone_numebr_verification(chat.id)
        if chat_data.pending_action == "waiting_for_otp":
            if data.text != "1111":
                return telegram_process_text_outputs.invalid_otp(chat.id)
            return telegram_process_text_outputs.phone_number_verified(chat.id)

    except Exception as e:
        logger.error(f"procces_text failed:{e}")
        raise


def chat_first_level_authentication(
    db: Session, data: TgChat, chat_db: Optional[Chat] = None
) -> Dict[str, Any] | bool:
    try:

        chat = chat_db or get_chat_by_chat_id(db, chat_id=data.id)
        if chat is None:
            create_chat(
                db, chat_id=data.id, first_name=data.first_name, username=data.username
            )

            return telegram_process_text_outputs.terms_and_conditions(data.id)
        if not chat.accepted_terms:
            return telegram_process_text_outputs.terms_and_conditions(chat.chat_id)
        return True
    except Exception as e:
        logger.error(f"chat_first_level_authentication failed: {e}")
        raise


def chat_second_lvl_authentication(
    db: Session, data: TgChat, chat_db: Optional[Chat] = None
) -> Dict[str, Any] | bool:
    try:
        chat = chat_db or get_chat_by_chat_id(db, chat_id=data.id)
        if not chat.phone_number:
            update_chat_by_chat_id(
                db, data.id, pending_action="waiting_for_phone_number"
            )
            return telegram_process_text_outputs.phone_number_input(chat.chat_id)
        if not chat.phone_number_validated:
            return telegram_process_text_outputs.phone_number_verfication_needed(
                chat.chat_id
            )
        return True
    except Exception as e:
        logger.error(f"chat_second_level_authentication failed: {e}")
        raise


def phone_number_authenticator(phone: str) -> bool:
    pattern = r"^09\d{9}$"
    return bool(re.match(pattern, phone))
