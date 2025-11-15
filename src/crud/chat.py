from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from src.models.chat import Chat
from typing import Optional, Dict
from src.config import logger


def create_chat(
    db: Session, *, chat_id: int, first_name: str, username: Optional[str] = None
) -> Chat | None:
    try:
        chat = Chat(chat_id=chat_id, first_name=first_name, username=username)
        db.add(chat)
        db.commit()
        db.refresh(chat)
        return chat
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"failed to create chat: {e}")
        return None


def get_chat_by_chat_id(db: Session, chat_id: int) -> Chat | None:
    try:
        return db.query(Chat).filter(Chat.chat_id == chat_id).first()
    except SQLAlchemyError as e:
        logger.error(f"failed to fetch chat: {e}")
        return None


def get_chat_by_id(db: Session, id: int) -> Chat | None:
    try:
        return db.get(Chat, id)
    except SQLAlchemyError as e:
        logger.error(f"failed to fetch chat: {e}")
        return None


def update_chat(db: Session, id: int, data: Dict) -> Chat | None:
    try:
        chat = db.get(Chat, id)
        if not chat:
            logger.error("no such chat exists")
            return None

        for key, value in data.items():
            if hasattr(chat, key):
                setattr(chat, key, value)

        db.commit()
        db.refresh(chat)
        return chat

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"failed to update chat: {e}")
        return None


def delete_chat_by_id(db: Session, id: int) -> bool:
    try:
        chat = db.get(Chat, id)
        if not chat:
            logger.error("no such chat exists")
            return False

        db.delete(chat)
        db.commit()
        return True

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"failed to delete chat: {e}")
        return False


def delete_chat_by_chat_id(db: Session, chat_id: int) -> bool:
    try:
        chat = db.query(Chat).filter(Chat.chat_id == chat_id).first()
        if not chat:
            logger.error("no such chat exists")
            return False

        db.delete(chat)
        db.commit()
        return True

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"failed to delete chat: {e}")
        return False
