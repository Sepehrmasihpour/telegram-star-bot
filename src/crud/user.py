from typing import Optional, Any

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select

from src.models import User, Chat
from src.config import logger


# --------------------
# User CRUD
# --------------------


def create_user(db: Session, *, phone_number: Optional[str] = None) -> User:
    """
    Create a new User. Telegram chat(s) are created separately and linked via Chat.user_id.
    """
    try:
        user = User(phone_number=phone_number)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    except SQLAlchemyError as e:
        db.rollback()
        logger.error("failed to create user: %s", e)
        raise


def get_user_by_id(db: Session, user_id: int) -> User | None:
    try:
        return db.get(User, user_id)
    except SQLAlchemyError:
        logger.exception("failed to fetch user by id=%s", user_id)
        raise


def get_user_by_phone(db: Session, phone_number: str) -> User | None:
    try:
        return db.query(User).filter(User.phone_number == phone_number).first()
    except SQLAlchemyError:
        logger.exception("failed to fetch user by phone_number=%s", phone_number)
        raise


def get_user_by_chat_id(db: Session, chat_id: str) -> User | None:
    try:
        stmt = select(User).join(User.chats).where(Chat.chat_id == int(chat_id))
        return db.execute(stmt).scalars().first()
    except SQLAlchemyError as e:
        logger.error("get_user_by_chat_id failed: %s", e)
        raise


def update_user(db: Session, user_id: int, **fields: Any) -> User | None:
    try:
        user = db.get(User, user_id)
        if not user:
            logger.info("update_user: no user with id=%s", user_id)
            return None

        for key, value in fields.items():
            if hasattr(user, key):
                setattr(user, key, value)
            else:
                raise AttributeError(f"User has no attribute '{key}'")

        db.commit()
        db.refresh(user)
        return user

    except SQLAlchemyError as e:
        db.rollback()
        logger.error("failed to update user: %s", e)
        raise


def delete_user_by_id(db: Session, user_id: int) -> bool:
    """
    Deleting a user will also delete all related chats because of the
    `ondelete='CASCADE'` + relationship cascade.
    """
    try:
        user = db.get(User, user_id)
        if not user:
            logger.info("delete_user_by_id: no user with id=%s", user_id)
            return False

        db.delete(user)
        db.commit()
        return True

    except SQLAlchemyError:
        db.rollback()
        logger.exception("failed to delete user by id=%s", user_id)
        return False


# --------------------
# Chat CRUD (child of User)
# --------------------


def create_chat(
    db: Session,
    *,
    user_id: int,
    chat_id: int,
    first_name: str,
    username: Optional[str] = None,
) -> Chat:
    """
    Create a Chat record for a given user.
    """
    try:
        user = db.get(User, user_id)
        if not user:
            raise ValueError(f"User with id={user_id} not found")

        chat = Chat(
            user_id=user_id,
            chat_id=chat_id,
            first_name=first_name,
            username=username,
        )
        db.add(chat)
        db.commit()
        db.refresh(chat)
        return chat
    except SQLAlchemyError as e:
        db.rollback()
        logger.error("failed to create chat: %s", e)
        raise


def get_chat_by_chat_id(db: Session, chat_id: int) -> Chat | None:
    try:
        return db.query(Chat).filter(Chat.chat_id == chat_id).first()
    except SQLAlchemyError:
        logger.exception("failed to fetch chat by chat_id=%s", chat_id)
        raise


def get_chat_by_id(db: Session, chat_id_pk: int) -> Chat | None:
    try:
        return db.get(Chat, chat_id_pk)
    except SQLAlchemyError:
        logger.exception("failed to fetch chat by id=%s", chat_id_pk)
        raise


def update_chat(db: Session, chat_id_pk: int, **fields: Any) -> Chat | None:
    """
    Update a Chat by its primary key `id`.
    """
    try:
        chat = db.get(Chat, chat_id_pk)
        if not chat:
            logger.info("update_chat: no chat with id=%s", chat_id_pk)
            return None

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
        logger.error("failed to update chat: %s", e)
        raise


def update_chat_by_chat_id(db: Session, chat_id: int, **fields: Any) -> Chat | None:
    """
    Update a Chat using Telegram's `chat_id`.
    """
    try:
        chat = db.query(Chat).filter(Chat.chat_id == chat_id).first()

        if chat is None:
            logger.info("update_chat_by_chat_id: no chat with chat_id=%s", chat_id)
            return None

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
        logger.error("failed to update chat by chat_id: %s", e)
        raise


def delete_chat_by_id(db: Session, chat_id_pk: int) -> bool:
    try:
        chat = db.get(Chat, chat_id_pk)
        if not chat:
            logger.info("delete_chat_by_id: no chat with id=%s", chat_id_pk)
            return False

        db.delete(chat)
        db.commit()
        return True

    except SQLAlchemyError:
        db.rollback()
        logger.exception("failed to delete chat by id=%s", chat_id_pk)
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
