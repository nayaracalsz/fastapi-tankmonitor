import re

from pydantic import EmailStr


def required_field(value: str, field_name: str = "Field") -> str:
    if not value or not value.strip():
        raise ValueError(f"{field_name} is required")
    return value.strip()


def normalize_email(value: EmailStr) -> str:
    return required_field(value, "Email").lower()


def validate_name(value: str) -> str:
    value = required_field(value, "Name")
    if not value or not value.strip():
        raise ValueError("The name cannot be empty")
    if len(value.strip()) < 2:
        raise ValueError("The name must have at least 2 characters")
    if not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚ\s]+$", value):
        raise ValueError("The name can only contain letters and spaces")
    return value


def validate_password(value: str) -> str:
    value = required_field(value, "Password")
    errors = []
    if len(value) < 8:
        errors.append("Must be at least 8 characters")
    if not re.search(r"[A-Z]", value):
        errors.append("Must contain at least one uppercase letter")
    if not re.search(r"[a-z]", value):
        errors.append("Must contain at least one lowercase letter")
    if not re.search(r"\d", value):
        errors.append("Must contain at least one number")
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
        errors.append("Must contain at least one special character")

    if errors:
        raise ValueError(" | ".join(errors))

    return value
