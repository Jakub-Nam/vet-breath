"""Application settings, loaded from the environment via Pydantic Settings.

All configuration enters the app here and nowhere else. Inject `get_settings`
through FastAPI's dependency system rather than reading `os.environ` in routers
or services.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "VetBreath API"
    environment: str = "development"

    # Database (FR: persistence for vets, owners, dogs, readings)
    database_url: str = "postgresql+psycopg://vetbreath:vetbreath@localhost:5432/vetbreath"

    # Auth
    secret_key: str = "CHANGE-ME-set-a-real-secret-in-env"
    access_token_expire_minutes: int = 60
    invitation_token_expire_days: int = 7

    # Transactional email via Resend (FR-003 invitations, FR-013 password reset).
    # Empty resend_api_key → console fallback (dev mode, no emails sent).
    email_from: str = "no-reply@vetbreath.local"
    resend_api_key: str = ""
    frontend_url: str = "http://localhost:4200"


@lru_cache
def get_settings() -> Settings:
    """Cached settings accessor. Use as a FastAPI dependency: `Depends(get_settings)`."""
    return Settings()
