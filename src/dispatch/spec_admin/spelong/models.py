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



class Spelong(Base,TimeStampMixin):
    
    __tablename__ = 'spelong'
    id = Column(BigInteger, primary_key=True,autoincrement=True)

    
    spec_id = Column(BigInteger, ForeignKey("spec.id"), nullable=False, )
    spec = relationship("Spec", backref="spec_spelong")

    mill_id = Column(BigInteger, ForeignKey("mill.id"), nullable=False, )
    mill = relationship("Mill", backref="mill_Spelong")
    
    
    
    thick_from = Column(Numeric(20, 10)) #Thickness From
    thick_to = Column(Numeric(20, 10)) #Thickness To
    location = Column(String(1)) #Sample Location
    elong_min_value = Column(Integer) #Min-Val
    elong_guage_code = Column(String(255)) #Code
    filler = Column(String(16))

    std = Column(String)
    fio = Column(String)
    tpsr = Column(String)
    pred = Column(String)
    freq = Column(String)
    pt = Column(String)

    __table_args__ = (UniqueConstraint('spec_id', 'thick_from', 'thick_to', name='spelong_uix_spec_thick_from_to'),)


class SpeLongResponse(BaseResponseModel):
    # spif_spec_code: Optional[str] = None
    # spif_variation_no: Optional[int] = None
    
    spec: Optional[SpecRead] = None
    spec_id:  Optional[int]=None 

    mill_id: Optional[int] = None
    mill: Optional[MillRead] = None
    thick_from: Optional[float] = None
    thick_to: Optional[float] = None
    location: Optional[str] = None
    elong_min_value: Optional[int] = None
    elong_guage_code: Optional[str] = None
    filler: Optional[str] = None

    std: Optional[str] = None
    fio: Optional[str] = None
    tpsr: Optional[str] = None
    pred: Optional[str] = None
    freq: Optional[str] = None
    pt: Optional[str] = None

class SpeLongCreate(SpeLongResponse):
    pass

class SpeLongUpdate(SpeLongResponse):
    pass

class SpeLongRead(SpeLongResponse):
    id: int

class SpeLongPagination(DispatchBase):
    total: int
    items: List[SpeLongRead] = []
    itemsPerPage: int
    page: int

class SpeLongUpdateNew(DispatchBase):
    id: int
    data: dict

class SpeLongBySpecCode(DispatchBase):
    spec_code: str
    page: int
    itemsPerPage: int

class SpeLongCopyToCode(DispatchBase):
    before_code: str
    after_code: str