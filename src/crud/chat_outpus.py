from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from typing import Sequence

from src.models import ChatOutput, Button, ButtonIndex, Placeholder
from src.models.chat_outputs import PlaceHolderTypes
from src.config import logger

from dataclasses import dataclass


def create_button(db: Session, name: str, text: str, callback_data: str):
    try:
        button = Button(name=name, text=text, callback_data=callback_data)
        db.add(button)
        db.refresh()
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"create_button crud operation failed:{e}")
        raise


def create_button_index(db: Session, chat_output_id: int, button_id):
    try:
        button_index = ButtonIndex(chat_output_id=chat_output_id, button_id=button_id)
        db.add(button_index)
        db.refresh()
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"create_button_index crud opeeration failed:{e}")


def create_placeholder(
    db: Session, chat_output_id: int, name: str, type: PlaceHolderTypes
):
    try:
        palceholder = Placeholder(chat_output_id=chat_output_id, name=name, type=type)
        db.add(palceholder)
        db.refresh()
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"create_placeholder crud operation failed:{e}")


def create_chat_output(db: Session, name: str, text: str):
    try:
        chat_output = ChatOutput(name=name, text=text)
        db.add(chat_output)
        db.refresh()
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"create_chat_output crud operation failed:{e}")
        raise
