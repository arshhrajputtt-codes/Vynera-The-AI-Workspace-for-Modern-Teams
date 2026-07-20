from sqlalchemy.orm import Session

from app.models.workspace import Workspace


class WorkspaceRepository:

    def create(
        self,
        db: Session,
        workspace: Workspace
    ) -> Workspace:

        db.add(workspace)
        db.commit()
        db.refresh(workspace)

        return workspace


    def get_all_by_owner(
        self,
        db: Session,
        owner_id: int
    ) -> list[Workspace]:

        return (
            db.query(Workspace)
            .filter(Workspace.owner_id == owner_id)
            .all()
        )


    def get_by_id(
        self,
        db: Session,
        workspace_id: int
    ) -> Workspace | None:

        return (
            db.query(Workspace)
            .filter(Workspace.id == workspace_id)
            .first()
        )


    def update(
        self,
        db: Session,
        workspace: Workspace
    ) -> Workspace:

        db.commit()
        db.refresh(workspace)

        return workspace


    def delete(
        self,
        db: Session,
        workspace: Workspace
    ):

        db.delete(workspace)
        db.commit()