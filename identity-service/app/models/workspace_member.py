import enum

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.sql import func

from app.db.database import Base


class WorkspaceRole(str, enum.Enum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"


class MembershipStatus(str, enum.Enum):
    PENDING = "pending"   # invited but not yet accepted (or user doesn't exist yet)
    ACTIVE = "active"


class WorkspaceMember(Base):
    __tablename__ = "workspace_members"

    id = Column(Integer, primary_key=True, index=True)

    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=False, index=True)

    # Null until the invited email registers/accepts and gets linked to a user.
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    invited_email = Column(String, nullable=False, index=True)

    role = Column(Enum(WorkspaceRole), nullable=False, default=WorkspaceRole.MEMBER)
    status = Column(Enum(MembershipStatus), nullable=False, default=MembershipStatus.PENDING)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
