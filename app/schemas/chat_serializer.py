def conversation_to_dict(conversation):
    return {
        "id": str(conversation["_id"]),
        "title": conversation["title"],
        "model": conversation["model"],
        "created_at": conversation["created_at"].isoformat(),
        "updated_at": conversation["updated_at"].isoformat(),
    }


def message_to_dict(message):
    return {
        "id": str(message["_id"]),
        "conversation_id": str(message["conversation_id"]),
        "role": message["role"],
        "content": message["content"],
        "created_at": message["created_at"].isoformat(),
    }