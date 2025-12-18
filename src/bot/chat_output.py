from typing import Union, Dict
from textwrap import dedent
from typing import Optional
from decimal import Decimal
from typing import Any


def _t(s: str) -> str:
    """Normalize multi-line text: remove common indent and trim outer whitespace."""
    return dedent(s).strip()


EMOJI_PAIRINGS = {"Premium Stars Pack": "🌟", "Telegram Premium Upgrade": "💎"}


class TelegrambotOutputs:

    @staticmethod
    def unsupported_command(chat_id: Union[str, int]):
        return {
            "chat_id": chat_id,
            "text": "command not supported",
        }

    @staticmethod
    def phone_number_input(chat_id: Union[str, int]):
        return {
            "chat_id": chat_id,
            "text": _t(
                """
                🌟 **Welcome to the testing bot!**

                📱 **To start, please enter your phone number:**
                .enter the phone number in the 09123456789 format
                .the phone number must belong to you
                .this phone number is used for verifying your identity and direct payment

                💡 **Keep note:**
                .your phone number will remain safe and secret
                .it will only be used for verifying your identity and payment
                .you can change it at any time

                🔐 **Security:**
                .all your information is stored using encryption
                .no data will be shared with a third party
                """
            ),
            "parse_mode": "Markdown",
        }

    @staticmethod
    def phone_number_verfication_needed(chat_id: Union[str, int]):
        return {
            "chat_id": chat_id,
            "text": _t(
                """
                ❌ **Your phone number has not been verified**
                📱 In order to continue please verify your phone number.
                """
            ),
            "parse_mode": "Markdown",
            "reply_markup": {
                "inline_keyboard": [
                    [
                        {
                            "text": "📱send verification code",
                            "callback_data": "send_validation_code",
                        }
                    ],
                    [
                        {
                            "text": "📝Edit phone number",
                            "callback_data": "edit_phone_number",
                        }
                    ],
                ]
            },
        }

    @staticmethod
    def authentication_failed(chat_id: Union[str, int]):
        return {
            "chat_id": chat_id,
            "text": "*authentication failed*",
            "parse_mode": "Markdown",
        }

    @staticmethod
    def phone_max_attempt(chat_id: Union[str, int]):
        return {
            "chat_id": chat_id,
            "text": "❌ *failed 3 times. canceled*",
            "parse_mode": "Markdown",
        }

    @staticmethod
    def invalid_phone_number(chat_id: Union[str, int]):
        return {
            "chat_id": chat_id,
            "text": "❌ *phone number is invalid*",
            "parse_mode": "Markdown",
        }

    @staticmethod
    def phone_numebr_verification(chat_id: Union[str, int]):
        return {
            "chat_id": chat_id,
            "text": _t(
                """
                ✅ **The verification code has been sent to your phone number.**
                Please enter the code.

                💳 **Important points about bank accounts:**
                .the account that you use for payment must belong to the owner of the phone number
                .the system verifies whether the phone number and the account number belong to the same person
                .in case they don't, your payment will not go through
                .if the account belongs to someone else, please use another account
                """
            ),
            "parse_mode": "Markdown",
            "reply_markup": {
                "inline_keyboard": [
                    [
                        {
                            "text": "📝Edit phone number",
                            "callback_data": "edit_phone_number",
                        }
                    ],
                ]
            },
        }

    @staticmethod
    def invalid_otp(chat_id: Union[str, int]):
        return {
            "chat_id": chat_id,
            "text": "❌ *invalid verification code*",
            "parse_mode": "Markdown",
        }

    @staticmethod
    def phone_number_verified(chat_id: Union[str, int]):
        return {
            "method": "verifiedPhone",
            "params": {
                "chat_id": chat_id,
                "text": _t(
                    """
                    ✅ **Phone number successfully verified!**
                    🌟Showing the products...
                    """
                ),
                "parse_mode": "Markdown",
            },
        }

    @staticmethod
    def loading_prices(chat_id: Union[str, int]):
        return {
            "method": "custom",
            "payload": {
                "chat_id": chat_id,
                "custom": "get_prices",
                "message": {
                    "chat_id": chat_id,
                    "text": "💰 please wait a moment to get the most up to date prices",
                },
            },
        }

    @staticmethod
    def get_prices(
        chat_id: Union[str, int],
        prices: Dict[str, Dict[str, Decimal | str]],
    ) -> Dict[str, Any]:
        lines: list[str] = ["📊 **Current Prices:**", ""]

        for product_name, variations in prices.items():
            emoji = EMOJI_PAIRINGS.get(product_name, "🛒")
            lines.append(f"{emoji} *{product_name}*\n")

            for variation, value in variations.items():
                if isinstance(value, Decimal):
                    normalized = value.quantize(Decimal("1"))
                    price_str = f"{normalized:,} T"

                else:
                    price_str = f"{value:,} T"

                lines.append(f"    ➜ **{variation}** ")
                lines.append(f"    💰price: {price_str}")
                lines.append("━━━━━━━━━━━━━━━━━━━━\n")
        final_text = _t("\n".join(lines))
        return {
            "chat_id": chat_id,
            "text": final_text,
            "parse_mode": "Markdown",
            "reply_markup": {
                "inline_keyboard": [
                    [
                        {
                            "text": "return to main menu",
                            "callback_data": "return_to_menu",
                        }
                    ],
                ]
            },
        }

    @staticmethod
    def empty_answer_callback(query_id: Union[str, int]):
        return {
            "method": "answerCallback",
            "params": {"callback_query_id": query_id},
        }

    @staticmethod
    def show_terms_condititons(
        chat_id: Union[str, int],
        message_id: Optional[Union[str, int]] = None,
        append: Optional[bool] = False,
        form: Optional[bool] = False,
    ):
        if append is False and message_id is None:
            raise ValueError("when append is false message_id cannot be None")
        inline_keyboard = (
            [
                [
                    {
                        "text": "I read the terms",
                        "callback_data": "read_the_terms",
                    }
                ],
            ]
            if form is True
            else [
                [
                    {
                        "text": "return to the menu",
                        "callback_data": "return_to_menu",
                    }
                ],
            ]
        )
        params = {
            "chat_id": chat_id,
            "text": _t(
                """
                📜 **Terms of service agreement**

                🔰 **Terms of Using the Test Bot:**

                1️⃣ **General Rules:**
                • This service is intended for purchasing Telegram Stars and Telegram Premium.
                • The user is required to provide accurate and complete information.
                • Any misuse of the service is prohibited.

                2️⃣ **Payment Rules:**
                • Payments are non-refundable.
                • By order of the Cyber Police (FATA), some transactions may require up to 72 hours
                  for verification before the product is delivered.

                3️⃣ **Privacy:**
                • Your personal information will be kept confidential.
                • The information is used for identity and payment verification.
                • Information will not be shared with any third party.

                4️⃣ **Responsibilities:**
                • We are committed to delivering products intact and on time.
                • The user is responsible for the accuracy of the information they provide.
                • Any form of fraud will result in being banned from the service.

                5️⃣ **Support:**
                • Support is available to you.
                • Response time: up to 2 hours.
                • Support contact: @TestSupport.

                ⚠️ **Note:** By using this service, you accept all of the above terms.
                """
            ),
            "parse_mode": "Markdown",
            "reply_markup": {"inline_keyboard": inline_keyboard},
        }
        if append is False:
            params["message_id"] = message_id
        return (
            {"method": "editMessageText", "params": params}
            if append is False
            else params
        )

    @staticmethod
    def terms_and_conditions(
        chat_id: Union[str, int],
        message_id: Optional[Union[str, int]] = None,
        append: Optional[bool] = False,
    ):
        if message_id is None and append is False:
            raise ValueError("when append is false message_id cannot be None")
        params = {
            "chat_id": chat_id,
            "text": _t(
                """
                **Terms and Conditions**

                By using the test bot you are obligated to follow our terms of service.
                If you agree to the terms, press the *'agree and accept'* button.
                """
            ),
            "parse_mode": "Markdown",
            "reply_markup": {
                "inline_keyboard": [
                    [
                        {
                            "text": "✅I agree and accept",
                            "callback_data": "accepted_terms",
                        }
                    ],
                    [
                        {
                            "text": "📜See terms of service",
                            "callback_data": "show_terms_for_acceptance",
                        }
                    ],
                ]
            },
        }
        if append is False:
            params["message_id"] = message_id

        return (
            {"method": "editMessageText", "params": params}
            if append is False
            else params
        )

    @staticmethod
    def return_to_menu(
        chat_id: Union[str, int],
        message_id: Optional[Union[str, int]] = None,
        append: Optional[bool] = False,
    ):
        if message_id is None and append is False:
            raise ValueError("message_id can't be none when append is false")
        params = {
            "chat_id": chat_id,
            "text": _t(
                """
                🌟 **Welcome to the test bot!**
                
                ━━━━━━━━━━━━━━━━━━━━

                💡To buy product no1, product no2, product no3, press the relevant button.

                ━━━━━━━━━━━━━━━━━━━━
                """
            ),
            "parse_mode": "Markdown",
            "reply_markup": {
                "inline_keyboard": [
                    [{"text": "🤖product no1", "callback_data": "buy_product_1"}],
                    [
                        {
                            "text": "🛒buy product no2",
                            "callback_data": "buy_product_2",
                        }
                    ],
                    [
                        {
                            "text": "🎯buy product no3",
                            "callback_data": "buy_product_3",
                        }
                    ],
                    [{"text": "💰show prices", "callback_data": "show_prices"}],
                    [
                        {
                            "text": "📜show terms of service",
                            "callback_data": "show_terms",
                        }
                    ],
                    [{"text": "🆘support", "callback_data": "support"}],
                ]
            },
        }

        if append is False:
            params["message_id"] = message_id
        return (
            {"method": "editMessageText", "params": params}
            if append is False
            else params
        )

    @staticmethod
    def support(
        chat_id: Union[str, int],
        message_id: Optional[Union[str, int]] = None,
        append: Optional[bool] = False,
    ):
        if message_id is None and append is False:
            raise ValueError(
                "telegram output support failed: message_id cannot be None when append is False"
            )

        params = {
            "chat_id": chat_id,
            "text": _t(
                """
                🆘 **Test bot support section**
                
                ━━━━━━━━━━━━━━━━━━━━

                In order to receive help, pick one of the options below:

                📞 *Contact with support* – contact info.
                ❓ *Commonly asked questions* – common answers.
                🔁 *Return to main menu* – returns to the main menu.
                
                ━━━━━━━━━━━━━━━━━━━━

                💡 **Note:** For faster support, first look at commonly asked questions.
                """
            ),
            "parse_mode": "Markdown",
            "reply_markup": {
                "inline_keyboard": [
                    [
                        {
                            "text": "📞contact with support",
                            "callback_data": "contact_support",
                        }
                    ],
                    [
                        {
                            "text": "❓commonly asked questions",
                            "callback_data": "common_questions",
                        }
                    ],
                    [
                        {
                            "text": "🔁return to main menu",
                            "callback_data": "return_to_menu",
                        }
                    ],
                ]
            },
        }

        if append is False:
            params["message_id"] = message_id

        return (
            {"method": "editMessageText", "params": params}
            if append is False
            else params
        )

    @staticmethod
    def contact_support_info(
        chat_id: Union[str, int],
        message_id: Optional[Union[str, int]] = None,
        append: Optional[bool] = False,
    ):
        if message_id is None and append is False:
            raise ValueError("message_id can't be None when append is False")

        params = {
            "chat_id": chat_id,
            "text": _t(
                """
                📞 **Support Contact Information**

                ━━━━━━━━━━━━━━━━━━━━

                👤 **Telegram Support:**
                • @TestSupport

                ━━━━━━━━━━━━━━━━━━━━

                ⏰ **Working Hours:**
                • 24/7 (Available around the clock)

                💡 **Important Notes:**
                • For the fastest response, provide your invoice ID
                • In case of payment issues, send your transaction details
                • For delivery tracking, include your delivery reference

                ━━━━━━━━━━━━━━━━━━━━

                🔗 **Useful Links:**
                • Official Channel: @TestBot
                """
            ),
            "parse_mode": "Markdown",
            "reply_markup": {
                "inline_keyboard": [
                    [{"text": "🔁 Return to Menu", "callback_data": "return_to_menu"}],
                    [
                        {
                            "text": "📞 Return to Support",
                            "callback_data": "return_to_support",
                        }
                    ],
                ]
            },
        }

        if append is False:
            params["message_id"] = message_id

        return (
            {"method": "editMessageText", "params": params}
            if append is False
            else params
        )

    @staticmethod
    def common_questions(
        chat_id: Union[str, int],
        message_id: Optional[Union[int, str]],
        append: Optional[bool] = False,
    ):
        if message_id is None and append is False:
            raise ValueError("message_id can't be None when append is False")
        params = {
            "chat_id": chat_id,
            "text": _t(
                """
                ❔ **commonly asked Q&A**

                ━━━━━━━━━━━━━━━━━━━━
                
                1- ....
                2- ....
                3- ....
                4- ....
                
                """
            ),
            "parse_mode": "Markdown",
            "reply_markup": {
                "inline_keyboard": [
                    [{"text": "🔁 Return to Menu", "callback_data": "return_to_menu"}],
                    [
                        {
                            "text": "📞 Return to Support",
                            "callback_data": "return_to_support",
                        }
                    ],
                ]
            },
        }

        if append is False:
            params["message_id"] = message_id

        return (
            {"method": "editMessageText", "params": params}
            if append is False
            else params
        )


telegram_process_bot_outputs = TelegrambotOutputs()
