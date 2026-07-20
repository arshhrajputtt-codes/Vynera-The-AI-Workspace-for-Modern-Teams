from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.usage_event import UsageEvent


class UsageRepository:
    def create(self, db: Session, event: UsageEvent) -> UsageEvent:
        db.add(event)
        db.commit()
        db.refresh(event)
        return event

    def summarize_for_workspace(
        self,
        db: Session,
        workspace_id: int,
        since: datetime | None = None,
        until: datetime | None = None,
    ) -> dict:
        query = db.query(
            func.count(UsageEvent.id).label("message_count"),
            func.coalesce(func.sum(UsageEvent.input_tokens), 0).label("input_tokens"),
            func.coalesce(func.sum(UsageEvent.output_tokens), 0).label("output_tokens"),
            func.coalesce(func.sum(UsageEvent.cost_usd), 0.0).label("cost_usd"),
        ).filter(UsageEvent.workspace_id == workspace_id)

        if since:
            query = query.filter(UsageEvent.created_at >= since)
        if until:
            query = query.filter(UsageEvent.created_at <= until)

        row = query.one()
        return {
            "message_count": row.message_count,
            "input_tokens": row.input_tokens,
            "output_tokens": row.output_tokens,
            "total_tokens": row.input_tokens + row.output_tokens,
            "cost_usd": round(row.cost_usd, 4),
        }

    def summarize_by_employee(self, db: Session, workspace_id: int) -> list[dict]:
        rows = (
            db.query(
                UsageEvent.employee_id,
                func.count(UsageEvent.id).label("message_count"),
                func.coalesce(func.sum(UsageEvent.input_tokens), 0).label("input_tokens"),
                func.coalesce(func.sum(UsageEvent.output_tokens), 0).label("output_tokens"),
                func.coalesce(func.sum(UsageEvent.cost_usd), 0.0).label("cost_usd"),
            )
            .filter(UsageEvent.workspace_id == workspace_id)
            .group_by(UsageEvent.employee_id)
            .all()
        )
        return [
            {
                "employee_id": row.employee_id,
                "message_count": row.message_count,
                "input_tokens": row.input_tokens,
                "output_tokens": row.output_tokens,
                "total_tokens": row.input_tokens + row.output_tokens,
                "cost_usd": round(row.cost_usd, 4),
            }
            for row in rows
        ]
