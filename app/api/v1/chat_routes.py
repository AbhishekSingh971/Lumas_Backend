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


# chat_service = ChatService()