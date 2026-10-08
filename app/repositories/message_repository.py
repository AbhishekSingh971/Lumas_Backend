from datetime import datetime
from bson import ObjectId

from app.database.mongo import get_db


class MessageRepository:
    COLLECTION = "messages"

    @property
    def collection(self):
        return get_db()[self.COLLECTION]

    def create(
        self,
        conversation_id: str,
        role: str,
        content: str,
        tokens: int = 0,
        metadata: dict | None = None
    ):
        document = {
            "conversation_id": ObjectId(conversation_id),
            "role": role,
            "content": content,
            "tokens": tokens,
            "metadata": metadata or {},
            "created_at": datetime.utcnow(),
        }

        result = self.collection.insert_one(document)

        document["_id"] = result.inserted_id

        return document

    def get_by_id(
        self,
        message_id: str
    ):
        return self.collection.find_one(
            {
                "_id": ObjectId(message_id)
            }
        )

    def get_conversation_messages(
        self,
        conversation_id: str,
        limit: int = 100
    ):
        return list(
            self.collection
            .find(
                {
                    "conversation_id": ObjectId(conversation_id)
                }
            )
            .sort("created_at", 1)
            .limit(limit)
        )

    def get_recent_messages(
        self,
        conversation_id: str,
        limit: int = 20
    ):
        messages = list(
            self.collection
            .find(
                {
                    "conversation_id": ObjectId(conversation_id)
                }
            )
            .sort("created_at", -1)
            .limit(limit)
        )

        return list(reversed(messages))

    def get_context_window(
        self,
        conversation_id: str,
        limit: int = 20
    ):
        messages = self.get_recent_messages(
            conversation_id,
            limit
        )

        return [
            {
                "role": message["role"],
                "content": message["content"]
            }
            for message in messages
        ]

    def count_messages(
        self,
        conversation_id: str
    ):
        return self.collection.count_documents(
            {
                "conversation_id": ObjectId(conversation_id)
            }
        )

    def delete_conversation_messages(
        self,
        conversation_id: str
    ):
        return self.collection.delete_many(
            {
                "conversation_id": ObjectId(conversation_id)
            }
        )

    def delete_message(
        self,
        message_id: str
    ):
        return self.collection.delete_one(
            {
                "_id": ObjectId(message_id)
            }
        )

    def search_messages(
        self,
        conversation_id: str,
        query: str,
        limit: int = 20
    ):
        return list(
            self.collection.find(
                {
                    "conversation_id": ObjectId(conversation_id),
                    "content": {
                        "$regex": query,
                        "$options": "i"
                    }
                }
            ).limit(limit)
        )

    def total_tokens(
        self,
        conversation_id: str
    ):
        pipeline = [
            {
                "$match": {
                    "conversation_id": ObjectId(conversation_id)
                }
            },
            {
                "$group": {
                    "_id": None,
                    "total": {
                        "$sum": "$tokens"
                    }
                }
            }
        ]

        result = list(
            self.collection.aggregate(pipeline)
        )

        return result[0]["total"] if result else 0