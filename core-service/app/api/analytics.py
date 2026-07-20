from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import CurrentUser
from app.dependencies.workspace import require_workspace_role
from app.schemas.analytics import EmployeeUsageResponse, UsageSummaryResponse
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/workspaces/{workspace_id}/analytics", tags=["Analytics"])

service = AnalyticsService()


@router.get("/usage", response_model=UsageSummaryResponse)
def get_usage_summary(
    workspace_id: int,
    since: datetime | None = Query(default=None),
    until: datetime | None = Query(default=None),
    db: Session = Depends(get_db),
    # Cost data is sensitive enough to keep at admin-and-up, same as
    # everything else that touches billing.
    current_user: CurrentUser = Depends(require_workspace_role("admin")),
):
    return service.workspace_summary(db, workspace_id, since, until)


@router.get("/usage/by-employee", response_model=list[EmployeeUsageResponse])
def get_usage_by_employee(
    workspace_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_workspace_role("admin")),
):
    return service.by_employee(db, workspace_id)
