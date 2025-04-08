from pydantic import BaseModel, Field


class TokenResquest(BaseModel):
    sub: str = "test@example.com"
    role: str = "admin"
    permissions: list[str] = Field(default_factory=lambda: ["read", "write", "delete"])