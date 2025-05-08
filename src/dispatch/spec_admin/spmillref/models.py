from typing import List, Optional
from pydantic import  Field

from sqlalchemy import (
    Column,
    Float,
    ForeignKey,
    String,
    BigInteger,
    Integer,
)
from datetime import datetime
from typing import Dict, Optional

from sqlalchemy.sql.schema import UniqueConstraint
from sqlalchemy_utils import TSVectorType

from dispatch.database import Base
from dispatch.mill.models import MillRead
from dispatch.models import TimeStampMixin, DispatchBase,BaseResponseModel

from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, BigInteger, Numeric, ForeignKey
from sqlalchemy import Column, Integer, CHAR, Text
from pydantic import BaseModel, Field, conint
from typing import Optional, List
from dispatch.spec_admin.spec.models import SpecRead



# (Base,TimeStampMixin):



class Spmillref(Base,TimeStampMixin):

    __tablename__ = 'spmillref'

    id = Column(BigInteger, primary_key=True,autoincrement=True)
    spec_id = Column(BigInteger, ForeignKey("spec.id"), nullable=False)
    spec = relationship("Spec", backref="spec_spmillref")
    mill_id = Column(BigInteger, ForeignKey("mill.id"), nullable=False)
    mill = relationship("Mill", backref="mill_spmillref", foreign_keys=[mill_id])
    other_mill_id = Column(BigInteger, ForeignKey("mill.id"), nullable=False)
    other_mill = relationship("Mill", backref="other_mill_spmillref", foreign_keys=[other_mill_id])
    thick_from = Column(Numeric(20, 10), nullable=False)
    thick_to = Column(Numeric(20, 10), nullable=False)
    spec_code = Column(String, nullable=False)

    __table_args__ = (UniqueConstraint('spec_id', 'thick_from', 'thick_to', name='spmillref_uix_spec_thick_from_to'),)



# BaseResponseModel

class SpmillrefResponse(BaseResponseModel):
    spec_id: Optional[int] = None
    spec: Optional[SpecRead] = None
    mill_id: Optional[int] = None
    mill: Optional[MillRead] = None
    other_mill_id: Optional[int] = None
    other_mill: Optional[MillRead] = None
    thick_from: Optional[float] = None
    thick_to: Optional[float] = None
    spec_code: Optional[str] = None

# Spmillref Response
class SpmillrefCreate(SpmillrefResponse):
    pass

class SpmillrefUpdate(SpmillrefResponse):
    pass

class SpmillrefRead(SpmillrefResponse):
    id: int

class SpmillrefPagination(DispatchBase):
    total: int
    items: List[SpmillrefRead] = []
    itemsPerPage: int
    page: int

class SpmillrefUpdateNew(DispatchBase):
    id: int
    data: dict


class SpmillrefBySpecCode(DispatchBase):
    spec_code: str
    page: int
    itemsPerPage: int


class SpmillrefCopyToCode(DispatchBase):
    before_code: str
    after_code: str