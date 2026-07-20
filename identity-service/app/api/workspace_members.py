from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.exceptions import AlreadyMemberError, InsufficientRoleError, NotWorkspaceMemberError
from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.models.workspace_member import WorkspaceRole
from app.repositories.workspace_repository import WorkspaceRepository
from app.schemas.workspace_member import MemberInvite, MemberResponse, MemberRoleUpdate
from app.services.workspace_member_service import WorkspaceMemberService

router = APIRouter(prefix="/workspaces/{workspace_id}/members", tags=["Workspace Members"])

service = WorkspaceMemberService()
workspace_repository = WorkspaceRepository()


def _get_workspace_or_404(db: Session, workspace_id: int):
    workspace = workspace_repository.get_by_id(db, workspace_id)
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return workspace


def _translate(exc: Exception) -> HTTPException:
    if isinstance(exc, NotWorkspaceMemberError):
        return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    if isinstance(exc, InsufficientRoleError):
        return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    if isinstance(exc, AlreadyMemberError):
        return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.post("/invite", response_model=MemberResponse, status_code=status.HTTP_201_CREATED)
def invite_member(
    workspace_id: int,
    data: MemberInvite,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_workspace_or_404(db, workspace_id)
    try:
        service.require_role(db, workspace_id, current_user.id, WorkspaceRole.ADMIN)
        return service.invite_member(db, workspace_id, data)
    except (NotWorkspaceMemberError, InsufficientRoleError, AlreadyMemberError) as exc:
        raise _translate(exc) from exc


@router.get("", response_model=list[MemberResponse])
def list_members(
    workspace_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_workspace_or_404(db, workspace_id)
    try:
        service.require_role(db, workspace_id, current_user.id, WorkspaceRole.MEMBER)
    except (NotWorkspaceMemberError, InsufficientRoleError) as exc:
        raise _translate(exc) from exc

    return service.list_members(db, workspace_id)


@router.get("/me", response_model=MemberResponse)
def get_my_membership(
    workspace_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Lets other services (e.g. core-service) check the caller's role in a
    workspace with one call, instead of fetching the whole member list.
    """
    _get_workspace_or_404(db, workspace_id)
    membership = service.get_membership(db, workspace_id, current_user.id)
    if not membership:
        raise HTTPException(status_code=403, detail="You are not a member of this workspace")
    return membership


@router.post("/accept", response_model=MemberResponse)
def accept_invite(
    workspace_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_workspace_or_404(db, workspace_id)
    try:
        return service.accept_invite(db, workspace_id, current_user)
    except NotWorkspaceMemberError as exc:
        raise HTTPException(status_code=404, detail="No pending invite for this email") from exc


@router.patch("/{member_id}/role", response_model=MemberResponse)
def update_member_role(
    workspace_id: int,
    member_id: int,
    data: MemberRoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_workspace_or_404(db, workspace_id)
    try:
        service.require_role(db, workspace_id, current_user.id, WorkspaceRole.ADMIN)
    except (NotWorkspaceMemberError, InsufficientRoleError) as exc:
        raise _translate(exc) from exc

    member = service.repository.get_by_id(db, member_id)
    if not member or member.workspace_id != workspace_id:
        raise HTTPException(status_code=404, detail="Member not found")

    if member.role == WorkspaceRole.OWNER:
        raise HTTPException(status_code=403, detail="Cannot change the owner's role")

    return service.update_role(db, member, data.role)


@router.delete("/{member_id}")
def remove_member(
    workspace_id: int,
    member_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_workspace_or_404(db, workspace_id)
    try:
        service.require_role(db, workspace_id, current_user.id, WorkspaceRole.ADMIN)
    except (NotWorkspaceMemberError, InsufficientRoleError) as exc:
        raise _translate(exc) from exc

    member = service.repository.get_by_id(db, member_id)
    if not member or member.workspace_id != workspace_id:
        raise HTTPException(status_code=404, detail="Member not found")

    if member.role == WorkspaceRole.OWNER:
        raise HTTPException(status_code=403, detail="Cannot remove the workspace owner")

    service.remove_member(db, member)
    return {"message": "Member removed"}
