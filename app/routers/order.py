from fastapi import APIRouter, HTTPException
from uuid import uuid4
from app.schemas.order import OrderCreate, OrderUpdate, OrderOut
from app.services.firebase import db
from typing import List
from datetime import datetime
# Firebase'in özel Timestamp türünü tanımak için bu import gerekli
from google.cloud.firestore_v1.types import Timestamp

router = APIRouter(prefix="/orders", tags=["Orders"])

def safe_doc_to_dict(doc):
    """Firestore belgesini güvenli bir şekilde sözlüğe dönüştürür ve tarihleri formatlar."""
    if not doc.exists:
        return None
    
    data = doc.to_dict()
    
    # Tarih alanlarını kontrol et ve Timestamp ise ISO formatına çevir
    for field in ["yapilacak_tarih", "verildigi_tarih"]:
        if field in data and isinstance(data[field], (datetime, Timestamp)):
            # Tarihi UTC'den alıp standart ISO 8601 formatına çeviriyoruz.
            data[field] = data[field].isoformat()

    data["id"] = doc.id
    return data

@router.get("/", response_model=List[OrderOut])
def get_orders():
    try:
        orders_stream = db.collection("orders").stream()
        return [safe_doc_to_dict(doc) for doc in orders_stream if doc.exists]
    except Exception as e:
        print(f"Error fetching orders: {e}")
        raise HTTPException(status_code=500, detail="Could not fetch orders")

@router.get("/columns")
def get_order_columns():
    try:
        sample_docs = db.collection("orders").limit(1).stream()
        for doc in sample_docs:
            if doc.exists:
                return {"columns": list(doc.to_dict().keys())}
        return {"columns": []}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Could not fetch columns")

@router.get("/{order_id}", response_model=OrderOut)
def get_order(order_id: str):
    doc_ref = db.collection("orders").document(order_id)
    order = safe_doc_to_dict(doc_ref.get())
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@router.post("/", response_model=OrderOut)
def create_order(order: OrderCreate):
    try:
        order_dict = order.model_dump()
        doc_ref = db.collection("orders").document()
        doc_ref.set(order_dict)
        return {**order_dict, "id": doc_ref.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not create order: {e}")

@router.put("/{order_id}", response_model=OrderOut)
def update_order(order_id: str, updated_data: OrderUpdate):
    ref = db.collection("orders").document(order_id)
    if not ref.get().exists:
        raise HTTPException(status_code=404, detail="Order not found")
    
    try:
        update_dict = updated_data.model_dump(exclude_unset=True)
        ref.update(update_dict)
        updated_doc = ref.get()
        return safe_doc_to_dict(updated_doc)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not update order: {e}")

@router.delete("/{order_id}")
def delete_order(order_id: str):
    ref = db.collection("orders").document(order_id)
    if not ref.get().exists:
        raise HTTPException(status_code=404, detail="Order not found")
    try:
        ref.delete()
        return {"message": "Order deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not delete order: {e}")

