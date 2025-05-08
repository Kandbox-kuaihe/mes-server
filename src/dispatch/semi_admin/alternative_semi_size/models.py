from typing import List, Optional
from datetime import datetime, date
from sqlalchemy import Column, Float, ForeignKey, String, BigInteger, Integer, DateTime, Date
from typing import Optional
from sqlalchemy.orm import relationship

from sqlalchemy_utils import TSVectorType

from dispatch.database import Base
from dispatch.mill.models import MillRead
from dispatch.semi_admin.semi_size.models import SemiSizeRead
from dispatch.models import TimeStampMixin, DispatchBase, BaseResponseModel

from sqlalchemy import Column, Integer, String, BigInteger, Numeric, ForeignKey
from dispatch.product_type.models import ProductTypeBase, ProductTypeRead


class AlternativeSemiSize(Base, TimeStampMixin):
    __tablename__ = "alternative_semi_size"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    product_type_id = Column(
        BigInteger,
        ForeignKey("product_type.id"),
        nullable=False,
    )
    product_type = relationship("ProductType", backref="product_type_alternative_semi_size")

    mill_id = Column(
        BigInteger,
        ForeignKey("mill.id"),
        nullable=False,
    )
    mill = relationship("Mill", backref="mill_alternative_semi_size")

    semi_size_id = Column(
        BigInteger,
        ForeignKey("semi_size.id"),
        nullable=False,
    )
    semi_size = relationship("SemiSize", backref="semi_size_alternative_semi_size")



    order_over_tol = Column(Numeric(20, 10), nullable=True)
    order_under_tol = Column(Numeric(20, 10), nullable=True)
    stock_over_tol = Column(Numeric(20, 10), nullable=True)
    stock_under_tol = Column(Numeric(20, 10), nullable=True)

    semi_type = Column(String, nullable=True)
    semi_width = Column(Numeric(20, 10), nullable=False)
    thickness = Column(Numeric(20, 10), nullable=False)

    opt_length = Column(Numeric(20, 10), nullable=True)
    weight = Column(Numeric(20, 10), default=0, nullable=False)
    max_length = Column(Numeric(20, 10), nullable=True)
    min_length = Column(Numeric(20, 10), nullable=True)

    not_to_sched = Column(String, nullable=True)
    source = Column(String)
    semi_length = Column(Numeric(20, 10), nullable=True)
    rank_seq = Column(Integer, nullable=False)


class AlternativeSemiSizeBase(BaseResponseModel):
    product_type_id: Optional[int] = None
    product_type: Optional[ProductTypeRead] = None
    mill_id: Optional[int] = None
    mill: Optional[MillRead] = None
    semi_size_id:Optional[int] = None
    semi_size:Optional[SemiSizeRead] = None
    semi_width: Optional[float] = None
    order_over_tol: Optional[int] = None
    order_under_tol: Optional[int] = None
    stock_over_tol: Optional[int] = None
    stock_under_tol: Optional[int] = None
    thickness: Optional[float] = None
    opt_length: Optional[float] = None
    weight: Optional[float] = None
    max_length: Optional[float] = None
    min_length: Optional[float] = None
    not_to_sched: Optional[str] = None
    source: Optional[str] = None
    semi_length: Optional[float] = None
    rank_seq: Optional[int] = None


class AlternativeSemiSizeCreate(AlternativeSemiSizeBase):
    pass


class AlternativeSemiSizeUpdate(AlternativeSemiSizeBase):
    id: Optional[int] = None


class AlternativeSemiSizeRead(AlternativeSemiSizeBase):
    id: int
    flex_form_data: Optional[dict]


class AlternativeSemiSizePagination(DispatchBase):
    total: int
    items: List[AlternativeSemiSizeRead] = []
    itemsPerPage: int
    page: int


class ReworkBase(DispatchBase):
    rework_type: Optional[str] = None
    rework_due_date: Optional[date] = None
    rework_finish_date: Optional[date] = None
    area_id: Optional[int] = None


class ReworkRead(ReworkBase):
    id: int


class ReworkUpdate(ReworkBase):
    ids: List[int]


class ReworkStatusBase(DispatchBase):
    rework_status: Optional[str] = None


class ReworkStatusUpdate(ReworkStatusBase):
    pass


class ReworkStatusRead(ReworkStatusBase):
    id: int
