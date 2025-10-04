from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# app/routers klasöründen ihtiyacımız olan router'ları import ediyoruz
# __init__.py dosyasında tanıttığımız için bu satır artık çalışır.
from app.routers import auth, order, expense 

app = FastAPI()

# CORS ayarları
origins = ["*"] # Geliştirme için, daha sonra frontend adresini yazarsın

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Router'ları uygulamaya dahil ediyoruz
# Her router'ı kendi modülü üzerinden çağırıyoruz
app.include_router(auth.router)
app.include_router(order.router)
app.include_router(expense.router)

@app.get("/")
def read_root():
    return {"message": "API is working correctly"}

