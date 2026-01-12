from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from src.models import ChatOutoput
from src.config import logger


def create_chat_output_instance(db: Session, name: str, text: str):
    try:
        chat_output = ChatOutoput(name=name, text=text)
        db.add(chat_output)
        db.commit()
        db.refresh(chat_output)
        return chat_output
    except SQLAlchemyError as e:
        db.rollback()
        logger.error("failed to create chat_output: %s", e)
        raise


def get_chat_output_by_name(db: Session, name: str) -> ChatOutoput | None:
    try:
        return db.query(ChatOutoput).filter(ChatOutoput.name == name).first()
    except SQLAlchemyError:
        logger.exception("failed to fetch chat_output by phone_number=%s", name)
        raise
