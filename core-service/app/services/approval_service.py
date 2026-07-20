from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from app.core.exceptions import NotFoundError
from app.models.approval import Approval, ApprovalStatus
from app.models.audit_log import AuditLogEntry
from app.models.usage_event import UsageEvent, UsageEventType, estimate_cost_usd
from app.repositories.approval_repository import ApprovalRepository, AuditLogRepository
from app.repositories.usage_repository import UsageRepository
from app.services.llm_service import LLMService


class ApprovalService:
    def __init__(
        self,
        approval_repository: ApprovalRepository | None = None,
        audit_repository: AuditLogRepository | None = None,
        usage_repository: UsageRepository | None = None,
        llm_service: LLMService | None = None,
    ):
        self.approval_repository = approval_repository or ApprovalRepository()
        self.audit_repository = audit_repository or AuditLogRepository()
        self.usage_repository = usage_repository or UsageRepository()
        self.llm_service = llm_service or LLMService()

    def _log(self, db: Session, workspace_id: int, actor_id: int, action: str, entity_id: int, metadata: dict | None = None):
        self.audit_repository.create(
            db,
            AuditLogEntry(
                workspace_id=workspace_id,
                actor_id=actor_id,
                action=action,
                entity_type="approval",
                entity_id=entity_id,
                event_metadata=metadata,
            ),
        )

    def create_draft(
        self,
        db: Session,
        workspace_id: int,
        employee,  # Employee
        requested_by: int,
        prompt: str,
        conversation_id: int | None,
    ) -> Approval:
        result = self.llm_service.complete(
            system_prompt=employee.system_prompt,
            messages=[{"role": "user", "content": prompt}],
            model=employee.model,
            temperature=employee.temperature,
        )

        approval = Approval(
            workspace_id=workspace_id,
            employee_id=employee.id,
            conversation_id=conversation_id,
            prompt=prompt,
            draft_content=result["content"],
            status=ApprovalStatus.PENDING,
            requested_by=requested_by,
        )
        approval = self.approval_repository.create(db, approval)

        self.usage_repository.create(
            db,
            UsageEvent(
                workspace_id=workspace_id,
                employee_id=employee.id,
                user_id=requested_by,
                conversation_id=conversation_id,
                event_type=UsageEventType.CHAT_COMPLETION,
                model=result["model"],
                input_tokens=result["input_tokens"],
                output_tokens=result["output_tokens"],
                cost_usd=estimate_cost_usd(result["model"], result["input_tokens"], result["output_tokens"]),
            ),
        )

        self._log(db, workspace_id, requested_by, "approval.created", approval.id)
        return approval

    def get_approval(self, db: Session, workspace_id: int, approval_id: int) -> Approval:
        approval = self.approval_repository.get_by_id(db, approval_id)
        if not approval or approval.workspace_id != workspace_id:
            raise NotFoundError("Approval", approval_id)
        return approval

    def list_approvals(
        self, db: Session, workspace_id: int, status: ApprovalStatus | None = None
    ) -> list[Approval]:
        return self.approval_repository.list_for_workspace(db, workspace_id, status)

    def approve(self, db: Session, approval: Approval, reviewer_id: int, note: str | None) -> Approval:
        approval.status = ApprovalStatus.APPROVED
        approval.reviewed_by = reviewer_id
        approval.review_note = note
        approval.reviewed_at = func.now()
        approval = self.approval_repository.update(db, approval)
        self._log(db, approval.workspace_id, reviewer_id, "approval.approved", approval.id, {"note": note})
        return approval

    def reject(self, db: Session, approval: Approval, reviewer_id: int, note: str | None) -> Approval:
        approval.status = ApprovalStatus.REJECTED
        approval.reviewed_by = reviewer_id
        approval.review_note = note
        approval.reviewed_at = func.now()
        approval = self.approval_repository.update(db, approval)
        self._log(db, approval.workspace_id, reviewer_id, "approval.rejected", approval.id, {"note": note})
        return approval

    def list_audit_log(self, db: Session, workspace_id: int):
        return self.audit_repository.list_for_workspace(db, workspace_id)
