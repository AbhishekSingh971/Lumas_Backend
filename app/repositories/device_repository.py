from bson import ObjectId
from app.database.mongo import get_db
from app.utils.time import utcnow

class DeviceRepository:
    @property
    def collection(self):
        return get_db().devices

    def upsert(self, user_id: str, payload: dict):
        now = utcnow()
        self.collection.update_one(
            {"user_id": user_id, "installation_id": payload["installation_id"]},
            {"$set": {**payload, "user_id": user_id, "last_seen_at": now, "updated_at": now}, "$setOnInsert": {"created_at": now}},
            upsert=True,
        )
        return self.collection.find_one({"user_id": user_id, "installation_id": payload["installation_id"]})

    def list_for_user(self, user_id: str):
        return list(self.collection.find({"user_id": user_id}).sort("last_seen_at", -1))

    def delete(self, user_id: str, device_id: str):
        if not ObjectId.is_valid(device_id):
            return 0
        return self.collection.delete_one({"_id": ObjectId(device_id), "user_id": user_id}).deleted_count
