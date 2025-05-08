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
from dispatch.spec_admin.tolerance.models import ToleranceRead
from dispatch.models import TimeStampMixin, DispatchBase, BaseResponseModel
from sqlalchemy.orm import relationship


class ToleranceDetail(Base,TimeStampMixin):
    __tablename__ = 'tolerance_detail'

    id = Column(BigInteger, primary_key=True,autoincrement=True)
    
    mill_id = Column(BigInteger, ForeignKey("mill.id"), nullable=False)
    mill = relationship("Mill", backref="mill_tolerance_detail")
    
    tolerance_id = Column(BigInteger, ForeignKey("tolerance.id"), nullable=False)
    tolerance = relationship("Tolerance", backref="tolerance_tolerance_detail")

    bar_loc_code = Column(String, nullable=True)
    value_min = Column(Numeric(precision=20, scale=10))
    value_max = Column(Numeric(precision=20, scale=10))
    diff_actual_min = Column(Numeric(precision=20, scale=10))
    diff_actual_max = Column(Numeric(precision=20, scale=10))
    diff_percent_min = Column(Numeric(precision=20, scale=10))
    diff_percent_max = Column(Numeric(precision=20, scale=10))

    search_vector = Column(
        TSVectorType(
            "bar_loc_code",
            weights={"bar_loc_code": "A"},
        )
    )

    __table_args__ = (UniqueConstraint('tolerance_id', 'bar_loc_code', 'value_min', name='uix_tolerance_id_bar_loc_code_value_min'),)


class ToleranceDetailBase(BaseResponseModel):
    mill_id: Optional[int] = None
    tolerance_id: Optional[int] = None
    bar_loc_code: Optional[str] = None
    value_min: Optional[float] = None
    value_max: Optional[float] = None
    diff_actual_min: Optional[float] = None
    diff_actual_max: Optional[float] = None
    diff_percent_min: Optional[float] = None
    diff_percent_max: Optional[float] = None


class ToleranceDetailCreate(ToleranceDetailBase):
    pass


class ToleranceDetailUpdate(ToleranceDetailBase):
    pass


class ToleranceDetailRead(ToleranceDetailBase):
    id: int
    mill: Optional[MillRead] = None
    tolerance: Optional[ToleranceRead] = None


class ToleranceDetailPagination(DispatchBase):
    total: int
    items: List[ToleranceDetailRead] = []
    itemsPerPage: int
    page : int