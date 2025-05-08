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
 

class Sptcert(Base,TimeStampMixin):

    __tablename__ = 'sptcert'

    id = Column(BigInteger, primary_key=True,autoincrement=True) 
    
    spec_id = Column(BigInteger, ForeignKey("spec.id"), nullable=False, )
    spec = relationship("Spec", backref="spec_sptcert")
    mill_id = Column(BigInteger, ForeignKey("mill.id"), nullable=True, )
    mill = relationship("Mill", backref="mill_Sptcert")
    thick_from = Column(Numeric(20, 10), nullable=False)
    thick_to = Column(Numeric(20, 10), nullable=False)
    ratio_element_cd1 = Column(String(2), nullable=False)
    ratio_element_cd2 = Column(String(2), nullable=False)
    ratio_min = Column(Integer, nullable=False)
    ratio_max = Column(Integer, nullable=False)
    filler = Column(String(20), nullable=True)

    __table_args__ = (UniqueConstraint('spec_id', 'thick_from', 'thick_to', name='sptcert_uix_spec_thick_from_to'),)



# BaseResponseModel

class SptcertResponse(BaseResponseModel):
    spec: Optional[SpecRead] = None
    spec_id:  Optional[int]=None 

    mill_id: Optional[int] = None
    mill: Optional[MillRead] = None
    thick_from: Optional[float] = None
    thick_to: Optional[float] = None
    ratio_element_cd1: Optional[str] = None
    ratio_element_cd2: Optional[str] = None
    ratio_min: Optional[int] = None
    ratio_max: Optional[int] = None
    filler: Optional[str] = None
    
    

# Sptcert Response
class SptcertCreate(SptcertResponse):
    pass

class SptcertUpdate(SptcertResponse):
    pass

class SptcertRead(SptcertResponse):
    id: int

class SptcertPagination(DispatchBase):
    total: int
    items: List[SptcertRead] = []
    itemsPerPage: int
    page: int

class SptcertUpdateNew(DispatchBase):
    id: int
    data: dict

class SptcertBySpecCode(DispatchBase):
    spec_code: str
    page: int
    itemsPerPage: int

class SptcertCopyToCode(DispatchBase):
    before_code: str
    after_code: str