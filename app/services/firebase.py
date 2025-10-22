import firebase_admin
from firebase_admin import credentials, firestore, auth
from dotenv import load_dotenv
import os
from pathlib import Path
# --- YENİ Importlar ---
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
# --- Importlar Sonu ---


# .env dosyasını yükle (Projenin kök dizininde olduğunu varsayıyoruz)
env_path = Path(__file__).resolve().parents[2] / ".env" # backend/app/services -> backend -> root
load_dotenv(dotenv_path=env_path)

# Firebase Admin SDK anahtar dosyasının yolu
# Render'da Secret File olarak eklenen dosyanın adını kullanıyoruz
FIREBASE_CREDENTIALS_PATH = os.getenv("FIREBASE_CREDENTIALS_PATH", "firebase_admin_sdk.json")

# Firebase'i başlat (sadece bir kez)
if not firebase_admin._apps:
    try:
        cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
        firebase_admin.initialize_app(cred)
        print("Firebase Admin SDK başarıyla başlatıldı.") # Başlatıldığını logla
    except FileNotFoundError:
        print(f"HATA: Firebase Admin SDK anahtar dosyası bulunamadı: {FIREBASE_CREDENTIALS_PATH}")
        # Uygulamanın çökmemesi için burada alternatif bir yol izlenebilir veya hata fırlatılabilir.
        # Şimdilik Firestore client'ı None olacak.
        db = None
    except Exception as e:
        print(f"HATA: Firebase Admin SDK başlatılamadı: {e}")
        db = None # Hata durumunda db None olsun
else:
    print("Firebase Admin SDK zaten başlatılmış.") # Zaten başlatıldıysa logla

# Firestore client'ını al (eğer SDK başarıyla başlatıldıysa)
if firebase_admin._apps:
    try:
        db = firestore.client()
        print("Firestore client başarıyla alındı.")
    except Exception as e:
         print(f"HATA: Firestore client alınamadı: {e}")
         db = None
else:
    db = None # SDK başlatılamadıysa db None

# --- YENİ: Token Doğrulama Mekanizması ---
# OAuth2PasswordBearer, FastAPI'nin isteğin Authorization başlığından
# Bearer token'ı otomatik olarak almasını sağlar.
# tokenUrl burada önemli değil, çünkü doğrulamayı kendimiz yapıyoruz.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_token(id_token: str):
    """Verilen Firebase ID Token'ını doğrular."""
    if not id_token:
        return None
    try:
        # Token'ı Firebase ile doğrula
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token
    except Exception as e:
        print(f"Token doğrulama hatası: {e}") # Hataları logla
        return None

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    FastAPI Bağımlılığı (Dependency):
    İstek başlığından alınan token'ı doğrular ve kullanıcı bilgilerini döndürür.
    Doğrulama başarısız olursa 401 Unauthorized hatası fırlatır.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    decoded_token = verify_token(token)
    if decoded_token is None:
        raise credentials_exception

    # Token geçerliyse, kullanıcı bilgilerini (veya sadece UID'yi) döndür
    # Router'larda bu bilgiye erişilebilir olacak.
    # Örneğin: Kullanıcının UID'si, e-postası vb.
    user_info = {
        "uid": decoded_token.get("uid"),
        "email": decoded_token.get("email"),
        # İstersen Firebase'den daha fazla kullanıcı detayı çekebilirsin:
        # user = auth.get_user(decoded_token.get("uid"))
        # "name": user.display_name,
    }
    return user_info
# --- YENİ BÖLÜM SONU ---

