from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserLogin
from app.services.auth import verify_password


router = APIRouter()

@router.post("/login")
def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_credentials.email).first()
    
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    if not verify_password(user_credentials.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect password")
    
    return {"message": "Login successful"}