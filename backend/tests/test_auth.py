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


def test_delete_vet_account_removes_clients_and_data(
    client: TestClient, vet, owner, session, vet_headers
):
    """Deleting a vet account cascades to its clients, dogs, readings, and notes."""
    from app.models.dog import Dog
    from app.models.note import Note
    from app.models.owner import Owner as OwnerModel
    from app.models.reading import Reading
    from app.models.vet import Vet as VetModel

    dog = Dog(name="Rex", breed="Labrador", age=3, owner_id=owner.id)
    session.add(dog)
    session.commit()
    session.refresh(dog)
    session.add(Reading(dog_id=dog.id, bpm=42, recommendation="go_to_vet"))
    session.add(Note(dog_id=dog.id, vet_id=vet.id, body="Keep watching"))
    session.commit()

    vet_id, owner_id, dog_id = vet.id, owner.id, dog.id

    response = client.delete("/auth/me", headers=vet_headers)
    assert response.status_code == 204

    assert session.get(VetModel, vet_id) is None
    assert session.get(OwnerModel, owner_id) is None
    assert session.get(Dog, dog_id) is None


def test_delete_account_requires_auth(client: TestClient):
    # No credentials → 401 Unauthorized (403 is reserved for an authenticated
    # user with the wrong role, e.g. get_current_vet).
    assert client.delete("/auth/me").status_code == 401
