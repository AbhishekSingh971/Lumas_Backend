import hashlib
import secrets
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from email_validator import validate_email, EmailNotValidError

_hasher = PasswordHasher()


def hash_password(password: str) -> str:
    return _hasher.hash(password)


def verify_password(password_hash: str, password: str) -> bool:
    try:
        return _hasher.verify(password_hash, password)
    except VerifyMismatchError:
        return False


def normalize_email(email: str) -> str:
    try:
        return validate_email(email, check_deliverability=False).normalized.lower()
    except EmailNotValidError as exc:
        raise ValueError(str(exc)) from exc


def new_opaque_token() -> str:
    return secrets.token_urlsafe(48)


def token_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()
