from sqlalchemy.orm import Session

from app.models.workspace_member import WorkspaceMember


class WorkspaceMemberRepository:
    def create(self, db: Session, member: WorkspaceMember) -> WorkspaceMember:
        db.add(member)
        db.commit()
        db.refresh(member)
        return member

    def get_by_id(self, db: Session, member_id: int) -> WorkspaceMember | None:
        return db.query(WorkspaceMember).filter(WorkspaceMember.id == member_id).first()

    def get_by_workspace_and_user(
        self, db: Session, workspace_id: int, user_id: int
    ) -> WorkspaceMember | None:
        return (
            db.query(WorkspaceMember)
            .filter(
                WorkspaceMember.workspace_id == workspace_id,
                WorkspaceMember.user_id == user_id,
            )
            .first()
        )

    def get_by_workspace_and_email(
        self, db: Session, workspace_id: int, email: str
    ) -> WorkspaceMember | None:
        return (
            db.query(WorkspaceMember)
            .filter(
                WorkspaceMember.workspace_id == workspace_id,
                WorkspaceMember.invited_email == email,
            )
            .first()
        )

    def list_for_workspace(self, db: Session, workspace_id: int) -> list[WorkspaceMember]:
        return (
            db.query(WorkspaceMember)
            .filter(WorkspaceMember.workspace_id == workspace_id)
            .all()
        )

    def list_pending_for_email(self, db: Session, email: str) -> list[WorkspaceMember]:
        return (
            db.query(WorkspaceMember)
            .filter(WorkspaceMember.invited_email == email)
            .all()
        )

    def update(self, db: Session, member: WorkspaceMember) -> WorkspaceMember:
        db.commit()
        db.refresh(member)
        return member

    def delete(self, db: Session, member: WorkspaceMember) -> None:
        db.delete(member)
        db.commit()
