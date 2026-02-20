from typing import Any

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from src.models import ChatOutput, Button, ButtonIndex, Placeholder
from src.models.chat_outputs import PlaceHolderTypes

from src.config import logger


def create_button(
    db: Session, name: str, text: str, callback_data: str, commit: bool = True
):
    try:
        button = Button(name=name, text=text, callback_data=callback_data)
        db.add(button)
        db.flush()
        if commit:
            db.commit()
            db.refresh(button)
        return button
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"create_button crud operation failed:{e}")
        raise


def create_button_index(
    db: Session, chat_output_id: int, button_id: int, number: int, commit: bool = True
):
    try:
        button_index = ButtonIndex(
            chat_output_id=chat_output_id, button_id=button_id, number=number
        )
        db.add(button_index)
        db.flush()
        if commit:
            db.commit()
            db.refresh(button_index)
        return button_index
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"create_button_index crud opeeration failed:{e}")
        raise


def create_placeholder(
    db: Session,
    chat_output_id: int,
    name: str,
    type: PlaceHolderTypes,
    commit: bool = True,
):
    try:
        placeholder = Placeholder(chat_output_id=chat_output_id, name=name, type=type)
        db.add(placeholder)
        db.flush()
        if commit:
            db.commit()
            db.refresh(placeholder)
        return placeholder
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"create_placeholder crud operation failed:{e}")


def create_chat_output(db: Session, name: str, text: str, commit: bool = True):
    try:
        chat_output = ChatOutput(name=name, text=text)
        db.add(chat_output)
        db.flush()
        if commit:
            db.commit()
            db.refresh(chat_output)
        return chat_output
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"create_chat_output crud operation failed:{e}")
        raise


def get_chat_output_by_name(db: Session, name: str):
    try:
        return db.query(ChatOutput).filter(ChatOutput.name == name).first()
    except SQLAlchemyError as e:
        logger.error(f"get_chat_output_by_name crud operatioin failed:{e}")
        raise


def get_button_by_name(db: Session, name: str):
    try:
        return db.query(Button).filter(Button.name == name).first()
    except SQLAlchemyError as e:
        logger.error(f"get_button_by_name crud operatioin failed:{e}")
        raise


def get_placeholder_by_name(db: Session, name: str):
    try:
        return db.query(Placeholder).filter(Placeholder.name == name).first()
    except SQLAlchemyError as e:
        logger.error(f"get_placeholder_by_name crud operatioin failed:{e}")
        raise


def update_chat_output_by_name(
    db: Session, name: str, commit: bool = True, **fields: Any
) -> ChatOutput:
    try:
        output = db.query(ChatOutput).filter(ChatOutput.name == name).first()
        if output is None:
            logger.info(f"update_chat_output_by_name: no output by this name: {name}")
            return None

        for key, value in fields.items():
            if hasattr(output, key):
                setattr(output, key, value)
            else:
                raise AttributeError(f"output has no attribute '{key}")
        if commit:
            db.commit()
            db.refresh(output)
        return output
    except SQLAlchemyError as e:
        logger.error(f"update_chat_output_by_name failed: {e}")
        raise
