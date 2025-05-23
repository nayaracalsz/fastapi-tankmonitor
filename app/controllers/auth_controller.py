import os
from datetime import datetime, timezone

import requests
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from firebase_admin import auth

from app.middleware import create_access_token
from app.models.user_model import UserFirestore
from app.schemas.user_schema import UserCreate, UserLogin

load_dotenv()
FIREBASE_API_KEY = os.getenv("FIREBASE_API_KEY")
router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register")
async def register_user(user: UserCreate):
    try:
        firebase_user = auth.create_user(
            email=user.email, password=user.password, display_name=user.name
        )

        firestore_user = UserFirestore(
            uid=firebase_user.uid, email=user.email, name=user.name
        )
        firestore_user.save()

        return {"uid": firebase_user.uid, "email": user.email}

    except auth.EmailAlreadyExistsError:
        raise HTTPException(status_code=409, detail="Email already exists.")

    except Exception as e:
        if "firebase_user" in locals() and firebase_user is not None:
            auth.delete_user(firebase_user.uid)
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")


@router.post("/login")
async def login_user(user: UserLogin):
    firebase_login_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"

    payload = {
        "email": user.email,
        "password": user.password,
        "returnSecureToken": True,
    }

    response = requests.post(firebase_login_url, json=payload)

    if response.status_code != 200:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    try:
        login_data = response.json()

        user_record = UserFirestore.get_by_email(user.email)
        if not user_record:
            raise HTTPException(status_code=401, detail="Email not registered")

        user_record.update_last_login()

        token_data = {
            "uid": login_data.get("localId"),
            "email": user.email,
            "token_version": user_record.token_version,
        }

        token = create_access_token(data=token_data)

        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "uid": login_data.get("localId"),
                "email": user.email,
            },
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Login failed internally: {str(e)}"
        )
