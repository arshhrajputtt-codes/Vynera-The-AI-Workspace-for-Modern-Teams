from datetime import datetime

from pydantic import BaseModel, Field

from app.models.approval import ApprovalStatus


class DraftRequest(BaseModel):
    prompt: str = Field(min_length=1)
    conversation_id: int | None = None


class ReviewDecision(BaseModel):
    note: str | None = Field(default=None, max_length=500)


class ApprovalResponse(BaseModel):
    id: int
    workspace_id: int
    employee_id: int
    conversation_id: int | None
    prompt: str
    draft_content: str
    status: ApprovalStatus
    requested_by: int
    reviewed_by: int | None
    review_note: str | None
    created_at: datetime
    reviewed_at: datetime | None

    model_config = {"from_attributes": True}


class AuditLogEntryResponse(BaseModel):
    id: int
    workspace_id: int
    actor_id: int
    action: str
    entity_type: str
    entity_id: int
    event_metadata: dict | None
    created_at: datetime

    model_config = {"from_attributes": True}
