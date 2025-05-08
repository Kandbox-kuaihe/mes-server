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



class Spyield(Base,TimeStampMixin):

    __tablename__ = 'spyield'

    id = Column(BigInteger, primary_key=True,autoincrement=True)
    mill_id = Column(BigInteger, ForeignKey("mill.id"), nullable=False, )
    mill = relationship("Mill", backref="mill_Spyield")
    
    spec_id = Column(BigInteger, ForeignKey("spec.id"), nullable=False, )
    spec = relationship("Spec", backref="spec_spyield")
    
    thick_from = Column(Numeric(20, 10)) #Thickness From
    thick_to = Column(Numeric(20, 10)) #Thickness To
    location = Column(String(1)) #Sample Location
    yield_min = Column(Integer) #min
    yield_max = Column(Integer) #Max
    yield_tens_rat_min = Column(Integer) #Y/T Min
    yield_tens_rat_max = Column(Integer) #Ratio Max
    stress_units = Column(String(1)) #Units
    filler = Column(String(10))

    fio = Column(String)
    tpsr = Column(String)
    pt = Column(String)
    pred = Column(String)
    std = Column(String)
    freq = Column(String)

    __table_args__ = (UniqueConstraint('spec_id', 'thick_from', 'thick_to', name='spyield_uix_spec_thick_from_to'),)


# BaseResponseModel

class SpyieldResponse(BaseResponseModel):
    spec: Optional[SpecRead] = None
    spec_id:  Optional[int]=None 

    mill_id: Optional[int] = None
    mill: Optional[MillRead] = None
    thick_from: Optional[float] = None
    thick_to: Optional[float] = None
    location: Optional[str] = None
    yield_min: Optional[int] = None
    yield_max: Optional[int] = None
    yield_tens_rat_min: Optional[int] = None
    yield_tens_rat_max: Optional[int] = None
    stress_units: Optional[str] = None
    filler: Optional[str] = None

    fio: Optional[str] = None
    tpsr: Optional[str] = None
    pt: Optional[str] = None
    pred: Optional[str] = None
    std: Optional[str] = None
    freq: Optional[str] = None


# Spyield Response
class SpyieldCreate(SpyieldResponse):
    pass

class SpyieldUpdate(SpyieldResponse):
    pass

class SpyieldRead(SpyieldResponse):
    id: int

class SpyieldPagination(DispatchBase):
    total: int
    items: List[SpyieldRead] = []
    itemsPerPage: int
    page: int

class SpyieldUpdateNew(DispatchBase):
    id: int
    data: dict


class SpyieldBySpecCode(DispatchBase):
    spec_code: str
    page: int
    itemsPerPage: int

class SpyieldCopyToCode(DispatchBase):
    before_code: str
    after_code: str