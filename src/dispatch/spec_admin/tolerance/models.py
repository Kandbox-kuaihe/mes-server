from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    Column,
    String,
    BigInteger,
    ForeignKey,
)
from sqlalchemy.sql.schema import UniqueConstraint
from sqlalchemy_utils import TSVectorType

from dispatch.database import Base
from dispatch.mill.models import MillRead
from dispatch.models import TimeStampMixin, DispatchBase
from sqlalchemy.orm import relationship


class Tolerance(Base,TimeStampMixin):
    __tablename__ = 'tolerance'
    id = Column(BigInteger, primary_key=True,autoincrement=True)
    mill_id = Column(BigInteger, ForeignKey("mill.id"), nullable=False)
    mill = relationship("Mill", backref="mill_Tolerance")
    code = Column(String, nullable=False)
    type = Column(String, nullable=True)
    name = Column(String, nullable=True)
    desc = Column(String, nullable=True)

    search_vector = Column(
        TSVectorType(
            "code",
            "name",
            weights={"code": "A", "name": "B"},
        )
    )

    __table_args__ = (UniqueConstraint('code', name='uix_tolerance_code'),)


class ToleranceBase(DispatchBase):
    mill_id: Optional[int] = None
    code: str=""
    type: Optional[str]=""
    name: Optional[str]=""
    desc: Optional[str]=""


class ToleranceCreate(ToleranceBase):
    pass


class ToleranceUpdate(ToleranceBase):
    pass


class ToleranceRead(ToleranceBase):
    id: int
    mill: Optional[MillRead] = None


class TolerancePagination(DispatchBase):
    total: int
    items: List[ToleranceRead] = []
    itemsPerPage: int
    page : int