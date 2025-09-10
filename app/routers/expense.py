from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List
from app.models.expense import Expense
from app.database import SessionLocal, get_db
from app.schemas.expense import ExpenseCreate, ExpenseOut, ExpenseUpdate

router = APIRouter()

# DB bağlantısı (gerekiyorsa yeniden tanımlanabilir)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Tüm giderleri getir
@router.get("/expenses")
def get_expenses(db=Depends(get_db)):
    result = db.execute(text("SELECT * FROM expenses"))
    columns = result.keys()
    rows = [dict(zip(columns, row)) for row in result.fetchall()]
    return rows

# Gider tablosunun sütun isimlerini getir
@router.get("/expenses/columns")
def get_expense_columns(db=Depends(get_db)):
    result = db.execute(text("SHOW COLUMNS FROM expenses"))
    columns = [row[0] for row in result.fetchall()]
    return {"columns": columns}

# Yeni gider ekle
@router.post("/expenses", response_model=ExpenseOut)
def create_expense(expense: ExpenseCreate, db: Session = Depends(get_db)):
    db_expense = Expense(**expense.model_dump())
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense

# Gider sil
@router.delete("/expenses/{expense_id}")
def delete_expense(expense_id: int, db: Session = Depends(get_db)):
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    db.delete(expense)
    db.commit()
    return {"message": "Expense deleted successfully"}

# Gider güncelle
@router.put("/expenses/{expense_id}", response_model=ExpenseOut)
def update_expense(expense_id: int, updated_data: ExpenseUpdate, db: Session = Depends(get_db)):
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Gider bulunamadı")

    for key, value in updated_data.model_dump().items():
        setattr(expense, key, value)

    db.commit()
    db.refresh(expense)
    return expense