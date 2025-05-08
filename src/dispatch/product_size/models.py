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

from dispatch.mill.models import MillRead
from dispatch.product_category.models import ProductCategoryRead
from dispatch.product_class.models import ProductClassRead


class ProductSize(Base,TimeStampMixin):
    __tablename__ = 'product_size'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    code = Column(String, nullable=False)
    
    mill_id = Column(BigInteger, ForeignKey("mill.id"), nullable=False)
    mill = relationship("Mill", backref="mill_product_size")

    product_category_id = Column(BigInteger, ForeignKey("product_category.id"))
    product_category = relationship("ProductCategory", backref="product_category_product_size")

    product_class_id = Column(BigInteger, ForeignKey("product_class.id"))
    product_class = relationship("ProductClass", backref="product_class_product_size")

    type = Column(String)
    desc = Column(String)
    dim1 = Column(Numeric(20, 10), default=0, nullable=False)
    dim2 = Column(Numeric(20, 10), default=0, nullable=False)
    product_code = Column(String, nullable=False)
    roll_ref_code = Column(String)

    search_vector = Column(
        TSVectorType(
            "code",
            weights={"code": "A"},
        )
    )

    __table_args__ = (
        UniqueConstraint('mill_id', 'code', name='product_size_unique_key_code_mill_id'),
    )


class ProductSizeBase(BaseResponseModel):
    code: str
    mill_id: Optional[int] = None
    mill_code: Optional[str] = None
    product_category_id: Optional[int] = None
    product_class_id: Optional[int] = None
    type: Optional[str] = None
    desc: Optional[str] = None
    dim1: Optional[float] = None
    dim2: Optional[float] = None
    product_code: Optional[str] = None
    roll_ref_code: Optional[str] = None


class ProductSizeCreate(ProductSizeBase):
    pass


class ProductSizeUpdate(ProductSizeBase):
    pass


class ProductSizeRead(ProductSizeBase):
    id: int
    mill: Optional[MillRead] = None
    product_category: Optional[ProductCategoryRead] = None
    product_class: Optional[ProductClassRead] = None

class ProductSizePagination(DispatchBase):
    total: int
    items: List[ProductSizeRead] = []
    itemsPerPage: int
    page : int