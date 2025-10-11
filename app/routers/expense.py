from fastapi import APIRouter, HTTPException
from app.schemas.expense import ExpenseCreate, ExpenseUpdate, ExpenseOut
from app.services.firebase import db
from typing import List
from datetime import datetime
from uuid import uuid4

router = APIRouter(prefix="/expenses", tags=["Expenses"])

def safe_doc_to_dict(doc):
    """Firestore belgesini güvenli bir şekilde sözlüğe dönüştürür ve tarihleri formatlar."""
    if not doc.exists:
        return None
    
    data = doc.to_dict()
    
    # Tarih alanını kontrol et ve datetime ise ISO formatına çevir
    if "tarih" in data and data["tarih"] and isinstance(data["tarih"], datetime):
        data["tarih"] = data["tarih"].isoformat()

    data["id"] = doc.id
    return data

@router.get("/", response_model=List[ExpenseOut])
def get_expenses():
    try:
        expenses_stream = db.collection("expenses").stream()
        return [safe_doc_to_dict(doc) for doc in expenses_stream if doc.exists]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not fetch expenses: {e}")

@router.post("/", response_model=ExpenseOut)
def create_expense(expense: ExpenseCreate):
    try:
        expense_id = str(uuid4())
        ref = db.collection("expenses").document(expense_id)
        ref.set(expense.model_dump())
        new_doc = ref.get()
        return safe_doc_to_dict(new_doc)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not create expense: {e}")

@router.put("/{expense_id}", response_model=ExpenseOut)
def update_expense(expense_id: str, updated_data: ExpenseUpdate):
    ref = db.collection("expenses").document(expense_id)
    if not ref.get().exists:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    try:
        update_dict = updated_data.model_dump(exclude_unset=True)
        ref.update(update_dict)
        updated_doc = ref.get()
        return safe_doc_to_dict(updated_doc)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not update expense: {e}")

@router.delete("/{expense_id}")
def delete_expense(expense_id: str):
    ref = db.collection("expenses").document(expense_id)
    if not ref.get().exists:
        raise HTTPException(status_code=404, detail="Expense not found")
    try:
        ref.delete()
        return {"message": "Expense deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not delete expense: {e}")

