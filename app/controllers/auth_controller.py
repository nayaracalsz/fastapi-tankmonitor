from fastapi import APIRouter
from fastapi.params import Depends, Body

from app.core.middleware import JWTBearer, decodeJWT, create_access_token
from app.models.test_token_request import TokenResquest

router = APIRouter()

@router.get("/token-check", dependencies=[Depends(JWTBearer())])
def protected():
    return {"message": "Valid token"}

@router.post("/token-example", include_in_schema=False)
def generate_token(payload: TokenResquest = Body(default=TokenResquest())):
    token = create_access_token(payload.model_dump())
    return {
        "access_token": token,
        "token_type": "bearer",
    }