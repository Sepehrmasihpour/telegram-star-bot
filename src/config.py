import logging.config
import os
import socket
import warnings
from enum import IntEnum, StrEnum
from ipaddress import IPv4Address
from typing import List, Union

from pydantic import BaseModel, HttpUrl, FilePath, Field, PositiveInt
from pydantic_settings import BaseSettings


class SecurityWarning(Warning):
    """Custom security warning."""


class AllowedPorts(IntEnum):
    tcp: int = 88
    http: int = 80
    https: int = 443
    openssl: int = 8443


class AllowedUpdates(StrEnum):
    """Updates to receive using the webhook.

    See Also:
        - Refer https://core.telegram.org/bots/api#update for the entire list of allowed updates.
        - However, for this POC, we only consider limited options.
    """

    message: str = "message"
    edited_message: str = "edited_message"
    channel_post: str = "channel_post"
    edited_channel_post: str = "edited_channel_post"
    callback_query: str = "callback_query"


class TelegramProcessTextOutputs:
    @staticmethod
    def shop_options(chat_id: Union[str, int]):
        return {
            "chat_id": chat_id,
            "text": "به ربات تست خوش آمدید",
            "reply_markup": {
                "inline_keyboard": [
                    [{"text": "product no1", "callback_data": "buy_product_1"}],
                    [{"text": "product no2", "callback_data": "buy_product_2"}],
                    [{"text": "product no3", "callback_data": "buy_product_3"}],
                    [{"text": "product no4", "callback_data": "show_prices"}],
                    [{"text": "show terms of service", "callback_data": "show_terms"}],
                    [{"text": "support", "callback_data": "support"}],
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
            "text": (
                """
                        🌟welcome to the testing bot!\n
                        📱to start please enter you'r phone number\n
                        .enter the phone number with the 09121764237 format\n
                        .the phone number must belong to you\n
                        .this phone number is used for verifying your identity and direct payment\n
                        \n
                        💡keep note:
                        .your phone number will remain safe and secret\n
                        .it will only be used for verifying your identity and payment\n
                        .you can change it at any time\n
                        \n
                        🔐security:
                        .all your infromation is stored using encryption\n
                        .no data will be shared with a third party
                            """
            ),
        }

    @staticmethod
    def phone_number_verfication_needed(chat_id: Union[str, int]):

        return {
            "chat_id": chat_id,
            "text": (
                """
                ❌you'r phone number has not been verified\n
                📱in order to continue please verify your phone number\n

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
        return {"chat_id": chat_id, "text": "this is the support section"}

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
            "text": """
                ✅the verification code has been sent to your phone number. please enter the code\n
                \n
                💳important points about bank acounts:\n
                .The acount that you use for payment must belong to the owner of the phone number\n
                .The  system verifies weather the phone number and the acount number belong to the same person\n
                .In case they don't, you'r payment will not go through\n
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

    @staticmethod
    def invalid_otp(chat_id: Union[str, int]):
        return {"chat_id": chat_id, "text": "❌invalid verification code"}

    @staticmethod
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
                "text": """
📜Terms of service agreement\n
\n
🔰Terms of Using the Test Bot:\n
\n
1️⃣General Rules:\n
• This service is intended for purchasing Telegram Stars and Telegram Premium\n
• The user is required to provide accurate and complete information\n
• Any misuse of the service is prohibited\n
\n
2️⃣Payment Rules:\n
• Payments are non-refundable\n
• By order of the Cyber Police (FATA), some transactions may require up to 72 hours for verification before the product is delivered\n
\n
3️⃣Privacy:\n
• Your personal information will be kept confidential\n
• The information is used for identity and payment verification\n
• Information will not be shared with any third party\n
\n
4️⃣Responsibilities:\n
• We are committed to delivering products intact and on time\n
• The user is responsible for the accuracy of the information they provide\n
• Any form of fraud will result in being banned from the service\n
\n
5️⃣Support:\n
• 24/7 support is available to you\n
• Response time: up to 2 hours\n
• Support contact: @TestSupport
\n
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

    @staticmethod
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

    @staticmethod
    def welcome_message(chat_id: Union[str, id]):
        return {
            "chat_id": chat_id,
            "text": """
            ✅the terms and condtionns has been accepted!\n
            \n
            🎉welcome! now you can use all the features\n
            \n
            💡To begin:\n
            .the command /buy for purchasing of products.\n
            .the command /prices for seeing the prices.\n
            .the command /support for support\n
            \n
            🔁the command /start for returning to main menu
            """,
        }


class Settings(BaseSettings):
    """Env configuration.

    References:
        https://docs.pydantic.dev/2.3/migration/#required-optional-and-nullable-fields
    """

    bot_token: str

    db_url: str

    # Tunneling specifics
    ngrok_token: str | None = None
    endpoint: str = "/telegram-webhook"

    # Webhook specifics
    webhook: HttpUrl | None = None
    webhook_ip: IPv4Address | None = None
    secret_token: str | None = Field(None, pattern="^[A-Za-z0-9_-]{1,256}$")
    certificate: FilePath | None = None
    drop_pending_updates: bool = True
    max_connections: PositiveInt = Field(40, le=100, ge=1)
    allowed_updates: List[AllowedUpdates] = [
        AllowedUpdates.message,
        AllowedUpdates.edited_message,
        AllowedUpdates.callback_query,
    ]

    # API specifics
    host: str = socket.gethostbyname("localhost")
    port: AllowedPorts = AllowedPorts.openssl
    bots_name: str = "test_bot"

    debug: bool = False

    # telegram processing config
    telegram_process_text_outputs: type[TelegramProcessTextOutputs] = (
        TelegramProcessTextOutputs
    )

    telegram_process_callback_query_outputs: type[
        TelegramProcessCallbackQueryOutput
    ] = TelegramProcessCallbackQueryOutput

    class Config:
        extra = "allow"
        env_file = os.environ.get("env_file", os.environ.get("ENV_FILE", ".env"))


settings = Settings()
if not (settings.ngrok_token or settings.webhook):
    raise RuntimeError(
        "Config error: set NGROK_TOKEN or WEBHOOK. You need one path to a public HTTPS URL."
    )


class LogConfig(BaseModel):
    """Logging configuration to be set for the server"""

    LOGGER_NAME: str = "TelegramAPI"
    LOG_FORMAT: str = "%(levelprefix)s %(message)s"
    LOG_LEVEL: str = "DEBUG" if settings.debug else "INFO"

    # Logging config
    version: int = 1
    disable_existing_loggers: bool = False
    formatters: dict = {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": LOG_FORMAT,
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    }
    handlers: dict = {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
    }
    loggers: dict = {
        LOGGER_NAME: {"handlers": ["default"], "level": LOG_LEVEL},
    }


logging.config.dictConfig(LogConfig().model_dump())
logger = logging.getLogger("TelegramAPI")

if settings.webhook and settings.webhook.scheme == "http":
    raise ValueError(
        "\n\nPre-configured webhook should be able to handle TLS1.2(+) HTTPS-traffic"
    )

if not (settings.ngrok_token or settings.certificate):
    target = str(settings.webhook) if settings.webhook else "<no-webhook-configured>"
    logger.critical(
        "No NGROK_TOKEN and no certificate file. "
        "If you are not using ngrok, '%s' must terminate TLS with a trusted CA.",
        target,
    )

if not settings.secret_token:
    warnings.warn(
        "It is highly recommended to set a value for `secret_token`, "
        "as it will ensure the request comes from a webhook set by you.",
        SecurityWarning,
    )

if settings.webhook and "ngrok" in settings.webhook.host.lower():
    logger.info("Using ngrok; no custom certificate needed.")
