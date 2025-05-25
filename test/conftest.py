import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.middleware.jwt_handler import create_access_token


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def auth_token():
    payload = {"sub": "test-user-uid", "email": "test@example.com", "token_version": 0}
    token, jti, exp = create_access_token(payload)
    return {"token": token, "jti": jti, "exp": exp}
