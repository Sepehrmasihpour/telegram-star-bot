from typing import Union
from textwrap import dedent


def _t(s: str) -> str:
    """Normalize multi-line text: remove common indent and trim outer whitespace."""
    return dedent(s).strip()


class TelegramProcessTextOutputs:
    @staticmethod
    def shop_options(chat_id: Union[str, int]):
        return {
            "chat_id": chat_id,
            "text": _t(
                """
                🌟welcome to the test bot!

                💡to buy product no1, product no2, product no3, press the relevant button.
                """
            ),
            "reply_markup": {
                "inline_keyboard": [
                    [{"text": "🤖product no1", "callback_data": "buy_product_1"}],
                    [{"text": "🛒product no2", "callback_data": "buy_product_2"}],
                    [{"text": "🎯product no3", "callback_data": "buy_product_3"}],
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
                🌟welcome to the testing bot!

                📱to start, please enter your phone number:
                .enter the phone number in the 09123456789 format
                .the phone number must belong to you
                .this phone number is used for verifying your identity and direct payment

                💡keep note:
                .your phone number will remain safe and secret
                .it will only be used for verifying your identity and payment
                .you can change it at any time

                🔐security:
                .all your information is stored using encryption
                .no data will be shared with a third party
                """
            ),
        }

    @staticmethod
    def phone_number_verfication_needed(chat_id: Union[str, int]):

        return {
            "chat_id": chat_id,
            "text": _t(
                """
                ❌your phone number has not been verified
                📱in order to continue please verify your phone number
                """
            ),
            "reply_markup": {
                "inline_keyboard": [
                    [
                        {
                            "text": "📱send verificaton code",
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
    def terms_and_conditions(chat_id: Union[str, int]):

        return {
            "chat_id": chat_id,
            "text": _t(
                """
                By using the test bot you are obligated to follow our terms of service.
                If you agree to the terms, press the 'agree and accept' button.
                """
            ),
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

    @staticmethod
    def authentication_failed(chat_id: Union[str, int]):
        return {
            "chat_id": chat_id,
            "text": "authentication failed",
        }

    @staticmethod
    def prices(chat_id: Union[str, int]):
        return {
            "method": "calculatePrices",
            "params": {
                "chat_id": chat_id,
                "text": "🔍Getting the most recent up to date prices...",
            },
        }

    @staticmethod
    def support(chat_id: Union[str, int]):
        return {
            "chat_id": chat_id,
            "text": _t(
                """
                🆘The Test bot support section

                in order to receive help, pick one of the options below:

                📞contact with support - contact info of the support team.
                ❓commonly asked questions - the answer to most of your questions.
                🔁return to main menu - returns you to the main menu.

                💡take note: for faster support, first look at commonly asked questions.
                """
            ),
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

    @staticmethod
    def phone_max_attempt(chat_id: Union[str, int]):
        return {"chat_id": chat_id, "text": "failed 3 times. canceled"}

    @staticmethod
    def invalid_phone_number(chat_id: Union[str, int]):
        return {"chat_id": chat_id, "text": "phone number is invalid"}

    @staticmethod
    def phone_numebr_verification(chat_id: Union[str, int]):
        return {
            "chat_id": chat_id,
            "text": _t(
                """
                ✅the verification code has been sent to your phone number. please enter the code

                💳important points about bank accounts:
                .the account that you use for payment must belong to the owner of the phone number
                .the system verifies whether the phone number and the account number belong to the same person
                .in case they don't, your payment will not go through
                .if the account belongs to someone else, please use another account
                """
            ),
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
        return {"chat_id": chat_id, "text": "❌invalid verification code"}

    @staticmethod
    def phone_number_verified(chat_id: Union[str, int]):
        return {
            "method": "verifiedPhone",
            "params": {
                "chat_id": chat_id,
                "text": _t(
                    """
                    ✅phone number successfully verified!
                    🌟Showing the products...
                    """
                ),
            },
        }


class TelegramProcessCallbackQueryOutput:

    @staticmethod
    def empty_answer_callback(query_id: Union[str, int]):
        return {
            "method": "answerCallback",
            "params": {"callback_query_id": query_id},
        }

    @staticmethod
    def show_terms_condititons(chat_id: Union[str, int], message_id: Union[str, int]):
        return {
            "method": "editMessageText",
            "params": {
                "chat_id": chat_id,
                "message_id": message_id,
                "text": _t(
                    """
                    📜Terms of service agreement

                    🔰Terms of Using the Test Bot:

                    1️⃣ General Rules:
                    • This service is intended for purchasing Telegram Stars and Telegram Premium.
                    • The user is required to provide accurate and complete information.
                    • Any misuse of the service is prohibited.

                    2️⃣ Payment Rules:
                    • Payments are non-refundable.
                    • By order of the Cyber Police (FATA), some transactions may require up to 72 hours
                      for verification before the product is delivered.

                    3️⃣ Privacy:
                    • Your personal information will be kept confidential.
                    • The information is used for identity and payment verification.
                    • Information will not be shared with any third party.

                    4️⃣ Responsibilities:
                    • We are committed to delivering products intact and on time.
                    • The user is responsible for the accuracy of the information they provide.
                    • Any form of fraud will result in being banned from the service.

                    5️⃣ Support:
                    • Support is available to you.
                    • Response time: up to 2 hours.
                    • Support contact: @TestSupport.

                    ⚠️Note: By using this service, you accept all of the above terms.
                    """
                ),
                "reply_markup": {
                    "inline_keyboard": [
                        [
                            {
                                "text": "I read the terms",
                                "callback_data": "read_the_terms",
                            }
                        ],
                    ]
                },
            },
        }

    @staticmethod
    def terms_and_conditions(chat_id: Union[str, int], message_id: Union[str, int]):
        return {
            "method": "editMessageText",
            "params": {
                "chat_id": chat_id,
                "message_id": message_id,
                "text": _t(
                    """
                    By using the test bot you are obligated to follow our terms of service.
                    If you agree to the terms, press the 'agree and accept' button.
                    """
                ),
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
            },
        }

    @staticmethod
    def welcome_message(chat_id: Union[str, id]):
        return {
            "chat_id": chat_id,
            "text": _t(
                """
                ✅the terms and conditions have been accepted!

                🎉welcome! now you can use all the features.

                💡To begin:
                .the command /buy for purchasing products
                .the command /prices for seeing the prices
                .the command /support for support

                🔁the command /start for returning to main menu
                """
            ),
        }


telegram_process_text_outputs = TelegramProcessTextOutputs()
telegram_process_callback_query_outputs = TelegramProcessCallbackQueryOutput()
