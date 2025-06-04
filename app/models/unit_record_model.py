import datetime
from uuid import uuid4

from firebase_admin import firestore

from app.firebase.firebase import db


class UnitRecordModel:
    def __init__(self, data: dict, user):
        self.id = str(uuid4())
        self.unit_number = data["unit_number"]
        self.operator_name = data["operator_name"]
        self.shift = data["shift"]
        self.last_trip = data.get("last_trip")
        self.replaced_part = data.get("replaced_part")
        self.mileage = data["mileage"]
        self.rpm = data["rpm"]
        self.created_at = firestore.SERVER_TIMESTAMP
        self.registered_by = user.sub
        self.registered_email = user.email

    def to_dict(self):
        return {
            "unit_number": self.unit_number,
            "operator_name": self.operator_name,
            "shift": self.shift,
            "last_trip": self.last_trip,
            "replaced_part": self.replaced_part,
            "mileage": self.mileage,
            "rpm": self.rpm,
            "created_at": self.created_at,
            "registered_by": self.registered_by,
            "registered_email": self.registered_email,
        }

    def save(self):
        db.collection("unit_records").document(self.id).set(self.to_dict())
        return self.id
