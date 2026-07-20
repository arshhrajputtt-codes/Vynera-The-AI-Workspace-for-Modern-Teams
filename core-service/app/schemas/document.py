from datetime import datetime

from pydantic import BaseModel

from app.models.document import DocumentStatus, DocumentType


class DocumentResponse(BaseModel):
    id: int
    workspace_id: int
    employee_id: int
    uploaded_by: int
    filename: str
    file_type: DocumentType
    status: DocumentStatus
    error_message: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
