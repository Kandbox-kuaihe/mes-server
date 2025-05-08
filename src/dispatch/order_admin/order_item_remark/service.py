from typing import List, Optional
from .models import OrderItemRemark, OrderItemRemarkCreate, OrderItemRemarkUpdate, OrderItemRemarkRead
from sqlalchemy import or_, and_, select
from sqlalchemy.orm import Session


def get(*, db_session, id: int) -> Optional[OrderItemRemark]:
    """Returns an order given an order id."""
    return db_session.query(OrderItemRemark).filter(OrderItemRemark.id == id).one_or_none()


def get_by_order_item_and_type(*, db_session, order_item_id: int, type: str) -> Optional[OrderItemRemark]:
    return db_session.query(OrderItemRemark).filter(
        and_(
            OrderItemRemark.order_item_id == order_item_id,
            OrderItemRemark.type == type
        )
    ).all()


def get_order_item_remark_by_id(db: Session, order_item_remark_id: int) -> Optional[OrderItemRemark]:
    return db.query(OrderItemRemark).filter(OrderItemRemark.id == order_item_remark_id).first()


def get_order_item_remark_by_identifier(db: Session, identifier: str) -> Optional[OrderItemRemark]:
    return db.query(OrderItemRemark).filter(OrderItemRemark.identifier == identifier).first()


def get_all_order_item_remarks(db: Session) -> List[OrderItemRemark]:
    return db.query(OrderItemRemark).all()


def get_all_order_item_remarks_by_order_item_id(db: Session, order_item_id: int) -> List[OrderItemRemark]:
    return db.query(OrderItemRemark).filter(OrderItemRemark.order_item_id == order_item_id).all()


def create_order_item_remark(db: Session, order_item_remark_data: OrderItemRemarkCreate) -> OrderItemRemark:
    db_order_item_remark = OrderItemRemark(
        **order_item_remark_data.model_dump(exclude_unset=True)
    )
    db.add(db_order_item_remark)
    db.commit()
    db.refresh(db_order_item_remark)
    return db_order_item_remark


def update_order_item_remark(db: Session, order_item_remark_id: int,
                             order_item_remark_data: OrderItemRemarkUpdate) -> OrderItemRemark:
    order_item_remark = db.query(OrderItemRemark).filter(OrderItemRemark.id == order_item_remark_id).first()
    if not order_item_remark:
        return None

    for field, value in order_item_remark_data.model_dump(exclude_unset=True).items():
        setattr(order_item_remark, field, value)

    db.commit()
    db.refresh(order_item_remark)
    return order_item_remark


def delete_order_item_remark(db: Session, order_item_remark_id: int) -> bool:
    db_order_item_remark = get_order_item_remark_by_id(db, order_item_remark_id)
    if not db_order_item_remark:
        return False

    db_order_item_remark.is_deleted = 1  # 假设模型中有 `is_deleted` 字段用于软删除
    db.add(db_order_item_remark)
    db.commit()
    return True
