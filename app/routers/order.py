from fastapi import APIRouter, HTTPException
from uuid import uuid4
from app.schemas.order import OrderCreate, OrderUpdate, OrderOut
from app.services.firebase import db
from typing import List

router = APIRouter(prefix="/orders", tags=["Orders"])

def safe_doc_to_dict(doc):
    """Firestore belgesini güvenli bir şekilde sözlüğe dönüştürür."""
    if not doc.exists:
        return None
    
    # Beklenen tüm alanları varsayılan değerlerle tanımla
    order_data = {
        "id": doc.id,
        "siparis": doc.get("siparis"),
        "yapilacak_tarih": doc.get("yapilacak_tarih"),
        "verildigi_tarih": doc.get("verildigi_tarih"),
        "musteri_isim": doc.get("musteri_isim"),
        "musteri_telefon": doc.get("musteri_telefon"),
        "ekip": doc.get("ekip"),
        "adres": doc.get("adres"),
        "fiyat": doc.get("fiyat"),
        "notlar": doc.get("notlar")
    }
    return order_data

@router.get("/", response_model=List[OrderOut])
def get_orders():
    try:
        orders_stream = db.collection("orders").stream()
        # Her belgeyi güvenli bir şekilde dönüştür
        return [safe_doc_to_dict(doc) for doc in orders_stream if doc.exists]
    except Exception as e:
        # Loglama için hata mesajını yazdırabilirsin
        print(f"Error fetching orders: {e}")
        raise HTTPException(status_code=500, detail="Could not fetch orders")

@router.get("/columns")
def get_order_columns():
    try:
        sample_docs = db.collection("orders").limit(1).stream()
        for doc in sample_docs:
            if doc.exists:
                return {"columns": list(doc.to_dict().keys())}
        return {"columns": []} # Koleksiyon boşsa
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
        # Firestore'a eklemeden önce ID'yi kaldır
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
