import re
from typing import Dict, Any, Optional, Union
from decimal import Decimal
from src.services.pricing import get_version_price
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select
from src.config import logger
from src.models import Chat, Product
from src.bot.chat_output import telegram_process_bot_outputs as bot_output
from src.bot import TgChat
from src.crud.user import (
    get_chat_by_chat_id,
    create_chat,
    update_chat_by_chat_id,
    create_user,
    update_user,
    update_chat,
)

_PHONE_PATTERN = re.compile(r"^09\d{9}$")


def chat_first_level_authentication(
    db: Session, data: Optional[TgChat] = None, chat_db: Optional[Chat] = None
) -> Dict[str, Any] | bool:
    try:

        chat = chat_db or get_chat_by_chat_id(db, chat_id=data.id)
        if chat is None:
            new_user = create_user(db)
            create_chat(
                db,
                user_id=new_user.id,
                chat_id=data.id,
                first_name=data.first_name,
                username=data.username,
            )

            return bot_output.terms_and_conditions(data.id, append=True)
        if not chat.accepted_terms:
            return bot_output.terms_and_conditions(chat.chat_id, append=True)
        return True
    except Exception as e:
        logger.error(f"chat_first_level_authentication failed: {e}")
        raise


def chat_second_lvl_authentication(db: Session, chat: Chat) -> Dict[str, Any] | bool:
    try:
        user = chat.user
        if not user.phone_number:
            update_chat(db, chat.id, pending_action="waiting_for_phone_number")
            return bot_output.phone_number_input(chat.chat_id)
        if not user.phone_number_validated:
            return bot_output.phone_number_verfication_needed(chat.chat_id)
        return True
    except Exception as e:
        logger.error(f"chat_second_level_authentication failed: {e}")
        raise


def phone_number_input(db: Session, phone_number: str, chat_data: Chat):
    valid_phone_number = phone_number_authenticator(phone_number)
    if not valid_phone_number:
        attempts = chat_data.phone_input_attempt
        if attempts >= 3:
            update_chat(db, chat_data.id, phone_input_attempt=0, pending_action=None)
            return bot_output.phone_max_attempt(chat_data.id)
        update_chat(db, chat_data.id, phone_input_attempt=attempts + 1)
        return bot_output.invalid_phone_number(chat_data.id)
    """
    ! we haven't reached that part yet but when we do 
    ! you should check to see if there is a user with that phone number 
    ! in the db or not if it is you need to check weather they are 
    ! the true owner of the phone an if yes delte the current user and chat instances
    ! and append the new data to the user instance with the phone number already in the db
    """
    update_user(db, chat_data.user_id, phone_number=phone_number)
    update_chat(
        db,
        chat_data.id,
        phone_input_attempt=0,
        pending_action="waiting_for_otp",
    )
    return bot_output.phone_numebr_verification(chat_data.id)


def otp_verify(text: str, chat: Chat):
    #!This is very much a place holder for later
    if text != "1111":
        return bot_output.invalid_otp(chat.id)
    return bot_output.phone_number_verified(chat.id)


def is_last_message(
    message_id: Union[str, int],
    db: Session,
    chat: Optional[Chat] = None,
    chat_id: Optional[Union[str, int]] = None,
):
    try:
        if chat_id is None and chat is None:
            raise ValueError("when chat is None chat_id cannot be None")
        chat = get_chat_by_chat_id(db, chat_id) if chat is None else chat
        if chat is None:
            return False
        last_message_id = chat.last_message_id
        if last_message_id is None:
            update_chat_by_chat_id(
                db=db, chat_id=chat.chat_id, last_message_id=int(message_id)
            )
            return True
        if int(message_id) > last_message_id:
            update_chat_by_chat_id(db, chat.chat_id, last_message_id=int(message_id))
            return True
        if int(message_id) == last_message_id:
            return True
        return False
    except Exception as e:
        logger.error(f"is_last_message function failed:{e}")
        raise


def get_prices(
    db: Session,
) -> Dict[str, Any]:
    try:
        stmt = (
            select(Product)
            .where(Product.display_in_bot.is_(True))
            .options(joinedload(Product.versions))
        )

        products = db.execute(stmt).unique().scalars().all()
        result: Dict[str, Dict[str, Decimal]] = {}

        for product in products:
            product_key = f"{product.name}"

            version_map: Dict[str, Decimal | str] = {}
            for version in product.versions:
                price = get_version_price(version, db)
                version_map[version.version_name] = price

            result[product_key] = version_map
        return result
    except Exception as e:
        logger.error(f"chat_flow/get_prices failed:{e}")
        raise


def get_product_prices(db: Session, product: Product) -> Dict[str, Any]:
    try:
        version_map: Dict[str, Decimal | str] = {}
        for version in product.versions:
            price = get_version_price(version, db)
            version_map[version.version_name] = price
        return version_map

    except Exception as e:
        logger.error(f"get_product_prices at services failed:{e}")
        raise


def phone_number_authenticator(phone: str) -> bool:
    return bool(_PHONE_PATTERN.match(phone))
