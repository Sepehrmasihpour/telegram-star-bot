import re


def phone_number_authenticator(phone: str) -> bool:
    pattern = r"^09\d{9}$"
    return bool(re.match(pattern, phone))
