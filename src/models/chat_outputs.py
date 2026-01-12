from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import Integer, String
from src.db.base import Base


class ChatOutoput(Base):
    __tablename__ = "chat_outputs"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(5, 70), nullable=False, unique=True)
    number_of_text_box: Mapped[int] = mapped_column(Integer, nullable=False)
    text: Mapped[str] = mapped_column(String, False)


# later on there needs to be text box as children for some of the chat outputs to work
