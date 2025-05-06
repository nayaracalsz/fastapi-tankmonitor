import re
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, field_validator


class UserBase(BaseModel):
    email: EmailStr
    name: str
    is_active: bool = True
    created_at: Optional[datetime] = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value):
        if not value or not value.strip():
            raise ValueError("The name cannot be empty")
        if len(value.strip()) < 2:
            raise ValueError("The name must have at least 2 characters")
        if not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚ\s]+$", value):
            raise ValueError("The name can only contain letters and spaces")
        return value


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    uid: str
