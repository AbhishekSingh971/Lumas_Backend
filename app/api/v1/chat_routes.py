from flask import Blueprint
from flask import request

from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
)

from pydantic import ValidationError

from app.services.chat_service import (
    ChatService,
)

from app.schemas.chat_schemas import (
    CreateConversationSchema,
    SendMessageSchema,
    RenameConversationSchema,
)

from app.schemas.chat_serializer import (
    conversation_to_dict,
    message_to_dict,
)

from app.utils.responses import (
    ok,
    fail,
)

bp = Blueprint(
    "chat",
    __name__,
    url_prefix="/chat",
)


def get_chat_service():
    return ChatService()

@bp.post("/conversations")
@jwt_required()
def create_conversation():
    user_id = get_jwt_identity()
    service = ChatService()

    try:
        data = request.get_json(silent=True) or {}
        payload = CreateConversationSchema.model_validate(data)

        conversation = service.create_conversation(
            user_id=user_id,
            title=getattr(payload, "title", "New Chat"),
            model=getattr(payload, "model", "gpt-5"),
        )

        return ok(conversation_to_dict(conversation))

    except ValidationError:
        return fail(
            "Invalid request data",
            400,
            "validation_error",
        )
    except ValueError as exc:
        return fail(
            str(exc),
            400,
            "invalid_request",
        )