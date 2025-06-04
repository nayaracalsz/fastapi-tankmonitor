from datetime import datetime
from io import BytesIO

import pandas as pd
from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import JSONResponse, StreamingResponse

from app.dependencies.roles import requires_role
from app.firebase.firebase import db
from app.utils.auth_util import get_user_from_request
from app.utils.handlers import handle_exceptions

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats/total")
@requires_role("admin")
@handle_exceptions()
async def get_total_unit_records(request: Request):
    total = len(db.collection("unit_records").get())
    return JSONResponse(
        status_code=status.HTTP_200_OK, content={"total_records": total}
    )


from collections import defaultdict


@router.get("/stats/total/by-shift")
@requires_role("admin")
@handle_exceptions()
async def get_records_by_shift(request: Request):
    docs = db.collection("unit_records").get()
    by_shift = defaultdict(int)

    for doc in docs:
        data = doc.to_dict()
        shift = data.get("shift")
        if shift:
            by_shift[shift] += 1

    return JSONResponse(
        status_code=status.HTTP_200_OK, content={"records_by_shift": dict(by_shift)}
    )


@router.get("/stats/total/by-month")
@requires_role("admin")
@handle_exceptions()
async def get_records_by_month(request: Request):
    docs = db.collection("unit_records").get()
    by_month = defaultdict(int)

    for doc in docs:
        data = doc.to_dict()
        created_at = data.get("created_at")

        if created_at:
            if hasattr(created_at, "to_datetime"):
                created_at = created_at.to_datetime()
            if isinstance(created_at, datetime):
                month_name = created_at.strftime("%B")
                by_month[month_name] += 1

    return JSONResponse(
        status_code=status.HTTP_200_OK, content={"records_by_month": dict(by_month)}
    )


@router.get("/stats/avg-rpm")
@requires_role("admin")
@handle_exceptions()
async def get_average_rpm(request: Request):
    docs = db.collection("unit_records").get()
    total_rpm = 0
    count = 0

    for doc in docs:
        data = doc.to_dict()
        rpm = data.get("rpm")
        if isinstance(rpm, (int, float)):
            total_rpm += rpm
            count += 1

    avg_rpm = total_rpm / count if count > 0 else 0

    return JSONResponse(
        status_code=status.HTTP_200_OK, content={"average_rpm": round(avg_rpm, 2)}
    )


@router.get("/stats/total/by-user")
@requires_role("admin")
@handle_exceptions()
async def get_records_by_user(request: Request):
    docs = db.collection("unit_records").get()
    by_uid = defaultdict(int)

    for doc in docs:
        data = doc.to_dict()
        uid = data.get("registered_by")
        if uid:
            by_uid[uid] += 1

    user_emails = {}
    users = db.collection("users").get()
    for user_doc in users:
        user_data = user_doc.to_dict()
        uid = user_doc.id
        email = user_data.get("email")
        if email:
            user_emails[uid] = email

    result = {}
    for uid, count in by_uid.items():
        email = user_emails.get(uid, f"(unknown: {uid})")
        result[email] = count

    return JSONResponse(
        status_code=status.HTTP_200_OK, content={"records_by_user": result}
    )


@router.get("/export")
@requires_role("admin")
@handle_exceptions()
async def export_unit_records(request: Request, format: str = "xlsx"):
    docs = db.collection("unit_records").get()
    records = []

    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        if hasattr(data.get("created_at"), "to_datetime"):
            data["created_at"] = data["created_at"].to_datetime()

        if isinstance(data.get("created_at"), datetime):
            data["created_at"] = data["created_at"].replace(tzinfo=None)
        records.append(data)

    df = pd.DataFrame(records)

    if format == "csv":
        output = BytesIO()
        df.to_csv(output, index=False)
        output.seek(0)
        return StreamingResponse(
            output,
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=unit_records_{datetime.now().date()}.csv"
            },
        )
    elif format == "xlsx":
        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="UnitRecords")
        output.seek(0)
        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename=unit_records_{datetime.now().date()}.xlsx"
            },
        )
    else:
        raise HTTPException(
            status_code=400, detail="Format not supported. Use 'csv' or 'xlsx'."
        )
