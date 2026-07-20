from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError, ProviderError
from app.db.session import get_db
from app.dependencies.auth import CurrentUser
from app.dependencies.workspace import require_workspace_role
from app.models.approval import ApprovalStatus
from app.repositories.employee_repository import EmployeeRepository
from app.schemas.approval import (
    ApprovalResponse,
    AuditLogEntryResponse,
    DraftRequest,
    ReviewDecision,
)
from app.services.approval_service import ApprovalService

router = APIRouter(prefix="/workspaces/{workspace_id}", tags=["Human Approval"])

service = ApprovalService()
employee_repository = EmployeeRepository()


@router.post(
    "/employees/{employee_id}/drafts",
    response_model=ApprovalResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_draft(
    workspace_id: int,
    employee_id: int,
    data: DraftRequest,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_workspace_role("member")),
):
    employee = employee_repository.get_by_id(db, employee_id)
    if not employee or employee.workspace_id != workspace_id:
        raise HTTPException(status_code=404, detail="Employee not found")

    try:
        return service.create_draft(
            db, workspace_id, employee, current_user.id, data.prompt, data.conversation_id
        )
    except ProviderError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.get("/approvals", response_model=list[ApprovalResponse])
def list_approvals(
    workspace_id: int,
    status_filter: ApprovalStatus | None = Query(default=None, alias="status"),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_workspace_role("member")),
):
    return service.list_approvals(db, workspace_id, status_filter)


@router.get("/approvals/{approval_id}", response_model=ApprovalResponse)
def get_approval(
    workspace_id: int,
    approval_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_workspace_role("member")),
):
    try:
        return service.get_approval(db, workspace_id, approval_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/approvals/{approval_id}/approve", response_model=ApprovalResponse)
def approve(
    workspace_id: int,
    approval_id: int,
    data: ReviewDecision,
    db: Session = Depends(get_db),
    # Approving/rejecting is a review action — requires at least admin,
    # same tier as configuring the employee that produced the draft.
    current_user: CurrentUser = Depends(require_workspace_role("admin")),
):
    try:
        approval = service.get_approval(db, workspace_id, approval_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    if approval.status != ApprovalStatus.PENDING:
        raise HTTPException(status_code=409, detail=f"Approval is already {approval.status.value}")

    return service.approve(db, approval, current_user.id, data.note)


@router.post("/approvals/{approval_id}/reject", response_model=ApprovalResponse)
def reject(
    workspace_id: int,
    approval_id: int,
    data: ReviewDecision,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_workspace_role("admin")),
):
    try:
        approval = service.get_approval(db, workspace_id, approval_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    if approval.status != ApprovalStatus.PENDING:
        raise HTTPException(status_code=409, detail=f"Approval is already {approval.status.value}")

    return service.reject(db, approval, current_user.id, data.note)


@router.get("/audit-log", response_model=list[AuditLogEntryResponse])
def get_audit_log(
    workspace_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_workspace_role("admin")),
):
    return service.list_audit_log(db, workspace_id)
