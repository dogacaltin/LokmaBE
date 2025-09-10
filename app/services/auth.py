from sqlalchemy.orm import Session
from app.models import user as user_model
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# auth.py
def verify_password(plain_password, hashed_password):
    return plain_password == hashed_password  # Şimdilik hash yerine düz kontrol

def authenticate_user(db: Session, email: str, password: str):
    user = db.query(user_model.User).filter(user_model.User.email == email).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user