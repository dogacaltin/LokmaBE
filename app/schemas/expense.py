from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# API'ye YENİ gider gönderilirken kullanılan yapı
class ExpenseBase(BaseModel):
    tutar: float
    aciklama: str
    tarih: datetime

class ExpenseCreate(ExpenseBase):
    pass

# API'ye GÜNCELLEME isteği gönderilirken kullanılan yapı
class ExpenseUpdate(BaseModel):
    tutar: Optional[float] = None
    aciklama: Optional[str] = None
    tarih: Optional[datetime] = None

# API'den DÖNEN cevabın yapısını tanımlar
class ExpenseOut(BaseModel):
    # Düzeltme 1: ID her zaman metindir (string).
    id: str
    
    # Düzeltme 2: Router, tarihi metne çevirdiği için,
    # bu şema da tarihi metin olarak beklemelidir.
    tarih: Optional[str] = None

    # Diğer alanlar
    tutar: Optional[float] = None
    aciklama: Optional[str] = None

    class Config:
        from_attributes = True

