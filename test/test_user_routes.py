from fastapi.testclient import TestClient
from app.main import app
from app.models.test_user_model import MockUser
from app.core.middleware.mock_auth import get_current_mock_user

def override_get_current_user():
    return MockUser()

app.dependency_overrides[get_current_mock_user] = override_get_current_user

client = TestClient(app)

def test_access_mock_protected_route():
    response = client.get("/test/mock-protected")
    assert response.status_code == 200
    assert response.json()["user_data"]["email"] == "test@example.com"
