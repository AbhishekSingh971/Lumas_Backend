from datetime import datetime

from app.repositories.conversation_repository import (
    ConversationRepository,
)

from app.repositories.message_repository import (
    MessageRepository,
)

from app.services.openai_service import (
    OpenAIService,
)

from app.repositories.usage_repository import (
    UsageRepository,
)


class ChatService:

    def __init__(self):
        self.conversation_repo = (
            ConversationRepository()
        )

        self.message_repo = (
            MessageRepository()
        )

        self.openai_service = (
            OpenAIService()
        )

        self.usage_repo = (
            UsageRepository()
        )

    def create_conversation(
        self,
        user_id: str,
        title: str = "New Chat",
        model: str = "gpt-5",
    ):
        return self.conversation_repo.create(
            user_id=user_id,
            title=title,
            model=model,
        )

    def get_conversation(
        self,
        user_id: str,
        conversation_id: str,
    ):
        return self.conversation_repo.get_user_conversation(
            conversation_id,
            user_id,
        )

    def list_conversations(
        self,
        user_id: str,
        page: int = 1,
        limit: int = 20,
    ):
        return self.conversation_repo.list_user_conversations(
            user_id=user_id,
            page=page,
            limit=limit,
        )

    def delete_conversation(
        self,
        user_id: str,
        conversation_id: str,
    ):
        self.message_repo.delete_conversation_messages(
            conversation_id
        )

        return self.conversation_repo.delete(
            conversation_id,
            user_id,
        )

    def send_message(
        self,
        user_id: str,
        conversation_id: str,
        user_message: str,
    ):
        conversation = (
            self.conversation_repo
            .get_user_conversation(
                conversation_id,
                user_id,
            )
        )

        if not conversation:
            raise ValueError(
                "Conversation not found"
            )

        self.message_repo.create(
            conversation_id=conversation_id,
            role="user",
            content=user_message,
            tokens=self.openai_service.count_tokens(
                user_message
            ),
        )

        prompt_tokens = (
            self.openai_service.count_tokens(
                user_message
                )
            )

        completion_tokens = (
            self.openai_service.count_tokens(
             ai_response
            )
        )

        self.usage_repo.create(
            user_id=user_id,
            conversation_id=conversation_id,
            model=conversation["model"],
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
        )

        context = (
            self.message_repo
            .get_context_window(
                conversation_id,
                limit=20,
            )
        )

        ai_response = (
            self.openai_service
            .generate_response(
                context,
                model=conversation["model"],
            )
        )

        self.message_repo.create(
            conversation_id=conversation_id,
            role="assistant",
            content=ai_response,
            tokens=self.openai_service.count_tokens(
                ai_response
            ),
        )

        self.conversation_repo.touch(
            conversation_id
        )

        if (
            conversation["title"]
            == "New Chat"
        ):
            try:
                generated_title = (
                    self.openai_service
                    .generate_title(
                        user_message
                    )
                )

                self.conversation_repo.update_title(
                    conversation_id,
                    generated_title,
                )
            except Exception:
                pass

        return {
            "conversation_id": conversation_id,
            "response": ai_response,
        }

    def get_messages(
        self,
        user_id: str,
        conversation_id: str,
    ):
        conversation = (
            self.conversation_repo
            .get_user_conversation(
                conversation_id,
                user_id,
            )
        )

        if not conversation:
            raise ValueError(
                "Conversation not found"
            )

        return (
            self.message_repo
            .get_conversation_messages(
                conversation_id
            )
        )

    def search_conversations(
        self,
        user_id: str,
        query: str,
    ):
        return (
            self.conversation_repo
            .search(
                user_id=user_id,
                query=query,
            )
        )

    def rename_conversation(
        self,
        user_id: str,
        conversation_id: str,
        title: str,
    ):
        conversation = (
            self.conversation_repo
            .get_user_conversation(
                conversation_id,
                user_id,
            )
        )

        if not conversation:
            raise ValueError(
                "Conversation not found"
            )

        return (
            self.conversation_repo
            .update_title(
                conversation_id,
                title,
            )
        )

    def stream_message(
    self,
    user_id: str,
    conversation_id: str,
    user_message: str,
    ):
        conversation = (
        self.conversation_repo
        .get_user_conversation(
            conversation_id,
            user_id,
            )
        )

        if not conversation:
            raise ValueError(
                "Conversation not found"
            )

        self.message_repo.create(
            conversation_id=conversation_id,
            role="user",
            content=user_message,
            tokens=self.openai_service.count_tokens(
                user_message
            ),
        )

        context = (
            self.message_repo
            .get_context_window(
                conversation_id,
                limit=20,
            )
        )

        complete_response = ""

        for chunk in (
            self.openai_service
            .stream_response(
                context,
                model=conversation["model"],
            )
        ):

            complete_response += chunk

            yield chunk

        self.message_repo.create(
            conversation_id=conversation_id,
            role="assistant",
            content=complete_response,
            tokens=self.openai_service.count_tokens(
                complete_response
            ),
        )

        self.conversation_repo.touch(
            conversation_id
        )
    