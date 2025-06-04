from fastapi import APIRouter, HTTPException, Request, status

from app.firebase.firebase import db
from app.models.user_model import UserFirestore
from app.schemas.user_schema import UpdateRoleRequest, UserResponse
from app.utils.auth_util import get_user_from_request

router = APIRouter(prefix="/users", tags=["User Management"])


@router.get("/")
def get_all_users(request: Request):
    current_user = get_user_from_request(request)
    if not current_user or current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view all users.",
        )

    docs = db.collection("users").get()
    users = []
    for doc in docs:
        data = doc.to_dict()
        try:
            users.append(
                UserResponse(
                    uid=doc.id,
                    email=data["email"],
                    role=data["role"],
                    name=data["name"],
                    is_active=data["is_active"],
                    created_at=data["created_at"],
                )
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
            )

    return users


@router.put("/{uid}/role")
def update_user_role(uid: str, request: Request, body: UpdateRoleRequest):
    current_user = get_user_from_request(request)
    if not current_user or current_user.role != "admin":
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
