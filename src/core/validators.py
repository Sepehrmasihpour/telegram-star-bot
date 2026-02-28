import re

IRAN_PHONE_PATTERN = re.compile(r"^(?:\+989\d{9}|09\d{9})$")

COMMON_PASSWORDS = {
    "password",
    "password123",
    "12345678",
    "123456789",
    "qwerty123",
    "letmein",
    "admin123",
    "iloveyou",
}

_LOWER = re.compile(r"[a-z]")
_UPPER = re.compile(r"[A-Z]")
_DIGIT = re.compile(r"\d")
_SYMBOL = re.compile(r"[^\w\s]")
_CONTROL = re.compile(r"[\x00-\x1F\x7F]")


class WeakPasswordError(ValueError):
    pass


def is_valid_iranian_phone(phone: str) -> bool:
    if not isinstance(phone, str):
        return False

    phone = phone.strip()
    return bool(IRAN_PHONE_PATTERN.fullmatch(phone))


def validate_strong_password(password: str, *, min_length: int = 12) -> bool:
    if not isinstance(password, str):
        raise WeakPasswordError("Password must be a string.")

    if password == "":
        raise WeakPasswordError("Password cannot be empty.")

    if password != password.strip():
        raise WeakPasswordError("Password must not start or end with whitespace.")

    if _CONTROL.search(password):
        raise WeakPasswordError("Password contains invalid control characters.")

    if len(password) < min_length:
        raise WeakPasswordError(
            f"Password must be at least {min_length} characters long."
        )

    classes = sum(bool(rx.search(password)) for rx in (_LOWER, _UPPER, _DIGIT, _SYMBOL))

    if classes < 3:
        raise WeakPasswordError(
            "Password must include at least 3 of: lowercase, uppercase, digits, symbols."
        )

    if password.lower() in COMMON_PASSWORDS:
        raise WeakPasswordError("Password is too common.")

    return True
