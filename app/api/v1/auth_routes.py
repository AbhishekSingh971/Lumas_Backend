from datetime import datetime, timezone
from flask import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt, create_access_token
from app.core.extensions import limiter
from app.schemas.auth_schemas import RegisterRequest, LoginRequest, ForgotPasswordRequest, ResetPasswordRequest, GoogleAuthRequest
from app.services import auth_service
from app.services.audit_service import audit
from app.repositories.user_repository import UserRepository
from app.repositories.token_repository import TokenRepository
from app.utils.responses import ok, fail
from app.utils.validation import validate_json

bp = Blueprint("auth", __name__, url_prefix="/auth")
users = UserRepository()
tokens = TokenRepository()

@bp.post("/register")
@limiter.limit("5 per hour")
@validate_json(RegisterRequest)
def register(payload):
    try:
        user, auth = auth_service.register(payload)
    except ValueError as exc:
        return fail(str(exc), 409, "account_exists")
    audit("register", str(user["_id"]))
    return ok({"user": auth_service.public_user(user), "auth": auth}, "Registration successful", 201)

@bp.post("/login")
@limiter.limit("10 per minute")
@validate_json(LoginRequest)
def login(payload):
    try:
        user, auth = auth_service.login(payload)
    except (ValueError, PermissionError):
        audit("login_failed", metadata={"email": str(payload.email)})
        return fail("Invalid email or password", 401, "invalid_credentials")
    audit("login_success", str(user["_id"]))
    return ok({"user": auth_service.public_user(user), "auth": auth})

@bp.post("/refresh")
@jwt_required(refresh=True)
def refresh():
    user_id = get_jwt_identity()
    user = users.find_by_id(user_id)
    if not user or not user.get("status", {}).get("is_active", True):
        return fail("Account unavailable", 401, "account_unavailable")
    token = create_access_token(identity=user_id, additional_claims={"email": user["email"]})
    return ok({"access_token": token, "token_type": "Bearer"})

@bp.post("/logout")
@jwt_required(verify_type=False)
def logout():
    claims = get_jwt()
    user_id = get_jwt_identity()
    expires_at = datetime.fromtimestamp(claims["exp"], tz=timezone.utc)
    tokens.revoke(claims["jti"], user_id, claims.get("type", "unknown"), expires_at)
    audit("logout", user_id)
    return ok(message="Logged out")

@bp.post("/forgot-password")
@limiter.limit("5 per hour")
@validate_json(ForgotPasswordRequest)
def forgot_password(payload):
    try:
        auth_service.forgot_password(str(payload.email))
    except ValueError:
        pass
    audit("password_reset_requested", metadata={"email": str(payload.email)})
    return ok(message="If an account exists for that email, a password reset message will be sent.")

@bp.post("/reset-password")
@limiter.limit("10 per hour")
@validate_json(ResetPasswordRequest)
def reset_password(payload):
    try:
        auth_service.reset_password(payload.token, payload.password)
    except ValueError as exc:
        return fail(str(exc), 400, "invalid_reset_token")
    audit("password_reset_completed")
    return ok(message="Password has been reset")

@bp.post("/google")
@limiter.limit("20 per minute")
@validate_json(GoogleAuthRequest)
def google(payload):
    try:
        user, auth = auth_service.google_login(payload.id_token)
    except Exception:
        return fail("Google authentication failed", 401, "google_auth_failed")
    audit("google_login", str(user["_id"]))
    return ok({"user": auth_service.public_user(user), "auth": auth})
