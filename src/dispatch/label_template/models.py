from typing import List, Optional
from datetime import datetime, date
from sqlalchemy import Column, Float, ForeignKey, String, BigInteger, Integer, DateTime, Date
from typing import Optional
from sqlalchemy.orm import relationship

from sqlalchemy_utils import TSVectorType

from dispatch.database import Base
from dispatch.mill.models import MillRead
from dispatch.models import TimeStampMixin, DispatchBase, BaseResponseModel

from sqlalchemy import Column, Integer, String, BigInteger, Numeric, ForeignKey
from sqlalchemy.sql.schema import UniqueConstraint


class LabelTemplate(Base, TimeStampMixin):
    __tablename__ = "label_template"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    type = Column(String, nullable=True)
    code = Column(String, nullable=False)
    template = Column(String, nullable=True)
    record_type = Column(String, nullable=True)  # 记录类型
    date = Column(String, nullable=True)         # 日期
    __table_args__ = (
        UniqueConstraint('code', name='unique_label_template_code'),
    )


class LabelTemplateBase(BaseResponseModel):
    type: Optional[str] = None
    code: Optional[str] = None
    template: Optional[str] = None
    record_type: Optional[str] = None  # 记录类型
    date: Optional[str] = None         # 日期


class LabelTemplateCreate(LabelTemplateBase):
    pass


class LabelTemplateUpdate(LabelTemplateBase):
    id: Optional[int] = None
    pass


class LabelTemplateRead(LabelTemplateBase, BaseResponseModel):
    id: int
    flex_form_data: Optional[dict]


class LabelTemplatePagination(DispatchBase):
    total: int
    items: List[LabelTemplateRead] = []
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
