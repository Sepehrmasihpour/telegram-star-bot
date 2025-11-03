import uvicorn
from fastapi import FastAPI

from bot.config import settings
from bot.router import router, lifespan

with open("README.md", encoding="utf-8") as file:
    readme_data = file.readlines()

app = FastAPI(
    lifespan=lifespan,
    title=readme_data[0].lstrip("#").strip() if readme_data else "Telegram Bot",
    description="\n".join(readme_data[1:]).strip() if len(readme_data) > 1 else "",
)

app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(app=app, host=settings.host, port=settings.port.value)
