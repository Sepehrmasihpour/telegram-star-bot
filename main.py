import uvicorn
import httpx

from fastapi import FastAPI
from contextlib import asynccontextmanager
from urllib.parse import urljoin
from sqlalchemy.orm import Session
from typing import Optional

from src.routers import auth, health, payment, telegram, bot
from src.config import settings, logger
from src.tunnel import start_ngrok_tunnel, stop_ngrok_tunnel, get_current_ngrok_url
from src.bot.webhook import set_webhook, delete_webhook
from src.bot.chat_output import TelegrambotOutputs
from src.db.seed import seed_initial_products, seed_initial_chat_outputs
from src.db.seed_data import SEED_TELEGRAM_OUTPUTS
from src.db import SessionLocal


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup:
      - create shared httpx AsyncClient
      - discover or start public URL (webhook or ngrok)
      - set Telegram webhook
    Shutdown:
      - delete Telegram webhook
      - stop ngrok if we started it
      - close AsyncClient
    """
    # 1) shared HTTP client
    app.state.http = httpx.AsyncClient()

    # 2) get public URL
    public_url: Optional[str] = None
    using_ngrok = False

    if settings.webhook:
        public_url = str(settings.webhook)
    else:
        using_ngrok = True
        public_url = start_ngrok_tunnel()
        if not public_url:
            # try to read the running ngrok url if the tunnel is already up
            public_url = get_current_ngrok_url()

    if not public_url:
        # can't serve webhooks at all
        await app.state.http.aclose()
        raise RuntimeError("Failed to acquire a public HTTPS URL (webhook or ngrok).")

    logger.info(
        "Local http://%s:%s  →  %s", settings.host, settings.port.value, public_url
    )

    # 3) set telegram webhook
    target_url = urljoin(public_url.rstrip("/") + "/", settings.endpoint.lstrip("/"))
    try:
        await set_webhook(target_url)
        logger.info("Webhook registered at: %s", target_url)
    except Exception as e:
        await app.state.http.aclose()
        if using_ngrok:
            stop_ngrok_tunnel()
        raise RuntimeError(f"Failed to set Telegram webhook: {e}") from e
    try:
        db: Session = SessionLocal()
        seed_initial_products(db)
        seed_initial_chat_outputs(db, seed_data=SEED_TELEGRAM_OUTPUTS)
        db.close()
    except Exception as e:
        logger.error(f"Database seeding failed: {e}")
    # ---- hand control to the app ----

    # ----- init of the telegram chat outputs----#
    app.state.outputs = TelegrambotOutputs()
    try:
        yield
    finally:
        # ---- graceful shutdown ----
        try:
            await delete_webhook(drop_pending=True)
            logger.info("Webhook deleted.")
        except Exception as e:
            logger.warning("Failed to delete webhook: %s", e)

        if using_ngrok:
            try:
                stop_ngrok_tunnel()
            except Exception as e:
                logger.warning("Failed to stop ngrok: %s", e)

        try:
            await app.state.http.aclose()
        except Exception:
            pass


with open("README.md", encoding="utf-8") as file:
    readme_data = file.readlines()

app = FastAPI(
    lifespan=lifespan,
    title=readme_data[0].lstrip("#").strip() if readme_data else "Telegram Bot",
    description="\n".join(readme_data[1:]).strip() if len(readme_data) > 1 else "",
)

app.include_router(health.router, prefix="/health", tags=["Health"])
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(telegram.router, prefix="/telegram", tags=["Telegram"])
app.include_router(payment.router, prefix="/payment", tags=["Payment"])
app.include_router(bot.router, prefix="/bot", tags=["Bot"])

if __name__ == "__main__":
    uvicorn.run(app=app, host=settings.host, port=settings.port.value)
