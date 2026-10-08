from datetime import datetime
from app.database.mongo import get_db
from app.utils.time import utcnow

class TokenRepository:
    @property
    def reset_tokens(self):
        return get_db().password_reset_tokens

    @property
    def revoked_tokens(self):
        return get_db().revoked_tokens

    def create_reset_token(self, user_id: str, token_hash: str, expires_at: datetime):
        self.reset_tokens.insert_one({
            "user_id": user_id,
            "token_hash": token_hash,
            "expires_at": expires_at,
            "used_at": None,
            "created_at": utcnow(),
        })

    def get_valid_reset_token(self, token_hash: str):
        return self.reset_tokens.find_one({"token_hash": token_hash, "used_at": None, "expires_at": {"$gt": utcnow()}})

    def mark_reset_used(self, token_hash: str):
        self.reset_tokens.update_one({"token_hash": token_hash}, {"$set": {"used_at": utcnow()}})

    def revoke(self, jti: str, user_id: str, token_type: str, expires_at: datetime):
        self.revoked_tokens.update_one(
            {"jti": jti},
            {"$setOnInsert": {"jti": jti, "user_id": user_id, "token_type": token_type, "expires_at": expires_at, "revoked_at": utcnow()}},
            upsert=True,
        )

    def is_revoked(self, jti: str) -> bool:
        return self.revoked_tokens.find_one({"jti": jti}, {"_id": 1}) is not None
