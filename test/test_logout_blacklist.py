from fastapi import status

from app.services.token_blacklist import add_token_to_blacklist, is_token_blacklisted


def test_logout_revokes_token(client, auth_token):
    token, jti = auth_token["token"], auth_token["jti"]

    assert is_token_blacklisted(jti) is False

    response = client.post("/auth/logout", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Logout successful."

    assert is_token_blacklisted(jti) is True


def test_revoked_token_cannot_access_protected_route(client, auth_token):
    token, jti, exp = auth_token["token"], auth_token["jti"], auth_token["exp"]

    add_token_to_blacklist(jti, exp)

    response = client.get("/profile/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert (
        "revoked" in response.json()["detail"].lower()
        or "invalid" in response.json()["detail"].lower()
    )
