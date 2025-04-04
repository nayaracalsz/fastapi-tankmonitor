from fastapi import FastAPI
from fastapi.responses import JSONResponse

from .core.middleware.security import get_security_middleware
from .firebase import db

app = FastAPI(middleware=get_security_middleware())

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
                "message": f"Firestore connection failed: {str(e)}"
            }
        )

