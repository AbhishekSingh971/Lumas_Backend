from bson import ObjectId
from pymongo.errors import DuplicateKeyError
from app.database.mongo import get_db
from app.utils.time import utcnow

class UserRepository:
    @property
    def collection(self):
        return get_db().users

    def find_by_email(self, email_normalized: str):
        return self.collection.find_one({"email_normalized": email_normalized})

    def find_by_id(self, user_id: str):
        if not ObjectId.is_valid(user_id):
            return None
        return self.collection.find_one({"_id": ObjectId(user_id)})

    def create(self, document: dict):
        result = self.collection.insert_one(document)
        return self.find_by_id(str(result.inserted_id))

    def update_profile(self, user_id: str, values: dict):
        updates = {f"profile.{k}": v for k, v in values.items() if v is not None}
        updates["updated_at"] = utcnow()
        try:
            self.collection.update_one({"_id": ObjectId(user_id)}, {"$set": updates})
        except DuplicateKeyError as exc:
            raise ValueError("Username is already in use") from exc
        return self.find_by_id(user_id)

    def set_password(self, user_id: str, password_hash: str):
        now = utcnow()
        self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"password_hash": password_hash, "security.password_changed_at": now, "updated_at": now}},
        )

    def record_login(self, user_id: str):
        now = utcnow()
        self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"security.last_login_at": now, "security.failed_login_count": 0, "updated_at": now}},
        )

    def record_failed_login(self, user_id: str):
        self.collection.update_one({"_id": ObjectId(user_id)}, {"$inc": {"security.failed_login_count": 1}})
