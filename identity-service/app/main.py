from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.api.workspace import router as workspace_router
from app.api.workspace_members import router as workspace_members_router
from app.core.config import settings
from app.db.database import Base, engine

# NOTE: create_all is fine for local/dev bootstrapping. For staging/prod,
# replace this with Alembic migrations so schema changes are versioned
# and reviewable instead of silently applied on startup.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    description="Authentication, authorization, and workspace management for Nexora",
    version=settings.APP_VERSION,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "message": "Welcome to Nexora",
        "service": "Identity Service",
        "version": settings.APP_VERSION,
    }


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(auth_router)
app.include_router(workspace_router)
app.include_router(workspace_members_router)
