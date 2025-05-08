from typing import List, Optional
from .models import OrderRemark, OrderRemarkCreate, OrderRemarkUpdate, OrderRemarkRead
from dispatch.rolling.rolling_list import service as rolling_service
from dispatch.mill import service as mill_service
from lxml import etree
from sqlalchemy import or_, and_, select
from sqlalchemy.orm import Session


def get(*, db_session, id: int) -> Optional[OrderRemark]:
    """Returns an order given an order id."""
    return db_session.query(OrderRemark).filter(OrderRemark.id == id).one_or_none()


def get_by_order_and_type(*, db_session, order_id: int, type: str) -> Optional[OrderRemark]:
    return db_session.query(OrderRemark).filter(
        and_(
            OrderRemark.order_id == order_id,
            OrderRemark.type == type
        )
    ).all()


def get_order_remark_by_id(db: Session, order_remark_id: int) -> Optional[OrderRemark]:
    """
    根据 ID 获取单个订单备注。
    """
    return db.query(OrderRemark).filter(OrderRemark.id == order_remark_id).first()


def get_order_remark_by_identifier(db: Session, identifier: str) -> Optional[OrderRemark]:
    """
    根据唯一标识符获取单个订单备注。
    """
    return db.query(OrderRemark).filter(OrderRemark.identifier == identifier).first()


def get_all_order_remarks(db: Session) -> List[OrderRemark]:
    """
    获取所有订单备注。
    """
    return db.query(OrderRemark).all()


def get_all_order_remarks_by_order_id(db: Session, order_id: int) -> List[OrderRemark]:
    return db.query(OrderRemark).filter(OrderRemark.order_id == order_id).all()


def create_order_remark(db: Session, order_remark_data: OrderRemarkCreate) -> OrderRemark:
    """
    创建一个新的订单备注。
    """
    db_order_remark = OrderRemark(
        **order_remark_data.model_dump(exclude_unset=True)
    )
    db.add(db_order_remark)
    db.commit()
    db.refresh(db_order_remark)
    return db_order_remark


def update_order_remark(db: Session, order_remark_id: int, order_remark_data: OrderRemarkUpdate) -> OrderRemark:
    """
    更新订单备注。
    """
    order_remark = db.query(OrderRemark).filter(OrderRemark.id == order_remark_id).first()
    if not order_remark:
        return None

    for field, value in order_remark_data.model_dump(exclude_unset=True).items():
        setattr(order_remark, field, value)

    db.commit()
    db.refresh(order_remark)
    return order_remark


def delete_order_remark(db: Session, order_remark_id: int) -> bool:
    """
    根据 ID 删除订单备注。
    """
    db_order_remark = get_order_remark_by_id(db, order_remark_id)
    db_order_remark.is_deleted = 1
    db.add(db_order_remark)
    db.commit()
    return True
