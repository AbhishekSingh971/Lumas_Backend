from datetime import timedelta, datetime, timezone
from urllib.parse import urlencode
from flask import current_app
from flask_jwt_extended import create_access_token, create_refresh_token
from pymongo.errors import DuplicateKeyError
from app.core.security import hash_password, verify_password, normalize_email, new_opaque_token, token_hash
from app.repositories.user_repository import UserRepository
from app.repositories.token_repository import TokenRepository
from app.services.email_service import send_password_reset_email
from app.services.google_service import verify_google_id_token
from app.utils.time import utcnow

users = UserRepository()
tokens = TokenRepository()


def public_user(user: dict) -> dict:
    return {
        "id": str(user["_id"]),
        "email": user["email"],
        "profile": user.get("profile", {}),
        "preferences": user.get("preferences", {}),
        "status": user.get("status", {}),
        "auth_providers": [{"provider": x.get("provider"), "linked_at": x.get("linked_at")} for x in user.get("auth_providers", [])],
        "created_at": user.get("created_at"),
        "updated_at": user.get("updated_at"),
    }


def issue_tokens(user: dict):
    identity = str(user["_id"])
    claims = {"email": user["email"]}
    return {
        "access_token": create_access_token(identity=identity, additional_claims=claims),
        "refresh_token": create_refresh_token(identity=identity, additional_claims=claims),
        "token_type": "Bearer",
    }


def register(payload):
    email = normalize_email(str(payload.email))
    if users.find_by_email(email):
        raise ValueError("An account with this email already exists")
    now = utcnow()
    doc = {
        "email": email,
        "email_normalized": email,
        "password_hash": hash_password(payload.password),
        "auth_providers": [{"provider": "local", "provider_user_id": email, "linked_at": now, "email_at_link_time": email}],
        "profile": {
            "first_name": payload.first_name.strip(),
            "last_name": payload.last_name.strip(),
            "display_name": (payload.display_name or f"{payload.first_name} {payload.last_name}".strip()).strip(),
            "username": None,
            "avatar_url": None,
            "phone": None,
            "phone_country_code": None,
            "locale": payload.locale,
            "timezone": payload.timezone,
            "country": None,
            "bio": None,
        },
        "preferences": {"theme": "system", "language": payload.locale or "en", "notifications": {"email": True, "push": True, "product_updates": False, "security_alerts": True}},
        "status": {"is_active": True, "is_email_verified": False, "is_phone_verified": False, "onboarding_completed": False},
        "security": {"password_changed_at": now, "failed_login_count": 0, "locked_until": None, "last_login_at": None},
        "created_at": now,
        "updated_at": now,
    }
    try:
        user = users.create(doc)
    except DuplicateKeyError as exc:
        raise ValueError("An account with this email already exists") from exc
    return user, issue_tokens(user)


def login(payload):
    email = normalize_email(str(payload.email))
    user = users.find_by_email(email)
    if not user or not user.get("password_hash") or not verify_password(user["password_hash"], payload.password):
        if user:
            users.record_failed_login(str(user["_id"]))
        raise PermissionError("Invalid email or password")
    if not user.get("status", {}).get("is_active", True):
        raise PermissionError("Account is disabled")
    users.record_login(str(user["_id"]))
    user = users.find_by_id(str(user["_id"]))
    return user, issue_tokens(user)


def forgot_password(email_input: str):
    email = normalize_email(email_input)
    user = users.find_by_email(email)
    if not user:
        return
    raw = new_opaque_token()
    digest = token_hash(raw)
    expires = utcnow() + timedelta(minutes=current_app.config["PASSWORD_RESET_MINUTES"])
    tokens.create_reset_token(str(user["_id"]), digest, expires)
    query = urlencode({"token": raw})
    reset_url = f'{current_app.config["APP_RESET_URL"]}?{query}'
    send_password_reset_email(user["email"], reset_url)


def reset_password(raw_token: str, password: str):
    digest = token_hash(raw_token)
    record = tokens.get_valid_reset_token(digest)
    if not record:
        raise ValueError("Reset token is invalid or expired")
    users.set_password(record["user_id"], hash_password(password))
    tokens.mark_reset_used(digest)


def google_login(raw_id_token: str):
    claims = verify_google_id_token(raw_id_token)
    email = normalize_email(claims["email"])
    provider_id = claims["sub"]
    user = users.find_by_email(email)
    now = utcnow()
    if user:
        providers = user.get("auth_providers", [])
        if not any(p.get("provider") == "google" and p.get("provider_user_id") == provider_id for p in providers):
            users.collection.update_one({"_id": user["_id"]}, {"$push": {"auth_providers": {"provider": "google", "provider_user_id": provider_id, "linked_at": now, "email_at_link_time": email}}, "$set": {"status.is_email_verified": True, "updated_at": now}})
            user = users.find_by_id(str(user["_id"]))
    else:
        name = claims.get("name", "").strip()
        given = claims.get("given_name", "")
        family = claims.get("family_name", "")
        doc = {
            "email": email,
            "email_normalized": email,
            "password_hash": None,
            "auth_providers": [{"provider": "google", "provider_user_id": provider_id, "linked_at": now, "email_at_link_time": email}],
            "profile": {"first_name": given, "last_name": family, "display_name": name or email.split("@")[0], "username": None, "avatar_url": claims.get("picture"), "phone": None, "phone_country_code": None, "locale": claims.get("locale"), "timezone": None, "country": None, "bio": None},
            "preferences": {"theme": "system", "language": claims.get("locale", "en"), "notifications": {"email": True, "push": True, "product_updates": False, "security_alerts": True}},
            "status": {"is_active": True, "is_email_verified": True, "is_phone_verified": False, "onboarding_completed": False},
            "security": {"password_changed_at": None, "failed_login_count": 0, "locked_until": None, "last_login_at": now},
            "created_at": now,
            "updated_at": now,
        }
        user = users.create(doc)
    users.record_login(str(user["_id"]))
    user = users.find_by_id(str(user["_id"]))
    return user, issue_tokens(user)
