# 🧪 Backend Test Suite

This folder contains all the backend tests for the project, including:

- Authentication (register, login, token verification)
- Protected routes (e.g., user profile)
- Token generation and validation
- Any future feature modules...

## 📁 Folder Structure

| File                     | Description                                             |
| ------------------------ | ------------------------------------------------------- |
| `conftest.py`            | Shared test fixtures: `client`, `auth_token`, etc.      |
| `test_auth_routes.py`    | Tests for `/auth/register` and `/auth/login` endpoints. |
| `test_jwt_tokens.py`     | Unit tests for JWT creation, expiration, and decoding.  |
| `test_profile_routes.py` | Tests for the `/profile/me` route, protected with JWT.  |

Additional test files may be added as features are implemented.

## 🚀 Running Tests

Make sure your **virtual environment** is activated and all dependencies are installed.

### Install required packages

```bash
pip install -r requirements.txt
# or
pip install pytest httpx pytest-asyncio
```

### Run all tests

```bash
pytest test/
```

### Run a specific test file

```bash
pytest test/test_auth_routes.py
```

### Run a specific test function

```bash
pytest test/test_profile_routes.py::test_profile_me_with_valid_token
```
