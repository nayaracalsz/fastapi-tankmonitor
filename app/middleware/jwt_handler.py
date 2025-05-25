import os
import uuid
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional

import jwt
from dotenv import load_dotenv
from fastapi import HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import PyJWTError
from pydantic import BaseModel

from app.models.user_model import UserFirestore
from app.services.token_blacklist import is_token_blacklisted

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
                detail="Invalid authentication scheme.",
            )
        if not self.verify_jwt(credentials.credentials):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid, expired or blacklisted token.",
            )

    def verify_jwt(self, token: str) -> bool:
        try:
            payload = decodeJWT(token)
            verify_token_version(payload)
            jti = payload.get("jti")
            if jti and is_token_blacklisted(jti):
                return False
            return True
        except HTTPException:
            return False


def create_access_token(data: Dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    jti = str(uuid.uuid4())

    to_encode.update({"exp": expire, "jti": jti})
    return (
        jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM),
        jti,
        int(expire.timestamp()),
    )


def decodeJWT(token: str) -> Dict:
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        if datetime.now(timezone.utc) > datetime.fromtimestamp(
            payload["exp"], tz=timezone.utc
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Token expired."
            )
        return payload
    except PyJWTError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                f"Token expired" if "expired" in str(e) else f"Invalid token: {str(e)}"
            ),
        )


def verify_token_version(payload: dict) -> None:
    uid = payload.get("sub")
    if not uid:
        raise HTTPException(status_code=403, detail="Token missing subject (sub).")

    user = UserFirestore.get_by_uid(uid)
    if not user or user.token_version != payload.get("token_version"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Token version mismatch. Please re-login.",
        )
