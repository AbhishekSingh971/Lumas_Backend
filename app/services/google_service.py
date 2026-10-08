from flask import current_app
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests


def verify_google_id_token(raw_token: str) -> dict:
    audience = current_app.config.get("GOOGLE_CLIENT_ID")
    if not audience:
        raise RuntimeError("GOOGLE_CLIENT_ID is not configured")
    claims = id_token.verify_oauth2_token(raw_token, google_requests.Request(), audience)
    if not claims.get("email_verified"):
        raise ValueError("Google email is not verified")
    return claims
