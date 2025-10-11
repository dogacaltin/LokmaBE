import os
import requests
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from firebase_admin import auth
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/auth", tags=["Auth"])

# Firebase Web API Anahtarını .env dosyasından al
FIREBASE_API_KEY = os.getenv("FIREBASE_API_KEY")

class UserLogin(BaseModel):
    email: str
    password: str

@router.post("/login", response_model=dict)
def login(user_login: UserLogin):
    """
    Kullanıcıyı Firebase Authentication REST API kullanarak doğrular
    ve başarılı olursa bir idToken döndürür.
    """
    if not FIREBASE_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="FIREBASE_API_KEY ortam değişkeni ayarlanmamış."
        )

    # Firebase'in kimlik doğrulama REST API endpoint'i
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
    
    payload = {
        "email": user_login.email,
        "password": user_login.password,
        "returnSecureToken": True,
    }

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        error_json = err.response.json().get("error", {})
        error_message = error_json.get("message", "Invalid email or password")
        raise HTTPException(status_code=401, detail=error_message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bir sunucu hatası oluştu: {e}")

    res_json = response.json()
    id_token = res_json.get("idToken")

    if not id_token:
        raise HTTPException(status_code=500, detail="Firebase'den token alınamadı.")

    try:
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token['uid']
        user_record = auth.get_user(uid)
        
        # Frontend'e göndereceğimiz cevabı hazırla
        response_data = {
            "message": f"Hoşgeldin {user_record.email}",
            "token": id_token,
            "uid": uid,
            "email": user_record.email,
        }

        # --- HATA AYIKLAMA İÇİN EKLENEN BÖLÜM ---
        # Bu satır, Render loglarına tam olarak ne gönderildiğini yazdıracak.
        print("DEBUG: Login response data:", response_data)
        # --- HATA AYIKLAMA BÖLÜMÜ SONU ---
        
        return response_data
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token doğrulanamadı: {str(e)}")

