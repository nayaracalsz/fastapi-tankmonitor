from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import re
import json


async def password_complexity_middleware(request: Request, call_next):
    if request.method == "POST" and "/auth/" in request.url.path:
        try:
            body = await request.json()
        except json.JSONDecodeError:
            return JSONResponse(
                status_code=400,
                content={"detail": "Invalid JSON body"}
            )

        password = body.get('password', '')

        errors = []
        if len(password) < 8:
            errors.append("Must be at least 8 characters")
        if not re.search(r"[A-Z]", password):
            errors.append("Must contain at least one uppercase letter")
        if not re.search(r"[a-z]", password):
            errors.append("Must contain at least one lowercase letter")
        if not re.search(r"\d", password):
            errors.append("Must contain at least one number")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            errors.append("Must contain at least one special character")

        if errors:
            raise HTTPException(
                status_code=422,  # Unprocessable Entity
                detail={
                    "type": "password_validation",
                    "errors": errors
                }
            )

    return await call_next(request)