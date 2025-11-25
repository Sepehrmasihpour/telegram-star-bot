from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, Boolean, String, UniqueConstraint, DateTime
from src.db.base import Base
from datetime import datetime


class Chat(Base):
    __tablename__ = "chats"

    id: Mapped[int] = mapped_column(primary_key=True)
    chat_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    first_name: Mapped[str] = mapped_column(String(255), nullable=False)
    username: Mapped[str | None] = mapped_column(String(255))
    accepted_terms: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="false"
    )
    phone_number: Mapped[str] = mapped_column(String, nullable=True)
    phone_number_validated: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="false"
    )
    last_time_verfication_code_sent: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, server_default=None
    )
    pending_action: Mapped[str | None] = mapped_column(String, nullable=True)
    phone_input_attempt: Mapped[int] = mapped_column(Integer, server_default="0")
    __table_args__ = (UniqueConstraint("phone_number", name="uq_chats_phone_number"),)


def __repr__(self):
    return f"<Chat {self.chat_id} {self.username}>"
