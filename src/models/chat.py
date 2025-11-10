from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, Boolean, String
from src.db.base import Base


class Chat(Base):
    __tablename__ = "chats"

    id: Mapped[int] = mapped_column(primary_key=True)
    chat_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    first_name: Mapped[str] = mapped_column(String(255), nullable=False)
    username: Mapped[str | None] = mapped_column(String(255))
    accepted_terms: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="false"
    )


def __repr__(self):
    return f"<Chat {self.chat_id} {self.username}>"
