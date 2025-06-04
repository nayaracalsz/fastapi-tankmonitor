from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from firebase_admin import firestore

from app.dependencies.roles import requires_role
from app.firebase.firebase import db
from app.schemas.unit_record_schema import UnitRecordCreate, UnitRecordResponse
from app.utils.auth_util import get_user_from_request
from app.utils.datetime_util import parse_firestore_timestamp
from app.utils.email_utils import send_email_notification
from app.utils.handlers import handle_exceptions

router = APIRouter(prefix="/units", tags=["Unit Records"])


@router.get("/")
@handle_exceptions()
async def get_all_unit_records(request: Request):
    current_user = get_user_from_request(request)
    query = db.collection("unit_records")

    if current_user.role != "admin":
        query = query.where(
            field_path="registered_by", op_string="==", value=current_user.uid
        )

    docs = query.order_by("created_at", direction=firestore.Query.DESCENDING).get()

    records = []
    for doc in docs:
        data = doc.to_dict()
        data.pop("id", None)
        # print(f"DATA DEL DOCUMENTO: {data}")
        data["created_at"] = parse_firestore_timestamp(data["created_at"])
        records.append(UnitRecordResponse(id=doc.id, **data))

    return records


@router.get("/{record_id}", response_model=UnitRecordResponse)
@handle_exceptions()
async def get_unit_record_by_id(record_id: str, request: Request):
    current_user = get_user_from_request(request)

    doc_ref = db.collection("unit_records").document(record_id)
    doc = doc_ref.get()

    if not doc.exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Record not found"
        )

    data = doc.to_dict()

    if current_user.role != "admin" and data["registered_by"] != current_user.uid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to this record"
        )

    data.pop("id", None)
    return UnitRecordResponse(id=doc.id, **data)


@router.post("/add", response_model=UnitRecordResponse)
@handle_exceptions()
async def create_unit_record(record: UnitRecordCreate, request: Request):
    current_user = get_user_from_request(request)

    new_doc_ref = db.collection("unit_records").document()

    created_data = {
        **record.model_dump(),
        "id": new_doc_ref.id,
        "created_at": datetime.now(timezone.utc),
        "registered_by": current_user.uid,
    }

    new_doc_ref.set(created_data)

    # Intentar enviar el correo de notificación
    try:
        send_email_notification(
            to=record.registered_email,
            subject="New Unit Record Created",
            body=(
                f"Hello,\n\nYour unit record (ID: {created_data['id']}) has been successfully registered "
                f"on {created_data['created_at'].strftime('%Y-%m-%d %H:%M:%S')} UTC.\n\n"
                "Thank you for using TankMonitor!"
            ),
        )
    except Exception as e:
        print(f"[ERROR] Failed to send email: {e}")

    return UnitRecordResponse(**created_data)


@router.put("/edit/{record_id}", response_model=UnitRecordResponse)
@requires_role("admin")
@handle_exceptions()
async def update_unit_record(
    record_id: str, updated_record: UnitRecordCreate, request: Request
):
    current_user = get_user_from_request(request)

    doc_ref = db.collection("unit_records").document(record_id)
    doc = doc_ref.get()

    if not doc.exists:
        raise HTTPException(status_code=404, detail="Record not found")

    data = {
        **updated_record.model_dump(),
        "registered_by": current_user.uid,
        "created_at": datetime.now(timezone.utc),
    }

    doc_ref.update(data)

    return UnitRecordResponse(id=record_id, **data)


@router.delete("/delete/{record_id}")
@requires_role("admin")
@handle_exceptions()
async def delete_unit_record(record_id: str, request: Request):

    doc_ref = db.collection("unit_records").document(record_id)
    doc = doc_ref.get()

    if not doc.exists:
        raise HTTPException(status_code=404, detail="Record not found")

    doc_ref.delete()

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"detail": "Record deleted successfully"},
    )
