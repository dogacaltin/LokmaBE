from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# API'ye YENİ sipariş gönderilirken kullanılan yapı
# Frontend'den gelen tarih metinleri (örn: "2025-10-11T14:30:00")
# Pydantic tarafından otomatik olarak datetime nesnesine çevrilir.
class OrderBase(BaseModel):
    siparis: str
    yapilacak_tarih: datetime
    musteri_isim: str
    musteri_telefon: str
    ekip: str
    adres: str
    fiyat: float
    notlar: Optional[str] = None

class OrderCreate(OrderBase):
    pass

# API'ye GÜNCELLEME isteği gönderilirken kullanılan yapı
# Tüm alanlar opsiyoneldir, böylece sadece istenen alanlar güncellenebilir.
class OrderUpdate(BaseModel):
    siparis: Optional[str] = None
    yapilacak_tarih: Optional[datetime] = None
    musteri_isim: Optional[str] = None
    musteri_telefon: Optional[str] = None
    ekip: Optional[str] = None
    adres: Optional[str] = None
    fiyat: Optional[float] = None
    notlar: Optional[str] = None

# API'den DÖNEN cevabın yapısını tanımlar
# Bu, router'daki safe_doc_to_dict fonksiyonunun çıktısıyla eşleşmelidir.
class OrderOut(BaseModel):
    # Düzeltme 1: ID her zaman metindir (string).
    id: str
    
    # Düzeltme 2: Router, tarihleri metne çevirdiği için,
    # bu şema da tarihleri metin olarak beklemelidir.
    yapilacak_tarih: Optional[str] = None
    verildigi_tarih: Optional[str] = None

    # Diğer alanlar opsiyonel olarak tanımlanarak esneklik sağlanır.
    siparis: Optional[str] = None
    musteri_isim: Optional[str] = None
    musteri_telefon: Optional[str] = None
    ekip: Optional[str] = None
    adres: Optional[str] = None
    fiyat: Optional[float] = None
    notlar: Optional[str] = None

    class Config:
        from_attributes = True

