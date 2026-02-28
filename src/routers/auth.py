from fastapi import Depends
from fastapi.routing import APIRouter
from fastapi.requests import Request
from typing import Union

from src.config import logger
from src.db import get_db
from src.schemas import auth as auth_schema
from src.schemas import common as common_schema
from src.crud import admin_user as admin_db
from src.core import security, validators

from sqlalchemy.orm import Session

router = APIRouter()


@router.post(
    "/register",
    response_model=Union[auth_schema.AccessToken, common_schema.ErrorMessage],
)
async def register(
    payload: auth_schema.ReqRegister, request: Request, db: Session = Depends(get_db)
):
    try:
        phone_number_valid = validators.is_valid_iranian_phone(payload.phone_number)
        if phone_number_valid is False:
            return {"ok": False, "error": "invalid phone number"}

        user_exists = admin_db.get_admin_user_by_phone(
            db=db, phone_number=payload.phone_number
        )
        if user_exists:
            return {"ok": False, "error": "user already registered"}

        password_valid = validators.validate_strong_password(payload.password)
        if password_valid is not True:
            return {"ok": False, "error": "password is weak"}

        ph = request.app.state.ph  # global password hasher instance
        hashed_password = security.hash_password(ph=ph, raw_password=payload.password)
        totp_secret = security.generate_user_totp_secret()
        new_admin_user = admin_db.create_admin_user(
            db=db,
            phone_number=payload.phone_number,
            password_hash=hashed_password,
            totp_secret=totp_secret,
        )
        access_token = security.encode_jwt(
            {
                "sub": new_admin_user.id,
                "pv": False,
                "sv": False,
                "nv": False,
                "uv": False,
            }
        )
        return {"access_token": access_token}

    except Exception as e:
        logger.exception(f"Unhandled error in /register endpoint: {e}")
        return {"ok": False, "error": "internal_error"}
