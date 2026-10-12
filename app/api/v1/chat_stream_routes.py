import json

from flask import Blueprint, Response, request, stream_with_context
from flask_jwt_extended import jwt_required, get_jwt_identity
from pydantic import ValidationError

from app.services.chat_service import ChatService
from app.schemas.chat_schemas import SendMessageSchema
from app.utils.responses import fail

bp = Blueprint(
    "chat_stream",
    __name__,
    url_prefix="/chat-stream",
)


@bp.post("/message")
@jwt_required()
def stream_message():
    user_id = get_jwt_identity()

    try:
        data = request.get_json(silent=True) or {}
        payload = SendMessageSchema.model_validate(data)

        service = ChatService()

        # Verify the conversation belongs to the authenticated user.
        conversation = service.get_conversation(
            user_id=user_id,
            conversation_id=str(payload.conversation_id),
        )

        if not conversation:
            return fail(
                "Conversation not found",
                404,
                "conversation_not_found",
            )

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

    conversation_id = str(payload.conversation_id)
    user_message = payload.message

    @stream_with_context
    def generate():
        try:
            for chunk in service.stream_message(
                user_id=user_id,
                conversation_id=conversation_id,
                user_message=user_message,
            ):
                yield (
                    "data: "
                    + json.dumps({"content": chunk})
                    + "\n\n"
                )

            yield "data: [DONE]\n\n"

        except Exception as exc:
            import traceback

            traceback.print_exc()
            yield (
                "event: error\n"
                + "data: "
                + json.dumps({
                    "error": "Failed to generate response"
                })
                + "\n\n"
            )

    return Response(
        generate(),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )