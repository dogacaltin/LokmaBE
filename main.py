from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Router'larımızı import ediyoruz
from app.routers import auth, order, expense 

app = FastAPI()

# CORS ayarları (Frontend'den gelen isteklere izin vermek için)
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:8080",
    # Frontend'inizin deploy edildiği adresleri buraya ekleyebilirsiniz
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Router'ları uygulamaya dahil ediyoruz
app.include_router(auth.router)
app.include_router(order.router)
app.include_router(expense.router)

@app.get("/")
def read_root():
    return {"message": "API is working correctly"}
