from flask import Blueprint
from app.database.mongo import get_db
from app.utils.responses import ok, fail

bp = Blueprint("health", __name__, url_prefix="/health")

@bp.get("")
def health():
    try:
        get_db().command("ping")
    except Exception:
        return fail("Database unavailable", 503, "database_unavailable")
    return ok({"service": "phase1-api", "database": "ok"})
