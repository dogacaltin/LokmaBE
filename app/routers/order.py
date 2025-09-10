from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List
from app.models.order import Order
from app.database import SessionLocal
from app.schemas.order import OrderCreate, OrderOut, OrderUpdate
from datetime import datetime
from app.database import get_db
from fastapi import HTTPException


router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


router = APIRouter()

@router.get("/orders")
def get_orders(db=Depends(get_db)):
    result = db.execute(text("SELECT * FROM orders"))
    columns = result.keys()
    rows = [dict(zip(columns, row)) for row in result.fetchall()]
    return rows

@router.get("/orders/columns")
def get_order_columns(db=Depends(get_db)):
    result = db.execute(text("SHOW COLUMNS FROM orders"))
    columns = [row[0] for row in result.fetchall()]
    return {"columns": columns}



@router.post("/orders")
def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    db_order = Order(**order.model_dump())
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order



@router.delete("/orders/{order_id}")
def delete_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    db.delete(order)
    db.commit()
    return {"message": "Order deleted successfully"}

@router.put("/orders/{order_id}", response_model=OrderOut)
def update_order(order_id: int, updated_data: OrderUpdate, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Sipariş bulunamadı")

    for key, value in updated_data.model_dump().items():
        setattr(order, key, value)

    db.commit()
    db.refresh(order)
    return order