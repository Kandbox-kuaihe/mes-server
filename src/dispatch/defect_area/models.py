from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    Column,
    Float,
    String,
    BigInteger,
    ForeignKey,
    Numeric
)

from dispatch.database import Base
from dispatch.mill.models import MillRead
from dispatch.label_template.models import LabelTemplateRead
from dispatch.models import TimeStampMixin, DispatchBase, BaseResponseModel
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import UniqueConstraint


class DefectArea(Base, TimeStampMixin):
    __tablename__ = 'defect_area'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    section_code = Column(String, nullable=True)
    weight = Column(Numeric(20, 10), nullable=True)
    thickness = Column(Numeric(20, 10), nullable=True)
    short_code = Column(String, nullable=True)
    quality_code = Column(String, nullable=True)
    cast_supplier_code = Column(String, nullable=True)
    shift_code = Column(String, nullable=True)
    defective_weight = Column(Numeric(20, 10), nullable=True)
    defect_code = Column(String, nullable=False)
    track_code = Column(String, nullable=True)
    prime_untested = Column(String, nullable=True)
    source = Column(String, nullable=True)
    old_current_week = Column(String, nullable=True)

    mill_id = Column(BigInteger, ForeignKey("mill.id"), nullable=True, )
    area_id = Column(BigInteger, ForeignKey("area.id"), nullable=True, )
    mill = relationship("Mill", backref="mill_DefectArea")
    label_template_id = Column(BigInteger, ForeignKey("label_template.id"), nullable=True, )
    label_template = relationship("LabelTemplate", backref="label_template_defect_area")
    __table_args__ = (
        UniqueConstraint('track_code', name='unique_track_code'),
    )


class DefectAreaBase(BaseResponseModel):
    section_code: Optional[str] = None
    weight: Optional[float] = None
    thickness: Optional[float] = None
    short_code: Optional[str] = None
    quality_code: Optional[str] = None
    cast_supplier_code: Optional[str] = None
    shift_code: Optional[str] = None
    defective_weight: Optional[float] = None
    defect_code: Optional[str] = None
    track_code: Optional[str] = None
    prime_untested: Optional[str] = None
    area_id: Optional[int] = None
    mill_id: Optional[int] = None
    mill: Optional[MillRead] = None
    label_template_id: Optional[int] = None
    label_template: Optional[LabelTemplateRead] = None


class DefectAreaCreate(DefectAreaBase):
    updated_at: Optional[datetime] = datetime.now()
    created_at: Optional[datetime] = datetime.now()


class DefectAreaUpdate(DefectAreaBase):
    updated_at: Optional[datetime] = datetime.now()


class DefectAreaRead(DefectAreaBase, BaseResponseModel):
    id: int


class DefectAreaPagination(DispatchBase):
    total: int
    items: List[DefectAreaRead] = []
    itemsPerPage: int
    page: int
