from typing import Dict, Any
from sqlalchemy.orm import Session
from src.config import logger
from src.bot.chat_output import TelegrambotOutputs
from src.bot import TgChat, NotPrivateChat, UnsuportedTextInput
from src.crud.products import get_products
from src.bot.chat_flow import (
    chat_first_level_authentication,
    is_last_message,
    phone_number_input,
    otp_verify,
    buy_product_version,
    buy_product,
    edit_phone_number,
    send_otp,
    login,
    cancel_order,
    crypto_payment,
    payment_gateway,
    confirm_payment,
)
from src.crud.user import (
    get_chat_by_chat_id,
    update_chat_by_chat_id,
)


def serialize_message(
    payload: Dict[str, Any], outputs: TelegrambotOutputs, db: Session
) -> Dict[str, Any]:
    try:

        chat_data = payload.get("chat") or {}
        from_data = payload.get("from") or {}
        if chat_data.get("type") != "private":
            raise NotPrivateChat("Only private chats are supported.")
        if chat_data.get("id") != from_data.get("id"):
            raise NotPrivateChat("chat.id and from.id must match for private messages.")
        chat = TgChat(**chat_data)
        data = payload.get("text")
        return process_text(chat=chat, text=data, db=db, outputs=outputs)

    except Exception as e:
        logger.error(f"serialize_message failed:{e}")
        raise


def serialize_callback_query(
    payload: Dict[str, Any], outputs: TelegrambotOutputs, db: Session
) -> Dict[str, Any]:
    try:
        from_data = payload.get("from") or {}
        chat_id = from_data.get("id")
        message = payload.get("message")
        message_id = message.get("message_id")
        query_data = payload.get("data")
        query_id = payload.get("id")
        return process_callback_query(
            query_id=query_id,
            chat_id=chat_id,
            query_data=query_data,
            message_id=message_id,
            db=db,
            outputs=outputs,
        )
    except Exception as e:
        logger.error(f"serialize_callback_query failed:{e}")
        raise


def process_callback_query(
    query_id: str,
    chat_id: str,
    query_data: str,
    message_id: str,
    db: Session,
    outputs: TelegrambotOutputs,
):
    try:
        chat = get_chat_by_chat_id(db, chat_id)
        last_message = is_last_message(message_id=message_id, db=db, chat=chat)

        if chat.pending_action is not None:
            return outputs.empty_answer_callback(query_id)

        if query_data == "show_terms_for_acceptance":
            return outputs.show_terms_condititons(chat_id, message_id)

        if query_data == "read_the_terms":
            return outputs.terms_and_conditions(chat_id, message_id)

        if query_data == "accepted_terms":
            if not chat.accepted_terms:
                update_chat_by_chat_id(db, chat_id, accepted_terms=True)
                products = get_products(db=db)
                return outputs.return_to_menu(
                    products=products, chat_id=chat_id, append=True
                )
            return outputs.empty_answer_callback(query_id)

        if query_data == "show_prices":
            return outputs.loading_prices(chat_id)

        if query_data == "return_to_menu":
            products = get_products(db=db)
            return (
                outputs.return_to_menu(
                    products=products, chat_id=chat_id, message_id=message_id
                )
                if last_message is True
                else outputs.return_to_menu(
                    products=products,
                    chat_id=chat_id,
                    message_id=message_id,
                    append=True,
                )
            )
        if query_data == "show_terms":
            return (
                outputs.show_terms_condititons(chat_id, message_id)
                if last_message is True
                else outputs.show_terms_condititons(chat_id, message_id, append=True)
            )

        if query_data == "support":
            return (
                outputs.support(chat_id, message_id)
                if last_message is True
                else outputs.support(chat_id, message_id, append=True)
            )

        if query_data == "contact_support":
            return (
                outputs.contact_support_info(chat_id, message_id)
                if last_message is True
                else outputs.contact_support_info(chat_id, message_id, append=True)
            )
        if query_data == "return_to_support":
            return (
                outputs.support(chat_id, message_id)
                if last_message is True
                else outputs.support(chat_id, message_id, True)
            )
        if query_data == "common_questions":
            return (
                outputs.common_questions(chat_id, message_id)
                if last_message is True
                else outputs.common_questions(chat_id, message_id, True)
            )

        if query_data == "edit_phone_number":
            return edit_phone_number(db=db, chat=chat, outputs=outputs)

        if query_data == "send_validation_code":
            return send_otp(outputs=outputs, db=db, chat=chat)

        if query_data.startswith("buy_product:"):
            _, product_id = query_data.split(":", 1)
            return buy_product(
                outputs=outputs, db=db, chat=chat, product_id=int(product_id)
            )

        if query_data.startswith("buy_product_version:"):
            _, prodcut_version_id = query_data.split(":", 1)
            return buy_product_version(
                outputs=outputs,
                db=db,
                chat=chat,
                product_version_id=int(prodcut_version_id),
            )
        if query_data.startswith("login_to_acount:"):
            _, phone_number = query_data.split(":", 1)
            return login(outputs=outputs, db=db, chat=chat, phone_number=phone_number)

        if query_data.startswith("payment_gateway:"):
            _, order_id = query_data.split(":", 1)
            return payment_gateway(outputs=outputs, db=db, chat=chat, order_id=order_id)

        if query_data.startswith("crypto_payment:"):
            _, order_id = query_data.split(":", 1)
            return crypto_payment(outputs=outputs, db=db, chat=chat, order_id=order_id)

        if query_data.startswith("cancel_order:"):
            _, order_id = query_data.split(":", 1)
            return cancel_order(outputs=outputs, db=db, chat=chat, order_id=order_id)

        if query_data.startswith("confirm_payment:"):
            _, order_id = query_data.split(":", 1)
            return confirm_payment(outputs=outputs, db=db, chat=chat, order_id=order_id)

        else:
            logger.error(
                f"process_callback_query failed: the the query data is unknown: {query_data}"
            )
            raise ValueError("unknown command")
    except Exception as e:
        logger.error(f"proccess_callback_query failed:{e}")
        raise


def process_text(
    outputs: TelegrambotOutputs, chat: TgChat, text: str, db: Session
) -> Dict[str, Any]:
    try:
        chat_data = get_chat_by_chat_id(db, chat.id)
        auth = chat_first_level_authentication(db=db, data=chat, chat_db=chat_data)
        if auth is not True:
            return auth
        if text == "/start":
            products = get_products(db=db)
            return outputs.return_to_menu(
                products=products, chat_id=chat.id, append=True
            )
        if chat_data.pending_action == "waiting_for_phone_number":
            return phone_number_input(
                outputs=outputs, db=db, phone_number=text, chat_data=chat_data
            )
        if chat_data.pending_action == "waiting_for_otp":
            return otp_verify(outputs=outputs, db=db, text=text, chat=chat_data)
        else:
            raise UnsuportedTextInput("unsupported command or text input")
    except Exception as e:
        logger.error(f"procces_text failed:{e}")
        raise
