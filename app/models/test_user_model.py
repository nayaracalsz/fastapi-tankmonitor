from pydantic import BaseModel

class MockUser(BaseModel):
    id: int = 1
    email: str = "test@example.com"
    is_active: bool = True

mock_users_db = {
    "test@example.com": {
        "id": 1,
        "password": "$2y$10$bjfc3URdRHMWfJJSj8a0cOTj1iySxMNDy6Q6X..vjESatSN.yaGL2"
    }
}