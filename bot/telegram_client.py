import httpx
from bot.telegram_models import SendMessage
from bot.config import settings

BASE_URL = f"https://api.telegram.org/bot{settings.bot_token}"


def send_message(payload: SendMessage):
    url = f"{BASE_URL}sendMessage"
    resp = httpx.post(url=url, json=payload.model_dump())
    resp.raise_for_status()
    return resp.json
