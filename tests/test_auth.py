from fastapi.testclient import TestClient


def test_health(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_register_sets_cookie(client: TestClient) -> None:
    response = client.post(
        "/api/auth/register",
        json={"email": "user@example.com", "password": "secret123", "full_name": "User"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "user@example.com"
    assert data["full_name"] == "User"
    assert "id" in data
    assert "access_token" in response.cookies


def test_register_duplicate_email(client: TestClient) -> None:
    payload = {"email": "dup@example.com", "password": "secret123"}
    assert client.post("/api/auth/register", json=payload).status_code == 201
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"


def test_login_success(client: TestClient) -> None:
    client.post(
        "/api/auth/register",
        json={"email": "login@example.com", "password": "secret123"},
    )
    client.cookies.clear()

    response = client.post(
        "/api/auth/login",
        json={"email": "login@example.com", "password": "secret123"},
    )
    assert response.status_code == 200
    assert response.json()["email"] == "login@example.com"
    assert "access_token" in response.cookies


def test_login_wrong_password(client: TestClient) -> None:
    client.post(
        "/api/auth/register",
        json={"email": "wrongpass@example.com", "password": "secret123"},
    )
    response = client.post(
        "/api/auth/login",
        json={"email": "wrongpass@example.com", "password": "bad-password"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"


def test_me_requires_auth(client: TestClient) -> None:
    response = client.get("/api/auth/me")
    assert response.status_code == 401


def test_me_returns_current_user(auth_client: TestClient) -> None:
    response = auth_client.get("/api/auth/me")
    assert response.status_code == 200
    assert response.json()["email"] == "owner@example.com"


def test_logout_clears_session(auth_client: TestClient) -> None:
    assert auth_client.get("/api/auth/me").status_code == 200

    logout = auth_client.post("/api/auth/logout")
    assert logout.status_code == 200
    assert logout.json()["message"] == "Logged out"

    auth_client.cookies.clear()
    assert auth_client.get("/api/auth/me").status_code == 401
