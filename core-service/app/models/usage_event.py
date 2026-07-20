import enum

from sqlalchemy import Column, DateTime, Enum, Float, Integer, String
from sqlalchemy.sql import func

from app.db.database import Base


class UsageEventType(str, enum.Enum):
    CHAT_COMPLETION = "chat_completion"
    EMBEDDING = "embedding"


# Static per-model $/million-token rates, checked at write time. Good enough
# for a v1 cost estimate; swap for a pricing table pulled from provider
# billing APIs if exact reconciliation ever matters.
_RATES_PER_MILLION_TOKENS = {
    "claude-sonnet-4-6": {"input": 3.00, "output": 15.00},
    "text-embedding-3-small": {"input": 0.02, "output": 0.0},
    "llama3": {"input": 0.0, "output": 0.0},  # local/free via Ollama
}


def estimate_cost_usd(model: str, input_tokens: int, output_tokens: int) -> float:
    rates = _RATES_PER_MILLION_TOKENS.get(model, {"input": 0.0, "output": 0.0})
    return (input_tokens * rates["input"] + output_tokens * rates["output"]) / 1_000_000


class UsageEvent(Base):
    __tablename__ = "usage_events"

    id = Column(Integer, primary_key=True, index=True)

    workspace_id = Column(Integer, nullable=False, index=True)
    employee_id = Column(Integer, nullable=True, index=True)
    user_id = Column(Integer, nullable=False)
    conversation_id = Column(Integer, nullable=True, index=True)

    event_type = Column(Enum(UsageEventType), nullable=False)
    model = Column(String(100), nullable=False)

    input_tokens = Column(Integer, nullable=False, default=0)
    output_tokens = Column(Integer, nullable=False, default=0)
    cost_usd = Column(Float, nullable=False, default=0.0)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
