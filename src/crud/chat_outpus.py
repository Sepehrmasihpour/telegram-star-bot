from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from typing import Sequence

from src.models import ChatOutput, Button, ButtonIndex
from src.config import logger

from dataclasses import dataclass


from src.db.seed_data import SEED_TELEGRAM_OUTPUTS


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
