import os
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict

import jwt
from dotenv import load_dotenv
from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jwt import PyJWTError
from pydantic import BaseModel

from app.models.user_model import UserFirestore

load_dotenv()

class AuthConfig(BaseModel):
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = os.getenv("ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

config = AuthConfig()

class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> str:
        credentials = await super().__call__(request)
        self._validate_credentials(credentials)
        return credentials.credentials

    def _validate_credentials(self, credentials: HTTPAuthorizationCredentials) -> None:
        if not credentials or credentials.scheme != "Bearer":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid authentication scheme."
            )
        if not self.verify_jwt(credentials.credentials):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid or expired token."
            )

    def verify_jwt(self, token: str) -> bool:
        try:
            payload = decodeJWT(token)
            verify_token_version(payload)
            return True
        except HTTPException:
            return False

def create_access_token(
    data: Dict,
    expires_delta: Optional[timedelta] = None
) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)

def decodeJWT(token: str) -> Dict:
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        if datetime.now(timezone.utc) > datetime.fromtimestamp(payload["exp"], tz=timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Token expired"
            )
        return payload
    except PyJWTError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Token expired" if "expired" in str(e) else f"Invalid token: {str(e)}"
        )

def verify_token_version(payload: dict) -> None:
    user = UserFirestore.get_by_uid(payload["uid"])
    if not user or user.token_version != payload.get("token_version"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Token version mismatch. Please re-login."
        )