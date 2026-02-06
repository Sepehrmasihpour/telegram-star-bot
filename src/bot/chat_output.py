import re

from typing import Union, Dict, List
from src.models import Product, ProductVersion, ChatOutput
from textwrap import dedent
from typing import Optional
from decimal import Decimal
from typing import Any
from sqlalchemy.orm import Session
from src.crud.chat_outpus import get_chat_output_by_name


def _t(s: str) -> str:
    """Normalize multi-line text: remove common indent and trim outer whitespace."""
    return dedent(s).strip()


PLACEHOLDER_RE = re.compile(r"{(\w+)}")


def _fill_placeholders(text: str, **fields: str) -> str:
    needed = set(PLACEHOLDER_RE.findall(text))
    provided = set(fields.keys())

    missing = needed - provided
    if missing:
        raise ValueError(f"Missing placeholders: {missing}")

    return text.format(**fields)


def _map_buttons_in_order(
    chat_output: ChatOutput,
    row_size: int = 1,
    button_url: Optional[str] = None,
    **placeholders,
) -> list[list[dict]]:
    buttons = sorted(chat_output.button_indexes, key=lambda bi: bi.number)

    rendered = []
    for bi in buttons:
        btn = bi.button
        rendered.append(
            {
                "text": _fill_placeholders(btn.text, **placeholders),
                "callback_data": _fill_placeholders(btn.callback_data, **placeholders),
            }
            if button_url is None
            else {
                "text": _fill_placeholders(btn.text, **placeholders),
                "callback_data": _fill_placeholders(btn.callback_data, **placeholders),
                "url": button_url,
            }
        )

    return [rendered[i : i + row_size] for i in range(0, len(rendered), row_size)]


def _render_chat_outputs(
    template: ChatOutput,
    chat_id: Union[str, int],
    row_size: int = 1,
    message_id: Optional[Union[str, int]] = None,
    method: Optional[str] = None,
    button_url: Optional[str] = None,
    **placeholders,
) -> dict:
    """
    Render a ChatOutput template into a Telegram-ready payload.
    """

    # Normalize text
    raw_text = _t(template.text)

    # Fill placeholders
    rendered_text = _fill_placeholders(raw_text, **placeholders)

    # Render buttons
    keyboard = _map_buttons_in_order(
        chat_output=template, row_size=row_size, button_url=button_url, **placeholders
    )
    params = {
        "chat_id": chat_id,
        "text": rendered_text,
        "parse_mode": "Markdown",
    }
    if message_id is not None:
        params["message_id"] = message_id
    if keyboard is not None:
        params["reply_markup"] = {"inline_keyboard": keyboard}

    return params if method is None else {"method": method, "params": params}


EMOJI_PAIRINGS = {"Premium Stars Pack": "🌟", "Telegram Premium Upgrade": "💎"}


class TelegrambotOutputs:
    def __init__(self):
        # outputs chche data
        self._chat_output_cache: Dict[str, ChatOutput] = {}

    def _get_template(self, db: Session, name: str) -> ChatOutput:
        template = self._chat_output_cache.get(name)
        if template is None:
            template = get_chat_output_by_name(db=db, name=name)
            self._chat_output_cache[name] = template
        return template

    def _render(
        self,
        db: Session,
        name: str,
        chat_id: Union[str, int],
        method: Optional[str] = None,
        message_id: Optional[Union[str, int]] = None,
        button_url: Optional[str] = None,
        **placeholders,
    ):
        template = self._get_template(db, name=name)
        return _render_chat_outputs(
            template=template,
            chat_id=chat_id,
            method=method,
            message_id=message_id,
            button_url=button_url,
            **placeholders,
        )

    def _render_with_keyboard_append_template(
        self,
        db: Session,
        name: str,
        chat_id: Union[str, int],
        dynamic_keyboard: list[list[dict]],
        row_size: int = 1,
        method: str | None = None,
        message_id: str | int | None = None,
        **placeholders,
    ) -> dict:
        """
        Render DB template text, then build:
        final_keyboard = dynamic_keyboard + template_keyboard(rendered from DB)
        Template keyboard remains editable in DB.
        """

        template = self._get_template(db=db, name=name)

        # Render text + other params using normal flow
        payload = _render_chat_outputs(
            template=template,
            chat_id=chat_id,
            row_size=row_size,
            method=method,
            message_id=message_id,
            **placeholders,
        )

        # Render template keyboard (from DB) with placeholders
        template_keyboard = _map_buttons_in_order(
            chat_output=template, row_size=row_size, **placeholders
        )

        # Merge: dynamic first, template buttons appended
        final_keyboard = (dynamic_keyboard or []) + (template_keyboard or [])

        if method is None:
            payload["reply_markup"] = {"inline_keyboard": final_keyboard}
            return payload

        payload["params"]["reply_markup"] = {"inline_keyboard": final_keyboard}
        return payload

    def _custom(self, chat_id: Union[str, int], custom: str, message: dict) -> dict:
        """
        Internal action envelope (non-Telegram). Keeps your special transport feature.
        """
        return {
            "method": "custom",
            "params": {
                "chat_id": chat_id,
                "custom": custom,
                "message": message,
            },
        }

    def unsupported_command(self, db: Session, chat_id: Union[str, int]):
        return self._render(db=db, name="unsupported_command", chat_id=chat_id)

    def phone_number_input(self, db: Session, chat_id: Union[str, int]):
        return self._render(db=db, name="phone_number_input", chat_id=chat_id)

    def phone_number_verification_needed(
        self, chat_id: Union[str, int], db: Session, phone_number: str
    ):
        return self._render(
            db=db,
            name="phone_number_verification_needed",
            chat_id=chat_id,
            phone_number=phone_number,
        )

    def authentication_failed(self, db: Session, chat_id: Union[str, int]):
        return self._render(db=db, name="authentication_failed", chat_id=chat_id)

    def max_attempt_reached(self, db: Session, chat_id: Union[str, int]):
        return self._render(db=db, name="max_attempt_reached", chat_id=chat_id)

    def invalid_phone_number(self, db: Session, chat_id: Union[str, int]):
        return self._render(db=db, name="invalid_phone_number", chat_id=chat_id)

    def invalid_otp(self, db: Session, chat_id: Union[str, int]):
        return self._render(db=db, name="invalid_otp", chat_id=chat_id)

    def chat_verification_needed(
        self, db: Session, chat_id: Union[str, int], phone_number: str
    ):
        return self._render(
            db=db,
            name="chat_verification_needed",
            chat_id=chat_id,
            phone_number=phone_number,
        )

    def login_to_acount(self, db: Session, chat_id: Union[str, int], phone_number: str):
        return self._render(
            db=db,
            name="login_to_acount",
            chat_id=chat_id,
            phone_number=phone_number,
        )

    def already_logged_in(
        self, db: Session, chat_id: Union[str, int], phone_number: str
    ):
        return self._render(
            db=db,
            name="already_logged_in",
            chat_id=chat_id,
            phone_number=phone_number,
        )

    def phone_numebr_verification(self, db: Session, chat_id: Union[str, int]):
        return self._render(db=db, name="phone_numebr_verification", chat_id=chat_id)

    def phone_number_verified(self, db: Session, chat_id: Union[str, int]):
        return self._render(db=db, name="phone_number_verified", chat_id=chat_id)

    def loading_prices(self, db: Session, chat_id: Union[str, int]) -> dict:
        message = self._render(db=db, name="loading_prices_message", chat_id=chat_id)
        return self._custom(chat_id=chat_id, custom="get_prices", message=message)

    def get_prices(
        self,
        db: Session,
        chat_id: Union[str, int],
        prices: Dict[str, Dict[str, Decimal | str]],
        message_id: str | int | None = None,
        append: bool = True,
    ) -> Dict[str, Any]:

        lines: list[str] = []
        for product_name, variations in prices.items():
            emoji = EMOJI_PAIRINGS.get(product_name, "")
            lines.append(f"{emoji} *{product_name}*")
            for variation, value in variations.items():
                if isinstance(value, Decimal):
                    normalized = value.quantize(Decimal("1"))
                    price_str = f"{normalized:,} T"
                else:
                    price_str = f"{value:,} T"
                lines.append(f"    ➜ **{variation}**")
                lines.append(f"    💰 price: {price_str}")
            lines.append("━━━━━━━━━━━━━━━━━━━━")
            lines.append("")

        prices_block = _t("\n".join(lines))

        if append:
            return self._render(
                db=db,
                name="get_prices",
                chat_id=chat_id,
                prices_block=prices_block,
            )

        if message_id is None:
            raise ValueError("message_id can't be None when append is False")

        return self._render(
            db=db,
            name="get_prices",
            chat_id=chat_id,
            method="editMessageText",
            message_id=message_id,
            prices_block=prices_block,
        )

    def buy_product(
        self,
        db: Session,
        chat_id: Union[str, int],
        product: Product,
        versions_prices: Dict[str, Any],
        message_id: str | int | None = None,
        append: bool = True,
    ) -> Dict[str, Any]:
        emoji = EMOJI_PAIRINGS.get(product.name, "🛒")

        # dynamic prices block for template text
        lines: list[str] = []
        for version_name, version_price in versions_prices.items():
            lines.append(f"{emoji} **{version_name}**")
            lines.append(f"💰 **price: {version_price}**")
            lines.append("━━━━━━━━━━━━━━━━━━━━")
            lines.append("")
        prices_block = _t("\n".join(lines))

        # dynamic keyboard: one per version
        dynamic_rows = [
            [
                {
                    "text": f"🛒 {v.version_name}",
                    "callback_data": f"buy_product_version:{v.id}",
                }
            ]
            for v in (product.versions or [])
        ]

        if append:
            return self._render_with_keyboard_append_template(
                db=db,
                name="buy_product",
                chat_id=chat_id,
                dynamic_keyboard=dynamic_rows,
                product_name=product.name,
                prices_block=prices_block,
            )

        if message_id is None:
            raise ValueError("message_id can't be None when append is False")

        return self._render_with_keyboard_append_template(
            db=db,
            name="buy_product",
            chat_id=chat_id,
            dynamic_keyboard=dynamic_rows,
            method="editMessageText",
            message_id=message_id,
            product_name=product.name,
            prices_block=prices_block,
        )

    def buy_product_version(
        self,
        db: Session,
        chat_id: Union[int, str],
        product_version: ProductVersion,
        price: Decimal,
        order_id: int,
    ):
        product = product_version.product
        product_name = product.name
        product_version_name = product_version.version_name

        return self._render(
            db=db,
            name="buy_product_version",
            chat_id=chat_id,
            product_name=product_name,
            product_version_name=product_version_name,
            price=price,
            order_id=order_id,
        )

    def payment_gateway(
        self,
        db: Session,
        chat_id: Union[str, int],
        order_id: Union[str, int],
        product_name: str,
        amount: Union[Decimal, int, str],
        pay_url: str,
    ):
        return self._render(
            db=db,
            name="payment_gateway",
            chat_id=chat_id,
            product_name=product_name,
            amount=amount,
            button_url=pay_url,
            order_id=order_id,
        )

    def payment_confirmed(
        self, db: Session, chat_id: Union[int, str], order_id: Union[int, str]
    ):
        return self._render(
            db=db,
            name="payment_confirmed",
            chat_id=chat_id,
            order_id=order_id,
        )

    def payment_not_confirmed(
        self, db: Session, chat_id: Union[int, str], order_id: Union[int, str]
    ):
        return self._render(
            db=db,
            name="payment_not_confirmed",
            chat_id=chat_id,
            order_id=order_id,
        )

    @staticmethod
    def empty_answer_callback(query_id: Union[str, int]):
        return {
            "method": "answerCallback",
            "params": {"callback_query_id": query_id},
        }

    """
    ! VERY VERY IMPORTANT
    ! The former structure of this output was so that depending
    ! of the paramater of form:bool it would either have a read_terms button
    ! or a return to menu button. Given the change to the handling of the outputs
    ! I have deleted that param and it will render both buttons each time
    ! so the flow needs to be handled in a lower level 
    
    """

    def show_terms_condititons(
        self,
        db: Session,
        chat_id: Union[str, int],
        message_id: str | int | None = None,
        append: bool = True,
    ) -> dict:
        if append:
            return self._render(db=db, name="show_terms_condititons", chat_id=chat_id)

        if message_id is None:
            raise ValueError("when append is False, message_id cannot be None")

        return self._render(
            db=db,
            name="show_terms_condititons",
            chat_id=chat_id,
            method="editMessageText",
            message_id=message_id,
        )

    def terms_and_conditions(
        self,
        db: Session,
        chat_id: Union[str, int],
        message_id: Optional[Union[str, int]] = None,
        append: Optional[bool] = False,
    ):
        if message_id is None and append is False:
            raise ValueError("when append is false message_id cannot be None")

        return (
            self._render(db=db, name="terms_and_conditions", chat_id=chat_id)
            if append is True
            else self._render(
                db=db,
                name="terms_and_conditions",
                chat_id=chat_id,
                method="editMessageText",
                message_id=message_id,
            )
        )

    def return_to_menu(
        self,
        db: Session,
        chat_id: Union[str, int],
        products: List[Product],
        message_id: str | int | None = None,
        append: bool = True,
    ) -> dict:
        # dynamic block for text
        if products:
            product_lines = []
            for p in products:
                emoji = EMOJI_PAIRINGS.get(p.name, "🛒")
                product_lines.append(f"{emoji} *{p.name}*")
            products_block = "\n".join(product_lines)
        else:
            products_block = "• *(No products are available right now.)*"

        # dynamic keyboard: one button per product
        dynamic_rows = [
            [{"text": f"🛒 Buy {p.name}", "callback_data": f"buy_product:{p.id}"}]
            for p in (products or [])
        ]

        if append:
            return self._render_with_keyboard_append_template(
                db=db,
                name="return_to_menu",
                chat_id=chat_id,
                dynamic_keyboard=dynamic_rows,
                products_block=products_block,
            )

        if message_id is None:
            raise ValueError("message_id can't be None when append is False")

        return self._render_with_keyboard_append_template(
            db=db,
            name="return_to_menu",
            chat_id=chat_id,
            dynamic_keyboard=dynamic_rows,
            method="editMessageText",
            message_id=message_id,
            products_block=products_block,
        )

    def support(
        self,
        db: Session,
        chat_id: Union[str, int],
        message_id: Optional[Union[str, int]] = None,
        append: Optional[bool] = False,
    ):
        if message_id is None and append is False:
            raise ValueError(
                "telegram output support failed: message_id cannot be None when append is False"
            )

        return (
            self._render(db=db, name="support", chat_id=chat_id)
            if append is True
            else self._render(
                db=db,
                name="support",
                chat_id=chat_id,
                method="editMessageText",
                message_id=message_id,
            )
        )

    def contact_support_info(
        self,
        db: Session,
        chat_id: Union[str, int],
        message_id: Optional[Union[str, int]] = None,
        append: Optional[bool] = False,
    ):
        if message_id is None and append is False:
            raise ValueError("message_id can't be None when append is False")

        return (
            self._render(db=db, name="contact_support_info", chat_id=chat_id)
            if append is True
            else self._render(
                db=db,
                name="contact_support_info",
                chat_id=chat_id,
                method="editMessageText",
                message_id=message_id,
            )
        )

    def common_questions(
        self,
        db: Session,
        chat_id: Union[str, int],
        message_id: Optional[Union[int, str]],
        append: Optional[bool] = False,
    ):
        if message_id is None and append is False:
            raise ValueError("message_id can't be None when append is False")

        return (
            self._render(db=db, name="common_questions", chat_id=chat_id)
            if append is True
            else self._render(
                db=db,
                name="common_questions",
                chat_id=chat_id,
                method="editMessageText",
                message_id=message_id,
            )
        )


telegram_process_bot_outputs = TelegrambotOutputs()


# from typing import Union, Dict, List
# from src.models import Product, ProductVersion
# from textwrap import dedent
# from typing import Optional
# from decimal import Decimal
# from typing import Any
# from sqlalchemy.orm import Session
# from datetime import timedelta, datetime
# from src.crud.chat_outpus import get_chat_output_by_name


# def _t(s: str) -> str:
#     """Normalize multi-line text: remove common indent and trim outer whitespace."""
#     return dedent(s).strip()


# def _fill_placeholders(text: str, **fields: str) -> str:
#     # this will basicly do the job of f"" and find the words that have []
#     # with the fields value that has the same name
#     ...


# EMOJI_PAIRINGS = {"Premium Stars Pack": "🌟", "Telegram Premium Upgrade": "💎"}


# class TelegrambotOutputs:
#     def __init__(self, minutes_to_update: Optional[datetime] = 5):
#         # minutes left to update
#         self.minutes_to_update = minutes_to_update
#         self.unsupported_command_update_expiry = None
#         self.phone_number_input_update_expiry = None
#         self.phone_number_verfication_needed_update_expiry = None
#         self.authentication_failed_update_expiry = None
#         self.max_attempt_reached_update_expiry = None
#         self.invalid_phone_number_update_expiry = None
#         self.invalid_otp_update_expiry = None
#         self.chat_verification_needed_update_expiry = None
#         self.login_to_acount_update_expiry = None
#         self.already_logged_in_update_expiry = None
#         self.phone_numebr_verification_update_expiry = None
#         self.phone_number_verified_update_expiry = None
#         self.loading_prices_update_expiry = None
#         self.get_prices_update_expiry = None
#         self.buy_product_update_expiry = None
#         self.buy_product_version_update_expiry = None
#         self.payment_gateway_update_expiry = None
#         self.payment_confirmed_update_expiry = None
#         self.payment_not_confirmed_update_expiry = None
#         self.empty_answer_callback_update_expiry = None
#         self.show_terms_condititons_update_expiry = None
#         self.terms_and_conditions_update_expiry = None
#         self.return_to_menu_update_expiry = None
#         self.support_update_expiry = None
#         self.contact_support_info_update_expiry = None
#         self.common_questions_update_expiry = None

#         # outputs chche texts
#         self.unsupported_command.text = None

#     def _needs_update(self, update_expiry: datetime | None):
#         if not update_expiry:
#             return True
#         current_time = datetime.now()
#         if not update_expiry - current_time > 0:
#             return True
#         return False

#     def unsupported_command(self, db: Session, chat_id: Union[str, int]):
#         if (
#             self._needs_update(update_expiry=self.unsupported_command_update_expiry)
#             is True
#         ):
#             chat_output = get_chat_output_by_name(db=db, name="unsupported_command")
#             self.unsupported_command_text = chat_output.text
#             self.unsupported_command_update_expiry = datetime.now + timedelta(
#                 minutes=self.minutes_to_update
#             )

#         return {
#             "chat_id": chat_id,
#             "text": _t(_fill_placeholdres(self.unsupported_command_text)),
#         }

#     @staticmethod
#     def phone_number_input(chat_id: Union[str, int]):

#         return {
#             "chat_id": chat_id,
#             "text": _t(
#                 """
#                 🌟 **Welcome to the testing bot!**

#                 📱 **To start, please enter your phone number:**
#                 .enter the phone number in the 09123456789 format
#                 .the phone number must belong to you
#                 .this phone number is used for verifying your identity and direct payment

#                 💡 **Keep note:**
#                 .your phone number will remain safe and secret
#                 .it will only be used for verifying your identity and payment
#                 .you can change it at any time

#                 🔐 **Security:**
#                 .all your information is stored using encryption
#                 .no data will be shared with a third party
#                 """
#             ),
#             "parse_mode": "Markdown",
#         }

#     @staticmethod
#     def phone_number_verfication_needed(chat_id: Union[str, int], phone_number: str):
#         return {
#             "chat_id": chat_id,
#             "text": _t(
#                 f"""
#                 ❌ **Your phone number ({phone_number}) has not been verified**
#                 📱 In order to continue please verify your phone number.
#                 """
#             ),
#             "parse_mode": "Markdown",
#             "reply_markup": {
#                 "inline_keyboard": [
#                     [
#                         {
#                             "text": "📱send verification code to phone number",
#                             "callback_data": "send_validation_code",
#                         }
#                     ],
#                     [
#                         {
#                             "text": "📝Edit phone number",
#                             "callback_data": "edit_phone_number",
#                         }
#                     ],
#                     [
#                         {
#                             "text": "🔁 return to menu",
#                             "callback_data": "return_to_menu",
#                         }
#                     ],
#                 ]
#             },
#         }

#     @staticmethod
#     def authentication_failed(chat_id: Union[str, int]):
#         return {
#             "chat_id": chat_id,
#             "text": "*authentication failed*",
#             "parse_mode": "Markdown",
#         }

#     @staticmethod
#     def max_attempt_reached(chat_id: Union[str, int]):
#         return {
#             "chat_id": chat_id,
#             "text": "❌ *failed 3 times. canceled*",
#             "parse_mode": "Markdown",
#         }

#     @staticmethod
#     def invalid_phone_number(chat_id: Union[str, int]):
#         return {
#             "chat_id": chat_id,
#             "text": "❌ *phone number is invalid*",
#             "parse_mode": "Markdown",
#         }

#     @staticmethod
#     def invalid_otp(chat_id: Union[str, int]):
#         return {
#             "chat_id": chat_id,
#             "text": "❌ *validation code is invalid*",
#             "parse_mode": "Markdown",
#         }

#     @staticmethod
#     def chat_verification_needed(chat_id: Union[str, int], phone_number: str):
#         return {
#             "chat_id": chat_id,
#             "text": _t(
#                 f"""
#                 we need to make sure that this chat belongs to the user with this phone
#                 number {phone_number}

#                 """
#             ),
#             "reply_markup": {
#                 "inline_keyboard": [
#                     [
#                         {
#                             "text": "📱 send verification code to phone number",
#                             "callback_data": "send_validation_code",
#                         }
#                     ],
#                     [
#                         {
#                             "text": "📝 Edit phone number",
#                             "callback_data": "edit_phone_number",
#                         }
#                     ],
#                     [
#                         {
#                             "text": "🔁 return to menu",
#                             "callback_data": "return_to_menu",
#                         }
#                     ],
#                 ]
#             },
#             "parse_mode": "Markdown",
#         }

#     @staticmethod
#     def login_to_acount(chat_id: Union[str, int], phone_number: str):
#         return {
#             "chat_id": chat_id,
#             "text": _t(
#                 """
#                 ⚠️ ** Theres a user with this phone number **
#                 do you want to login to this acount or edit your phone number
#                 """
#             ),
#             "reply_markup": {
#                 "inline_keyboard": [
#                     [
#                         {
#                             "text": "🚪Login",
#                             "callback_data": f"login_to_acount:{phone_number}",
#                         }
#                     ],
#                     [
#                         {
#                             "text": "📝 Edit phone number",
#                             "callback_data": "edit_phone_number",
#                         }
#                     ],
#                     [
#                         {
#                             "text": "🔁 return to menu",
#                             "callback_data": "return_to_menu",
#                         }
#                     ],
#                 ]
#             },
#         }

#     @staticmethod
#     def already_logged_in(chat_id: Union[str, int], phone_number: str):
#         return {
#             "chat_id": chat_id,
#             "text": _t(
#                 f"""
#                 ❌ ** you are already logged in **
#                 you are currently logged in into the acount with the phone number
#                 of ({phone_number})
#                 """
#             ),
#             "reply_markup": {
#                 "inline_keyboard": [
#                     [
#                         {
#                             "text": "🔁 return to menu",
#                             "callback_data": "return_to_menu",
#                         }
#                     ],
#                 ]
#             },
#         }

#     @staticmethod
#     def phone_numebr_verification(chat_id: Union[str, int]):
#         return {
#             "chat_id": chat_id,
#             "text": _t(
#                 """
#                 ✅ **The verification code has been sent to your phone number.**
#                 Please enter the code.

#                 💳 **Important points about bank accounts:**
#                 .the account that you use for payment must belong to the owner of the phone number
#                 .the system verifies whether the phone number and the account number belong to the same person
#                 .in case they don't, your payment will not go through
#                 .if the account belongs to someone else, please use another account
#                 """
#             ),
#             "parse_mode": "Markdown",
#         }

#     @staticmethod
#     def phone_number_verified(chat_id: Union[str, int]):
#         return {
#             "chat_id": chat_id,
#             "text": _t(
#                 """
#                     ✅ **Phone number successfully verified!**
#                     🌟Showing the products...
#                     """
#             ),
#             "parse_mode": "Markdown",
#         }

#     @staticmethod
#     def loading_prices(chat_id: Union[str, int]):
#         return {
#             "method": "custom",
#             "payload": {
#                 "chat_id": chat_id,
#                 "custom": "get_prices",
#                 "message": {
#                     "chat_id": chat_id,
#                     "text": "💰 please wait a moment to get the most up to date prices",
#                 },
#             },
#         }

#     @staticmethod
#     def get_prices(
#         chat_id: Union[str, int],
#         prices: Dict[str, Dict[str, Decimal | str]],
#     ) -> Dict[str, Any]:
#         lines: list[str] = ["📊 **Current Prices:**", ""]

#         for product_name, variations in prices.items():
#             emoji = EMOJI_PAIRINGS.get(product_name, "🛒")
#             lines.append(f"{emoji} *{product_name}*\n")

#             for variation, value in variations.items():
#                 if isinstance(value, Decimal):
#                     normalized = value.quantize(Decimal("1"))
#                     price_str = f"{normalized:,} T"

#                 else:
#                     price_str = f"{value:,} T"

#                 lines.append(f"    ➜ **{variation}** ")
#                 lines.append(f"    💰price: {price_str}")
#                 lines.append("━━━━━━━━━━━━━━━━━━━━\n")
#         final_text = _t("\n".join(lines))
#         return {
#             "chat_id": chat_id,
#             "text": final_text,
#             "parse_mode": "Markdown",
#             "reply_markup": {
#                 "inline_keyboard": [
#                     [
#                         {
#                             "text": "return to main menu",
#                             "callback_data": "return_to_menu",
#                         }
#                     ],
#                 ]
#             },
#         }

#     @staticmethod
#     def buy_product(
#         chat_id: Union[str, int],
#         product: Product,
#         versions_prices,
#     ) -> Dict[str, Any]:
#         lines: List[str] = []
#         emoji = EMOJI_PAIRINGS.get(product.name, "🛒")
#         versions = product.versions
#         for version_name, version_price in versions_prices.items():
#             lines.append(f"{emoji} **{version_name}**")
#             lines.append(f"💰 **price:{version_price}**")
#             lines.append("━━━━━━━━━━━━━━━━━━━━\n")
#         prices_text = "\n".join(lines)
#         text = "\n".join(
#             [
#                 f"🎉 *Buying {product.name}!*",
#                 "",
#                 "**list of prices** 📋",
#                 "",
#                 prices_text,
#                 "",
#                 "💡 *In order to choose the desired product press the releavent button*",
#             ]
#         )
#         version_rows = [
#             [
#                 {
#                     "text": f"🛒 {v.version_name}",
#                     "callback_data": f"buy_product_version:{v.id}",
#                 }
#             ]
#             for v in versions
#         ]
#         keyboard = version_rows + [
#             [{"text": "return to menu 🔁", "callback_data": "return_to_menu"}]
#         ]
#         return {
#             "chat_id": chat_id,
#             "text": text,
#             "parse_mode": "Markdown",
#             "reply_markup": {"inline_keyboard": keyboard},
#         }

#     @staticmethod
#     def buy_product_version(
#         chat_id: Union[int, str],
#         product_version: ProductVersion,
#         price: Decimal,
#         order_id: int,
#     ):
#         product = product_version.product
#         product_name = product.name
#         emoji = EMOJI_PAIRINGS.get(product_name, "🛒")
#         text = "\n".join(
#             [
#                 "🛒 **Chosen product:",
#                 f"{emoji} {product.name}-{product_version.version_name}",
#                 "",
#                 f"💰 Price: {price}",
#                 "",
#                 "━━━━━━━━━━━━━━━━━━━━",
#                 "💳 please chose your payment method:",
#                 "",
#                 "💻 payment gateway-online payment with test gateway",
#                 "*₿* crypto-payment using crypto currency",
#                 "",
#                 "━━━━━━━━━━━━━━━━━━━━",
#             ]
#         )
#         keyboard = [
#             [
#                 {
#                     "text": "💻 payment gateway",
#                     "callback_data": f"payment_gateway:{order_id}",
#                 }
#             ],
#             [{"text": "₿ crypto", "callback_data": f"crypto_payment:{order_id}"}],
#             [{"text": "❌ cancel order", "callback_data": f"cancel_order:{order_id}"}],
#         ]
#         return {
#             "chat_id": chat_id,
#             "text": text,
#             "parse_mode": "Markdown",
#             "reply_markup": {"inline_keyboard": keyboard},
#         }

#     @staticmethod
#     def payment_gateway(
#         chat_id: Union[str, int],
#         order_id: Union[str, int],
#         product_name: ProductVersion,
#         amount: Union[Decimal, int, str],
#         pay_url: str,
#     ):
#         emoji = EMOJI_PAIRINGS.get(product_name, "🛒")

#         text = "\n".join(
#             [
#                 "💻 **Pay via Payment Gateway (Test Gateway)**",
#                 "",
#                 f"📦 Product: {emoji} {product_name}",
#                 f"💰 Amount: {amount}",
#                 "",
#                 "━━━━━━━━━━━━━━━━━━━━",
#                 "",
#                 "📝 **Instructions:**",
#                 '1️⃣ Tap **"Pay Invoice"**',
#                 "2️⃣ Review the invoice details",
#                 "3️⃣ Tap **Online Payment** on the invoice page",
#                 "4️⃣ You will be redirected to the payment gateway",
#                 "5️⃣ Enter your card/bank details",
#                 '6️⃣ After a successful payment, tap **"I Paid"** here',
#                 "",
#                 f"🆔 Invoice ID: `{order_id}`",
#                 "",
#                 "━━━━━━━━━━━━━━━━━━━━",
#             ]
#         )

#         keyboard = [
#             [{"text": "💳 Pay Invoice", "url": pay_url}],
#             [{"text": "✅ I Paid", "callback_data": f"confirm_payment:{order_id}"}],
#             [{"text": "❌ Cancel Order", "callback_data": f"cancel_order:{order_id}"}],
#         ]

#         return {
#             "chat_id": chat_id,
#             "text": text,
#             "parse_mode": "Markdown",
#             "reply_markup": {"inline_keyboard": keyboard},
#         }

#     @staticmethod
#     def payment_confirmed(chat_id: Union[int, str], order_id: Union[int, str]):
#         text = "\n".join(
#             [
#                 "✅ **Payment Confirmed**",
#                 "",
#                 "Thank you. Your payment has been successfully verified.",
#                 "Your order is now marked as **PAID** and will be processed.",
#                 "",
#                 "━━━━━━━━━━━━━━━━━━━━",
#                 f"🆔 Order ID: `{order_id}`",
#                 "",
#                 "If you need anything else, you can return to the main menu.",
#             ]
#         )

#         keyboard = [
#             [{"text": "🏠 Return to Menu", "callback_data": "menu"}],
#         ]

#         return {
#             "chat_id": chat_id,
#             "text": text,
#             "parse_mode": "Markdown",
#             "reply_markup": {"inline_keyboard": keyboard},
#         }

#     @staticmethod
#     def payment_not_confirmed(chat_id: Union[int, str], order_id: Union[int, str]):
#         text = "\n".join(
#             [
#                 "⏳ **Payment Not Found**",
#                 "",
#                 "We could not verify any successful payment for this order yet.",
#                 "This may happen if:",
#                 "• The payment is still being processed",
#                 "• The payment failed or was canceled",
#                 "• You have not completed the payment",
#                 "",
#                 "━━━━━━━━━━━━━━━━━━━━",
#                 f"🆔 Order ID: `{order_id}`",
#                 "",
#                 'Please complete the payment and then press **"I Paid"** again.',
#             ]
#         )

#         keyboard = [
#             [
#                 {
#                     "text": "💳 Try Payment Again",
#                     "callback_data": f"payment_gateway:{order_id}",
#                 }
#             ],
#             [{"text": "❌ Cancel Order", "callback_data": f"cancel_order:{order_id}"}],
#             [{"text": "🏠 Return to Menu", "callback_data": "menu"}],
#         ]

#         return {
#             "chat_id": chat_id,
#             "text": text,
#             "parse_mode": "Markdown",
#             "reply_markup": {"inline_keyboard": keyboard},
#         }

#     @staticmethod
#     def empty_answer_callback(query_id: Union[str, int]):
#         return {
#             "method": "answerCallback",
#             "params": {"callback_query_id": query_id},
#         }


#! VERY VERY IMPORTANT
#! The former structure of this output was so that depending
#! of the paramater of form:bool it would either have a read_terms button
#! or a return to menu button. Given the change to the handling of the outputs
#! I have deleted that param and it will render both buttons each time
#! so the flow needs to be handled in a lower level

# @staticmethod
# def show_terms_condititons(
#     chat_id: Union[str, int],
#     message_id: Optional[Union[str, int]] = None,
#     append: Optional[bool] = False,
# ):
#     if append is False and message_id is None:
#         raise ValueError("when append is false message_id cannot be None")
#     inline_keyboard = [
#         [
#             {
#                 "text": "I read the terms",
#                 "callback_data": "read_the_terms",
#             }
#         ],
#         [
#             {
#                 "text": "return to the menu",
#                 "callback_data": "return_to_menu",
#             }
#         ],
#     ]
#     params = {
#         "chat_id": chat_id,
#         "text": _t(
#             """
#             📜 **Terms of service agreement**

#             🔰 **Terms of Using the Test Bot:**

#             1️⃣ **General Rules:**
#             • This service is intended for purchasing Telegram Stars and Telegram Premium.
#             • The user is required to provide accurate and complete information.
#             • Any misuse of the service is prohibited.

#             2️⃣ **Payment Rules:**
#             • Payments are non-refundable.
#             • By order of the Cyber Police (FATA), some transactions may require up to 72 hours
#               for verification before the product is delivered.

#             3️⃣ **Privacy:**
#             • Your personal information will be kept confidential.
#             • The information is used for identity and payment verification.
#             • Information will not be shared with any third party.

#             4️⃣ **Responsibilities:**
#             • We are committed to delivering products intact and on time.
#             • The user is responsible for the accuracy of the information they provide.
#             • Any form of fraud will result in being banned from the service.

#             5️⃣ **Support:**
#             • Support is available to you.
#             • Response time: up to 2 hours.
#             • Support contact: @TestSupport.

#             ⚠️ **Note:** By using this service, you accept all of the above terms.
#             """
#         ),
#         "parse_mode": "Markdown",
#         "reply_markup": {"inline_keyboard": inline_keyboard},
#     }
#     if append is False:
#         params["message_id"] = message_id
#     return (
#         {"method": "editMessageText", "params": params}
#         if append is False
#         else params
#     )

#     @staticmethod
#     def terms_and_conditions(
#         chat_id: Union[str, int],
#         message_id: Optional[Union[str, int]] = None,
#         append: Optional[bool] = False,
#     ):
#         if message_id is None and append is False:
#             raise ValueError("when append is false message_id cannot be None")
#         params = {
#             "chat_id": chat_id,
#             "text": _t(
#                 """
#                 **Terms and Conditions**

#                 By using the test bot you are obligated to follow our terms of service.
#                 If you agree to the terms, press the *'agree and accept'* button.
#                 """
#             ),
#             "parse_mode": "Markdown",
#             "reply_markup": {
#                 "inline_keyboard": [
#                     [
#                         {
#                             "text": "✅I agree and accept",
#                             "callback_data": "accepted_terms",
#                         }
#                     ],
#                     [
#                         {
#                             "text": "📜See terms of service",
#                             "callback_data": "show_terms_for_acceptance",
#                         }
#                     ],
#                 ]
#             },
#         }
#         if append is False:
#             params["message_id"] = message_id

#         return (
#             {"method": "editMessageText", "params": params}
#             if append is False
#             else params
#         )

#     @staticmethod
#     def return_to_menu(
#         chat_id: Union[str, int],
#         products: List[Product],
#         message_id: Optional[Union[str, int]] = None,
#         append: Optional[bool] = False,
#     ):
#         if message_id is None and append is False:
#             raise ValueError("message_id can't be none when append is false")

#         # --------- dynamic text ----------
#         if products:
#             lines = []
#             for p in products:
#                 emoji = EMOJI_PAIRINGS.get(p.name, "🛒")  # fallback emoji
#                 lines.append(f"{emoji} *{p.name}*")  # use *...* for Markdown emphasis
#             products_text = "\n".join(lines)
#             hint_text = "💡 Choose a product below:"
#         else:
#             products_text = "• *(No products are available right now.)*"
#             hint_text = "💡 Please check back later."

#         text = "\n".join(
#             [
#                 "🌟 *Welcome to the test bot!*",
#                 "",
#                 "━━━━━━━━━━━━━━━━━━━━",
#                 "",
#                 hint_text,
#                 "",
#                 products_text,
#                 "",
#                 "━━━━━━━━━━━━━━━━━━━━",
#             ]
#         )

#         # --------- dynamic keyboard (one button per product) ----------
#         # callback_data format recommendation:
#         #   buy_product:<product_id>
#         product_rows = [
#             [{"text": f"🛒 Buy {p.name}", "callback_data": f"buy_product:{p.id}"}]
#             for p in (products or [])
#         ]

#         # --------- append your static actions ----------
#         keyboard = product_rows + [
#             [{"text": "💰 Show prices", "callback_data": "show_prices"}],
#             [{"text": "📜 Show terms of service", "callback_data": "show_terms"}],
#             [{"text": "🆘 Support", "callback_data": "support"}],
#         ]

#         params = {
#             "chat_id": chat_id,
#             "text": text,
#             "parse_mode": "Markdown",
#             "reply_markup": {"inline_keyboard": keyboard},
#         }

#         if append is False:
#             params["message_id"] = message_id
#             return {"method": "editMessageText", "params": params}

#         # append=True => sendMessage style payload
#         return params

#     @staticmethod
#     def support(
#         chat_id: Union[str, int],
#         message_id: Optional[Union[str, int]] = None,
#         append: Optional[bool] = False,
#     ):
#         if message_id is None and append is False:
#             raise ValueError(
#                 "telegram output support failed: message_id cannot be None when append is False"
#             )

#         params = {
#             "chat_id": chat_id,
#             "text": _t(
#                 """
#                 🆘 **Test bot support section**

#                 ━━━━━━━━━━━━━━━━━━━━

#                 In order to receive help, pick one of the options below:

#                 📞 *Contact with support* – contact info.
#                 ❓ *Commonly asked questions* – common answers.
#                 🔁 *Return to main menu* – returns to the main menu.

#                 ━━━━━━━━━━━━━━━━━━━━

#                 💡 **Note:** For faster support, first look at commonly asked questions.
#                 """
#             ),
#             "parse_mode": "Markdown",
#             "reply_markup": {
#                 "inline_keyboard": [
#                     [
#                         {
#                             "text": "📞contact with support",
#                             "callback_data": "contact_support",
#                         }
#                     ],
#                     [
#                         {
#                             "text": "❓commonly asked questions",
#                             "callback_data": "common_questions",
#                         }
#                     ],
#                     [
#                         {
#                             "text": "🔁return to main menu",
#                             "callback_data": "return_to_menu",
#                         }
#                     ],
#                 ]
#             },
#         }

#         if append is False:
#             params["message_id"] = message_id

#         return (
#             {"method": "editMessageText", "params": params}
#             if append is False
#             else params
#         )

#     @staticmethod
#     def contact_support_info(
#         chat_id: Union[str, int],
#         message_id: Optional[Union[str, int]] = None,
#         append: Optional[bool] = False,
#     ):
#         if message_id is None and append is False:
#             raise ValueError("message_id can't be None when append is False")

#         params = {
#             "chat_id": chat_id,
#             "text": _t(
#                 """
#                 📞 **Support Contact Information**

#                 ━━━━━━━━━━━━━━━━━━━━

#                 👤 **Telegram Support:**
#                 • @TestSupport

#                 ━━━━━━━━━━━━━━━━━━━━

#                 ⏰ **Working Hours:**
#                 • 24/7 (Available around the clock)

#                 💡 **Important Notes:**
#                 • For the fastest response, provide your invoice ID
#                 • In case of payment issues, send your transaction details
#                 • For delivery tracking, include your delivery reference

#                 ━━━━━━━━━━━━━━━━━━━━

#                 🔗 **Useful Links:**
#                 • Official Channel: @TestBot
#                 """
#             ),
#             "parse_mode": "Markdown",
#             "reply_markup": {
#                 "inline_keyboard": [
#                     [{"text": "🔁 Return to Menu", "callback_data": "return_to_menu"}],
#                     [
#                         {
#                             "text": "📞 Return to Support",
#                             "callback_data": "return_to_support",
#                         }
#                     ],
#                 ]
#             },
#         }

#         if append is False:
#             params["message_id"] = message_id

#         return (
#             {"method": "editMessageText", "params": params}
#             if append is False
#             else params
#         )

#     @staticmethod
#     def common_questions(
#         chat_id: Union[str, int],
#         message_id: Optional[Union[int, str]],
#         append: Optional[bool] = False,
#     ):
#         if message_id is None and append is False:
#             raise ValueError("message_id can't be None when append is False")
#         params = {
#             "chat_id": chat_id,
#             "text": _t(
#                 """
#                 ❔ **commonly asked Q&A**

#                 ━━━━━━━━━━━━━━━━━━━━

#                 1- ....
#                 2- ....
#                 3- ....
#                 4- ....

#                 """
#             ),
#             "parse_mode": "Markdown",
#             "reply_markup": {
#                 "inline_keyboard": [
#                     [{"text": "🔁 Return to Menu", "callback_data": "return_to_menu"}],
#                     [
#                         {
#                             "text": "📞 Return to Support",
#                             "callback_data": "return_to_support",
#                         }
#                     ],
#                 ]
#             },
#         }

#         if append is False:
#             params["message_id"] = message_id

#         return (
#             {"method": "editMessageText", "params": params}
#             if append is False
#             else params
#         )


# telegram_process_bot_outputs = TelegrambotOutputs()
