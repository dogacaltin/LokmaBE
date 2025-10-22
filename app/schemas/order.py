from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

# API'ye YENİ sipariş gönderilirken kullanılan temel yapı
# Not: Frontend şu an yeni siparişte 'ekstra_telefon' göndermiyor,
# ama gelecekte eklenebilir diye buraya da ekliyoruz.
class OrderBase(BaseModel):
    siparis: str
    yapilacak_tarih: datetime
    musteri_isim: str
    musteri_telefon: str
    ekip: str
    adres: str
    fiyat: float
    notlar: Optional[str] = None
    ekstra_telefon: Optional[str] = None # YENİ ALAN EKLENDİ

class OrderCreate(OrderBase):
    pass

# API'ye GÜNCELLEME isteği gönderilirken kullanılan yapı
# Frontend sadece 'notlar' veya 'ekstra_telefon' gönderdiğinde de çalışır.
class OrderUpdate(BaseModel):
    siparis: Optional[str] = None
    yapilacak_tarih: Optional[datetime] = None
    musteri_isim: Optional[str] = None
    musteri_telefon: Optional[str] = None
    ekip: Optional[str] = None
    adres: Optional[str] = None
    fiyat: Optional[float] = None
    notlar: Optional[str] = None
    ekstra_telefon: Optional[str] = None # YENİ ALAN EKLENDİ

# API'den DÖNEN cevabın yapısını tanımlar
class OrderOut(BaseModel):
    id: str # ID her zaman string
    yapilacak_tarih: Optional[str] = None # Tarihler string olarak döner
    verildigi_tarih: Optional[str] = None # Tarihler string olarak döner
    siparis: Optional[str] = None
    musteri_isim: Optional[str] = None
    musteri_telefon: Optional[str] = None
    ekip: Optional[str] = None
    adres: Optional[str] = None
    fiyat: Optional[float] = None
    notlar: Optional[str] = None
    ekstra_telefon: Optional[str] = None # YENİ ALAN EKLENDİ

    class Config:
        from_attributes = True # Pydantic v2 için 'orm_mode' yerine kullanılır

