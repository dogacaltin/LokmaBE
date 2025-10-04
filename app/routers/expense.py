from fastapi import APIRouter, HTTPException
from uuid import uuid4
from typing import List
from app.schemas.expense import ExpenseCreate, ExpenseOut, ExpenseUpdate
from app.services.firebase import db  # firestore.client()

router = APIRouter(prefix="/expenses", tags=["Expenses"])

# ✅ Tüm giderleri getir
@router.get("/", response_model=List[ExpenseOut])
def get_expenses():
    expenses = db.collection("expenses").stream()
    return [
        {**doc.to_dict(), "id": doc.id}
        for doc in expenses
    ]

# ✅ Tablonun "sütun" isimlerini getir (örnek belgeye bakar)
@router.get("/columns")
def get_expense_columns():
    sample_doc = db.collection("expenses").limit(1).stream()
    for doc in sample_doc:
        return {"columns": list(doc.to_dict().keys())}
    return {"columns": []}

# ✅ Yeni gider ekle
@router.post("/", response_model=ExpenseOut)
def create_expense(expense: ExpenseCreate):
    expense_id = str(uuid4())
    db.collection("expenses").document(expense_id).set(expense.model_dump())
    return {**expense.model_dump(), "id": expense_id}

# ✅ Tek gider getir
@router.get("/{expense_id}", response_model=ExpenseOut)
def get_expense(expense_id: str):
    doc = db.collection("expenses").document(expense_id).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Expense not found")
    return {**doc.to_dict(), "id": doc.id}

# ✅ Gider güncelle
@router.put("/{expense_id}", response_model=ExpenseOut)
def update_expense(expense_id: str, updated_data: ExpenseUpdate):
    ref = db.collection("expenses").document(expense_id)
    if not ref.get().exists:
        raise HTTPException(status_code=404, detail="Expense not found")
    ref.update(updated_data.model_dump(exclude_unset=True))
    updated_doc = ref.get()
    return {**updated_doc.to_dict(), "id": expense_id}

# ✅ Gider sil
@router.delete("/{expense_id}")
def delete_expense(expense_id: str):
    ref = db.collection("expenses").document(expense_id)
    if not ref.get().exists:
        raise HTTPException(status_code=404, detail="Expense not found")
    ref.delete()
    return {"message": "Expense deleted successfully"}