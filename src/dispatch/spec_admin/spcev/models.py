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


class Spcev(Base,TimeStampMixin):

    __tablename__ = 'spcev'

    id = Column(BigInteger, primary_key=True,autoincrement=True)

    spec_id = Column(BigInteger, ForeignKey("spec.id"), nullable=False)
    spec = relationship("Spec", backref="spec_spcev")
    mill_id = Column(BigInteger, ForeignKey("mill.id"), nullable=False)
    mill = relationship("Mill", backref="mill_Spcev")   

    cev_value = Column(Integer)
    steel_type = Column(String(5))
    material_type = Column(String(5))
    flange = Column(Integer)
    flange_min = Column(Numeric(20, 10))
    flange_max = Column(Numeric(20, 10))
    quality_code = Column(String(20))
    risk = Column(String(5))
    desc = Column(String(5))
    
    cev_min = Column(Numeric(20, 10))
    cev_max = Column(Numeric(20, 10))
    st = Column(String(5))
    notes = Column(String)

    __table_args__ = (
        UniqueConstraint('spec_id', 'cev_value', name='unique_key_cev_value_spec_id'),
    )


class SpcevResponse(BaseResponseModel):

    spec: Optional[SpecRead] = None
    spec_id:  Optional[int]=None 
    mill_id: Optional[int] = None
    mill: Optional[MillRead] = None
    cev_value: Optional[int] = None
    steel_type: Optional[str] = None
    material_type: Optional[str] = None
    flange: Optional[int] = None
    flange_min: Optional[float] = None
    flange_max: Optional[float] = None
    quality_code: Optional[str] = None
    risk: Optional[str] = None
    desc: Optional[str] = None
    
    cev_min: Optional[float] = None
    cev_max: Optional[float] = None
    st: Optional[str] = None
    notes: Optional[str] = None


class SpcevCreate(SpcevResponse):
    pass

class SpcevUpdate(SpcevResponse):
    pass

class SpcevRead(SpcevResponse):
    id: int

class SpcevPagination(DispatchBase):
    total: int
    items: List[SpcevRead] = []
    itemsPerPage: int
    page: int

class SpcevUpdateNew(DispatchBase):
    id: int
    data: dict

class SpcevBySpecCode(DispatchBase):
    spec_code: str
    page: int
    itemsPerPage: int

class SpcevCopyToCode(DispatchBase):
    before_code: str
    after_code: str