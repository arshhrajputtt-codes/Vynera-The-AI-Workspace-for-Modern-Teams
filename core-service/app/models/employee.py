from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text
from sqlalchemy.sql import func

from app.db.database import Base


class Employee(Base):
    """An 'AI Employee': a configured persona (prompt + model) scoped to a workspace."""

    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)

    # No ForeignKey — workspaces/users live in identity-service's own
    # database. Cross-service references are validated via IdentityClient
    # at request time, not via a DB-level constraint.
    workspace_id = Column(Integer, nullable=False, index=True)
    created_by = Column(Integer, nullable=False)

    name = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)
    system_prompt = Column(Text, nullable=False)

    model = Column(String(100), nullable=False, default="claude-sonnet-4-6")
    temperature = Column(Float, nullable=False, default=0.7)

    is_active = Column(Boolean, nullable=False, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
