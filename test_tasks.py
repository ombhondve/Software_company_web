def test_tasks_require_auth(client):
    assert client.get("/tasks").status_code == 401
    assert client.post("/tasks", json={"title": "x"}).status_code == 401
    assert client.put("/tasks/1", json={"title": "x"}).status_code == 401
    assert client.delete("/tasks/1").status_code == 401


def test_invalid_token_rejected(client):
    r = client.get("/tasks", headers={"Authorization": "Bearer nope"})
    assert r.status_code == 401


def test_token_for_deleted_user_rejected(client):
    from app.security import create_access_token

    r = client.get("/tasks", headers={"Authorization": f"Bearer {create_access_token(9999)}"})
    assert r.status_code == 401


def test_create_and_list_tasks(client, auth_headers):
    h = auth_headers()
    r = client.post("/tasks", json={"title": "Write tests", "description": "pytest"}, headers=h)
    assert r.status_code == 201
    assert r.json()["completed"] is False
    r = client.get("/tasks", headers=h)
    assert r.status_code == 200
    assert [t["title"] for t in r.json()] == ["Write tests"]


def test_create_task_invalid_payload_returns_400(client, auth_headers):
    h = auth_headers()
    assert client.post("/tasks", json={"title": ""}, headers=h).status_code == 400
    assert client.post("/tasks", json={}, headers=h).status_code == 400


def test_update_task(client, auth_headers):
    h = auth_headers()
    tid = client.post("/tasks", json={"title": "Old"}, headers=h).json()["id"]
    r = client.put(f"/tasks/{tid}", json={"title": "New", "completed": True}, headers=h)
    assert r.status_code == 200
    assert r.json()["title"] == "New"
    assert r.json()["completed"] is True


def test_update_missing_task_404(client, auth_headers):
    h = auth_headers()
    assert client.put("/tasks/999", json={"title": "x"}, headers=h).status_code == 404


def test_delete_task(client, auth_headers):
    h = auth_headers()
    tid = client.post("/tasks", json={"title": "Temp"}, headers=h).json()["id"]
    assert client.delete(f"/tasks/{tid}", headers=h).status_code == 204
    assert client.get("/tasks", headers=h).json() == []
    assert client.delete(f"/tasks/{tid}", headers=h).status_code == 404


def test_users_cannot_access_each_others_tasks(client, auth_headers):
    h1 = auth_headers("one@example.com")
    h2 = auth_headers("two@example.com")
    tid = client.post("/tasks", json={"title": "Private"}, headers=h1).json()["id"]

    assert client.get("/tasks", headers=h2).json() == []
    assert client.put(f"/tasks/{tid}", json={"title": "Hack"}, headers=h2).status_code == 404
    assert client.delete(f"/tasks/{tid}", headers=h2).status_code == 404
    assert client.get("/tasks", headers=h1).json()[0]["title"] == "Private"
