from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# Temel alanları tanımlar. API'ye gelen isteklerde bu kullanılır.
# FastAPI, gelen metin formatındaki tarihleri otomatik olarak datetime'a çevirebilir.
class OrderBase(BaseModel):
    siparis: str
    yapilacak_tarih: datetime
    musteri_isim: str
    musteri_telefon: str
    ekip: str
    adres: str
    fiyat: float
    notlar: Optional[str] = None # str | None yerine Optional[str] kullanmak daha yaygındır

class OrderCreate(OrderBase):
    pass

class OrderUpdate(BaseModel):
    # Güncelleme için tüm alanların opsiyonel olması daha esnektir.
    siparis: Optional[str] = None
    yapilacak_tarih: Optional[datetime] = None
    musteri_isim: Optional[str] = None
    musteri_telefon: Optional[str] = None
    ekip: Optional[str] = None
    adres: Optional[str] = None
    fiyat: Optional[float] = None
    notlar: Optional[str] = None

# API'den DÖNEN cevabın yapısını tanımlar.
# Bu şema, backend'in gönderdiği veriyle %100 uyumlu olmalıdır.
class OrderOut(BaseModel):
    # Düzeltme 1: ID her zaman string'dir.
    id: str
    
    siparis: str
    
    # Düzeltme 2: Backend tarihleri metin olarak gönderdiği için,
    # bu şema da tarihleri metin olarak beklemelidir.
    yapilacak_tarih: Optional[str] = None
    verildigi_tarih: Optional[str] = None
    
    musteri_isim: str
    musteri_telefon: str
    ekip: str
    adres: str
    fiyat: float
    notlar: Optional[str] = None

    class Config:
        from_attributes = True
