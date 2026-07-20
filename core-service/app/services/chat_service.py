from collections.abc import Generator

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.models.conversation import Conversation
from app.models.message import Message, MessageRole
from app.models.usage_event import UsageEvent, UsageEventType, estimate_cost_usd
from app.repositories.conversation_repository import ConversationRepository, MessageRepository
from app.repositories.usage_repository import UsageRepository
from app.services.llm_service import LLMService
from app.services.vector_search_service import VectorSearchService

RAG_SYSTEM_TEMPLATE = """{base_prompt}

You have access to the following excerpts from the workspace's knowledge base. \
Use them to answer the user's question when relevant, and cite sources using \
[1], [2], etc. matching the excerpt numbers below. If the excerpts don't \
contain the answer, say so plainly instead of guessing.

{context_block}"""


class ChatService:
    def __init__(
        self,
        conversation_repository: ConversationRepository | None = None,
        message_repository: MessageRepository | None = None,
        usage_repository: UsageRepository | None = None,
        vector_search_service: VectorSearchService | None = None,
        llm_service: LLMService | None = None,
    ):
        self.conversation_repository = conversation_repository or ConversationRepository()
        self.message_repository = message_repository or MessageRepository()
        self.usage_repository = usage_repository or UsageRepository()
        self.vector_search_service = vector_search_service or VectorSearchService()
        self.llm_service = llm_service or LLMService()

    def get_or_create_conversation(
        self, db: Session, workspace_id: int, employee_id: int, user_id: int, conversation_id: int | None
    ) -> Conversation:
        if conversation_id is not None:
            conversation = self.conversation_repository.get_by_id(db, conversation_id)
            if not conversation or conversation.employee_id != employee_id or conversation.user_id != user_id:
                raise NotFoundError("Conversation", conversation_id)
            return conversation

        conversation = Conversation(workspace_id=workspace_id, employee_id=employee_id, user_id=user_id)
        return self.conversation_repository.create(db, conversation)

    def list_history(self, db: Session, conversation: Conversation) -> list[Message]:
        return self.message_repository.list_for_conversation(db, conversation.id)

    def stream_reply(
        self,
        db: Session,
        conversation: Conversation,
        employee,  # app.models.employee.Employee
        user_id: int,
        user_text: str,
    ) -> Generator[dict, None, None]:
        """
        Streaming generator: yields {"type": "delta", "text": ...} chunks as
        the model responds, then a final {"type": "done", "message_id",
        "content", "citations"} event once history/usage have been saved.
        The API layer turns these into SSE frames.
        """
        self.message_repository.create(
            db, Message(conversation_id=conversation.id, role=MessageRole.USER, content=user_text)
        )

        chunks = self.vector_search_service.search(db, employee.id, user_text)
        citations = [
            {
                "document_id": chunk.document_id,
                "chunk_id": chunk.id,
                "filename": f"document-{chunk.document_id}",
                "snippet": chunk.content[:280],
            }
            for chunk in chunks
        ]
        context_block = "\n\n".join(
            f"[{i + 1}] {chunk.content}" for i, chunk in enumerate(chunks)
        ) or "(no relevant excerpts found)"

        system_prompt = RAG_SYSTEM_TEMPLATE.format(
            base_prompt=employee.system_prompt, context_block=context_block
        )
        history = self.list_history(db, conversation)
        messages = [{"role": m.role.value, "content": m.content} for m in history]

        full_text = ""
        input_tokens = 0
        output_tokens = 0
        actual_model = employee.model

        for event in self.llm_service.stream_completion(
            system_prompt, messages, employee.model, employee.temperature
        ):
            if event["type"] == "delta":
                full_text += event["text"]
                yield event
            elif event["type"] == "usage":
                input_tokens = event["input_tokens"]
                output_tokens = event["output_tokens"]
                actual_model = event.get("model", employee.model)

        assistant_message = self.message_repository.create(
            db,
            Message(
                conversation_id=conversation.id,
                role=MessageRole.ASSISTANT,
                content=full_text,
                citations=citations or None,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
            ),
        )

        self.usage_repository.create(
            db,
            UsageEvent(
                workspace_id=conversation.workspace_id,
                employee_id=employee.id,
                user_id=user_id,
                conversation_id=conversation.id,
                event_type=UsageEventType.CHAT_COMPLETION,
                model=actual_model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost_usd=estimate_cost_usd(actual_model, input_tokens, output_tokens),
            ),
        )

        yield {
            "type": "done",
            "message_id": assistant_message.id,
            "content": full_text,
            "citations": citations,
        }
