import re
from datetime import datetime
from typing import Optional

from firebase_admin import firestore
from google.cloud.firestore_v1 import FieldFilter
from pydantic import BaseModel, EmailStr, field_validator

db = firestore.client()

class UserBase(BaseModel):
    email: EmailStr
    name: str
    is_active: bool = True
    created_at: Optional[datetime] = None

    @field_validator('name')
    @classmethod
    def validate_name(cls, value):
        if not value or not value.strip():
            raise ValueError('The name cannot be empty')
        if len(value.strip()) < 2:
            raise ValueError('The name must have at least 2 characters')
        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚ\s]+$', value):
            raise ValueError('The name can only contain letters and spaces')
        return value

class UserCreate(UserBase):
    password: str

class UserFirestore(UserBase):
    uid: str
    token_version: int = 0
    last_login: Optional[datetime] = None

    @classmethod
    def get_by_email(cls, email: EmailStr) -> Optional["UserFirestore"]:
        query = db.collection("users").where(filter=FieldFilter("email", "==", email)).limit(1).get()
        return cls(**query[0].to_dict()) if query else None

    @classmethod
    def get_by_uid(cls, uid: str) -> Optional["UserFirestore"]:
        doc = db.collection("users").document(uid).get()
        return cls(**doc.to_dict()) if doc.exists else None

    def save(self):
        user_data = self.model_dump()
        user_data["created_at"] = firestore.SERVER_TIMESTAMP
        db.collection("users").document(self.uid).set(user_data, merge=True)

class UserPublic(UserBase):
    uid: str