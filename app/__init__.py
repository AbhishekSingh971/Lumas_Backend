from flask import Flask
from flask_cors import CORS
from app.core.config import Config
from app.core.extensions import jwt, limiter
from app.database.mongo import init_mongo
from app.database.indexes import ensure_indexes
from app.repositories.token_repository import TokenRepository
from app.utils.responses import fail
from app.database.chat_indexes import (
    ensure_chat_indexes
)
from app.api.v1.chat_routes import bp as chat_bp
from app.api.v1.chat_stream_routes import bp as chat_stream_bp


def create_app(config_object=Config):
    app = Flask(__name__)
    app.config.from_object(config_object)

    init_mongo(app)
    jwt.init_app(app)
    limiter.init_app(app)
    CORS(
    app,
    resources={
        r"/api/*": {
            "origins": app.config["CORS_ORIGINS"],
            "methods": [
                "GET", "POST", "PUT", "PATCH",
                "DELETE", "OPTIONS",
            ],
            "allow_headers": [
                "Content-Type",
                "Authorization",
            ],
        }
    },
    supports_credentials=False,
)

    from app.api.v1.auth_routes import bp as auth_bp
    from app.api.v1.user_routes import bp as user_bp
    from app.api.v1.device_routes import bp as device_bp
    from app.api.v1.notification_routes import bp as notification_bp
    from app.api.v1.health_routes import bp as health_bp

    prefix = "/api/v1"
    for blueprint in (
        auth_bp,
        user_bp,
        device_bp,
        notification_bp,
        health_bp,
        chat_bp,
        chat_stream_bp,
    ):
        app.register_blueprint(blueprint, url_prefix=prefix + blueprint.url_prefix)
        

    @jwt.token_in_blocklist_loader
    def token_is_revoked(jwt_header, jwt_payload):
        return TokenRepository().is_revoked(
            jwt_payload["jti"]
        )

    @jwt.unauthorized_loader
    def unauthorized(reason):
        print("[JWT UNAUTHORIZED]", reason)
        return fail(
            "Authentication required",
            401,
            "authentication_required",
        )

    @jwt.invalid_token_loader
    def invalid_token(reason):
        print("[JWT INVALID]", reason)
        return fail(
            "Invalid token",
            401,
            "invalid_token",
        )

    @jwt.expired_token_loader
    def expired_token(jwt_header, jwt_payload):
        print("[JWT EXPIRED]", jwt_payload)
        return fail(
            "Access token expired. Please log in again.",
            401,
            "token_expired",
        )

    @jwt.revoked_token_loader
    def revoked_token(jwt_header, jwt_payload):
        print("[JWT REVOKED]", jwt_payload.get("jti"))
        return fail(
            "Token has been revoked",
            401,
            "revoked_token",
        )

    @app.errorhandler(404)
    def not_found(error):
        return fail("Route not found", 404, "not_found")

    @app.errorhandler(429)
    def ratelimit(error):
        return fail("Too many requests", 429, "rate_limited")

    with app.app_context():
        ensure_indexes()
        ensure_chat_indexes()
    return app
