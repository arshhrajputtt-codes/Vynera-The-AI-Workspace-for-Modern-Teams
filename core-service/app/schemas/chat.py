from datetime import datetime

from pydantic import BaseModel

from app.models.message import MessageRole


class ChatRequest(BaseModel):
    message: str
    conversation_id: int | None = None  # omit to start a new conversation


class Citation(BaseModel):
    document_id: int
    chunk_id: int
    filename: str
    snippet: str


class MessageResponse(BaseModel):
    id: int
    conversation_id: int
    role: MessageRole
    content: str
    citations: list[Citation] | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ConversationResponse(BaseModel):
    id: int
    workspace_id: int
    employee_id: int
    user_id: int
    title: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
