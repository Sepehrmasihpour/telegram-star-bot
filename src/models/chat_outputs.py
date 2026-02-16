from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import (
    Integer,
    String,
    UniqueConstraint,
    ForeignKey,
    Enum as SAEnum,
)
from src.db.base import Base
from enum import Enum


class PlaceHolderTypes(str, Enum):
    INLINE = "inline"
    OUTLINE = "outline"


class ChatOutput(Base):
    __tablename__ = "chat_outputs"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(70), nullable=False, unique=True)
    text: Mapped[str] = mapped_column(String(5000), nullable=False)
    placeholders: Mapped[list["Placeholder"]] = relationship(
        back_populates="chat_output", cascade="all,delete-orphan"
    )
    button_indexes: Mapped[list["ButtonIndex"]] = relationship(
        back_populates="chat_output", cascade="all,delete-orphan"
    )
    __table_args__ = (UniqueConstraint("name", name="uq_chat_output_name"),)


class Placeholder(Base):
    __tablename__ = "placeholders"
    id: Mapped[int] = mapped_column(primary_key=True)
    chat_output_id: Mapped[int] = mapped_column(
        ForeignKey("chat_outputs.id", ondelete="CASCADE")
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    type: Mapped[PlaceHolderTypes] = mapped_column(
        SAEnum(PlaceHolderTypes), nullable=False
    )

    __table_args__ = (
        UniqueConstraint("chat_output_id", "name", name="uq_placeholder_per_output"),
    )


class ButtonIndex(Base):
    __tablename__ = "button_indexes"
    id: Mapped[int] = mapped_column(primary_key=True)
    chat_output_id: Mapped[int] = mapped_column(
        ForeignKey("chat_outputs.id", ondelete="CASCADE")
    )
    button_id: Mapped[int] = mapped_column(ForeignKey("buttons.id"))
    number: Mapped[int] = mapped_column(Integer, nullable=False)
    chat_output: Mapped["ChatOutput"] = relationship(back_populates="button_indexes")
    button: Mapped["Button"] = relationship(
        "Button",
        foreign_keys=[button_id],
        back_populates="button_indexes",
        lazy="joined",  # optional: avoids N+1 for small keyboards
    )
    __table_args__ = (
        UniqueConstraint("chat_output_id", "number", name="uq_button_index_order"),
    )


class Button(Base):
    __tablename__ = "buttons"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    text: Mapped[str] = mapped_column(String(600), nullable=False)
    callback_data: Mapped[str] = mapped_column(String(500), nullable=False)
    button_indexes: Mapped[list["ButtonIndex"]] = relationship(
        "ButtonIndex",
        back_populates="button",
    )
    __table_args__ = (UniqueConstraint("name", name="uq_button_name"),)
