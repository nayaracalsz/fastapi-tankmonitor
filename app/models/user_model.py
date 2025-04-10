from datetime import datetime
from typing import Optional

from firebase_admin import firestore
from pydantic import BaseModel, EmailStr

db = firestore.client()

class UserBase(BaseModel):
    email: EmailStr
    name: str
    is_active: bool = True
    created_at: datetime = datetime.now()

class UserCreate(UserBase):
    password: str

class UserFirestore(UserBase):
    uid: str
    token_version: int = 0
    last_login: Optional[datetime] = None

    def get_by_uid(cls, uid: str) -> Optional["UserFirestore"]:
        doc = db.collection("users").document(uid).get()
        return cls(**doc.model_dump()) if doc.exists else None

    def save(self):
        user_data = self.model_dump()
        user_data["create_at"] = firestore.SERVER_TIMESTAMP
        db.collection("users").document(self.uid).set(user_data, merge=True)

class UserPublic(UserBase):
    uid: str