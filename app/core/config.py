import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


def _bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


class Config:
    ENV = os.getenv("FLASK_ENV", "production")
    DEBUG = ENV == "development"

    SECRET_KEY = os.getenv("SECRET_KEY", "")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "")
    if ENV == "production" and (not SECRET_KEY or not JWT_SECRET_KEY):
        raise RuntimeError("SECRET_KEY and JWT_SECRET_KEY are required in production")

    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/ai_assistant")
    MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "ai_assistant")

    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=int(os.getenv("ACCESS_TOKEN_MINUTES", "15")))
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=int(os.getenv("REFRESH_TOKEN_DAYS", "30")))
    JWT_TOKEN_LOCATION = ["headers"]

    PASSWORD_RESET_MINUTES = int(os.getenv("PASSWORD_RESET_MINUTES", "20"))
    APP_RESET_URL = os.getenv("APP_RESET_URL", "http://localhost:5173/reset-password")
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")

    CORS_ORIGINS = [
    origin.strip().rstrip("/")
    for origin in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://localhost:61718",
    ).split(",")
    if origin.strip()
]
    RATE_LIMIT_STORAGE_URI = os.getenv("RATE_LIMIT_STORAGE_URI", "memory://")

    SMTP_HOST = os.getenv("SMTP_HOST", "")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
    SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL", "no-reply@example.com")
    SMTP_USE_TLS = _bool("SMTP_USE_TLS", True)
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY","")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL","gpt-5")
    OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE","0.7"))
    OPENAI_MAX_TOKENS = int(os.getenv("OPENAI_MAX_TOKENS","4000"))