from datetime import datetime

from pydantic import BaseModel, EmailStr

from app.models.workspace_member import MembershipStatus, WorkspaceRole


class MemberInvite(BaseModel):
    email: EmailStr
    role: WorkspaceRole = WorkspaceRole.MEMBER


class MemberRoleUpdate(BaseModel):
    role: WorkspaceRole


class MemberResponse(BaseModel):
    id: int
    workspace_id: int
    user_id: int | None
    invited_email: str
    role: WorkspaceRole
    status: MembershipStatus
    created_at: datetime

    model_config = {"from_attributes": True}
