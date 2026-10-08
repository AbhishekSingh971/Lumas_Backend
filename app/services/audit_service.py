from flask import request
from app.database.mongo import get_db
from app.utils.time import utcnow

def audit(event_type: str, user_id: str | None = None, metadata: dict | None = None):
    get_db().security_events.insert_one({
        "user_id": user_id,
        "type": event_type,
        "ip": request.headers.get("X-Forwarded-For", request.remote_addr),
        "user_agent": request.headers.get("User-Agent", "")[:1000],
        "metadata": metadata or {},
        "created_at": utcnow(),
    })
