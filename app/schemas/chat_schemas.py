from pydantic import BaseModel, Field
from typing import Optional


class CreateConversationSchema(BaseModel):
    title: Optional[str] = Field(
        default="New Chat",
        min_length=1,
        max_length=200
    )

    model: str = Field(
        default="gpt-5",
        min_length=1,
        max_length=100
    )


class SendMessageSchema(BaseModel):
    conversation_id: str

    message: str = Field(
        min_length=1,
        max_length=8000
    )


class RenameConversationSchema(BaseModel):
    title: str = Field(
        min_length=1,
        max_length=200
    )


class SearchConversationSchema(BaseModel):
    query: str = Field(
        min_length=1,
        max_length=200
    )


class ConversationResponse(BaseModel):
    id: str
    title: str
    model: str
    created_at: str
    updated_at: str


class MessageResponse(BaseModel):
    id: str
    conversation_id: str
    role: str
    content: str
    created_at: str