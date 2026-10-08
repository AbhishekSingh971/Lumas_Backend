from app.database.mongo import get_db


def ensure_chat_indexes():

    db = get_db()

    db.conversations.create_index(
        [
            ("user_id", 1),
            ("updated_at", -1)
        ]
    )

    db.conversations.create_index(
        [
            ("title", "text")
        ]
    )

    db.messages.create_index(
        [
            ("conversation_id", 1),
            ("created_at", 1)
        ]
    )

    db.messages.create_index(
        [
            ("content", "text")
        ]
    )

    db.ai_usage_logs.create_index(
        [
            ("user_id", 1),
            ("created_at", -1)
        ]
    )

    db.ai_usage_logs.create_index(
        [
            ("conversation_id", 1)
        ]
    )