from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    Column,
    String,
    BigInteger,
    Numeric,
    ForeignKey,
)
from sqlalchemy.sql.schema import UniqueConstraint
from sqlalchemy_utils import TSVectorType

from dispatch.database import Base
from dispatch.mill.models import MillRead
from dispatch.models import TimeStampMixin, DispatchBase, BaseResponseModel
from sqlalchemy.orm import relationship


class SemiSizeDetail(Base,TimeStampMixin):
    __tablename__ = 'semi_size_detail'

    id = Column(BigInteger, primary_key=True,autoincrement=True)
    
    mill_id = Column(BigInteger, ForeignKey("mill.id"), nullable=False)
    mill = relationship("Mill", backref="mill_semi_size_detail")
    
    semi_size_id = Column(BigInteger, ForeignKey("semi_size.id"), nullable=False)
    # semi_size = relationship("SemiSize", backref="semi_size_semi_size_detail")

    length_mm = Column(Numeric(precision=20, scale=10), nullable=False)
    standard_weight_t = Column(Numeric(precision=20, scale=10))
    min_weight_t = Column(Numeric(precision=20, scale=10))
    max_weight_t = Column(Numeric(precision=20, scale=10))
    min_length_mm = Column(Numeric(precision=20, scale=10))
    max_length_mm = Column(Numeric(precision=20, scale=10))





class SemiSizeDetailBase(BaseResponseModel):
    mill_id: Optional[int] = None
    semi_size_id: Optional[int] = None
    length_mm: Optional[float] = None
    standard_weight_t : Optional[float] = None
    min_weight_t : Optional[float] = None
    max_weight_t : Optional[float] = None
    min_length_mm: Optional[float] = None
    max_length_mm: Optional[float] = None

class SemiSizeDetailCreate(SemiSizeDetailBase):
    pass


class SemiSizeDetailUpdate(SemiSizeDetailBase):
    pass


class SemiSizeDetailRead(SemiSizeDetailBase):
    id: int
    mill: Optional[MillRead] = None
    # semi_size: Optional[SemiSizeRead] = None


class SemiSizeDetailPagination(DispatchBase):
    total: int
    items: List[SemiSizeDetailRead] = []
    itemsPerPage: int
    page : int