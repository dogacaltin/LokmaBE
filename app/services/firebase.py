import firebase_admin
from firebase_admin import credentials, firestore, auth
import os
from dotenv import load_dotenv
from pathlib import Path

# --- Başlangıç Ayarları ---
# Bu blok, uygulamanın herhangi bir yerinden ilk kez import edildiğinde
# sadece bir defa çalışacak ve Firebase bağlantısını kuracak.

# Projenin kök dizinindeki .env dosyasını bul ve yükle
# Bu, yerel geliştirme için gereklidir. Render gibi servisler
# ortam değişkenlerini kendi panellerinden yönetir.
env_path = Path(__file__).resolve().parent.parent.parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)

# Ortam değişkeninden Firebase kimlik bilgisi dosyasının yolunu al
# Render'da bu bir "Secret File" olarak ayarlanmalıdır.
FIREBASE_CREDENTIALS_PATH = os.getenv("FIREBASE_CREDENTIALS_PATH")

if FIREBASE_CREDENTIALS_PATH is None:
    raise ValueError("FIREBASE_CREDENTIALS_PATH ortam değişkeni ayarlanmamış!")

# --- Tek Seferlik Firebase Başlatma ---
# _apps listesini kontrol ederek uygulamanın zaten başlatılmadığından emin oluyoruz.
if not firebase_admin._apps:
    try:
        cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
        firebase_admin.initialize_app(cred)
        print("Firebase Admin SDK başarıyla başlatıldı.")
    except Exception as e:
        print(f"Firebase başlatılırken hata oluştu: {e}")
        # Hata durumunda uygulamanın devam etmesini engellemek için
        # burada bir exception fırlatmak daha doğru olabilir.
        raise e

# --- Global Olarak Kullanılacak Servisler ---
# Firestore veritabanı client'ı.
# Artık projenin her yerinden bu 'db' objesini import ederek Firestore kullanabiliriz.
db = firestore.client()


# --- Kimlik Doğrulama Fonksiyonları ---
# Bu fonksiyon, bir client'tan (örneğin frontend) gelen JWT'yi doğrulamak için kullanılır.
def verify_token(id_token: str):
    """
    Verilen ID token'ını doğrular ve kullanıcı bilgilerini döndürür.
    Token geçersizse None döndürür.
    """
    try:
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token
    except Exception as e:
        print(f"Token doğrulanırken hata: {e}")
        return None
