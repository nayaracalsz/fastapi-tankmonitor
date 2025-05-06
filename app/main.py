from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.controllers.auth_controller import router as auth_controller
from app.firebase.firebase import db
from app.middleware.password_validator import password_complexity_middleware
from app.middleware.security import get_security_middleware

app = FastAPI(middleware=get_security_middleware(is_production=False))
app.middleware("http")(password_complexity_middleware)
app.include_router(auth_controller)


@app.get("/")
def root():
    return {"message": "✅ Backend is working!"}


@app.get("/firestore-status")
def firestore_status():
    try:
        _ = list(db.collections())
        return {"status": "ok", "message": "Firestore connection is working."}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Firestore connection failed: {str(e)}",
            },
        )
