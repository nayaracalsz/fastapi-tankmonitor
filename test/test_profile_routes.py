from fastapi import status


def test_profile_with_valid_token(client, auth_token):
    response = client.get(
        "/profile/me", headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "uid" in data
    assert "email" in data
    assert "token_version" in data
    assert "exp" in data


def test_profile_with_invalid_token(client):
    response = client.get(
        "/profile/me", headers={"Authorization": "Bearer invalid.token.value"}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "Invalid or expired token" in response.json()["detail"]


def test_profile_without_token(client):
    response = client.get("/profile/me")
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == "Not authenticated"
