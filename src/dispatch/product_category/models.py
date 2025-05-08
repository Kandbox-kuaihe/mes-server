from typing import List, Optional
from datetime import datetime
from sqlalchemy import Column, Integer, String, Numeric
from sqlalchemy.sql.schema import ForeignKey, UniqueConstraint
from dispatch.database import Base
from dispatch.mill.models import MillRead
from dispatch.models import DispatchBase, TimeStampMixin
from sqlalchemy.orm import relationship
from sqlalchemy_utils import TSVectorType


class ProductCategory(Base, TimeStampMixin):
    """
    Model for product categories.
    """
    __tablename__ = 'product_category'

    id = Column(Integer, primary_key=True, autoincrement=True)
    mill_id = Column(Integer, ForeignKey('mill.id'), nullable=False)  # Assuming 'mill' is the referenced table
    mill = relationship("Mill", backref="mill_ProductCategory")

    code = Column(String, nullable=False)
    type = Column(String, nullable=True)
    desc = Column(String, nullable=True)
    dim1 = Column(Numeric(20, 10), nullable=True)
    dim2 = Column(Numeric(20, 10), nullable=True)
    dim3 = Column(Numeric(20, 10), nullable=True)
    dim4 = Column(Numeric(20, 10), nullable=True)

    __table_args__ = (
        UniqueConstraint('code', 'mill_id', name='product_category_code_mill_id'),
    )

    search_vector = Column(
        TSVectorType(
            "code",
            "type",
            weights={"code": "A", "type": "B"},
        )
    )

    # def __init__(self, **kwargs):
    #     super().__init__(**kwargs)
    #     # 生成 code 值
    #     self.code = f"{self.dim1}-{self.dim2}" if self.dim1 is not None and self.dim2 is not None else None


# Pydantic models...

class ProductCategoryBase(DispatchBase):
    mill_id: Optional[int] = None
    mill_code: Optional[str] = None
    mill: Optional[MillRead] = None
    code: Optional[str] = None
    type: Optional[str] = None
    desc: Optional[str] = None
    dim1: Optional[float] = None
    dim2: Optional[float] = None
    dim3: Optional[float] = None
    dim4: Optional[float] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ProductCategoryCreate(ProductCategoryBase):
    updated_by: Optional[str] = None


class ProductCategoryUpdate(ProductCategoryBase):
    updated_by: Optional[str] = None


class ProductCategoryRead(ProductCategoryBase):
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    updated_by: Optional[str] = None


class ProductCategoryPagination(DispatchBase):
    total: int
    items: List[ProductCategoryRead] = []
    itemsPerPage: int
    page: int
