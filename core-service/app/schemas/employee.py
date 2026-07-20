from datetime import datetime

from pydantic import BaseModel, Field


class EmployeeCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    system_prompt: str = Field(min_length=1)
    model: str = "claude-sonnet-4-6"
    temperature: float = Field(default=0.7, ge=0.0, le=1.0)


class EmployeeUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    system_prompt: str | None = None
    model: str | None = None
    temperature: float | None = Field(default=None, ge=0.0, le=1.0)
    is_active: bool | None = None


class EmployeeResponse(BaseModel):
    id: int
    workspace_id: int
    created_by: int
    name: str
    description: str | None
    system_prompt: str
    model: str
    temperature: float
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
