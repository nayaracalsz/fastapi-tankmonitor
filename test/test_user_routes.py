from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)

def test_register_user():
    response = client.post("/auth/register", json={
        "email": "test@example.com",
        "password": "123456",
        "name": "test user",
    })
    print(response.json())
    assert response.status_code == 200
    assert "uid" in response.json()