from flask import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.repositories.device_repository import DeviceRepository
from app.schemas.device_schemas import DeviceRegisterRequest
from app.services.audit_service import audit
from app.utils.responses import ok, fail
from app.utils.validation import validate_json

bp = Blueprint("devices", __name__, url_prefix="/devices")
repo = DeviceRepository()

def serialize(doc):
    out = dict(doc)
    out["id"] = str(out.pop("_id"))
    return out

@bp.post("/register")
@jwt_required()
@validate_json(DeviceRegisterRequest)
def register_device(payload):
    user_id = get_jwt_identity()
    doc = repo.upsert(user_id, payload.model_dump())
    audit("device_registered", user_id, {"platform": payload.platform, "installation_id": payload.installation_id})
    return ok(serialize(doc), "Device registered", 201)

@bp.get("")
@jwt_required()
def list_devices():
    return ok([serialize(x) for x in repo.list_for_user(get_jwt_identity())])

@bp.delete("/<device_id>")
@jwt_required()
def delete_device(device_id):
    deleted = repo.delete(get_jwt_identity(), device_id)
    if not deleted:
        return fail("Device not found", 404, "not_found")
    return ok(message="Device removed")
