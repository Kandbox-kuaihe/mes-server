from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    Column,
    String,
    Integer,
    BigInteger,
    ForeignKey,
)
from sqlalchemy.sql.schema import UniqueConstraint
from sqlalchemy_utils import TSVectorType

from dispatch.database import Base
from dispatch.mill.models import MillRead
from dispatch.models import TimeStampMixin, DispatchBase
from sqlalchemy.orm import relationship

from dispatch.semi_admin.semi_size_detail.models import SemiSizeDetail, SemiSizeDetailRead


class SemiSize(Base,TimeStampMixin):
    __tablename__ = 'semi_size'
    id = Column(BigInteger, primary_key=True,autoincrement=True)
    mill_id = Column(BigInteger, ForeignKey("mill.id"), nullable=False)
    mill = relationship("Mill", backref="mill_semi_size")
    mill_type = Column(String,nullable=True)
    semi_type = Column(String, nullable=True)
    code = Column(String, unique=True, nullable=False)
    width_mm = Column(Integer, nullable=False)
    thick_mm = Column(Integer, nullable=False)
    norm_suffix = Column(String, nullable=True)
    semi_size_detail = relationship("SemiSizeDetail", uselist=False,
                                  primaryjoin="SemiSize.id == SemiSizeDetail.semi_size_id",
                                  lazy="joined")
    search_vector = Column(
        TSVectorType(
            "semi_type",
            "code",
            weights={"semi_type": "A", "code": "B"},
        )
    )

    __table_args__ = (
        UniqueConstraint('code', name='uix_code'),)


class SemiSizeBase(DispatchBase):
    mill_id: Optional[int] = None
    code: Optional[str] = None
    semi_type: Optional[str] = None
    width_mm: Optional[int] = None
    thick_mm: Optional[int] = None
    norm_suffix:Optional[str] = None

class SemiSizeCreate(SemiSizeBase):
    pass


class SemiSizeUpdate(SemiSizeBase):
    pass


class SemiSizeRead(SemiSizeBase):
    id: int
    mill: Optional[MillRead] = None
    semi_size_detail: Optional[SemiSizeDetailRead] = None


class SemiSizePagination(DispatchBase):
    total: int
    items: List[SemiSizeRead] = []
    itemsPerPage: int
    page : int