from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import Integer, String, UniqueConstraint, ForeignKey, Enum as SAEnum
from src.db.base import Base
from enum import Enum


class PlaceHolderTypes(str, Enum):
    INLINE = "inline"
    OUTLINE = "outline"


class ChatOutput(Base):
    __tablename__ = "chat_outputs"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(5, 70), nullable=False, unique=True)
    text: Mapped[str] = mapped_column(String(5, 5000), nullable=False)
    button_count: Mapped[int] = mapped_column(Integer, server_default="0", default=0)
    placehoders: Mapped[list["Placeholder"]] = relationship(
        back_populates="chat_output", cascade="all,delete-orphan"
    )
    buttons: Mapped[list["Button"]] = relationship(
        back_populates="chat_output", cascade="all,delete-orphan"
    )
    __table_args__ = (UniqueConstraint("name", name="uq_chat_output_name"),)


class Placeholder(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    chat_output_id: Mapped[int] = mapped_column(
        ForeignKey("chat_outputs.id", ondelete="CASCADE")
    )
    name: Mapped[str] = mapped_column(String(5, 100), nullable=False)
    type: Mapped[PlaceHolderTypes] = mapped_column(
        SAEnum(PlaceHolderTypes),
        nullable=False,
    )
    chat_output: Mapped["ChatOutput"] = relationship(back_populates="placeholders")


class Button(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    chat_output_id: Mapped[int] = mapped_column(
        ForeignKey("chat_outputs.id", ondelete="CASCADE")
    )
    number: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(String(5, 100), nullable=False)
    text: Mapped[str] = mapped_column(String(1, 600), nullable=False)
    chat_output: Mapped["ChatOutput"] = relationship(back_populates="buttons")
