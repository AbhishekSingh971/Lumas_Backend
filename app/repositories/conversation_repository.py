from datetime import datetime
from bson import ObjectId

from app.database.mongo import get_db


class ConversationRepository:
    COLLECTION = "conversations"

    @property
    def collection(self):
        return get_db()[self.COLLECTION]

    def create(
        self,
        user_id: str,
        title: str = "New Chat",
        model: str = "gpt-5"
    ):
        now = datetime.utcnow()

        document = {
            "user_id": ObjectId(user_id),
            "title": title,
            "model": model,
            "is_archived": False,
            "created_at": now,
            "updated_at": now,
        }

        result = self.collection.insert_one(document)

        document["_id"] = result.inserted_id

        return document

    def get_by_id(self, conversation_id: str):
        return self.collection.find_one(
            {
                "_id": ObjectId(conversation_id)
            }
        )

    def get_user_conversation(
        self,
        conversation_id: str,
        user_id: str
    ):
        return self.collection.find_one(
            {
                "_id": ObjectId(conversation_id),
                "user_id": ObjectId(user_id)
            }
        )

    def list_user_conversations(
        self,
        user_id: str,
        page: int = 1,
        limit: int = 20
    ):
        skip = (page - 1) * limit

        conversations = list(
            self.collection
            .find(
                {
                    "user_id": ObjectId(user_id),
                    "is_archived": False
                }
            )
            .sort("updated_at", -1)
            .skip(skip)
            .limit(limit)
        )

        return conversations

    def update_title(
        self,
        conversation_id: str,
        title: str
    ):
        return self.collection.update_one(
            {
                "_id": ObjectId(conversation_id)
            },
            {
                "$set": {
                    "title": title,
                    "updated_at": datetime.utcnow()
                }
            }
        )

    def touch(
        self,
        conversation_id: str
    ):
        return self.collection.update_one(
            {
                "_id": ObjectId(conversation_id)
            },
            {
                "$set": {
                    "updated_at": datetime.utcnow()
                }
            }
        )

    def archive(
        self,
        conversation_id: str,
        user_id: str
    ):
        return self.collection.update_one(
            {
                "_id": ObjectId(conversation_id),
                "user_id": ObjectId(user_id)
            },
            {
                "$set": {
                    "is_archived": True,
                    "updated_at": datetime.utcnow()
                }
            }
        )

    def delete(
        self,
        conversation_id: str,
        user_id: str
    ):
        return self.collection.delete_one(
            {
                "_id": ObjectId(conversation_id),
                "user_id": ObjectId(user_id)
            }
        )

    def search(
        self,
        user_id: str,
        query: str,
        limit: int = 20
    ):
        return list(
            self.collection.find(
                {
                    "user_id": ObjectId(user_id),
                    "title": {
                        "$regex": query,
                        "$options": "i"
                    }
                }
            ).limit(limit)
        )