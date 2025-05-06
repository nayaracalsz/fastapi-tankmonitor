from http.client import responses

from fastapi.testclient import TestClient

from app.main import app
from app.middleware.auth import create_access_token

client = TestClient(app)


def test_generate_token():
    response = client.post("/test/token-example")
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "token_type" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_protected_route_with_valid_token():
    token = create_access_token({"sub": "test@example.com"})
    response = client.get(
        "/test/token-check", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Valid token"


def test_protected_route_with_invalid_token():
    response = client.get(
        "/test/token-check", headers={"Authorization": "Bearer invalid.token.value"}
    )
    assert response.status_code == 403
    assert "Invalid" in response.json()["detail"]


def test_protected_route_without_token():
    response = client.get("/test/token-check")
    assert response.status_code == 403
    assert "detail" in response.json()
