import re
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


class ShitfEnum(str, Enum):
    matutino = "Matutino"
    vespertino = "Vespertino"
    nocturno = "Nocturno"


class UnitRecordCreate(BaseModel):
    unit_id: str
    operator_name: str
    shift: ShitfEnum
    last_trip: Optional[str]
    replaced_part: Optional[str]
    mileage: float
    rpm: int
    registered_email: EmailStr

    @field_validator("unit_id")
    @classmethod
    def validate_unit_id_format(cls, v):
        if not re.fullmatch(r"PMX\d{6}", v):
            raise ValueError(
                "unit_id must start with 'PMX' followed by exactly 6 digits"
            )
        return v


class UnitRecordResponse(UnitRecordCreate):
    id: str
    created_at: datetime
    registered_by: str
