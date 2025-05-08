from typing import List, Optional

from sqlalchemy import (
    Column,
    Float,
    ForeignKey,
    String,
    BigInteger,
    Integer,
    DateTime, Numeric
)

from typing import Optional
from dispatch.database import Base
from dispatch.models import TimeStampMixin, DispatchBase, BaseResponseModel
from sqlalchemy.sql.schema import UniqueConstraint
from sqlalchemy.orm import relationship

from dispatch.runout_admin.runout_list.models import RunoutRead
from dispatch.spec_admin.spec.models import SpecRead
from dispatch.cast.models import CastRead


class CoverEndUse(Base, TimeStampMixin):
    __tablename__ = 'cover_end_use'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    runout_id = Column(BigInteger, ForeignKey('runout.id'), nullable=False)
    runout = relationship("Runout", backref="runout_cover_end_use")
    spec_id = Column(BigInteger, ForeignKey('spec.id'), nullable=False)
    spec = relationship("Spec", backref="spec_cover_end_use")
    cast_id = Column(BigInteger, ForeignKey('cast.id'), nullable=True)
    cast = relationship("Cast", backref="cast_cover_end_use")
    tensile_score = Column(Integer, nullable=False)
    impact_score = Column(Integer, nullable=False)
    added_by = Column(String)
    comment = Column(String)
    auto_end_use_flag = Column(String)
    mill_id = Column(BigInteger, ForeignKey('mill.id'), nullable=False)
    mill = relationship("Mill", backref="mill_cover_end_use")
    __table_args__ = (
        UniqueConstraint("runout_id", "spec_id",  name="unique_key_runout_spec"),
    )

class CoverEndUseBase(BaseResponseModel):
    runout_id: Optional[int] = None
    spec_id: Optional[int] = None
    mill_id: Optional[int] = None
    tensile_score: Optional[int] = None
    impact_score: Optional[int] = None
    added_by: Optional[str] = "system"
    comment: Optional[str] = None


class CoverEndUseCreate(CoverEndUseBase):
    pass


class CoverEndUseUpdate(CoverEndUseBase):
    pass


class CoverEndUseRead(CoverEndUseBase, BaseResponseModel):
    id: int
    runout: Optional[RunoutRead] = None
    spec: Optional[SpecRead] = None
    cast: Optional[CastRead] = None


class CoverEndUsePagination(DispatchBase):
    total: int
    items: List[CoverEndUseRead] = []
    itemsPerPage: int
    page: int
