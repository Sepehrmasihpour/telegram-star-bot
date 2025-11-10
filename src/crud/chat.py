from sqlalchemy.orm import Session
from src.models.chat import Chat
from typing import Optional
from src.config import logger


def create_chat(
    db: Session, *, chat_id: int, first_name: str, username: Optional[str] = None
) -> Chat:
    chat = Chat(chat_id=chat_id, first_name=first_name, username=username)
    db.add(chat)
    db.commit()
    db.refresh(chat)
    return chat


def get_chat_by_chat_id(db: Session, chat_id: int) -> Chat | None:
    return db.query(Chat).filter(Chat.chat_id == chat_id).first()


def get_chat_by_id(db: Session, id: int) -> Chat | None:
    return db.get(Chat, id)


def delete_chat_by_id(db: Session, id: int) -> bool:
    chat = db.get(Chat, id)
    if not chat:
        logger.error("no such chat exists")
        return False
    db.delete(chat)
    db.commit()
    return True


def delete_chata_by_chat_id(db: Session, chat_id: int) -> bool:
    chat = db.query(Chat).filter(Chat.chat_id == chat_id).first()
    if not chat:
        logger.error("no such chat exists")
        return False
    db.delete(chat)
    db.commit()
    return True
