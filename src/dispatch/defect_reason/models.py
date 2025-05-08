from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    Column,
    Float,
    String,
    BigInteger,
)

from sqlalchemy.sql.schema import UniqueConstraint
from sqlalchemy_utils import TSVectorType

from dispatch.database import Base
from dispatch.mill.models import MillRead
from dispatch.models import TimeStampMixin, DispatchBase, BaseResponseModel
from sqlalchemy.orm import relationship
from sqlalchemy import  ForeignKey


class DefectReason(Base, TimeStampMixin):
    __tablename__ = 'defect_reason'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    code = Column(String, nullable=False)
    name = Column(String, nullable=False)
    type = Column(String, nullable=True)
    desc = Column(String, nullable=True)
    required_roles = Column(String, nullable=True)

    mill_id = Column(BigInteger, ForeignKey("mill.id"), nullable=False, )
    mill = relationship("Mill", backref="mill_DefectReason")
    search_vector = Column(
        TSVectorType(
            "code",
            "type",
            weights={"code": "A", "type": "B",},
        )
    )

    __table_args__ = (UniqueConstraint('mill_id', 'code', 'type', name='unique_defect_reason'),)


class DefectReasonBase(BaseResponseModel):
    code: str = ""
    name: str = ""
    type: Optional[str] = ""
    desc: Optional[str] = ""
    required_roles : Optional[str] = ""    
    mill_id: Optional[int] = None



class DefectReasonCreate(DefectReasonBase):
    pass


class DefectReasonUpdate(DefectReasonBase):
    id: int


class DefectReasonRead(DefectReasonBase,BaseResponseModel):
    id: int
    mill: Optional[MillRead] = None


class DefectReasonPagination(DispatchBase):
    total: int
    items: List[DefectReasonRead] = []
    itemsPerPage: int
    page: int
