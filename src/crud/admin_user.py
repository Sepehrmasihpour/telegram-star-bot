from typing import Any

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from src.models import AdminUser
from src.config import logger


def create_admin_user(
    db: Session,
    *,
    phone_number: str,
    password_hash: str,
    otp_token: str,
    commit: bool = True,
) -> AdminUser:
    try:
        admin_user = AdminUser(
            phone_number=phone_number, password_hash=password_hash, otp_token=otp_token
        )
        db.add(admin_user)
        db.flush()
        if commit:
            db.commit()
            db.refresh(AdminUser)
        return admin_user
    except SQLAlchemyError as e:
        logger.error(f"create_admin_user crud operation failed: {e}")
        raise


def update_admin_user(
    db: Session, user_id: int, commit: bool = True, **fields: Any
) -> AdminUser | None:
    try:
        user = db.get(AdminUser, user_id)
        if not user:
            logger.info("update_admin_user: no user with id=%s", user_id)
            return None

        for key, value in fields.items():
            if hasattr(user, key):
                setattr(user, key, value)
            else:
                raise AttributeError(f"AdminUser has no attribute '{key}'")
        db.flush()
        if commit:
            db.commit()
            db.refresh(user)
        return user

    except SQLAlchemyError as e:
        db.rollback()
        logger.error("failed to update user: %s", e)
        raise


def get_admin_user(db: Session, id: int) -> AdminUser:
    try:
        return db.get(AdminUser, id)
    except SQLAlchemyError:
        logger.exception("failed to fetch admin_user by id=%s", id)
        raise


def get_admin_user_by_phone(db: Session, phone_number: str) -> AdminUser | None:
    try:
        return (
            db.query(AdminUser).filter(AdminUser.phone_number == phone_number).first()
        )
    except SQLAlchemyError:
        logger.exception("failed to fetch admin_user by phone_number=%s", phone_number)
        raise
