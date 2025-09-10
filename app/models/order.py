from sqlalchemy import Column, Integer, String, DateTime, Float
from app.database import Base
from datetime import datetime

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    siparis = Column(String)
    yapilacak_tarih = Column(DateTime)
    verildigi_tarih = Column(DateTime, default=datetime.utcnow)
    musteri_isim = Column(String)
    musteri_telefon = Column(String)
    ekip = Column(String)
    adres = Column(String)
    fiyat = Column(Float)  
    notlar = Column(String, nullable=True)