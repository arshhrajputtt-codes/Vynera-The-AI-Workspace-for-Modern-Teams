from pydantic import BaseModel, Field


class WorkspaceCreate(BaseModel):
    name: str = Field(
        min_length=3,
        max_length=100
    )

    description: str | None = Field(
        default=None,
        max_length=500
    )


class WorkspaceUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=3,
        max_length=100
    )

    description: str | None = Field(
        default=None,
        max_length=500
    )


class WorkspaceResponse(BaseModel):
    id: int
    name: str
    slug: str
    description: str | None
    owner_id: int

    model_config = {
        "from_attributes": True
    }