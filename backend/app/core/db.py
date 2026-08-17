"""Database engine and the request-scoped session dependency.

The engine is created once at import and connects lazily on first use, so importing
this module does not require a reachable database. Inject ``get_session`` via
FastAPI's ``Depends`` — services receive the session as an argument and never open
their own (per backend/CLAUDE.md).
"""

from collections.abc import Generator

from sqlmodel import Session, create_engine

from app.core.config import get_settings

engine = create_engine(get_settings().database_url, echo=False, pool_pre_ping=True)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
