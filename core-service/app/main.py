from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.api.analytics import router as analytics_router
from app.api.approvals import router as approvals_router
from app.api.chat import router as chat_router
from app.api.documents import router as documents_router
from app.api.employees import router as employees_router
from app.core.config import settings
from app.db.database import Base, engine

# pgvector's extension must exist before create_all() can create a column
# of type Vector. CREATE EXTENSION requires appropriate DB privileges —
# on managed Postgres (RDS, Supabase, etc.) this is usually pre-enabled or
# a one-time admin step instead.
with engine.connect() as conn:
    conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    conn.commit()

# NOTE: same caveat as identity-service — fine for dev, replace with
# Alembic migrations before this touches staging/prod.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    description="AI Employees, knowledge base, chat, human approval, and usage analytics for Nexora",
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
    return {"message": "Welcome to Nexora", "service": "Core Service", "version": settings.APP_VERSION}


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(employees_router)
app.include_router(documents_router)
app.include_router(chat_router)
app.include_router(approvals_router)
app.include_router(analytics_router)
