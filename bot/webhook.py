# telegram_webhook_client.py

from typing import Any, Dict, List, Optional

import json
import httpx
from pydantic import HttpUrl

from bot.config import settings, logger


BASE_URL = f"https://api.telegram.org/bot{settings.bot_token}"


def _api(method: str) -> str:
    return f"{BASE_URL}/{method}"


def _allowed_updates() -> List[str]:
    # settings.allowed_updates is a list of StrEnum; convert to plain strings
    return [str(u.value) for u in settings.allowed_updates]


async def get_webhook() -> Dict[str, Any]:
    """
    https://core.telegram.org/bots/api#getwebhookinfo
    """
    url = _api("getWebhookInfo")
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        try:
            resp.raise_for_status()
        except httpx.HTTPStatusError as e:
            logger.error("getWebhookInfo failed: %s", e.response.text)
            raise
        data = resp.json()
        logger.info(data)
        return data


async def delete_webhook(drop_pending: Optional[bool] = None) -> Dict[str, Any]:
    """
    https://core.telegram.org/bots/api#deletewebhook
    """
    url = _api("deleteWebhook")
    payload: Dict[str, Any] = {}
    if drop_pending is not None:
        payload["drop_pending_updates"] = bool(drop_pending)

    timeout = httpx.Timeout(20.0, connect=5.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        # Telegram supports JSON body for this endpoint
        resp = await client.post(url, json=payload or None)
        try:
            resp.raise_for_status()
        except httpx.HTTPStatusError as e:
            logger.error("deleteWebhook failed: %s", e.response.text)
            raise
        data = resp.json()
        logger.info("Webhook removed: %s", data)
        return data


async def set_webhook(webhook: HttpUrl) -> Dict[str, Any]:
    """
    https://core.telegram.org/bots/api#setwebhook

    Sends JSON when no certificate is provided.
    Falls back to multipart/form-data only when uploading a certificate file.
    """
    url = _api("setWebhook")

    # Common fields
    base_payload: Dict[str, Any] = {
        "url": str(webhook),
        "drop_pending_updates": settings.drop_pending_updates,
        "max_connections": settings.max_connections,
    }

    # Optional fields
    if settings.secret_token:
        base_payload["secret_token"] = settings.secret_token
    if settings.webhook_ip:
        base_payload["ip_address"] = str(settings.webhook_ip)

    # allowed_updates must be a JSON-serialized array when using multipart.
    # With pure JSON body, we can send a plain list.
    updates_list = _allowed_updates()

    async with httpx.AsyncClient() as client:
        if settings.certificate:
            # Multipart/form-data path: add fields as form-data and attach the file.
            payload_form = dict(base_payload)
            payload_form["allowed_updates"] = json.dumps(updates_list)

            cert_path = settings.certificate
            filename = cert_path.name  # stem + suffix
            # Open/close the file properly while doing the request
            with cert_path.open("rb") as f:
                files = {"certificate": (filename, f, "application/octet-stream")}
                resp = await client.post(url, data=payload_form, files=files)
        else:
            # Pure JSON path (preferred when no cert file is used)
            payload_json = dict(base_payload)
            payload_json["allowed_updates"] = updates_list
            resp = await client.post(url, json=payload_json)

        try:
            resp.raise_for_status()
        except httpx.HTTPStatusError as e:
            logger.error("setWebhook failed: %s", e.response.text)
            raise

        data = resp.json()
        logger.info("Webhook set to: %s | response: %s", webhook, data)
        return data
