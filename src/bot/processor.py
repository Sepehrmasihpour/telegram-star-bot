from typing import Dict, Any
from sqlalchemy.orm import Session
from src.config import logger
from src.bot.chat_output import telegram_process_bot_outputs as bot_output
from src.bot import TgChat, NotPrivateChat, UnsuportedTextInput
from src.bot.chat_flow import (
    chat_first_level_authentication,
    # chat_second_lvl_authentication,
    is_last_message,
    phone_number_authenticator,
)
from src.crud.user import (
    get_chat_by_chat_id,
    update_chat_by_chat_id,
    update_user,
    # get_user_by_id,
    # get_user_by_phone,
)


def serialize_message(payload: Dict[str, Any], db: Session) -> Dict[str, Any]:
    try:

        chat_data = payload.get("chat") or {}
        from_data = payload.get("from") or {}
        if chat_data.get("type") != "private":
            raise NotPrivateChat("Only private chats are supported.")
        if chat_data.get("id") != from_data.get("id"):
            raise NotPrivateChat("chat.id and from.id must match for private messages.")
        chat = TgChat(**chat_data)
        data = payload.get("text")
        return process_text(chat, data, db)

    except Exception as e:
        logger.error(f"serialize_message failed:{e}")
        raise


async def serialize_callback_query(
    payload: Dict[str, Any], db: Session
) -> Dict[str, Any]:
    try:
        from_data = payload.get("from") or {}
        chat_id = from_data.get("id")
        message = payload.get("message")
        message_id = message.get("message_id")
        query_data = payload.get("data")
        query_id = payload.get("id")
        return await process_callback_query(
            query_id, chat_id, query_data, message_id, db
        )
    except Exception as e:
        logger.error(f"serialize_callback_query failed:{e}")
        raise


async def process_callback_query(
    query_id: str, chat_id: str, query_data: str, message_id: str, db: Session
):
    try:
        chat = get_chat_by_chat_id(db, chat_id)
        last_message = is_last_message(message_id=message_id, db=db, chat=chat)
        if query_data == "show_terms_for_acceptance":
            if chat.accepted_terms is True:
                return bot_output.empty_answer_callback(query_id)
            return bot_output.show_terms_condititons(chat_id, message_id, form=True)

        if query_data == "read_the_terms":
            return bot_output.terms_and_conditions(chat_id, message_id)

        if query_data == "accepted_terms":
            if not chat.accepted_terms:
                update_chat_by_chat_id(db, chat_id, accepted_terms=True)
                return bot_output.return_to_menu(chat_id=chat_id, append=True)
            return bot_output.empty_answer_callback(query_id)

        if query_data == "show_prices":
            prices = ""
            return bot_output.loading_prices(chat_id, message_id, prices)

        if query_data == "return_to_menu":
            return (
                bot_output.return_to_menu(chat_id, message_id)
                if last_message is True
                else bot_output.return_to_menu(chat_id, message_id, append=True)
            )
        if query_data == "show_terms":
            return (
                bot_output.show_terms_condititons(chat_id, message_id)
                if last_message is True
                else bot_output.show_terms_condititons(chat_id, message_id, append=True)
            )

        if query_data == "support":
            return (
                bot_output.support(chat_id, message_id)
                if last_message is True
                else bot_output.support(chat_id, message_id, append=True)
            )

        if query_data == "contact_support":
            return (
                bot_output.contact_support_info(chat_id, message_id)
                if last_message is True
                else bot_output.contact_support_info(chat_id, message_id, append=True)
            )
        if query_data == "return_to_support":
            return (
                bot_output.support(chat_id, message_id)
                if last_message is True
                else bot_output.support(chat_id, message_id, True)
            )
        if query_data == "common_questions":
            return (
                bot_output.common_questions(chat_id, message_id)
                if last_message is True
                else bot_output.common_questions(chat_id, message_id, True)
            )
        else:
            ...
    except Exception as e:
        logger.error(f"proccess_callback_query failed:{e}")
        raise


def process_text(chat: TgChat, text: str, db: Session) -> Dict[str, Any]:
    try:
        chat_data = get_chat_by_chat_id(db, chat.id)
        if chat_data is None or chat_data.pending_action is None:
            auth_result = chat_first_level_authentication(db, chat, chat_data)
            if text == "/start":
                return (
                    bot_output.return_to_menu(chat.id, append=True)
                    if auth_result is True
                    else auth_result
                )
            else:
                raise UnsuportedTextInput("unsupported command or text input")
        if chat_data.pending_action == "waiting_for_phone_number":
            valid_phone_number = phone_number_authenticator(text)
            if not valid_phone_number:
                attempts = chat_data.phone_input_attempt
                if attempts >= 3:
                    update_chat_by_chat_id(
                        db, chat.id, phone_input_attempt=0, pending_action=None
                    )
                    return bot_output.phone_max_attempt(chat.id)
                update_chat_by_chat_id(db, chat.id, phone_input_attempt=attempts + 1)
                return bot_output.invalid_phone_number(chat.id)
            """
            ! we haven't reached that part yet but when we do 
            ! you should check to see if there is a user with that phone number 
            ! in the db or not if it is you need to check weather they are 
            ! the true owner of the phone an if yes delte the current user and chat instances
            ! and append the new data to the user instance with the phone number already in the db
            """
            update_user(db, chat_data.user_id, phone_number=text)
            update_chat_by_chat_id(
                db,
                chat.id,
                phone_input_attempt=0,
                pending_action="waiting_for_otp",
            )
            return bot_output.phone_numebr_verification(chat.id)
        if chat_data.pending_action == "waiting_for_otp":
            if text != "1111":
                return bot_output.invalid_otp(chat.id)
            return bot_output.phone_number_verified(chat.id)

    except Exception as e:
        logger.error(f"procces_text failed:{e}")
        raise
