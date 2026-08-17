from fastapi.testclient import TestClient


def test_register_vet(client: TestClient):
    r = client.post("/auth/register", json={"email": "new@vet.com", "password": "pass123", "full_name": "Dr. New"})
    assert r.status_code == 201
    data = r.json()
    assert data["email"] == "new@vet.com"
    assert data["full_name"] == "Dr. New"
    assert "id" in data


def test_register_duplicate_email(client: TestClient, vet):
    r = client.post("/auth/register", json={"email": "vet@test.com", "password": "x"})
    assert r.status_code == 409


def test_login_vet(client: TestClient, vet):
    r = client.post("/auth/login", json={"email": "vet@test.com", "password": "secret"})
    assert r.status_code == 200
    assert "access_token" in r.json()


def test_login_wrong_password(client: TestClient, vet):
    r = client.post("/auth/login", json={"email": "vet@test.com", "password": "wrong"})
    assert r.status_code == 401


def test_login_owner(client: TestClient, owner):
    r = client.post("/auth/login", json={"email": "owner@test.com", "password": "ownerpass"})
    assert r.status_code == 200
    assert "access_token" in r.json()


def test_accept_invitation(client: TestClient, vet, session):
    from app.models.enums import OwnerStatus
    from app.models.owner import Owner
    from app.core.security import create_invitation_token

    o = Owner(
        email="pending@test.com",
        status=OwnerStatus.pending.value,
        supervising_vet_id=vet.id,
    )
    session.add(o)
    session.commit()
    session.refresh(o)

    token = create_invitation_token(o.id)
    r = client.post("/auth/accept-invitation", json={"token": token, "password": "newpass"})
    assert r.status_code == 200
    assert "access_token" in r.json()

    session.refresh(o)
    assert o.status == OwnerStatus.active.value
