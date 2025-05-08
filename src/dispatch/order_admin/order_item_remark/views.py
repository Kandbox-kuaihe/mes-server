from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from . import service
from .models import OrderItemRemarkRead, OrderItemRemarkCreate, OrderItemRemarkUpdate
from dispatch.database import get_db

router = APIRouter()


@router.get("/{order_item_remark_id}", response_model=OrderItemRemarkRead)
def get_order_item_remark(order_item_remark_id: int, db: Session = Depends(get_db)):
    """根据 ID 获取单个订单项备注。"""
    order_item_remark = service.get_order_item_remark_by_id(db, order_item_remark_id)
    if not order_item_remark:
        raise HTTPException(status_code=400, detail="Order item remark not found")
    return order_item_remark


@router.get("/order_item/{order_item_id}", response_model=List[OrderItemRemarkRead])
def get_order_item_remarks_by_order_item_id(order_item_id: int, db: Session = Depends(get_db)):
    """根据订单项 ID 获取所有关联的订单项备注。"""
    order_item_remarks = service.get_all_order_item_remarks_by_order_item_id(db, order_item_id)
    if not order_item_remarks:
        raise HTTPException(status_code=400, detail="No order item remarks found for the given order item ID")
    return order_item_remarks


@router.get("/", response_model=List[OrderItemRemarkRead])
def get_all_order_item_remarks(db: Session = Depends(get_db)):
    """获取所有订单项备注。"""
    return service.get_all_order_item_remarks(db)


@router.post("/", response_model=OrderItemRemarkRead)
def create_order_item_remark(order_item_remark_data: OrderItemRemarkCreate, db: Session = Depends(get_db)):
    """创建一个新的订单项备注。"""
    return service.create_order_item_remark(db, order_item_remark_data)


@router.put("/{order_item_remark_id}", response_model=OrderItemRemarkRead)
def update_order_item_remark(order_item_remark_id: int, order_item_remark_data: OrderItemRemarkUpdate, db: Session = Depends(get_db)):
    """更新订单项备注。"""
    updated_remark = service.update_order_item_remark(db, order_item_remark_id, order_item_remark_data)
    if not updated_remark:
        raise HTTPException(status_code=400, detail="Order item remark not found")
    return updated_remark


@router.delete("/{order_item_remark_id}", response_model=bool)
def delete_order_item_remark(order_item_remark_id: int, db: Session = Depends(get_db)):
    """根据 ID 删除订单项备注。"""
    order_item_remark = service.get_order_item_remark_by_id(db, order_item_remark_id)
    if not order_item_remark:
        raise HTTPException(status_code=400, detail="Order item remark not found")
    return service.delete_order_item_remark(db, order_item_remark_id)