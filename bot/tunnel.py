import re
from pyngrok import ngrok
from pyngrok.conf import get_default
from pyngrok.exception import PyngrokError
from bot.config import settings, logger

# Set up pyngrok configuration
get_default().config_path = "ngrok.yaml"

# Authenticate ngrok if token exists
if settings.ngrok_token:
    ngrok.set_auth_token(settings.ngrok_token)
else:
    logger.warning(
        "No NGROK_TOKEN found. You can still use ngrok, but tunnels may expire quickly."
    )


def start_ngrok_tunnel() -> str | None:
    """
    Starts an ngrok HTTP tunnel and returns the public HTTPS URL.
    If an error occurs, returns None instead of crashing the app.
    """
    try:
        # Create a new tunnel to your FastAPI server
        endpoint = ngrok.connect(settings.port.value, "http")
        public_url = endpoint.public_url

        # Always prefer https even if pyngrok returns http
        if public_url.startswith("http://"):
            public_url = public_url.replace("http://", "https://")

        logger.info(f"✅ Ngrok tunnel started: {public_url}")
        return public_url

    except PyngrokError as err:
        logger.error(f"❌ Failed to start ngrok tunnel: {err}")
        return None


def stop_ngrok_tunnel() -> None:
    """
    Terminates all active ngrok tunnels.
    Safe to call even if no tunnels exist.
    """
    try:
        ngrok.kill()  # uses default config when None is passed
        logger.info("🛑 Ngrok tunnel stopped.")
    except Exception as err:
        logger.warning(f"⚠ Failed to stop ngrok tunnel: {err}")


def get_current_ngrok_url() -> str | None:
    """
    Retrieves the currently active ngrok public URL, if available.
    This queries the local ngrok API (http://127.0.0.1:4040/status).
    """
    import httpx

    try:
        r = httpx.get("http://127.0.0.1:4040/status")
        match = re.search(r"https://[a-z0-9\-]+\.ngrok[-\w]*\.app", r.text)
        if match:
            return match.group(0)
    except Exception as err:
        logger.debug(f"Could not fetch current ngrok URL: {err}")
    return None
