from fastapi import APIRouter, Depends, Request
from fastapi.security import HTTPAuthorizationCredentials

from app.middleware import decodeJWT
from app.middleware.jwt_handler import JWTBearer

router = APIRouter(prefix="/profile", tags=["Profile"])


@router.get("/me")
async def get_profile(
    request: Request, token: HTTPAuthorizationCredentials = Depends(JWTBearer())
):
    payload = decodeJWT(token)
    return {
        "uid": payload["sub"],
        "email": payload["email"],
        "token_version": payload["token_version"],
        "exp": payload["exp"],
    }
