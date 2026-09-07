"""Application settings, loaded from the environment via Pydantic Settings.

All configuration enters the app here and nowhere else. Inject `get_settings`
through FastAPI's dependency system rather than reading `os.environ` in routers
or services.
"""

from functools import lru_cache

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_PLACEHOLDER_SECRET = "CHANGE-ME-set-a-real-secret-in-env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "VetBreath API"
    environment: str = "development"

    # Database (FR: persistence for vets, owners, dogs, readings)
    database_url: str = "postgresql+psycopg://vetbreath:vetbreath@localhost:5432/vetbreath"

    # Auth
    secret_key: str = _PLACEHOLDER_SECRET
    access_token_expire_minutes: int = 60

    # Frontend origin — used for CORS (app/main.py). The app sends no transactional
    # email: vets create client accounts directly (email + password), no invitations.
    frontend_url: str = "http://localhost:4200"

    @model_validator(mode="after")
    def _normalize_database_url(self) -> "Settings":
        # Railway (and most managed PG) inject `postgresql://…`, but this app uses psycopg v3,
        # so SQLAlchemy needs the `postgresql+psycopg://…` scheme or it falls back to the
        # absent psycopg2 driver. Normalize here — config is the only place env enters.
        if self.database_url.startswith("postgresql://"):
            self.database_url = self.database_url.replace("postgresql://", "postgresql+psycopg://", 1)
        return self

    @model_validator(mode="after")
    def _reject_placeholder_secret_in_production(self) -> "Settings":
        if self.environment == "production" and self.secret_key == _PLACEHOLDER_SECRET:
            raise ValueError(
                "SECRET_KEY is still the development placeholder; set a real secret via "
                "the SECRET_KEY environment variable before running in production."
            )
        return self


@lru_cache
def get_settings() -> Settings:
    """Cached settings accessor. Use as a FastAPI dependency: `Depends(get_settings)`."""
    return Settings()
