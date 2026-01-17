from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from typing import Sequence

from src.models import ChatOutput
from src.config import logger

from dataclasses import dataclass


@dataclass(frozen=True)
class CreatePlaceholderItem:
    chat_output_id: int
    name: str
    type: str


@dataclass(frozen=True)
class CreateButtonItem:
    chat_output_id: int
    name: str
    text: str
    number: int


# TODO
def create_chat_output_instance_with_placeholder_and_button(
    db: Session,
    name: str,
    text: str,
    placeholder_items: Sequence[CreatePlaceholderItem],
    button_items: Sequence[CreateButtonItem],
):
    try:
        """
        this will create a chat output instance wiht the placeholder and button children
        """
        ...
    except SQLAlchemyError as e:
        db.rollback()
        logger.error("failed to create chat_output: %s", e)
        raise


def get_chat_output_by_name(db: Session, name: str) -> ChatOutput | None:
    try:
        return db.query(ChatOutput).filter(ChatOutput.name == name).first()
    except SQLAlchemyError:
        logger.exception("failed to fetch chat_output by phone_number=%s", name)
        raise
