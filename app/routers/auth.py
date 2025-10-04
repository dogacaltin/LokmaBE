from fastapi import APIRouter, HTTPException
from app.services.firebase import verify_token, auth  # Kendi servis dosyamızdan import ediyoruz
from app.schemas.user import UserLogin
import requests
import os
from dotenv import load_dotenv

# .env dosyasını yükler (yerel geliştirme için)
load_dotenv()

router = APIRouter(prefix="/auth", tags=["Auth"])

# .env dosyasından veya Render ortam değişkenlerinden Firebase Web API Key'i alır
FIREBASE_API_KEY = os.getenv("FIREBASE_API_KEY")

if not FIREBASE_API_KEY:
    raise RuntimeError("FIREBASE_API_KEY ortam değişkeni ayarlanmamış!")

@router.post("/login")
def login(user_login: UserLogin):
    # Firebase'in kimlik doğrulama REST API'sine istek gönderiyoruz
    # Bu API, e-posta ve şifreyi alıp doğruluğunu kontrol eder
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
    
    payload = {
        "email": user_login.email,
        "password": user_login.password,
        "returnSecureToken": True
    }

    # İsteği gönder
    response = requests.post(url, json=payload)

    # Firebase'den hata dönerse (örn: şifre yanlış), istemciye hata fırlat
    if response.status_code != 200:
        raise HTTPException(status_code=401, detail="Geçersiz e-posta veya şifre")

    # Başarılı olursa, Firebase'in cevabını işle
    res_json = response.json()
    id_token = res_json.get("idToken")

    # Admin SDK ile token'ı doğrulayıp kullanıcı bilgilerini alalım
    decoded_token = verify_token(id_token)
    if not decoded_token:
        raise HTTPException(status_code=401, detail="Token doğrulanamadı veya geçersiz")

    try:
        uid = decoded_token["uid"]
        user_record = auth.get_user(uid)
        
        # Kullanıcının özel yetkilerini (custom claims) kontrol et
        is_admin = False
        if user_record.custom_claims and "admin" in user_record.custom_claims:
            is_admin = user_record.custom_claims["admin"]

        return {
            "message": f"Hoş geldiniz {user_record.email}",
            "uid": uid,
            "email": user_record.email,
            "is_admin": is_admin,
            "idToken": id_token
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Kullanıcı bilgileri alınamadı: {str(e)}")

