def test_register_creates_user_and_returns_token(client):
    resp = client.post("/auth/register", json={
        "name": "Jane Doe", "email": "jane@example.com", "password": "secret123",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["access_token"]
    assert data["user"]["email"] == "jane@example.com"


def test_register_duplicate_email_rejected(client):
    payload = {"name": "Jane", "email": "dupe@example.com", "password": "secret123"}
    client.post("/auth/register", json=payload)
    resp = client.post("/auth/register", json=payload)
    assert resp.status_code == 400


def test_login_success(client):
    client.post("/auth/register", json={
        "name": "Jane", "email": "login@example.com", "password": "secret123",
    })
    resp = client.post("/auth/login", json={"email": "login@example.com", "password": "secret123"})
    assert resp.status_code == 200
    assert resp.json()["access_token"]


def test_login_wrong_password_rejected(client):
    client.post("/auth/register", json={
        "name": "Jane", "email": "wrongpw@example.com", "password": "secret123",
    })
    resp = client.post("/auth/login", json={"email": "wrongpw@example.com", "password": "nope"})
    assert resp.status_code == 401


def test_me_requires_auth(client):
    resp = client.get("/auth/me")
    assert resp.status_code in (401, 403)


def test_me_with_valid_token(client, auth_headers):
    resp = client.get("/auth/me", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["email"] == "test@example.com"
