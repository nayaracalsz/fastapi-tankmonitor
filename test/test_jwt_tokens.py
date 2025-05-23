from datetime import timedelta

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from app.middleware.jwt_handler import JWTBearer, create_access_token, decodeJWT


def test_token_creation_and_verification():
    token = create_access_token({"sub": "test@example.com"})
    payload = decodeJWT(token)
    assert payload["sub"] == "test@example.com"


def test_expired_token():
    token = create_access_token({"sub": "test"}, timedelta(seconds=-1))
    with pytest.raises(Exception) as exc:
        decodeJWT(token)
    assert "expired" in str(exc.value.detail.lower())


def test_jwt_bearer_invalid_scheme():
    bearer = JWTBearer()
    with pytest.raises(HTTPException) as exc:
        bearer._validate_credentials(
            HTTPAuthorizationCredentials(scheme="Basic", credentials="xxx")
        )
    assert "Invalid authentication scheme." in str(exc.value.detail)
