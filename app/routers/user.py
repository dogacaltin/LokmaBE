from fastapi import APIRouter, HTTPException
from firebase_admin import auth
from app.schemas.user import UserLogin
import requests
import os
from dotenv import load_dotenv

load_dotenv()
router = APIRouter(prefix="/auth", tags=["Auth"])

FIREBASE_API_KEY = os.getenv("FIREBASE_API_KEY")  # .env'de saklanmalı

@router.post("/login")
def login(user_login: UserLogin):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
    payload = {
        "email": user_login.email,
        "password": user_login.password,
        "returnSecureToken": True
    }

    response = requests.post(url, json=payload)
    if response.status_code != 200:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    res_json = response.json()
    id_token = res_json.get("idToken")

    # Firebase Admin SDK üzerinden kullanıcı bilgilerini alalım
    try:
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token["uid"]
        user_record = auth.get_user(uid)
        return {
            "message": f"Welcome {user_record.email}",
            "uid": uid,
            "email": user_record.email,
            "is_admin": user_record.custom_claims.get("admin") if user_record.custom_claims else False
        }
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token verification failed: {str(e)}")