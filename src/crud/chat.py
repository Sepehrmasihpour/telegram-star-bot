from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from src.models.chat import Chat
from typing import Optional, Any
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
        raise


def get_chat_by_chat_id(db: Session, chat_id: int) -> Chat | None:
    try:
        return db.query(Chat).filter(Chat.chat_id == chat_id).first()
    except SQLAlchemyError:
        logger.exception("failed to fetch chat by chat_id=%s", chat_id)
        raise


def get_chat_by_id(db: Session, id: int) -> Chat | None:
    try:
        return db.get(Chat, id)
    except SQLAlchemyError as e:
        logger.error(f"failed to fetch chat: {e}")
        raise


def update_chat(db: Session, id: int, **fields: Any) -> Chat | None:
    try:
        chat = db.get(Chat, id)
        if not chat:
            logger.info("update_chat: no chat with id=%s", id)
            return None

        for key, value in Any.items():
            if hasattr(chat, key):
                setattr(chat, key, value)
            else:
                raise AttributeError(f"Chat has no attribute '{key}'")

        db.commit()
        db.refresh(chat)
        return chat

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"failed to update chat: {e}")
        raise


def update_chat_by_chat_id(db: Session, chat_id: int, **fields: Any):
    try:
        chat = db.query(Chat).filter(Chat.chat_id == chat_id).first()

        if chat is None:
            raise ValueError(f"Chat with chat_id={chat_id} not found")

        for key, value in fields.items():
            if hasattr(chat, key):
                setattr(chat, key, value)
            else:
                raise AttributeError(f"Chat has no attribute '{key}'")

        db.commit()
        db.refresh(chat)
        return chat
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"failed to update chat: {e}")
        raise


def delete_chat_by_id(db: Session, id: int) -> bool:
    try:
        chat = db.get(Chat, id)
        if not chat:
            logger.info("delete_chat_by_id: no chat with id=%s", id)
            return False

        db.delete(chat)
        db.commit()
        return True

    except SQLAlchemyError:
        db.rollback()
        logger.exception("failed to delete chat by id=%s", id)
        return False


def delete_chat_by_chat_id(db: Session, chat_id: int) -> bool:
    try:
        chat = db.query(Chat).filter(Chat.chat_id == chat_id).first()
        if not chat:
            logger.info("delete_chat_by_chat_id: no chat with chat_id=%s", chat_id)
            return False

        db.delete(chat)
        db.commit()
        return True

    except SQLAlchemyError:
        db.rollback()
        logger.exception("failed to delete chat by chat_id=%s", chat_id)
        return False
