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

    # Transactional email (FR-003 invitations, FR-013 password reset) — wire a provider here.
    # No mailer ships with FastAPI; placeholder until a provider (Resend/Postmark/SES) is chosen.
    email_from: str = "no-reply@vetbreath.local"


@lru_cache
def get_settings() -> Settings:
    """Cached settings accessor. Use as a FastAPI dependency: `Depends(get_settings)`."""
    return Settings()
