import pytest
from fastapi.testclient import TestClient

from app.models.enums import OwnerStatus
from app.models.owner import Owner
from app.models.vet import Vet
from app.services.email import EmailSendError


def test_health(client: TestClient):
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert "version" in body


def test_invite_client(client: TestClient, vet_headers):
    r = client.post(
        "/vets/clients",
        json={"email": "newclient@test.com", "full_name": "New Client"},
        headers=vet_headers,
    )
    assert r.status_code == 201
    assert r.json()["status"] == "pending"
    assert r.json()["email"] == "newclient@test.com"


def test_invite_duplicate_client(client: TestClient, vet_headers, owner):
    r = client.post(
        "/vets/clients",
        json={"email": "owner@test.com"},
        headers=vet_headers,
    )
    assert r.status_code == 409


def test_add_dog(client: TestClient, owner_headers):
    r = client.post("/dogs", json={"name": "Rex", "breed": "Labrador", "age": 5}, headers=owner_headers)
    assert r.status_code == 201
    assert r.json()["name"] == "Rex"


def test_list_dogs_empty(client: TestClient, owner_headers):
    r = client.get("/dogs", headers=owner_headers)
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_create_reading(client: TestClient, owner_headers, owner, session):
    from app.models.dog import Dog

    dog = Dog(name="Buddy", breed="Beagle", age=3, owner_id=owner.id)
    session.add(dog)
    session.commit()
    session.refresh(dog)

    r = client.post("/readings", json={"dog_id": dog.id, "bpm": 45}, headers=owner_headers)
    assert r.status_code == 201
    assert r.json()["recommendation"] == "go_to_vet"
    assert r.json()["bpm"] == 45


def test_create_reading_wrong_dog(client: TestClient, owner_headers):
    r = client.post("/readings", json={"dog_id": 99999, "bpm": 30}, headers=owner_headers)
    assert r.status_code == 404


def test_panel(client: TestClient, vet_headers, owner, session):
    from app.models.dog import Dog
    from app.models.reading import Reading

    dog = Dog(name="Panel Dog", breed="Poodle", age=2, owner_id=owner.id)
    session.add(dog)
    session.commit()
    session.refresh(dog)

    reading = Reading(dog_id=dog.id, bpm=50, recommendation="go_to_vet")
    session.add(reading)
    session.commit()

    r = client.get("/vets/panel", headers=vet_headers)
    assert r.status_code == 200
    data = r.json()
    assert len(data["clients"]) >= 1
    assert any(d["name"] == "Panel Dog" and d["needs_attention"] for d in data["dogs"])


def test_readings_access_control(client: TestClient, vet_headers, owner, session):
    from app.models.dog import Dog

    dog = Dog(name="Access Dog", breed="Husky", age=1, owner_id=owner.id)
    session.add(dog)
    session.commit()
    session.refresh(dog)

    r = client.get(f"/readings?dog_id={dog.id}", headers=vet_headers)
    assert r.status_code == 200


def test_unauthenticated_request(client: TestClient):
    r = client.get("/vets/panel")
    assert r.status_code in (401, 403)


def _pending_client(session, vet: Vet) -> Owner:
    owner = Owner(
        email="pending@test.com",
        full_name="Pending Client",
        status=OwnerStatus.pending.value,
        supervising_vet_id=vet.id,
    )
    session.add(owner)
    session.commit()
    session.refresh(owner)
    return owner


def test_resend_invitation_pending(client: TestClient, vet_headers, vet, session):
    owner = _pending_client(session, vet)
    r = client.post(f"/vets/clients/{owner.id}/resend", headers=vet_headers)
    assert r.status_code == 200
    assert r.json()["status"] == "pending"
    assert r.json()["email"] == "pending@test.com"


def test_resend_invitation_already_active(client: TestClient, vet_headers, owner):
    # `owner` fixture is already active — nothing to resend.
    r = client.post(f"/vets/clients/{owner.id}/resend", headers=vet_headers)
    assert r.status_code == 409


def test_resend_invitation_unknown_client(client: TestClient, vet_headers):
    r = client.post("/vets/clients/9999/resend", headers=vet_headers)
    assert r.status_code == 404


def test_resend_invitation_other_vets_client(client: TestClient, session, vet):
    other_vet = Vet(email="other@test.com", hashed_password="x", full_name="Other")
    session.add(other_vet)
    session.commit()
    session.refresh(other_vet)
    owner = _pending_client(session, vet)  # belongs to `vet`, not `other_vet`

    from app.core.security import create_access_token

    headers = {"Authorization": f"Bearer {create_access_token(other_vet.id, 'vet')}"}
    r = client.post(f"/vets/clients/{owner.id}/resend", headers=headers)
    assert r.status_code == 404


def test_resend_invitation_email_failure_returns_502(
    client: TestClient, vet_headers, vet, session, monkeypatch
):
    owner = _pending_client(session, vet)
    monkeypatch.setattr(
        "app.services.email._send",
        lambda *args, **kwargs: (_ for _ in ()).throw(EmailSendError("boom")),
    )
    r = client.post(f"/vets/clients/{owner.id}/resend", headers=vet_headers)
    assert r.status_code == 502


def test_invite_email_failure_rolls_back(
    client: TestClient, vet_headers, session, monkeypatch
):
    monkeypatch.setattr(
        "app.services.email._send",
        lambda *args, **kwargs: (_ for _ in ()).throw(EmailSendError("boom")),
    )
    r = client.post(
        "/vets/clients",
        json={"email": "ghost@test.com", "full_name": "Ghost"},
        headers=vet_headers,
    )
    assert r.status_code == 502
    # The failed send must not leave an orphaned pending client behind.
    from sqlmodel import select

    remaining = session.exec(select(Owner).where(Owner.email == "ghost@test.com")).first()
    assert remaining is None
