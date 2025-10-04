# backend/app/services/database.py

import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv
import os
from pathlib import Path

# .env dosyasını yükle
env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# Firebase ayarlarını oku
FIREBASE_CREDENTIALS_PATH = os.getenv("FIREBASE_CREDENTIALS_PATH")
FIREBASE_PROJECT_ID = os.getenv("FIREBASE_PROJECT_ID")

# Firebase'e bağlan
if not firebase_admin._apps:
    cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
    firebase_admin.initialize_app(cred, {
        'projectId': FIREBASE_PROJECT_ID
    })

# Firestore client'ını oluştur
db = firestore.client()