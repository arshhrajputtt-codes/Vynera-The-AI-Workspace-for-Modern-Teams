from datetime import datetime

from sqlalchemy.orm import Session

from app.repositories.usage_repository import UsageRepository


class AnalyticsService:
    def __init__(self, usage_repository: UsageRepository | None = None):
        self.usage_repository = usage_repository or UsageRepository()

    def workspace_summary(
        self, db: Session, workspace_id: int, since: datetime | None, until: datetime | None
    ) -> dict:
        return self.usage_repository.summarize_for_workspace(db, workspace_id, since, until)

    def by_employee(self, db: Session, workspace_id: int) -> list[dict]:
        return self.usage_repository.summarize_by_employee(db, workspace_id)
