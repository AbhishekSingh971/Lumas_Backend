# Phase 2 Extension - AI Chat Platform

> This document extends the existing Phase 1 Authentication Backend.
>
> Nothing from Phase 1 is removed.
>
> All existing modules remain active and are reused by Phase 2.

---

# Existing Phase 1 Modules

```text
Authentication
├── Register
├── Login
├── Refresh Token
├── Logout
├── Forgot Password
├── Reset Password
└── Google SSO

Users
├── User Profile
├── Security Events
└── Account Management

Devices
├── Device Registration
├── Device Tracking
└── Device Removal

Notifications
├── Web Push Subscription
├── Notification Preferences
└── Push Management

Infrastructure
├── Flask
├── MongoDB
├── JWT
├── Repository Pattern
├── Service Layer
├── Pydantic
├── Rate Limiting
└── SMTP Email
```

---

# Phase 2 Modules

```text
AI Chat
├── Conversations
├── Messages
├── Context Memory
├── Conversation Search
├── Conversation Titles
├── OpenAI Integration
├── Streaming Responses
├── Usage Analytics
└── Token Tracking
```

---

# Updated Backend Structure

```text
app/
├── api/
│   └── v1/
│       ├── auth_routes.py
│       ├── user_routes.py
│       ├── device_routes.py
│       ├── notification_routes.py
│       ├── health_routes.py
│       │
│       ├── chat_routes.py
│       └── conversation_routes.py
│
├── repositories/
│   ├── user_repository.py
│   ├── token_repository.py
│   ├── device_repository.py
│   ├── notification_repository.py
│   │
│   ├── conversation_repository.py
│   ├── message_repository.py
│   └── usage_repository.py
│
├── services/
│   ├── auth_service.py
│   ├── email_service.py
│   ├── device_service.py
│   ├── notification_service.py
│   │
│   ├── openai_service.py
│   ├── chat_service.py
│   ├── memory_service.py
│   └── title_service.py
│
├── schemas/
│   ├── auth_schemas.py
│   ├── user_schemas.py
│   ├── device_schemas.py
│   ├── notification_schemas.py
│   │
│   ├── chat_schemas.py
│   └── conversation_schemas.py
│
├── database/
│   ├── mongo.py
│   ├── indexes.py
│   └── chat_indexes.py
│
├── core/
├── utils/
└── tests/
```

---

# Existing MongoDB Collections

```text
users
devices
revoked_tokens
security_events
push_subscriptions
password_reset_tokens
```

---

# New MongoDB Collections

```text
conversations
messages
ai_usage_logs
```

---

# Development Order

```text
Phase 1
✅ Authentication System

Phase 2
1. conversation_repository.py
2. message_repository.py
3. chat_schemas.py
4. openai_service.py
5. chat_service.py
6. chat_routes.py
7. chat_indexes.py

Phase 3
1. Resume Upload
2. Resume Parsing
3. ATS Engine
4. AI Resume Review
5. Job Matching
```

---

# Future SmartAI Vision

```text
SmartAI
├── Authentication
├── AI Chat
├── Resume Analyzer
├── Portfolio Reviewer
├── GitHub Analyzer
├── Job Search Assistant
├── Personal Finance Assistant
├── Mobile MCP
├── Developer MCP
└── Agent Marketplace
```