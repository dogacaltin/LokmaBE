from fastapi import APIRouter, HTTPException, Depends # Depends eklendi
from app.schemas.order import OrderCreate, OrderUpdate, OrderOut
from app.services.firebase import db, get_current_user # get_current_user eklendi
# --- YENİ: typing modülünden gerekli importlar ---
from typing import List, Dict, Any, Optional
# --- Import Sonu ---
from datetime import datetime
from uuid import uuid4

router = APIRouter(
    prefix="/orders",
    tags=["Orders"],
    dependencies=[Depends(get_current_user)] # TÜM sipariş endpoint'leri artık giriş gerektiriyor
)

def safe_doc_to_dict(doc) -> Optional[Dict[str, Any]]:
    """Firestore belgesini güvenli bir şekilde sözlüğe dönüştürür ve tarihleri formatlar."""
    if not doc.exists:
        return None

    data = doc.to_dict()
    if not data: # Belge var ama içi boşsa
        return {"id": doc.id} # Sadece ID'yi döndür veya boş bir dict döndür

    # Tarih alanlarını kontrol et ve datetime ise ISO formatına çevir
    for field in ["yapilacak_tarih", "verildigi_tarih"]:
        timestamp = data.get(field) # .get() kullanarak KeyError'dan kaçın
        if timestamp and isinstance(timestamp, datetime):
            try:
                data[field] = timestamp.isoformat()
            except Exception as e:
                 print(f"Warning: Could not format date field {field} for doc {doc.id}: {e}")
                 data[field] = str(timestamp) # Formatlayamazsa string'e çevir

    data["id"] = doc.id
    # --- YENİ: ekstra_telefon alanını da dahil et ---
    # Eğer Firestore'da yoksa .get() None döndürecektir, bu schema ile uyumlu.
    data["ekstra_telefon"] = data.get("ekstra_telefon")
    # --- GÜNCELLEME SONU ---

    # Şemada olmayan alanları temizleyebiliriz (opsiyonel ama iyi pratik)
    allowed_keys = OrderOut.model_fields.keys()
    return {k: v for k, v in data.items() if k in allowed_keys}


@router.get("/", response_model=List[OrderOut])
def get_orders(current_user: dict = Depends(get_current_user)): # current_user parametresi
    """Tüm siparişleri listeler."""
    try:
        orders_stream = db.collection("orders").stream()
        results = [safe_doc_to_dict(doc) for doc in orders_stream if doc.exists]
        # None dönenleri filtrele (boş belgeler olabilir)
        return [res for res in results if res is not None]
    except Exception as e:
        print(f"Error fetching orders: {e}") # Hataları logla
        raise HTTPException(status_code=500, detail=f"Siparişler alınamadı: {e}")

@router.get("/columns")
def get_order_columns(current_user: dict = Depends(get_current_user)):
    """İlk siparişin alan adlarını (sütunları) döndürür."""
    try:
        sample_docs = db.collection("orders").limit(1).stream()
        for doc in sample_docs:
            if doc.exists and doc.to_dict():
                # ekstra_telefon'u kolon listesinden çıkarabiliriz (formda kullanılmıyor)
                return {"columns": [k for k in doc.to_dict().keys() if k != "ekstra_telefon"]}
        return {"columns": []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sütun bilgisi alınamadı: {e}")

@router.post("/", response_model=OrderOut)
def create_order(order: OrderCreate, current_user: dict = Depends(get_current_user)):
    """Yeni bir sipariş oluşturur."""
    try:
        order_id = str(uuid4())
        ref = db.collection("orders").document(order_id)
        # Pydantic modelini sözlüğe çevirirken None değerleri dahil etme
        order_data = order.model_dump(exclude_unset=True)
        order_data["verildigi_tarih"] = datetime.utcnow() # Siparişin verildiği anı ekle
        # ekstra_telefon alanı şemada olduğu için otomatik olarak dahil edilir (varsa).
        ref.set(order_data)
        new_doc = ref.get() # Oluşturulan belgeyi tekrar oku
        return safe_doc_to_dict(new_doc)
    except Exception as e:
        print(f"Error creating order: {e}")
        raise HTTPException(status_code=500, detail=f"Sipariş oluşturulamadı: {e}")

# --- GÜNCELLENDİ: update_order ---
@router.put("/{order_id}", response_model=OrderOut)
def update_order(order_id: str, updated_data: OrderUpdate, current_user: dict = Depends(get_current_user)):
    """Belirli bir siparişi günceller (kısmi güncelleme destekler)."""
    ref = db.collection("orders").document(order_id)
    doc = ref.get() # Önce belgeyi al
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Sipariş bulunamadı")

    try:
        # Gelen veriyi sözlüğe çevir, sadece gönderilen (None olmayan) alanları al
        update_dict = updated_data.model_dump(exclude_unset=True)

        # ÖNEMLİ: Eğer yapilacak_tarih geliyorsa ve datetime ise Firestore'a uygun formatta sakla
        if 'yapilacak_tarih' in update_dict and isinstance(update_dict['yapilacak_tarih'], datetime):
             # Pydantic zaten string'i datetime'a çevirmiş olmalı, direkt kullanabiliriz.
             pass # Firestore datetime nesnelerini anlar.
        elif 'yapilacak_tarih' in update_dict:
             # Eğer datetime değilse (ki şema zorunlu kılıyor), hata olabilir veya None gelmiştir
             # None gelirse Firestore'dan alanı siler, dikkatli olmalı.
             # Şema (OrderUpdate) zaten Optional[datetime] olduğu için sorun olmamalı.
             pass


        # Firestore'a sadece güncellenecek alanları gönder
        if update_dict: # Eğer güncellenecek veri varsa
            ref.update(update_dict)
        else:
            # Güncellenecek veri yoksa (boş istek?), belki bir uyarı loglanabilir
            print(f"Warning: Empty update request for order {order_id}")

        updated_doc = ref.get() # Güncellenmiş belgeyi tekrar oku
        return safe_doc_to_dict(updated_doc)
    except Exception as e:
        print(f"Error updating order {order_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Sipariş güncellenemedi: {e}")
# --- GÜNCELLEME SONU ---

@router.delete("/{order_id}", response_model=dict) # response_model düzeltildi
def delete_order(order_id: str, current_user: dict = Depends(get_current_user)):
    """Belirli bir siparişi siler."""
    ref = db.collection("orders").document(order_id)
    if not ref.get().exists:
        raise HTTPException(status_code=404, detail="Sipariş bulunamadı")
    try:
        ref.delete()
        return {"message": "Sipariş başarıyla silindi"}
    except Exception as e:
        print(f"Error deleting order {order_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Sipariş silinemedi: {e}")

