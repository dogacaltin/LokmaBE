from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware

from backend import models, schemas
from backend.database import get_db
from backend.auth import verify_password  # varsa
from backend.routers import auth_router
from backend.routers import giderler


app = FastAPI()

# CORS ayarları
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Gerekirse "*" yerine sadece frontend URL'si yaz
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Router'lar
app.include_router(auth_router.router, prefix="/auth")
app.include_router(giderler.router)

# Login endpoint – dilersen bunu `auth_router.py` içinde tut, burada gereksiz olur
@app.post("/login")
def login(request: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == request.email).first()
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"message": "Login successful"}