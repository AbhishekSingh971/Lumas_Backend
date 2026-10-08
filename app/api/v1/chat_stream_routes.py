from flask import Blueprint
from flask import request
from flask import Response
from flask import stream_with_context

from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
)

from app.services.chat_service import (
    ChatService,
)

bp = Blueprint(
    "chat_stream",
    __name__,
    url_prefix="/chat-stream",
)

# chat_service = ChatService()
