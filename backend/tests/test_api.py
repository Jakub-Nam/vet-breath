from fastapi.testclient import TestClient


def test_health(client: TestClient):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


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
