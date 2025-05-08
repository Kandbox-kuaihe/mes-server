from typing import List, Optional
from datetime import datetime, date

from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    BigInteger,
    Numeric,
    String,
    Date,
    DateTime,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import UniqueConstraint
from sqlalchemy_utils import TSVectorType

from dispatch.database import Base
from dispatch.models import TimeStampMixin, DispatchBase, BaseResponseModel


class OrderItemRemark(Base, TimeStampMixin):
    __tablename__ = 'order_item_remark'

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    order_item_id = Column(BigInteger, ForeignKey("order_item.id"), nullable=False)
    order_item = relationship("OrderItem", backref="order_item_remarks")

    type = Column(String, nullable=False)
    identifier = Column(String)
    text = Column(String)

    search_vector = Column(
        TSVectorType(
            "identifier",
            "text",
            weights={"identifier": "A", "text": "B"},
        )
    )


class OrderItemRemarkBase(DispatchBase):
    order_item_id: Optional[int] = None
    type: Optional[str] = None
    identifier: Optional[str] = None
    text: Optional[str] = None


class OrderItemRemarkCreate(OrderItemRemarkBase):
    pass


class OrderItemRemarkUpdate(OrderItemRemarkBase):
    pass


class OrderItemRemarkRead(OrderItemRemarkBase):

    id: int
    created_at: Optional[datetime] = None  # 创建时间
    updated_at: Optional[datetime] = None  # 更新时间


class OrderItemRemarkPagination(BaseResponseModel):
    total: int
    items: List[OrderItemRemarkRead] = []
    itemsPerPage: int
    page: int