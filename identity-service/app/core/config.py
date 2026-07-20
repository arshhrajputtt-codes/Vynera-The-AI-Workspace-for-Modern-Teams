from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Central application configuration.

    Values are read from environment variables (or a .env file in local
    development). Nothing sensitive is hardcoded in source — this is what
    lets the exact same code run in dev, staging, and prod with different
    secrets/URLs injected at deploy time.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- App metadata ---
    APP_NAME: str = "Nexora Identity Service"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"  # development | staging | production
    DEBUG: bool = True

    # --- Database ---
    DATABASE_URL: str = "sqlite:///./nexora.db"

    # --- JWT / auth ---
    SECRET_KEY: str = "CHANGE-ME-IN-PRODUCTION"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # --- CORS ---
    ALLOWED_ORIGINS: list[str] = ["*"]


@lru_cache
def get_settings() -> Settings:
    """
    Cached settings accessor.

    Using a function (rather than a module-level singleton) means it can be
    overridden cleanly in tests via dependency_overrides or monkeypatching
    the cache.
    """
    return Settings()


settings = get_settings()
