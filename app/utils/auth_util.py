from fastapi import HTTPException, Request, status

from app.middleware.jwt_handler import decodeJWT
from app.models.user_model import UserFirestore


def get_user_from_request(request: Request) -> UserFirestore:
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing or invalid token."
        )

    token = auth_header.split("Bearer ")[1]
    payload = decodeJWT(token)

    user = UserFirestore.get_by_uid(payload.get("sub"))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found."
        )

    return user
