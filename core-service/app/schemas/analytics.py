from pydantic import BaseModel


class UsageSummaryResponse(BaseModel):
    message_count: int
    input_tokens: int
    output_tokens: int
    total_tokens: int
    cost_usd: float


class EmployeeUsageResponse(BaseModel):
    employee_id: int | None
    message_count: int
    input_tokens: int
    output_tokens: int
    total_tokens: int
    cost_usd: float
