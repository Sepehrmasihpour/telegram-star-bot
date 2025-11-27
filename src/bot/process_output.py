from typing import Union


class TelegramProcessTextOutputs:
    def shop_options(chat_id: Union[str, int]):
        return {
            "chat_id": chat_id,
            "text": """
🌟welcome to the test bot!\n
💡to buy product no1, product no2, product no3, press the relevent button.
""",
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

    def unsupported_command(chat_id: Union[str, int]):
        return {
            "chat_id": chat_id,
            "text": "command not supported",
        }

    def phone_number_input(chat_id: Union[str, int]):

        return {
            "chat_id": chat_id,
            "text": (
                """
🌟welcome to the testing bot!\n
📱to start please enter you'r phone number
.enter the phone number with the 09121764237 format
.the phone number must belong to you
.this phone number is used for verifying your identity and direct payment\n
💡keep note:
.your phone number will remain safe and secret
.it will only be used for verifying your identity and payment
.you can change it at any time\n
🔐security:
.all your infromation is stored using encryption
.no data will be shared with a third party
                            """
            ),
        }

    def phone_number_verfication_needed(chat_id: Union[str, int]):

        return {
            "chat_id": chat_id,
            "text": (
                """
❌you'r phone number has not been verified
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

    def terms_and_conditions(chat_id: Union[str, int]):

        return {
            "chat_id": chat_id,
            "text": "By using the test bot you are obligated to follow our terms of service if you agree to the terms press the 'agree and accept' button",
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

    def authentication_failed(chat_id: Union[str, int]):
        return {
            "chat_id": chat_id,
            "text": "authentication failed",
        }

    def prices(chat_id: Union[str, int]):
        return {
            "method": "calculatePrices",
            "params": {
                "chat_id": chat_id,
                "text": "🔍Getting the most recent up to date prices...",
            },
        }

    def support(chat_id: Union[str, int]):
        return {
            "chat_id": chat_id,
            "text": """
🆘The Test bot support section\n
in order to recive help pick one of the options bellow:\n
📞contact with support - contact info of the support team.
❓commonly asked questions - the answer to most of your questions.
🔁return to main menu - it will return you to the main menu.\n
💡take point: in order to recive quicker support first take a look at commonly asked questions.
                """,
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

    def phone_max_attempt(chat_id: Union[str, int]):
        return {"chat_id": chat_id, "text": "failed 3 times. canceled"}

    def invalid_phone_number(chat_id: Union[str, int]):
        return {"chat_id": chat_id, "text": "phone number is invalid"}

    def phone_numebr_verification(chat_id: Union[str, int]):
        return {
            "chat_id": chat_id,
            "text": """
✅the verification code has been sent to your phone number. please enter the code\n
💳important points about bank acounts:
.The acount that you use for payment must belong to the owner of the phone number
.The  system verifies weather the phone number and the acount number belong to the same person
.In case they don't, you'r payment will not go through
.If the acount belongs to someone else, please use another acount
            """,
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

    def invalid_otp(chat_id: Union[str, int]):
        return {"chat_id": chat_id, "text": "❌invalid verification code"}

    def phone_number_verified(chat_id: Union[str, int]):
        return {
            "method": "verifiedPhone",
            "params": {
                "chat_id": chat_id,
                "text": """
                ✅phone number successfully verified!\n
                🌟Showing the products...
                """,
            },
        }


class TelegramProcessCallbackQueryOutput:

    def empty_answer_callback(query_id: Union[str, int]):
        return {
            "method": "answerCallback",
            "params": {"callback_query_id": query_id},
        }

    def show_terms_condititons(chat_id: Union[str, int], message_id: Union[str, int]):
        return {
            "method": "editMessageText",
            "params": {
                "chat_id": chat_id,
                "message_id": message_id,
                "text": """
📜Terms of service agreement
\n
🔰Terms of Using the Test Bot:
\n
1️⃣General Rules:
• This service is intended for purchasing Telegram Stars and Telegram Premium.
• The user is required to provide accurate and complete information.
• Any misuse of the service is prohibited.\n
2️⃣Payment Rules:
• Payments are non-refundable.
• By order of the Cyber Police (FATA), some transactions may require up to 72 hours for verification before the product is delivered.\n
3️⃣Privacy:
• Your personal information will be kept confidential.
• The information is used for identity and payment verification.
• Information will not be shared with any third party.\n
4️⃣Responsibilities:
• We are committed to delivering products intact and on time.
• The user is responsible for the accuracy of the information they provide.
• Any form of fraud will result in being banned from the service.\n
5️⃣Support:
• 24/7 support is available to you.
• Response time: up to 2 hours.
• Support contact: @TestSupport.
\n
⚠️Note: By using this service, you accept all of the above terms
                """,
                "reply_markup": {
                    "inline_keyboard": [
                        [{"text": "خواندم", "callback_data": "read_the_terms"}],
                    ]
                },
            },
        }

    def terms_and_conditions(chat_id: Union[str, int], message_id: Union[str, int]):
        return {
            "method": "editMessageText",
            "params": {
                "chat_id": chat_id,
                "message_id": message_id,
                "text": "By using the test bot you are obligated to follow our terms of service if you agree to the terms press the 'agree and accept' button",
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

    def welcome_message(chat_id: Union[str, id]):
        return {
            "chat_id": chat_id,
            "text": """
✅the terms and condtionns has been accepted!
\n
🎉welcome! now you can use all the features
💡To begin:
.the command /buy for purchasing of products.
.the command /prices for seeing the prices.
.the command /support for support
\n
🔁the command /start for returning to main menu
            """,
        }


telegram_process_text_outputs = TelegramProcessTextOutputs()
telegram_process_callback_query_outputs = TelegramProcessCallbackQueryOutput()
