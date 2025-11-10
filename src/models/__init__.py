from src.db.base import Base
from src.models.chat import Chat

# Alembic needs Base.metadata to see models
__all__ = ["Base", "Chat"]
