from datetime import datetime
from bson import ObjectId

from app.database.mongo import get_db


class UsageRepository:

    COLLECTION = "ai_usage_logs"

    @property
    def collection(self):
        return get_db()[self.COLLECTION]

    def create(
        self,
        user_id: str,
        conversation_id: str,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
    ):

        document = {
            "user_id": ObjectId(user_id),
            "conversation_id": ObjectId(conversation_id),
            "model": model,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": (
                prompt_tokens
                + completion_tokens
            ),
            "created_at": datetime.utcnow(),
        }

        result = self.collection.insert_one(
            document
        )

        document["_id"] = result.inserted_id

        return document

    def get_user_usage(
        self,
        user_id: str,
        limit: int = 100,
    ):

        return list(
            self.collection
            .find(
                {
                    "user_id": ObjectId(user_id)
                }
            )
            .sort("created_at", -1)
            .limit(limit)
        )

    def total_tokens_by_user(
        self,
        user_id: str,
    ):

        pipeline = [
            {
                "$match": {
                    "user_id": ObjectId(user_id)
                }
            },
            {
                "$group": {
                    "_id": None,
                    "tokens": {
                        "$sum": "$total_tokens"
                    }
                }
            }
        ]

        result = list(
            self.collection.aggregate(
                pipeline
            )
        )

        if not result:
            return 0

        return result[0]["tokens"]

    def total_tokens_by_conversation(
        self,
        conversation_id: str,
    ):

        pipeline = [
            {
                "$match": {
                    "conversation_id":
                    ObjectId(conversation_id)
                }
            },
            {
                "$group": {
                    "_id": None,
                    "tokens": {
                        "$sum": "$total_tokens"
                    }
                }
            }
        ]

        result = list(
            self.collection.aggregate(
                pipeline
            )
        )

        if not result:
            return 0

        return result[0]["tokens"]

    def delete_conversation_usage(
        self,
        conversation_id: str,
    ):

        return self.collection.delete_many(
            {
                "conversation_id":
                ObjectId(conversation_id)
            }
        )