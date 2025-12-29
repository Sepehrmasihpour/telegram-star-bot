from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, Boolean, String, UniqueConstraint, DateTime, ForeignKey
from src.db.base import Base
from datetime import datetime


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    phone_number: Mapped[str] = mapped_column(String(13), nullable=True, unique=True)
    phone_number_validated: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="false"
    )
    last_time_verfication_code_sent: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, server_default=None
    )
    chats: Mapped[list["Chat"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    __table_args__ = (UniqueConstraint("phone_number", name="uq_users_phone_number"),)


class Chat(Base):
    __tablename__ = "chats"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
    )
    chat_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    chat_verified: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="false"
    )
    first_name: Mapped[str] = mapped_column(String(255), nullable=False)
    username: Mapped[str | None] = mapped_column(String(255))
    accepted_terms: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="false"
    )
    pending_action: Mapped[str | None] = mapped_column(String, nullable=True)
    phone_input_attempt: Mapped[int] = mapped_column(Integer, server_default="0")
    last_message_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    user: Mapped["User"] = relationship(back_populates="chats")


def __repr__(self):
    return f"<Chat {self.chat_id} {self.username}>"
