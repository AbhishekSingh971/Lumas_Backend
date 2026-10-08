# Phase 2 & 3 Integration Architecture

## Existing Phase 1 (Detected)
- Flask
- JWT Authentication
- MongoDB
- Repositories Layer
- Services Layer
- Schemas Layer
- Device Management
- Notifications
- Google Auth
- Audit Service

## Phase 2: AI Chat

app/
├── api/v1/
│   ├── chat_routes.py
├── repositories/
│   ├── conversation_repository.py
│   ├── message_repository.py
├── services/
│   ├── openai_service.py
│   ├── chat_service.py
├── schemas/
│   ├── chat_schemas.py

MongoDB Collections:
- conversations
- messages
- ai_usage_logs

Endpoints:
POST /api/v1/chat/conversations
GET  /api/v1/chat/conversations
GET  /api/v1/chat/conversations/<id>
POST /api/v1/chat/messages
DELETE /api/v1/chat/conversations/<id>

## Phase 3: Resume Analyzer

app/
├── api/v1/
│   ├── resume_routes.py
├── repositories/
│   ├── resume_repository.py
├── services/
│   ├── resume_parser_service.py
│   ├── ats_service.py
│   ├── resume_ai_service.py
├── schemas/
│   ├── resume_schemas.py

MongoDB Collections:
- resumes
- resume_reports

Endpoints:
POST /api/v1/resume/upload
POST /api/v1/resume/analyze
GET  /api/v1/resume/reports
GET  /api/v1/resume/reports/<id>

Packages:
- openai
- pymupdf
- pdfplumber
- python-docx
- tiktoken

Production Additions:
- Streaming responses
- Token usage tracking
- Conversation title generation
- Resume versioning
- Audit logs
- Rate limiting
- Background jobs
