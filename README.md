# Flask Phase 1 Backend

Production-oriented Phase 1 API for the AI Assistant platform.

## Implemented

- Email/password register and login
- JWT access and refresh tokens
- Logout and server-side token revocation
- Forgot/reset password token flow
- Google ID-token SSO endpoint
- Current user profile
- Device registration and metadata
- Notification preferences
- PWA Web Push subscription persistence
- Security/audit events
- MongoDB indexes and TTL cleanup
- Rate limiting and CORS
- Docker configuration

## Run locally

```bash
cp .env.example .env
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python run.py
```

Or:

```bash
docker compose up --build
```

API base:

```text
http://localhost:8000/api/v1
```

## Important setup

1. Replace both secret keys with cryptographically random values.
2. Configure MongoDB Atlas or local MongoDB.
3. Configure Google OAuth client ID before using `/auth/google`.
4. Configure a transactional SMTP provider before production password resets.
5. Replace in-memory rate-limit storage with Redis before running multiple API instances.
6. Run behind HTTPS in production.

## Google sign-in integration model

The Flutter/PWA client signs in with the official Google client SDK and sends the returned Google ID token to:

```text
POST /api/v1/auth/google
```

The backend verifies the token, creates or links the user, and returns this application's JWT access/refresh pair.

## PWA note

This repository is the backend. A PWA client still needs its own web manifest and service worker. The backend already provides storage endpoints for Web Push subscriptions.
