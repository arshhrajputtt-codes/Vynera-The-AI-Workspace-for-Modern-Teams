from sqlalchemy.orm import Session

from app.core.exceptions import AlreadyMemberError, InsufficientRoleError, NotWorkspaceMemberError
from app.models.user import User
from app.models.workspace_member import MembershipStatus, WorkspaceMember, WorkspaceRole
from app.repositories.user_repository import UserRepository
from app.repositories.workspace_member_repository import WorkspaceMemberRepository
from app.schemas.workspace_member import MemberInvite

# Higher number = more privilege. Used by require_role() to check "at least this role".
_ROLE_RANK = {
    WorkspaceRole.MEMBER: 0,
    WorkspaceRole.ADMIN: 1,
    WorkspaceRole.OWNER: 2,
}


class WorkspaceMemberService:
    def __init__(
        self,
        repository: WorkspaceMemberRepository | None = None,
        user_repository: UserRepository | None = None,
    ):
        self.repository = repository or WorkspaceMemberRepository()
        self.user_repository = user_repository or UserRepository()

    def add_owner(self, db: Session, workspace_id: int, owner: User) -> WorkspaceMember:
        """Called right after a workspace is created so the creator is a member of it."""
        member = WorkspaceMember(
            workspace_id=workspace_id,
            user_id=owner.id,
            invited_email=owner.email,
            role=WorkspaceRole.OWNER,
            status=MembershipStatus.ACTIVE,
        )
        return self.repository.create(db, member)

    def get_membership(self, db: Session, workspace_id: int, user_id: int) -> WorkspaceMember | None:
        return self.repository.get_by_workspace_and_user(db, workspace_id, user_id)

    def require_role(
        self, db: Session, workspace_id: int, user_id: int, minimum_role: WorkspaceRole
    ) -> WorkspaceMember:
        """Raises if the user isn't an active member with at least `minimum_role`."""
        membership = self.get_membership(db, workspace_id, user_id)

        if not membership or membership.status != MembershipStatus.ACTIVE:
            raise NotWorkspaceMemberError()

        if _ROLE_RANK[membership.role] < _ROLE_RANK[minimum_role]:
            raise InsufficientRoleError(minimum_role.value)

        return membership

    def invite_member(
        self, db: Session, workspace_id: int, data: MemberInvite
    ) -> WorkspaceMember:
        if self.repository.get_by_workspace_and_email(db, workspace_id, data.email):
            raise AlreadyMemberError(data.email)

        existing_user = self.user_repository.get_by_email(db, data.email)

        member = WorkspaceMember(
            workspace_id=workspace_id,
            user_id=existing_user.id if existing_user else None,
            invited_email=data.email,
            role=data.role,
            # If they already have an account we still mark this PENDING —
            # they should explicitly accept before showing up as an active
            # member with access to the workspace's data.
            status=MembershipStatus.PENDING,
        )
        return self.repository.create(db, member)

    def accept_invite(self, db: Session, workspace_id: int, user: User) -> WorkspaceMember:
        membership = self.repository.get_by_workspace_and_email(db, workspace_id, user.email)

        if not membership:
            raise NotWorkspaceMemberError()

        membership.user_id = user.id
        membership.status = MembershipStatus.ACTIVE
        return self.repository.update(db, membership)

    def list_members(self, db: Session, workspace_id: int) -> list[WorkspaceMember]:
        return self.repository.list_for_workspace(db, workspace_id)

    def update_role(
        self, db: Session, member: WorkspaceMember, role: WorkspaceRole
    ) -> WorkspaceMember:
        member.role = role
        return self.repository.update(db, member)

    def remove_member(self, db: Session, member: WorkspaceMember) -> None:
        self.repository.delete(db, member)
