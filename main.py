from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware

# Local imports
from app import models, schemas
from backend.app.services.database import get_db
from app.services.auth import verify_password
from app.models.user import User
from app.schemas.user import UserLogin

# Router imports
from routers import auth_router
from app.routers import expense
from app.routers import order_router  # Bunu da ekliyoruz

app = FastAPI()

# CORS ayarları – frontend bağlantısı için gerekli
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Production'da "*" yerine frontend URL'i yazman önerilir
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Router'ları dahil et
app.include_router(auth_router.router, prefix="/auth")
app.include_router(expense.router)
app.include_router(order_router)  # Order router'ını da ekledik

# Giriş endpoint'i (opsiyonel olarak auth_router içine de alabilirsin)
@app.post("/login")
def login(request: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"message": "Login successful"}