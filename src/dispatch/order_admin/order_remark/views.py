from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from dispatch.order_admin.order import service as order_service
from . import service
from .models import OrderRemarkRead, OrderRemarkCreate, OrderRemarkUpdate
from dispatch.database import get_db

router = APIRouter()


@router.get("/{order_remark_id}", response_model=OrderRemarkRead)
def get_order_remark(order_remark_id: int, db: Session = Depends(get_db)):
    order_remark = service.get_order_remark_by_id(db, order_remark_id)
    if not order_remark:
        raise HTTPException(status_code=400, detail="Order remark not found")
    return order_remark


@router.get("/order/{order_id}", response_model=List[OrderRemarkRead])
def get_order_remark(order_id: int, db: Session = Depends(get_db)):
    order_remark = service.get_all_order_remarks_by_order_id(db, order_id)
    if not order_remark:
        raise HTTPException(status_code=400, detail="Order remark not found")
    return order_remark


@router.get("/", response_model=List[OrderRemarkRead])
def get_all_order_remarks(db: Session = Depends(get_db)):
    return service.get_all_order_remarks(db)


@router.post("/", response_model=OrderRemarkRead)
def create_order_remark(order_remark_data: OrderRemarkCreate, db: Session = Depends(get_db)):
    return service.create_order_remark(db, order_remark_data)


@router.put("/{order_remark_id}", response_model=OrderRemarkRead)
def update_order_remark(order_remark_id: int, order_remark_data: OrderRemarkUpdate, db: Session = Depends(get_db)):
    updated_remark = service.update_order_remark(db, order_remark_id, order_remark_data)
    if not updated_remark:
        raise HTTPException(status_code=400, detail="Order remark not found")
    return updated_remark


@router.delete("/{order_remark_id}", response_model=bool)
def delete_order_remark(order_remark_id: int, db: Session = Depends(get_db)):
    order_remark = service.get_order_remark_by_id(db, order_remark_id)
    if not order_remark:
        raise HTTPException(status_code=400, detail="Order remark not found")
    return service.delete_order_remark(db, order_remark_id)
