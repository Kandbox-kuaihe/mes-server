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



class Spbend(Base,TimeStampMixin):

    __tablename__ = 'spbend'

    id = Column(BigInteger, primary_key=True,autoincrement=True)
    mill_id = Column(BigInteger, ForeignKey("mill.id"), nullable=False)
    mill = relationship("Mill", backref="mill_Spbend")
    
    
    spec_id = Column(BigInteger, ForeignKey("spec.id"), nullable=False)
    spec = relationship("Spec", backref="spec_Spbend")
    
    thick_from = Column(Numeric(precision=20, scale=10), nullable=False)
    thick_to = Column(Numeric(precision=20, scale=10), nullable=False)
    info_only = Column(String)
    direction = Column(String)
    angle = Column(String)
    diameter_mm = Column(Numeric(precision=20, scale=10), nullable=False)
    heat_code = Column(String)
    freq = Column(String)
    fio = Column(String)

    __table_args__ = (UniqueConstraint('spec_id', 'thick_from', 'thick_to', name='Spbend_uix_spec_thick_from_to'),)



# BaseResponseModel

class SpbendResponse(BaseResponseModel):
    mill_id: Optional[int] = None
    spec_id:  Optional[int]=None
    thick_from: Optional[float] = None
    thick_to: Optional[float] = None
    info_only: Optional[str] = None
    direction: Optional[str] = None
    angle: Optional[str] = None
    diameter_mm: Optional[float] = None
    heat_code: Optional[str] = None
    freq: Optional[str] = None
    fio: Optional[str] = None

# Spbend Response
class SpbendCreate(SpbendResponse):
    pass

class SpbendUpdate(SpbendResponse):
    pass

class SpbendRead(SpbendResponse):
    id: int
    spec: Optional[SpecRead] = None
    mill: Optional[MillRead] = None

class SpbendPagination(DispatchBase):
    total: int
    items: List[SpbendRead] = []
    itemsPerPage: int
    page: int

class SpbendUpdateNew(DispatchBase):
    id: int
    data: dict


class SpbendBySpecCode(DispatchBase):
    spec_code: str
    page: int
    itemsPerPage: int


class SpbendCopyToCode(DispatchBase):
    before_code: str
    after_code: str

class SpbendPrintCardReturnValue(DispatchBase):
    spec_id: Optional[int] = None
    product_type_id: Optional[int] = None