from datetime import datetime
from typing import List, Optional

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import UniqueConstraint
from dispatch.database import Base
from dispatch.models import DispatchBase, BaseResponseModel, TimeStampMixin
from dispatch.mill.models import Mill, MillRead
from sqlalchemy_utils import TSVectorType


class ProductClass(Base, TimeStampMixin):
    __tablename__ = "product_class"
    __table_args__ = (
        UniqueConstraint('code', 'mill_id', name='product_class_code_mill_id'),
    )
    id = Column(Integer, primary_key=True)
    mill_id = Column(Integer, ForeignKey("mill.id"), nullable=False)  # 外键，指向 Mill 表
    code = Column(String, nullable=False)  # 唯一键
    type = Column(String, nullable=True)
    desc = Column(String, nullable=True)

    mill = relationship("Mill", foreign_keys=[mill_id])  # 设置外键关系

    search_vector = Column(
        TSVectorType(
            "code",
            "type",
            weights={"code": "A", "type": "B"},
        )
    )


class ProductClassBase(BaseResponseModel):
    mill_id: Optional[int] = None
    code: Optional[str] = None
    type: Optional[str] = None
    desc: Optional[str] = None
    mill: Optional[MillRead] = None
    mill_code: Optional[str] = None


class ProductClassCreate(ProductClassBase):
    pass


class ProductClassUpdate(ProductClassBase):
    pass


class ProductClassRead(ProductClassBase):
    id: int


class ProductClassPagination(DispatchBase):
    total: int
    items: List[ProductClassRead] = []
    itemsPerPage: int
    page: int
