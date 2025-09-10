# app/config.py

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

def setup_cors(app: FastAPI):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Gerekirse "http://localhost:3000" yaz
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )