import os
from datetime import timezone, datetime

import requests
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from firebase_admin import auth

from app.core.middleware import create_access_token
from app.models.user_model import UserFirestore, UserCreate, UserLogin

load_dotenv()
FIREBASE_API_KEY = os.getenv("FIREBASE_API_KEY")
router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register")
async def register_user(user: UserCreate):
    try:
        if UserFirestore.get_by_email(user.email) is not None:
            raise HTTPException(
                status_code=400,
                detail="Email already registered"
            )

        firebase_user = auth.create_user(
            email=user.email,
            password=user.password,
            display_name=user.name
        )

        firestore_user = UserFirestore(
            uid=firebase_user.uid,
            email=user.email,
            name=user.name,
            last_login=datetime.now(timezone.utc),
            token_version=0
        )
        firestore_user.create_user()

        return {"uid": firebase_user.uid,"email": user.email}

    except auth.EmailAlreadyExistsError:
        raise HTTPException(
            status_code=400,
            detail="Email already exists in Firebase Auth"
        )

    except Exception as e:
        if 'firebase_user' in locals() and firebase_user is not None:
            auth.delete_user(firebase_user.uid)
        raise HTTPException(
            status_code=500,
            detail=f"Registration failed: {str(e)}"
        )

@router.post("/login")
async def login_user(user: UserLogin):
    try:
        firebase_login_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"

        payload = {
            "email": user.email,
            "password": user.password,
            "returnSecureToken": True
        }

        response = requests.post(firebase_login_url, json=payload)

        if response.status_code != 200:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        login_data = response.json()

        user_record = UserFirestore.get_by_uid(login_data.get("localId"))

        if not user_record:
            raise HTTPException(status_code=404, detail="User record not found")

        user_record.last_login = datetime.now(timezone.utc)
        user_record.update_last_login()

        token_data = {
            "uid": login_data.get("localId"),
            "email": user.email,
            "token_version": user_record.token_version
        }
        token = create_access_token(data=token_data)


        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "uid": login_data.get("localId"),
                "email": user.email,
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")