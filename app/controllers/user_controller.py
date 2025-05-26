from fastapi import APIRouter, HTTPException, Request, status

from app.firebase.firebase import db
from app.middleware.jwt_handler import decodeJWT
from app.models.user_model import UserFirestore
from app.schemas.user_schema import UpdateRoleRequest, UserResponse

router = APIRouter(prefix="/users", tags=["User Management"])


@router.get("/", response_model=list[UserResponse])
def get_all_users(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Authorization header missing or invalid.",
        )

    token = auth_header.split("Bearer ")[1]
    payload = decodeJWT(token)

    requester = UserFirestore.get_by_uid(payload.get("sub"))
    if not requester or requester.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view all users.",
        )

    docs = db.collection("users").stream()
    users = []
    for doc in docs:
        data = doc.to_dict()
        users.append(
            UserResponse(uid=doc.id, email=data.get("email"), role=data.get("role"))
        )

    return users


@router.put("/{uid}/role")
def update_user_role(uid: str, request: Request, body: UpdateRoleRequest):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Authorization header missing or invalid.",
        )

    token = auth_header.split("Bearer ")[1]
    payload = decodeJWT(token)

    requester = UserFirestore.get_by_uid(payload.get("sub"))
    if not requester or requester.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update user roles.",
        )

    target_user = UserFirestore.get_by_uid(uid)
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    target_user.role = body.role
    target_user.save()

    return {
        "message": f"User role updated successfully to '{body.role}' for user {uid}."
    }
