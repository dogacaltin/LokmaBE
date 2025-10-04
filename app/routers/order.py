from fastapi import APIRouter, HTTPException
from uuid import uuid4
from app.schemas.order import OrderCreate, OrderUpdate, OrderOut
from app.services.firebase import db  # firestore.client()
from typing import List

router = APIRouter(prefix="/orders", tags=["Orders"])

# ✅ Tüm siparişleri getir
@router.get("/", response_model=List[OrderOut])
def get_orders():
    orders = db.collection("orders").stream()
    return [
        {**doc.to_dict(), "id": doc.id}
        for doc in orders
    ]

# ✅ Sadece iki siparişi getir
@router.get("/limited", response_model=List[OrderOut])
def get_limited_orders():
    orders = db.collection("orders").limit(2).stream()
    return [
        {**doc.to_dict(), "id": doc.id}
        for doc in orders
    ]

# ✅ Sipariş tablosundaki "sütun" isimlerini getir (Firestore'da sabit değil, örnek döner)
@router.get("/columns")
def get_order_columns():
    sample_doc = db.collection("orders").limit(1).stream()
    for doc in sample_doc:
        return {"columns": list(doc.to_dict().keys())}
    return {"columns": []}

# ✅ Tek bir siparişi getir
@router.get("/{order_id}", response_model=OrderOut)
def get_order(order_id: str):
    doc = db.collection("orders").document(order_id).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Order not found")
    return {**doc.to_dict(), "id": doc.id}

# ✅ Yeni sipariş oluştur
@router.post("/", response_model=OrderOut)
def create_order(order: OrderCreate):
    order_id = str(uuid4())
    db.collection("orders").document(order_id).set(order.model_dump())
    return {**order.model_dump(), "id": order_id}

# ✅ Siparişi güncelle
@router.put("/{order_id}", response_model=OrderOut)
def update_order(order_id: str, updated_data: OrderUpdate):
    ref = db.collection("orders").document(order_id)
    if not ref.get().exists:
        raise HTTPException(status_code=404, detail="Order not found")
    ref.update(updated_data.model_dump(exclude_unset=True))
    updated_doc = ref.get()
    return {**updated_doc.to_dict(), "id": order_id}

# ✅ Siparişi sil
@router.delete("/{order_id}")
def delete_order(order_id: str):
    ref = db.collection("orders").document(order_id)
    if not ref.get().exists:
        raise HTTPException(status_code=404, detail="Order not found")
    ref.delete()
    return {"message": "Order deleted successfully"}