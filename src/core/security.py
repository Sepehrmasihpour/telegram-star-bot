import pyotp
import jwt
import time
import secrets

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, InvalidHash
from typing import Any, Dict

from src.config import settings


class JWTError(ValueError):
    pass


#! add error handling later


def hash_password(ph: PasswordHasher, raw_password: str) -> str:
    if not isinstance(raw_password, str) or raw_password == "":
        raise ValueError("Invalid password.")
    return ph.hash(raw_password)


def verify_password(
    ph: PasswordHasher, raw_password: str, hashed_password: str
) -> bool:
    try:
        return ph.verify(hashed_password, raw_password)
    except (VerifyMismatchError, InvalidHash):
        return False


def generate_user_totp_secret() -> str:
    return pyotp.random_base32()


def verify_totp(secret: str, code: str) -> bool:
    totp = pyotp.TOTP(secret)
    return totp.verify(code)


def generate_jti() -> str:
    return secrets.token_urlsafe(32)


def encode_jwt(
    payload: Dict[str, Any],
) -> str:
    """
    Encodes payload into JWT using HS256.
    Automatically adds iat and exp.
    """
    if not isinstance(payload, dict):
        raise JWTError("Payload must be a dictionary.")

    now = int(time.time())

    payload_to_encode = {
        **payload,
        "jti": generate_jti(),
        "iat": now,
        "exp": now + settings.jwt_token_expirty_per_seconds,
    }

    return jwt.encode(
        payload_to_encode,
        settings.jwt_secret,
        algorithm="HS256",
    )


def decode_jwt(token: str) -> Dict[str, Any]:
    """
    Decodes JWT and validates signature + expiration.
    """
    try:
        return jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=["HS256"],
        )
    except jwt.ExpiredSignatureError:
        raise JWTError("Token has expired.")
    except jwt.InvalidTokenError:
        raise JWTError("Invalid token.")
