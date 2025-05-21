from fastapi import APIRouter, HTTPException
from firebase_admin import auth

from app.models.user_model import UserFirestore
from app.schemas.user_schema import UserCreate

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register")
async def register_user(user: UserCreate):
    lowercase_email = user.email.strip().lower()
    try:
        firebase_user = auth.create_user(
            email=user.email, password=user.password, display_name=user.name
        )

        firestore_user = UserFirestore(
            uid=firebase_user.uid, email=lowercase_email, name=user.name
        )
        firestore_user.save()

        return {"uid": firebase_user.uid, "email": lowercase_email}

    except auth.EmailAlreadyExistsError:
        raise HTTPException(status_code=409, detail="Email already exists.")

    except Exception as e:
        if "firebase_user" in locals() and firebase_user is not None:
            auth.delete_user(firebase_user.uid)
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")
