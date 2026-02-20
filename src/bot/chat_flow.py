import re
from typing import Dict, Any, Optional, Union
from urllib.parse import urlencode
from decimal import Decimal

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select
from src.models import Chat, Product

from src.bot import TgChat
from src.bot.chat_output import TelegrambotOutputs

from src.crud.products import get_product_version_by_id, get_product_by_id
from src.crud import order
from src.crud import user

from src.config import logger
from src.config import settings

from src.services.pricing import get_version_price

_PHONE_PATTERN = re.compile(r"^09\d{9}$")


def chat_first_level_authentication(
    outputs: TelegrambotOutputs,
    db: Session,
    data: Optional[TgChat] = None,
    chat_db: Optional[Chat] = None,
) -> Dict[str, Any] | bool:
    try:

        chat = chat_db or user.get_chat_by_chat_id(db, chat_id=data.id)
        if chat is None:
            new_user = user.create_user(db)
            user.create_chat(
                db,
                user_id=new_user.id,
                chat_id=data.id,
                first_name=data.first_name,
                username=data.username,
            )

            return outputs.terms_and_conditions(data.id, append=True)
        if not chat.accepted_terms:
            return outputs.terms_and_conditions(chat.chat_id, append=True)
        return True
    except Exception as e:
        logger.error(f"chat_first_level_authentication failed: {e}")
        raise


def chat_second_lvl_authentication(
    outputs: TelegrambotOutputs, db: Session, chat: Chat
) -> Dict[str, Any] | bool:
    try:
        if chat.chat_verified is not True:
            user = chat.user
            if not user.phone_number:
                user.update_chat(db, chat.id, pending_action="waiting_for_phone_number")
                return outputs.phone_number_input(chat.chat_id)
            if not user.phone_number_validated:
                return outputs.phone_number_verfication_needed(
                    chat.chat_id, phone_number=user.phone_number
                )
            return outputs.chat_verification_needed(
                chat_id=chat.chat_id, phone_number=user.phone_number
            )

        return True
    except Exception as e:
        logger.error(f"chat_second_level_authentication failed: {e}")
        raise


def buy_product(
    outputs: TelegrambotOutputs, db: Session, chat: Chat, product_id: int
) -> Dict | None:
    try:

        product = get_product_by_id(db=db, id=product_id)
        versions_prices = get_product_prices(db=db, product=product)
        return outputs.buy_product(
            chat_id=chat.chat_id,
            product=product,
            versions_prices=versions_prices,
        )
    except Exception as e:
        logger.error(f"but_product at chat flow failed:{e}")
        raise


def edit_phone_number(outputs: TelegrambotOutputs, db: Session, chat: Chat):
    try:

        user.update_chat(
            db=db,
            chat_id_pk=chat.id,
            chat_verified=False,
            pending_action="waiting_for_phone_number",
        )
        return outputs.phone_number_input(chat_id=chat.chat_id)
    except Exception as e:
        logger.error(f"edit_phone_number at chat flow failed:{e}")
        raise


def buy_product_version(
    outputs: TelegrambotOutputs, db: Session, chat: Chat, product_version_id: int
) -> Dict | None:
    try:
        auth = chat_second_lvl_authentication(db=db, chat=chat)
        if auth is not True:
            return auth
        product_version = get_product_version_by_id(db=db, id=product_version_id)
        product_version_price = get_version_price(version=product_version, db=db)
        order_data = order.create_order_with_items(
            db=db,
            user_id=chat.user_id,
            items=[order.CreateOrderItemIn(product_version_id=int(product_version_id))],
            commit=True,
        )
        return outputs.buy_product_version(
            chat_id=chat.chat_id,
            product_version=product_version,
            price=product_version_price,
            order_id=order_data.id,
        )
    except Exception as e:
        logger.error(f"buy_product_version at chat flow failed:{e}")
        raise


def phone_number_input(
    outputs: TelegrambotOutputs, db: Session, phone_number: str, chat_data: Chat
):
    try:
        valid_phone_number = phone_number_authenticator(phone_number)
        if not valid_phone_number:
            attempts = chat_data.phone_input_attempt
            if attempts >= 2:
                user.update_chat(
                    db, chat_data.id, phone_input_attempt=0, pending_action=None
                )
                return outputs.max_attempt_reached(chat_data.chat_id)
            user.update_chat(db, chat_data.id, phone_input_attempt=attempts + 1)
            return outputs.invalid_phone_number(chat_data.chat_id)
        user_with_the_same_phone = user.get_user_by_phone(db, phone_number=phone_number)
        if (
            user_with_the_same_phone
            and chat_data.user_id != user_with_the_same_phone.id
        ):
            user.update_chat(db=db, chat_id_pk=chat_data.id, pending_action=None)
            return outputs.login_to_acount(
                chat_id=chat_data.chat_id, phone_number=phone_number
            )
        updated_chat = user.update_chat(
            db=db, chat_id_pk=chat_data.id, pending_action=None
        )
        user.update_user(db=db, user_id=chat_data.user_id, phone_number=phone_number)
        return chat_second_lvl_authentication(db=db, chat=updated_chat)

    except Exception as e:
        logger.error(f"phone_number_input failed at chat flow:{e}")
        raise


def login(outputs: TelegrambotOutputs, db: Session, chat: Chat, phone_number: str):
    try:

        user_to_login_to = user.get_user_by_phone(db=db, phone_number=phone_number)
        if chat.user.id == user_to_login_to.id:
            return outputs.already_logged_in(
                chat_id=chat.chat_id, phone_number=phone_number
            )

        updated_chat = user.update_chat(
            db=db, chat_id_pk=chat.id, user_id=user_to_login_to.id, chat_verified=False
        )
        return chat_second_lvl_authentication(db=db, chat=updated_chat)
    except Exception as e:
        logger.error(f"login at chat_flow failed:{e}")
        raise


def send_otp(outputs: TelegrambotOutputs, db: Session, chat: Chat):
    try:

        #! this is a placeholder for when we actually send the otp
        user.update_chat(db=db, chat_id_pk=chat.id, pending_action="waiting_for_otp")
        return outputs.phone_numebr_verification(chat_id=chat.chat_id)
    except Exception as e:
        logger.error(f"send_otp at chat flow failed:{e}")
        raise


def otp_verify(outputs: TelegrambotOutputs, db: Session, text: str, chat: Chat):
    try:

        if not text == "1111":  #!This is very much a place holder for later
            attemps = chat.otp_input_attempt
            if attemps >= 2:
                user.update_chat(
                    db=db, chat_id_pk=chat.id, otp_input_attempt=0, pending_action=None
                )
                return outputs.max_attempt_reached(chat_id=chat.chat_id)
            user.update_chat(db=db, chat_id_pk=chat.id, otp_input_attempt=attemps + 1)
            return outputs.invalid_otp(chat.chat_id)
        user.update_chat(
            db=db,
            chat_id_pk=chat.id,
            pending_action=None,
            otp_input_attempt=0,
            chat_verified=True,
        )
        user.update_user(db=db, user_id=chat.user_id, phone_number_validated=True)
        return outputs.phone_number_verified(chat.chat_id)
    except Exception as e:
        logger.error(f"otp_verify at chat flow failed: {e}")
        raise


def is_last_message(
    outputs: TelegrambotOutputs,
    message_id: Union[str, int],
    db: Session,
    chat: Optional[Chat] = None,
    chat_id: Optional[Union[str, int]] = None,
):
    try:
        if chat_id is None and chat is None:
            raise ValueError("when chat is None chat_id cannot be None")
        chat = user.get_chat_by_chat_id(db, chat_id) if chat is None else chat
        if chat is None:
            return False
        last_message_id = chat.last_message_id
        if last_message_id is None:
            user.update_chat_by_chat_id(
                db=db, chat_id=chat.chat_id, last_message_id=int(message_id)
            )
            return True
        if int(message_id) > last_message_id:
            user.update_chat_by_chat_id(
                db, chat.chat_id, last_message_id=int(message_id)
            )
            return True
        if int(message_id) == last_message_id:
            return True
        return False
    except Exception as e:
        logger.error(f"is_last_message function failed:{e}")
        raise


def get_prices(
    outputs: TelegrambotOutputs,
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


def payment_gateway(
    outputs: TelegrambotOutputs, db: Session, chat: Chat, order_id: Union[str, int]
):
    try:
        order_data = order.get_order(db=db, order_id=order_id)
        order_item = order.items[0]
        product_version_id = order_item.product_version_id
        unit_price = order_item.unit_price
        product_version = get_product_version_by_id(db=db, id=product_version_id)
        product_name = product_version.product.name
        return outputs.payment_gateway(
            chat_id=chat.chat_id,
            order_id=order_data.id,
            product_name=product_name,
            amount=unit_price,
            pay_url=f"{settings.base_url}/pay?{urlencode({"order_id":order_id})}",
        )
    except Exception as e:
        logger.error(f"payment_gateway at chat_flow failed:{e}")
        raise


def cancel_order(
    outputs: TelegrambotOutputs, db: Session, chat: Chat, order_id: Union[int, str]
):
    order.delete_order(db=db, order_id=order_id)
    return outputs.return_to_menu(chat_id=chat.chat_id)


def confirm_payment(
    outputs: TelegrambotOutputs, db: Session, chat: Chat, order_id: Union[int, str]
):
    order_data = order.get_order(db=db, order_id=order_id)
    if order_data.status != "paid":
        return outputs.payment_confirmed(chat_id=chat.chat_id, order_id=order_id)
    return outputs.payment_not_confirmed(chat_id=chat.chat_id, order_id=order_id)


def crypto_payment(
    outputs: TelegrambotOutputs, db: Session, chat: Chat, order_id: Union[str, int]
): ...


def get_product_prices(
    outputs: TelegrambotOutputs, db: Session, product: Product
) -> Dict[str, Any]:
    try:
        version_map: Dict[str, Decimal | str] = {}
        for version in product.versions:
            price = get_version_price(version, db)
            version_map[version.version_name] = price
        return version_map

    except Exception as e:
        logger.error(f"get_product_prices at services failed:{e}")
        raise


def phone_number_authenticator(outputs: TelegrambotOutputs, phone: str) -> bool:
    return bool(_PHONE_PATTERN.match(phone))
