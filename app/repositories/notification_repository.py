from app.database.mongo import get_db
from app.utils.time import utcnow

class NotificationRepository:
    @property
    def subscriptions(self):
        return get_db().push_subscriptions

    def upsert_web_push(self, user_id: str, payload: dict):
        now = utcnow()
        self.subscriptions.update_one(
            {"endpoint": payload["endpoint"]},
            {"$set": {
                "user_id": user_id,
                "device_id": payload["device_id"],
                "provider": "webpush",
                "endpoint": payload["endpoint"],
                "keys": {"p256dh": payload["p256dh"], "auth": payload["auth"]},
                "is_active": True,
                "updated_at": now,
            }, "$setOnInsert": {"created_at": now}},
            upsert=True,
        )

    def remove_web_push(self, user_id: str, endpoint: str):
        return self.subscriptions.update_one(
            {"user_id": user_id, "endpoint": endpoint},
            {"$set": {"is_active": False, "updated_at": utcnow()}},
        ).modified_count
