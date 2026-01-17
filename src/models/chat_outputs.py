from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import Integer, String, UniqueConstraint, ForeignKey
from src.db.base import Base


class ChatOutput(Base):
    __tablename__ = "chat_outputs"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(5, 70), nullable=False, unique=True)
    number_of_text_box: Mapped[int] = mapped_column(Integer, nullable=False)
    text: Mapped[str] = mapped_column(String(5, 5000), nullable=False)
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
    type: Mapped[str] = mapped_column(String(5, 100), nullable=False)
    # * the type field is to difrentiate between place holders that only take up a words
    # * or few worth of space and those that take entire block of a message
    text: Mapped[str] = mapped_column(String(1, 600), nullable=False)
    chat_output: Mapped["ChatOutput"] = relationship(back_populates="placeholders")


class Button(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    chat_output_id: Mapped[int] = mapped_column(
        ForeignKey("chat_outputs.id", ondelete="CASCADE")
    )
    name: Mapped[str] = mapped_column(String(5, 100), nullable=False)
    text: Mapped[str] = mapped_column(String(1, 600), nullable=False)
    chat_output: Mapped["ChatOutput"] = relationship(back_populates="buttons")
