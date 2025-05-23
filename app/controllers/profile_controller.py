from fastapi import APIRouter, Depends, Request

from app.middleware import JWTBearer, decodeJWT

router = APIRouter(prefix="/profile", tags=["Profile"])


@router.get("/me", dependencies=[Depends(JWTBearer())])
async def get_profile(request: Request):
    token = request.headers.get("Authorization").split(" ")[1]
    payload = decodeJWT(token)
    return {
        "uid": payload["uid"],
        "email": payload["email"],
        "token_version": payload["token_version"],
        "exp": payload["exp"],
    }
