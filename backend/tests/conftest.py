import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlmodel import Session, create_engine

from app.core.config import get_settings
from app.core.db import get_session
from app.core.security import create_access_token, hash_password
from app.main import app
from app.models.enums import OwnerStatus
from app.models.owner import Owner
from app.models.vet import Vet

_engine = create_engine(get_settings().database_url, echo=False)

_TABLES = ("reading", "dog", "owner", "vet")


@pytest.fixture(autouse=True)
def _stub_email(monkeypatch):
    """Keep the suite hermetic: never hit the real email provider, even when a
    RESEND_API_KEY is present in the environment. Tests that need to exercise a
    send failure override this by patching ``_send`` to raise ``EmailSendError``."""
    monkeypatch.setattr("app.services.email._send", lambda *args, **kwargs: None)


@pytest.fixture(autouse=True)
def _clean_db():
    yield
    with Session(_engine) as s:
        for t in _TABLES:
            s.exec(text(f"TRUNCATE {t} CASCADE"))
        s.commit()


@pytest.fixture(name="session")
def session_fixture():
    with Session(_engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def override():
        yield session

    app.dependency_overrides[get_session] = override
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def vet(session: Session) -> Vet:
    v = Vet(email="vet@test.com", hashed_password=hash_password("secret"), full_name="Dr. Test")
    session.add(v)
    session.commit()
    session.refresh(v)
    return v


@pytest.fixture
def vet_headers(vet: Vet) -> dict[str, str]:
    token = create_access_token(vet.id, "vet")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def owner(session: Session, vet: Vet) -> Owner:
    o = Owner(
        email="owner@test.com",
        hashed_password=hash_password("ownerpass"),
        full_name="Jane Owner",
        status=OwnerStatus.active.value,
        supervising_vet_id=vet.id,
    )
    session.add(o)
    session.commit()
    session.refresh(o)
    return o


@pytest.fixture
def owner_headers(owner: Owner) -> dict[str, str]:
    token = create_access_token(owner.id, "owner")
    return {"Authorization": f"Bearer {token}"}
