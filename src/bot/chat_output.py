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
    map_url: Optional[Dict[str, str]] = None,
    **placeholders,
) -> list[list[dict]]:
    buttons = sorted(chat_output.button_indexes, key=lambda bi: bi.number)

    rendered = []
    for bi in buttons:
        btn = bi.button
        item = {
            "text": _fill_placeholders(btn.text, **placeholders),
        }

        # if this button name is in url_map, render url button
        if map_url and btn.name in map_url:
            item["url"] = map_url[btn.name]
        else:
            item["callback_data"] = _fill_placeholders(
                btn.callback_data, **placeholders
            )

        rendered.append(item)

    return [rendered[i : i + row_size] for i in range(0, len(rendered), row_size)]


def _render_chat_outputs(
    template: ChatOutput,
    chat_id: Union[str, int],
    row_size: int = 1,
    message_id: Optional[Union[str, int]] = None,
    method: Optional[str] = None,
    map_url: Optional[Dict[str, str]] = None,
    **placeholders,
) -> dict:
    """
    Render a ChatOutput template into a Telegram-ready payload.
    """

    # Normalize text
    raw_text = _t(template.text)

    # assert wether or not the placeholders are allowed or not
    _assert_placeholders_allowed(template=template, text=raw_text)

    # Fill placeholders
    rendered_text = _fill_placeholders(raw_text, **placeholders)

    # Render buttons
    keyboard = _map_buttons_in_order(
        chat_output=template, row_size=row_size, map_url=map_url, **placeholders
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


def _assert_placeholders_allowed(template: ChatOutput, text: str):
    allowed = {p.name for p in (template.placeholders or [])}
    used = set(PLACEHOLDER_RE.findall(text))
    illegal = used - allowed
    if illegal:
        raise ValueError(
            f"Template '{template.name}' uses unknown placeholders: {illegal}. "
            f"Allowed: {sorted(allowed)}"
        )


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
        map_url: Optional[Dict[str, str]] = None,
        method: Optional[str] = None,
        message_id: Optional[Union[str, int]] = None,
        **placeholders,
    ):
        template = self._get_template(db, name=name)
        return _render_chat_outputs(
            template=template,
            chat_id=chat_id,
            method=method,
            message_id=message_id,
            map_url=map_url,
            **placeholders,
        )

    def _render_with_keyboard_append_template(
        self,
        db: Session,
        name: str,
        chat_id: Union[str, int],
        dynamic_keyboard: list[list[dict]],
        row_size: int = 1,
        map_url: Dict[str, str] = None,
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
            map_url=map_url,
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
            pay_url=pay_url,
            order_id=order_id,
            url_map={"btn_pay_invoice": pay_url},
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
