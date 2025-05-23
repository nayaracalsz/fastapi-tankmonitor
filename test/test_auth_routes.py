from uuid import uuid4

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from firebase_admin import auth, firestore

from app.firebase.firebase import db
from app.main import app

db = firestore.client()


def test_register_user(client):
    email = f"test_{uuid4()}@example.com"
    user_data = {
        "email": email,
        "password": "SecurePass123!",
        "name": "Test User",
    }

    response = client.post("/auth/register", json=user_data)
    assert response.status_code == status.HTTP_200_OK
    assert "uid" in response.json()

    uid = response.json()["uid"]

    try:
        user = auth.get_user(uid)
        assert user.email == user_data["email"]
        assert user.display_name == user_data["name"]
    except auth.UserNotFoundError:
        pytest.fail("User not found in Firebase Auth")

    doc = db.collection("users").document(uid).get()
    assert doc.exists
    assert doc.to_dict()["email"] == user_data["email"]
    assert "password" not in doc.to_dict()


def test_weak_password_validation(client):
    response = client.post(
        "/auth/register",
        json={"email": "weakpass@example.com", "password": "123", "name": "Weak User"},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    detail = response.json().get("detail", [])

    assert any(
        "8 characters" in err.get("msg", "") or "uppercase" in err.get("msg", "")
        for err in detail
    )


def test_duplicate_email(client):
    email = f"duplicate_{uuid4()}@example.com"
    user_data = {"email": email, "password": "Pass123!", "name": "User Dup"}

    response1 = client.post("/auth/register", json=user_data)
    assert response1.status_code == status.HTTP_200_OK

    response2 = client.post("/auth/register", json=user_data)
    assert response2.status_code == status.HTTP_409_CONFLICT
    assert "already exists" in response2.json().get("detail", "").lower()


def test_login_with_correct_credentials(client):
    email = f"login_{uuid4()}@example.com"
    password = "LoginPass123!"
    name = "Login Test"

    client.post(
        "/auth/register", json={"email": email, "password": password, "name": name}
    )

    response = client.post("/auth/login", json={"email": email, "password": password})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == email


def test_login_with_wrong_password(client):
    email = f"wrongpass_{uuid4()}@example.com"
    password = "Correct123!"
    name = "Wrong Pass"

    client.post(
        "/auth/register", json={"email": email, "password": password, "name": name}
    )

    response = client.post(
        "/auth/login", json={"email": email, "password": "WrongPass"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "invalid credentials" in response.json()["detail"].lower()
