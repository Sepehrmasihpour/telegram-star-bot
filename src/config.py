import logging.config
import os
import socket
import warnings
from enum import IntEnum, StrEnum
from ipaddress import IPv4Address
from typing import List

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


class Settings(BaseSettings):
    """Env configuration.

    References:
        https://docs.pydantic.dev/2.3/migration/#required-optional-and-nullable-fields
    """

    bot_token: str

    db_url: str

    jwt_secret: str
    jwt_token_expirty_per_seconds: int = 480

    # Tunneling specifics
    ngrok_token: str | None = None
    endpoint: str = "telegram/telegram-webhook"

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

    base_url: str = ""  #! this is for testing later this should be better

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
