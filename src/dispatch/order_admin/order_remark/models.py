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
from dispatch.order_admin.order.models import OrderRead


class OrderRemark(Base,TimeStampMixin):
    __tablename__ = 'order_remark'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    
    order_id = Column(BigInteger, ForeignKey("order.id"), nullable=False)
    order = relationship("Order", backref="order_remarks")

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


class OrderRemarkBase(DispatchBase):
    order_id: Optional[int] = None
    type: Optional[str] = None
    identifier: Optional[str] = None
    text: Optional[str] = None



class OrderRemarkCreate(OrderRemarkBase):
    pass


class OrderRemarkUpdate(OrderRemarkBase):
    pass


class OrderRemarkRead(OrderRemarkBase):
    id: int
    created_at: Optional[datetime] = None  # 创建时间
    updated_at: Optional[datetime] = None  # 更新时间
    order: Optional[OrderRead] = None


class OrderRemarkPagination(BaseResponseModel):
    total: int
    items: List[OrderRemarkRead] = []
    itemsPerPage: int
    page: int
