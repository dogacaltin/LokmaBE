from fastapi import FastAPI
from app.routers import order, user
from app.config import setup_cors
from app.routers import expense

app = FastAPI()

# CORS ayarları (frontend erişimi için)
setup_cors(app)

# Router'lar
app.include_router(order.router)
app.include_router(user.router)
app.include_router(expense.router)