from fastapi import APIRouter, HTTPException, Query, status
from firebase_admin import auth

from app.utils.email_utils import send_email_notification

router = APIRouter(prefix="/verify", tags=["Email Verification"])


@router.get("/status")
async def check_email_verification(
    email: str = Query(..., description="Email to verify")
):
    try:
        user = auth.get_user_by_email(email)
        return {"email": email, "email_verified": user.email_verified}
    except auth.UserNotFoundError:
        raise HTTPException(status_code=404, detail="User not found")


@router.post("/send-link")
async def send_verification_email(
    email: str = Query(..., description="Email to send verification link")
):
    try:
        link = auth.generate_email_verification_link(email)
        send_email_notification(
            to=email,
            subject="Verify your email",
            body=f"Hey! Please verify your email by clicking this link: {link}",
        )
        return {"detail": f"Verification email sent to {email}"}
    except auth.UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
