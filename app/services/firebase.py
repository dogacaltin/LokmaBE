# app/service/firebase.py

import firebase_admin
from firebase_admin import credentials, auth
import os

# Tek seferlik başlatma (idempotent)
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_admin_sdk.json")  # JSON anahtar dosyan
    firebase_admin.initialize_app(cred)

def verify_token(id_token: str):
    try:
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token
    except Exception as e:
        return None