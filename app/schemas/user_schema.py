import re
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.schemas.validators import (
    normalize_email,
    required_field,
    validate_name,
    validate_password,
)


class UserBase(BaseModel):
    email: EmailStr
    name: str
    is_active: bool = True
    created_at: Optional[datetime] = None

    @field_validator("email")
    @classmethod
    def _normalize_email(cls, value):
        return normalize_email(value)

    @field_validator("name")
    @classmethod
    def _validate_name(cls, value):
        return validate_name(value)


class UserCreate(UserBase):
    password: str

    @field_validator("password")
    @classmethod
    def _validate_password(cls, value):
        return validate_password(value)


class UserResponse(UserBase):
    uid: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str

    @field_validator("email")
    @classmethod
    def _normalize_email(cls, value):
        return normalize_email(value)

    @field_validator("password")
    @classmethod
    def _validate_password(cls, v):
        return required_field(v, "Password")
