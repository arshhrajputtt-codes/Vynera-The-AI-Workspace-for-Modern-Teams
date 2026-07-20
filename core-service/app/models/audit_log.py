from sqlalchemy import JSON, Column, DateTime, Integer, String
from sqlalchemy.sql import func

from app.db.database import Base


class AuditLogEntry(Base):
    __tablename__ = "audit_log_entries"

    id = Column(Integer, primary_key=True, index=True)

    workspace_id = Column(Integer, nullable=False, index=True)
    actor_id = Column(Integer, nullable=False)

    action = Column(String(100), nullable=False)       # e.g. "approval.approved"
    entity_type = Column(String(50), nullable=False)   # e.g. "approval"
    entity_id = Column(Integer, nullable=False)

    event_metadata = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
