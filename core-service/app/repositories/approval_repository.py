from sqlalchemy.orm import Session

from app.models.approval import Approval, ApprovalStatus
from app.models.audit_log import AuditLogEntry


class ApprovalRepository:
    def create(self, db: Session, approval: Approval) -> Approval:
        db.add(approval)
        db.commit()
        db.refresh(approval)
        return approval

    def get_by_id(self, db: Session, approval_id: int) -> Approval | None:
        return db.query(Approval).filter(Approval.id == approval_id).first()

    def list_for_workspace(
        self, db: Session, workspace_id: int, status: ApprovalStatus | None = None
    ) -> list[Approval]:
        query = db.query(Approval).filter(Approval.workspace_id == workspace_id)
        if status:
            query = query.filter(Approval.status == status)
        return query.order_by(Approval.created_at.desc()).all()

    def update(self, db: Session, approval: Approval) -> Approval:
        db.commit()
        db.refresh(approval)
        return approval


class AuditLogRepository:
    def create(self, db: Session, entry: AuditLogEntry) -> AuditLogEntry:
        db.add(entry)
        db.commit()
        db.refresh(entry)
        return entry

    def list_for_workspace(self, db: Session, workspace_id: int) -> list[AuditLogEntry]:
        return (
            db.query(AuditLogEntry)
            .filter(AuditLogEntry.workspace_id == workspace_id)
            .order_by(AuditLogEntry.created_at.desc())
            .all()
        )
