from app.database.mongo import get_db

def ensure_indexes():
    db = get_db()
    db.users.create_index("email_normalized", unique=True)
    db.users.create_index("username", unique=True, sparse=True)
    db.users.create_index("auth_providers.provider_user_id", sparse=True)
    db.devices.create_index([("user_id", 1), ("installation_id", 1)], unique=True)
    db.push_subscriptions.create_index("endpoint", unique=True)
    db.password_reset_tokens.create_index("token_hash", unique=True)
    db.password_reset_tokens.create_index("expires_at", expireAfterSeconds=0)
    db.revoked_tokens.create_index("jti", unique=True)
    db.revoked_tokens.create_index("expires_at", expireAfterSeconds=0)
    db.security_events.create_index([("user_id", 1), ("created_at", -1)])
    db.conversations.create_index([("user_id", 1), ("updated_at", -1)])
    db.conversations.create_index([("title", "text")])
    db.messages.create_index([("conversation_id", 1),("created_at", 1)])
    db.messages.create_index([("conversation_id", 1)])
    db.messages.create_index([("content", "text")])