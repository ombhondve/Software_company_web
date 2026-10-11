def test_register_success(client):
    r = client.post("/users/register", json={"email": "A@Example.com", "password": "password123"})
    assert r.status_code == 201
    body = r.json()
    assert body["email"] == "a@example.com"
    assert "password" not in body and "password_hash" not in body


def test_register_duplicate_email(client):
    payload = {"email": "dup@example.com", "password": "password123"}
    assert client.post("/users/register", json=payload).status_code == 201
    assert client.post("/users/register", json=payload).status_code == 409


def test_register_invalid_payload_returns_400(client):
    r = client.post("/users/register", json={"email": "not-an-email", "password": "short"})
    assert r.status_code == 400


def test_register_missing_fields_returns_400(client):
    assert client.post("/users/register", json={}).status_code == 400


def test_login_success_returns_jwt(client):
    client.post("/users/register", json={"email": "u@example.com", "password": "password123"})
    r = client.post("/users/login", json={"email": "u@example.com", "password": "password123"})
    assert r.status_code == 200
    assert r.json()["token_type"] == "bearer"
    assert r.json()["access_token"]


def test_login_wrong_password(client):
    client.post("/users/register", json={"email": "u@example.com", "password": "password123"})
    r = client.post("/users/login", json={"email": "u@example.com", "password": "wrongpass"})
    assert r.status_code == 401


def test_login_unknown_user(client):
    r = client.post("/users/login", json={"email": "no@example.com", "password": "password123"})
    assert r.status_code == 401


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}
