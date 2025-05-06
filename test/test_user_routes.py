import pytest
from fastapi.testclient import TestClient
from firebase_admin import auth

from app.firebase.firebase import db
from app.main import app

client = TestClient(app)


def test_register_user():
    # Test data
    user_data = {
        "email": "test_register@example.com",
        "password": "SecurePass123!",
        "name": "Test User",
    }

    # Calls the endpoint
    response = client.post("/auth/register", json=user_data)
    assert response.status_code == 200
    assert "uid" in response.json()

    uid = response.json()["uid"]

    # Checks if exists in Firebase Auth
    try:
        user = auth.get_user(uid)
        assert user.email == user_data["email"]
        assert user.display_name == user_data["name"]
    except auth.UserNotFoundError:
        pytest.fail("User not found in Firebase Auth")

    # Checks metadata in Firestore
    doc = db.collection("users").document(uid).get()
    assert doc.exists
    assert doc.to_dict()["email"] == user_data["email"]
    assert "password" not in doc.to_dict()


def test_weak_password():
    response = client.post(
        "/auth/register",
        json={"email": "test2@example.com", "password": "123", "name": "Test User"},
    )
    assert response.status_code == 422
    response_data = response.json()

    assert any(
        "8 characters" in error or "uppercase" in error or "number" in error
        for error in response_data.get("detail", {}).get("errors", [])
    )


def test_duplicate_email():
    user_data = {"email": "dup@example.com", "password": "Pass123!", "name": "Test"}
    response1 = client.post("/auth/register", json=user_data)
    assert response1.status_code == 200

    response2 = client.post("/auth/register", json=user_data)
    assert response2.status_code == 400
    assert "already registered" in response2.json().get("detail", "").lower()
