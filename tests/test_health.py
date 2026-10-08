from app import create_app

class TestConfig:
    TESTING = True
    DEBUG = True
    SECRET_KEY = "test"
    JWT_SECRET_KEY = "test-jwt"
    MONGO_URI = "mongodb://localhost:27017/ai_assistant_test"
    MONGO_DB_NAME = "ai_assistant_test"
    CORS_ORIGINS = ["http://localhost"]
    RATE_LIMIT_STORAGE_URI = "memory://"
    JWT_ACCESS_TOKEN_EXPIRES = __import__("datetime").timedelta(minutes=15)
    JWT_REFRESH_TOKEN_EXPIRES = __import__("datetime").timedelta(days=30)
    PASSWORD_RESET_MINUTES = 20
    APP_RESET_URL = "http://localhost/reset-password"
    GOOGLE_CLIENT_ID = ""
    SMTP_HOST = ""
    SMTP_PORT = 587
    SMTP_USERNAME = ""
    SMTP_PASSWORD = ""
    SMTP_FROM_EMAIL = "test@example.com"
    SMTP_USE_TLS = False


def test_unknown_route_returns_json():
    app = create_app(TestConfig)
    client = app.test_client()
    response = client.get("/does-not-exist")
    assert response.status_code == 404
    assert response.get_json()["success"] is False
