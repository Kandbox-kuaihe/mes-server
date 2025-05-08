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



class Spscond(Base,TimeStampMixin):

    __tablename__ = 'spscond'

    id = Column(BigInteger, primary_key=True,autoincrement=True)
    mill_id = Column(BigInteger, ForeignKey("mill.id"), nullable=True, )
    mill = relationship("Mill", backref="mill_Spscond")
    
    
    spec_id = Column(BigInteger, ForeignKey("spec.id"), nullable=False, )
    spec = relationship("Spec", backref="spec_spscond")
    
    thick_from = Column(Numeric(20, 10), nullable=False)
    thick_to = Column(Numeric(20, 10), nullable=False)
    code = Column(String(4), nullable=False)
    location = Column(String(1), nullable=False)
    filler = Column(String(100), nullable=False)

    __table_args__ = (UniqueConstraint('spec_id', 'thick_from', 'thick_to', name='spscond_uix_spec_thick_from_to'),)



# BaseResponseModel

class SpscondResponse(BaseResponseModel):
    spec: Optional[SpecRead] = None
    spec_id:  Optional[int]=None 

    mill_id: Optional[int] = None
    mill: Optional[MillRead] = None
    thick_from: Optional[float] = None
    thick_to: Optional[float] = None
    code: Optional[str] = None
    location: Optional[str] = None
    filler: Optional[str] = None

# Spscond Response
class SpscondCreate(SpscondResponse):
    pass

class SpscondUpdate(SpscondResponse):
    pass

class SpscondRead(SpscondResponse):
    id: int

class SpscondPagination(DispatchBase):
    total: int
    items: List[SpscondRead] = []
    itemsPerPage: int
    page: int

class SpscondUpdateNew(DispatchBase):
    id: int
    data: dict


class SpscondBySpecCode(DispatchBase):
    spec_code: str
    page: int
    itemsPerPage: int


class SpscondCopyToCode(DispatchBase):
    before_code: str
    after_code: str