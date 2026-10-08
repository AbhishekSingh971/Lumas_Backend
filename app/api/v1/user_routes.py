from flask import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.database.mongo import get_db
from app.repositories.user_repository import UserRepository
from app.schemas.user_schemas import ProfileUpdateRequest
from app.services.auth_service import public_user
from app.utils.responses import ok, fail
from app.utils.validation import validate_json

bp = Blueprint("users", __name__, url_prefix="/users")
users = UserRepository()

@bp.get("/me")
@jwt_required()
def me():
    user = users.find_by_id(get_jwt_identity())
    if not user:
        return fail("User not found", 404, "not_found")
    return ok(public_user(user))

@bp.patch("/me")
@jwt_required()
@validate_json(ProfileUpdateRequest)
def update_me(payload):
    values = payload.model_dump(exclude_unset=True)
    try:
        user = users.update_profile(get_jwt_identity(), values)
    except ValueError as exc:
        return fail(str(exc), 409, "conflict")
    return ok(public_user(user), "Profile updated")

@bp.get("/me/security-events")
@jwt_required()
def security_events():
    user_id = get_jwt_identity()
    docs = list(get_db().security_events.find({"user_id": user_id}).sort("created_at", -1).limit(50))
    for doc in docs:
        doc["id"] = str(doc.pop("_id"))
    return ok(docs)
