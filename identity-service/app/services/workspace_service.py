from slugify import slugify
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.workspace import Workspace
from app.repositories.workspace_repository import WorkspaceRepository
from app.schemas.workspace import WorkspaceCreate, WorkspaceUpdate
from app.services.workspace_member_service import WorkspaceMemberService


class WorkspaceService:

    def __init__(
        self,
        repository: WorkspaceRepository | None = None,
        member_service: WorkspaceMemberService | None = None,
    ):
        self.repository = repository or WorkspaceRepository()
        self.member_service = member_service or WorkspaceMemberService()


    def create_workspace(
        self,
        db: Session,
        workspace_data: WorkspaceCreate,
        owner: User
    ):

        workspace = Workspace(
            name=workspace_data.name,
            slug=slugify(workspace_data.name),
            description=workspace_data.description,
            owner_id=owner.id
        )

        workspace = self.repository.create(
            db,
            workspace
        )

        # Creating a workspace makes you its OWNER member — every other
        # membership/role check downstream depends on this row existing.
        self.member_service.add_owner(db, workspace.id, owner)

        return workspace


    def get_my_workspaces(
        self,
        db: Session,
        owner_id: int
    ):

        return self.repository.get_all_by_owner(
            db,
            owner_id
        )


    def get_workspace(
        self,
        db: Session,
        workspace_id: int
    ):

        return self.repository.get_by_id(
            db,
            workspace_id
        )


    def update_workspace(
        self,
        db: Session,
        workspace: Workspace,
        data: WorkspaceUpdate
    ):

        if data.name is not None:
            workspace.name = data.name
            workspace.slug = slugify(data.name)

        if data.description is not None:
            workspace.description = data.description

        return self.repository.update(
            db,
            workspace
        )


    def delete_workspace(
        self,
        db: Session,
        workspace: Workspace
    ):

        self.repository.delete(
            db,
            workspace
        )