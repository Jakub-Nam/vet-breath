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


def test_password_reset_is_role_scoped(client: TestClient, vet, owner):
    """A reset token for the owner must not touch a vet sharing the same id.

    In a freshly-truncated DB the first vet and first owner both get id=1
    (independent sequences), so the old id-only lookup reset the wrong account.
    """
    from app.core.security import create_password_reset_token

    assert vet.id == owner.id  # the collision precondition this test guards

    token = create_password_reset_token(owner.id, "owner")
    r = client.post("/auth/password-reset", json={"token": token, "new_password": "brandnew"})
    assert r.status_code == 200

    # Owner password changed to the new one...
    assert client.post("/auth/login", json={"email": "owner@test.com", "password": "brandnew"}).status_code == 200
    # ...and the vet with the same id was left untouched.
    assert client.post("/auth/login", json={"email": "vet@test.com", "password": "secret"}).status_code == 200


def test_password_reset_rejects_invitation_token(client: TestClient, owner):
    """An invitation token (type='invitation') must not be accepted at /password-reset."""
    from app.core.security import create_invitation_token

    token = create_invitation_token(owner.id)
    r = client.post("/auth/password-reset", json={"token": token, "new_password": "x"})
    assert r.status_code == 400
