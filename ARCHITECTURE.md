# Phase 1 Backend Architecture — Flask + MongoDB

## 1. Scope

This Phase 1 backend is the production foundation for a future Flutter application and a Progressive Web App (PWA).

### Phase 1 capabilities

```text
Identity & Access
├── Register with email/password
├── Login
├── Refresh access token
├── Logout / token revocation
├── Forgot password
├── Reset password
├── Email verification foundation
├── Google Sign-In / SSO token verification
└── Current-session identity (/me)

User Platform
├── User profile
├── Account status
├── Notification preferences
├── Device registration
├── Device metadata
├── Push subscription storage
├── Security event history
└── Account timestamps / audit fields

Production Foundation
├── App factory
├── API versioning
├── MongoDB indexes
├── JWT access + refresh tokens
├── Token blocklist
├── Argon2 password hashing
├── Pydantic request validation
├── Rate limiting
├── CORS allow-list
├── Structured errors
├── Health checks
├── Docker
├── Environment configuration
└── Pytest smoke tests
```

## 2. Technology decisions

```text
Runtime
└── Python 3.12+

Web
└── Flask 3.1.x

Database
└── MongoDB
    └── PyMongo

Authentication
├── Flask-JWT-Extended
├── Argon2 password hashing
└── Google ID-token verification

Validation
└── Pydantic v2

Security
├── Flask-Limiter
├── CORS allow-list
├── JWT revocation
└── Security-event logging

Email
└── SMTP abstraction

Future
├── Redis
├── PostgreSQL
├── OpenAI
├── MCP server/tool layer
└── Mobile push provider
```

> Mongoose is intentionally not used. Mongoose is a Node.js ODM. A Flask/Python service should use PyMongo or a Python ODM.

## 3. High-level architecture

```text
                 ┌────────────────────────┐
                 │      Flutter App       │
                 └───────────┬────────────┘
                             │ HTTPS/JSON
                 ┌───────────▼────────────┐
                 │       Flask API        │
                 │       /api/v1          │
                 └───────────┬────────────┘
                             │
      ┌──────────────────────┼──────────────────────┐
      │                      │                      │
┌─────▼─────┐          ┌─────▼──────┐        ┌──────▼─────┐
│ Auth      │          │ Users      │        │ Devices    │
│ Service   │          │ Service    │        │ Service    │
└─────┬─────┘          └─────┬──────┘        └──────┬─────┘
      │                      │                      │
      └──────────────────────┼──────────────────────┘
                             │
                    ┌────────▼────────┐
                    │    MongoDB      │
                    └─────────────────┘

External identity:
Google SDK (Flutter/PWA) -> Google ID token -> Flask verification endpoint

Password reset:
Flask -> SMTP provider -> reset link -> PWA/Flutter -> reset endpoint
```

## 4. Backend folder tree

```text
flask_phase1_backend/
├── app/
│   ├── __init__.py
│   ├── api/
│   │   └── v1/
│   │       ├── auth_routes.py
│   │       ├── user_routes.py
│   │       ├── device_routes.py
│   │       ├── notification_routes.py
│   │       └── health_routes.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   ├── extensions.py
│   │   ├── errors.py
│   │   └── security.py
│   │
│   ├── database/
│   │   ├── mongo.py
│   │   └── indexes.py
│   │
│   ├── repositories/
│   │   ├── user_repository.py
│   │   ├── token_repository.py
│   │   ├── device_repository.py
│   │   └── notification_repository.py
│   │
│   ├── schemas/
│   │   ├── auth_schemas.py
│   │   ├── user_schemas.py
│   │   └── device_schemas.py
│   │
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── email_service.py
│   │   ├── google_service.py
│   │   └── audit_service.py
│   │
│   └── utils/
│       ├── responses.py
│       ├── validation.py
│       └── time.py
│
├── tests/
│   └── test_health.py
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── run.py
└── README.md
```

## 5. MongoDB collection design

### users

```text
users
├── _id
├── email
├── email_normalized
├── password_hash                nullable for Google-only accounts
├── auth_providers[]
│   ├── provider                 local | google
│   ├── provider_user_id
│   ├── linked_at
│   └── email_at_link_time
├── profile
│   ├── first_name
│   ├── last_name
│   ├── display_name
│   ├── username
│   ├── avatar_url
│   ├── phone
│   ├── phone_country_code
│   ├── date_of_birth            optional
│   ├── gender                   optional
│   ├── locale
│   ├── timezone
│   ├── country
│   └── bio
├── preferences
│   ├── theme
│   ├── language
│   └── notifications
│       ├── email
│       ├── push
│       ├── product_updates
│       └── security_alerts
├── status
│   ├── is_active
│   ├── is_email_verified
│   ├── is_phone_verified
│   └── onboarding_completed
├── security
│   ├── password_changed_at
│   ├── failed_login_count
│   ├── locked_until
│   └── last_login_at
├── created_at
└── updated_at
```

Sensitive/optional demographic fields should be collected only when the product actually needs them. The backend supports them without forcing users to provide them.

### devices

```text
devices
├── _id
├── user_id
├── installation_id
├── platform                    android | ios | web | windows | macos | linux
├── device
│   ├── manufacturer
│   ├── model
│   ├── device_name
│   ├── os_name
│   ├── os_version
│   ├── app_version
│   ├── app_build_number
│   ├── browser_name
│   ├── browser_version
│   ├── user_agent
│   ├── locale
│   ├── timezone
│   └── screen
│       ├── width
│       ├── height
│       └── pixel_ratio
├── notification
│   ├── provider                webpush | fcm | apns | onesignal | none
│   ├── token                   optional
│   └── permission              granted | denied | prompt | unknown
├── last_seen_at
├── created_at
└── updated_at
```

### push_subscriptions

```text
push_subscriptions
├── _id
├── user_id
├── device_id
├── provider                    webpush initially
├── endpoint
├── keys
│   ├── p256dh
│   └── auth
├── is_active
├── created_at
└── updated_at
```

### password_reset_tokens

```text
password_reset_tokens
├── _id
├── user_id
├── token_hash
├── expires_at                  TTL index
├── used_at
└── created_at
```

### revoked_tokens

```text
revoked_tokens
├── _id
├── jti
├── user_id
├── token_type
├── expires_at                  TTL index
└── revoked_at
```

### security_events

```text
security_events
├── _id
├── user_id                     nullable
├── type
├── ip
├── user_agent
├── metadata
└── created_at
```

## 6. API surface — Phase 1

```text
/api/v1
├── /health
│   └── GET /
│
├── /auth
│   ├── POST /register
│   ├── POST /login
│   ├── POST /refresh
│   ├── POST /logout
│   ├── POST /forgot-password
│   ├── POST /reset-password
│   └── POST /google
│
├── /users
│   ├── GET  /me
│   ├── PATCH /me
│   └── GET  /me/security-events
│
├── /devices
│   ├── POST /register
│   ├── GET  /
│   └── DELETE /<device_id>
│
└── /notifications
    ├── GET   /preferences
    ├── PATCH /preferences
    ├── POST  /web-push/subscribe
    └── DELETE /web-push/subscribe
```

## 7. Authentication flow

### Local login

```text
Flutter/PWA
   │
   ├── email + password
   ▼
POST /auth/login
   │
   ├── normalize email
   ├── rate-limit
   ├── check account lock
   ├── verify Argon2 hash
   ├── create access JWT
   └── create refresh JWT
   ▼
Client
```

### Google SSO

```text
Flutter / PWA
   │
   ├── Google SDK authentication
   ├── receives Google ID token
   ▼
POST /auth/google
   │
   ├── verify Google signature/audience
   ├── verify email / subject
   ├── find or create user
   ├── link Google provider safely
   └── issue platform JWT pair
   ▼
Client
```

This token-verification model is easier to reuse across Flutter, Android, iOS, and PWA than making the backend own the browser redirect UI.

## 8. Forgot-password flow

```text
POST /forgot-password
        │
        ├── always return generic response
        ├── if account exists:
        │    ├── generate cryptographic random token
        │    ├── store only SHA-256 token hash
        │    ├── TTL expiration
        │    └── email raw token in reset URL
        ▼
PWA / Flutter reset screen
        │
        ▼
POST /reset-password
        │
        ├── hash supplied token
        ├── validate token + expiry + unused state
        ├── change Argon2 password
        ├── mark reset token used
        └── revoke outstanding refresh/access tokens by user cutoff strategy
```

## 9. Security baseline

```text
Passwords
└── Argon2id

Tokens
├── short-lived access JWT
├── longer-lived refresh JWT
└── server-side revocation collection

Abuse controls
├── login rate limits
├── forgot-password limits
├── registration limits
└── generic account-recovery responses

Browser security
├── explicit CORS origins
├── HTTPS in production
└── no wildcard credentialed CORS

Audit
├── login_success
├── login_failed
├── register
├── password_reset_requested
├── password_reset_completed
├── google_login
├── logout
└── device_registered
```

## 10. PWA readiness

The backend is PWA-compatible because it is a stateless HTTPS JSON API. The PWA frontend will later add:

```text
pwa/
├── manifest.webmanifest
├── service-worker.js
├── install prompt UX
├── offline cache strategy
└── Web Push subscription creation
```

Web Push subscriptions are stored in this backend. Flutter mobile push can later plug into the same `devices.notification` abstraction.

## 11. Production deployment target

```text
Internet
   │
   ▼
CDN / WAF
   │
   ▼
Reverse Proxy (Nginx/Caddy/managed ingress)
   │
   ▼
Gunicorn
   │
   ▼
Flask app (multiple workers)
   │
   ├─────────────► MongoDB Atlas
   ├─────────────► SMTP / transactional email provider
   └─────────────► Google token verification
```

## 12. Future evolution

```text
Phase 1
├── Flask
├── MongoDB
└── Authentication / profile / devices

Phase 2+
├── OpenAI chat
├── Resume analysis
├── GitHub analysis
└── MCP tool layer

Scale-up
├── Redis
│   ├── distributed rate limiting
│   ├── caching
│   └── queues
├── Celery/RQ/Dramatiq
└── object storage

Finance phase
└── PostgreSQL
    ├── subscriptions
    ├── invoices
    ├── transactions
    └── financial ledger
```
