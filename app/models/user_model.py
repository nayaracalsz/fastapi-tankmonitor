from datetime import datetime
from typing import Optional

from firebase_admin import firestore
from google.cloud.firestore_v1 import FieldFilter
from pydantic import EmailStr

from app.schemas.user_schema import UserBase

db = firestore.client()


class UserFirestore(UserBase):
    uid: str
    token_version: int = 0
    last_login: Optional[datetime] = None

    @classmethod
    def get_by_email(cls, email: EmailStr) -> Optional["UserFirestore"]:
        query = (
            db.collection("users")
            .where(filter=FieldFilter("email", "==", email))
            .limit(1)
            .get()
        )
        return cls(**query[0].to_dict()) if query else None

    @classmethod
    def get_by_uid(cls, uid: str) -> Optional["UserFirestore"]:
        doc = db.collection("users").document(uid).get()
        return cls(**doc.to_dict()) if doc.exists else None

    def save(self):
        user_data = self.model_dump()
        user_data["created_at"] = firestore.SERVER_TIMESTAMP
        db.collection("users").document(self.uid).set(user_data, merge=True)

    def update_last_login(self):
        db.collection("users").document(self.uid).update(
            {"last_login": firestore.SERVER_TIMESTAMP}
        )
