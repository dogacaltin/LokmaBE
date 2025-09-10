from sqlalchemy import Column, Integer, Float, String, DateTime
from app.database import Base
from datetime import datetime

class Expense(Base):
    __tablename__ = "expenses"
    id = Column(Integer, primary_key=True, index=True)
    tutar = Column(Float)
    aciklama = Column(String)
    tarih = Column(DateTime, default=datetime.utcnow)