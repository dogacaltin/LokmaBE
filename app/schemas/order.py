from pydantic import BaseModel
from datetime import datetime

class OrderBase(BaseModel):
    siparis: str
    yapilacak_tarih: datetime
    musteri_isim: str
    musteri_telefon: str
    ekip: str
    adres: str
    fiyat : float 
    notlar : str | None = None

class OrderCreate(OrderBase):
    pass

class OrderUpdate(OrderBase):
    pass

class OrderOut(OrderBase):
    id: int
    verildigi_tarih: datetime

    class Config:
        from_attributes = True  # Pydantic v2 için