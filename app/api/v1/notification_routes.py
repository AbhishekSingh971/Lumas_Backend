from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.repositories.notification_repository import NotificationRepository
from app.repositories.user_repository import UserRepository
from app.schemas.device_schemas import WebPushSubscriptionRequest
from app.schemas.user_schemas import NotificationPreferencesRequest
from app.utils.responses import ok, fail
from app.utils.validation import validate_json
from app.utils.time import utcnow

bp = Blueprint("notifications", __name__, url_prefix="/notifications")
repo = NotificationRepository()
users = UserRepository()

@bp.get("/preferences")
@jwt_required()
def preferences():
    user = users.find_by_id(get_jwt_identity())
    return ok(user.get("preferences", {}).get("notifications", {}))

@bp.patch("/preferences")
@jwt_required()
@validate_json(NotificationPreferencesRequest)
def update_preferences(payload):
    values = payload.model_dump(exclude_unset=True)
    updates = {f"preferences.notifications.{k}": v for k, v in values.items()}
    updates["updated_at"] = utcnow()
    users.collection.update_one({"_id": users.find_by_id(get_jwt_identity())["_id"]}, {"$set": updates})
    user = users.find_by_id(get_jwt_identity())
    return ok(user.get("preferences", {}).get("notifications", {}), "Preferences updated")

@bp.post("/web-push/subscribe")
@jwt_required()
@validate_json(WebPushSubscriptionRequest)
def subscribe(payload):
    repo.upsert_web_push(get_jwt_identity(), payload.model_dump())
    return ok(message="Web Push subscription saved", status=201)

@bp.delete("/web-push/subscribe")
@jwt_required()
def unsubscribe():
    endpoint = (request.get_json(silent=True) or {}).get("endpoint")
    if not endpoint:
        return fail("endpoint is required", 422, "validation_error")
    repo.remove_web_push(get_jwt_identity(), endpoint)
    return ok(message="Web Push subscription disabled")
