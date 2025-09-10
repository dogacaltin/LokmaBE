from pydantic import BaseModel
from datetime import datetime

# Giderlerin temel şeması
class ExpenseBase(BaseModel):
    tutar: float
    aciklama: str
    tarih: datetime  # ISO 8601 formatı: "2025-08-20T14:00"

# Yeni gider oluşturma için (POST)
class ExpenseCreate(ExpenseBase):
    pass

# Gider güncelleme için (PUT)
class ExpenseUpdate(ExpenseBase):
    pass

# Gider görüntüleme (GET) için
class ExpenseOut(ExpenseBase):
    id: int

    class Config:
        from_attributes = True  # Pydantic v2 (önceki adı: orm_mode = True)