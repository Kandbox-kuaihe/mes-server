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

class Spjominy(Base,TimeStampMixin):
    __tablename__ = 'spjominy'  # spac_jominy
    id = Column(BigInteger, primary_key=True,autoincrement=True)
 
    
    
    mill_id = Column(BigInteger, ForeignKey("mill.id"), nullable=True, )
    mill = relationship("Mill", backref="mill_Spjominy")    
    spec_id = Column(BigInteger, ForeignKey("spec.id"), nullable=True, )
    spec = relationship("Spec", backref="spec_spjominy")

    thick_from = Column(Numeric(20, 10))
    thick_to = Column(Numeric(20, 10))
    units = Column(String(1))
    ideal_dia_min = Column(Integer)
    ideal_dia_max = Column(Integer)
    tin_ratio_min = Column(Integer)
    tin_ratio_max = Column(Integer)
    first_jominy_pos = Column(Integer)
    first_jominy_min = Column(Integer)
    first_jominy_max = Column(Integer)
    other_jominy_pos_1 = Column(Integer)
    other_jominy_min_1 = Column(Integer)
    other_jominy_max_1 = Column(Integer)
    other_jominy_pos_2 = Column(Integer)
    other_jominy_min_2 = Column(Integer)
    other_jominy_max_2 = Column(Integer)
    other_jominy_pos_3 = Column(Integer)
    other_jominy_min_3 = Column(Integer)
    other_jominy_max_3 = Column(Integer)
    other_jominy_pos_4 = Column(Integer)
    other_jominy_min_4 = Column(Integer)
    other_jominy_max_4 = Column(Integer)
    other_jominy_pos_5 = Column(Integer)
    other_jominy_min_5 = Column(Integer)
    other_jominy_max_5 = Column(Integer)
    other_jominy_pos_6 = Column(Integer)
    other_jominy_min_6 = Column(Integer)
    other_jominy_max_6 = Column(Integer)
    other_jominy_pos_7 = Column(Integer)
    other_jominy_min_7 = Column(Integer)
    other_jominy_max_7 = Column(Integer)
    other_jominy_pos_8 = Column(Integer)
    other_jominy_min_8 = Column(Integer)
    other_jominy_max_8 = Column(Integer)
    other_jominy_pos_9 = Column(Integer)
    other_jominy_min_9 = Column(Integer)
    other_jominy_max_9 = Column(Integer)
    other_jominy_pos_10 = Column(Integer)
    other_jominy_min_10 = Column(Integer)
    other_jominy_max_10 = Column(Integer)
    other_jominy_pos_11 = Column(Integer)
    other_jominy_min_11 = Column(Integer)
    other_jominy_max_11 = Column(Integer)
    sdist_min = Column(Integer)
    sdist_max = Column(Integer)
    filler = Column(String(24))

    __table_args__ = (UniqueConstraint('spec_id', 'thick_from', 'thick_to', name='spjominy_uix_spec_thick_from_to'),)



# BaseResponseModel


class SpecJominyResponse(BaseResponseModel):
 
    
    spec: Optional[SpecRead] = None
    spec_id:  Optional[int]=None 

    mill_id: Optional[int] = None
    mill: Optional[MillRead] = None
    thick_from: Optional[float] = None
    thick_to: Optional[float] = None
    units: Optional[str] = None
    ideal_dia_min: Optional[int] = None
    ideal_dia_max: Optional[int] = None
    tin_ratio_min: Optional[int] = None
    tin_ratio_max: Optional[int] = None
    first_jominy_pos: Optional[int] = None
    first_jominy_min: Optional[int] = None
    first_jominy_max: Optional[int] = None
    other_jominy_pos_1: Optional[int] = None
    other_jominy_min_1: Optional[int] = None
    other_jominy_max_1: Optional[int] = None
    other_jominy_pos_2: Optional[int] = None
    other_jominy_min_2: Optional[int] = None
    other_jominy_max_2: Optional[int] = None
    other_jominy_pos_3: Optional[int] = None
    other_jominy_min_3: Optional[int] = None
    other_jominy_max_3: Optional[int] = None
    other_jominy_pos_4: Optional[int] = None
    other_jominy_min_4: Optional[int] = None
    other_jominy_max_4: Optional[int] = None
    other_jominy_pos_5: Optional[int] = None
    other_jominy_min_5: Optional[int] = None
    other_jominy_max_5: Optional[int] = None
    other_jominy_pos_6: Optional[int] = None
    other_jominy_min_6: Optional[int] = None
    other_jominy_max_6: Optional[int] = None
    other_jominy_pos_7: Optional[int] = None
    other_jominy_min_7: Optional[int] = None
    other_jominy_max_7: Optional[int] = None
    other_jominy_pos_8: Optional[int] = None
    other_jominy_min_8: Optional[int] = None
    other_jominy_max_8: Optional[int] = None
    other_jominy_pos_9: Optional[int] = None
    other_jominy_min_9: Optional[int] = None
    other_jominy_max_9: Optional[int] = None
    other_jominy_pos_10: Optional[int] = None
    other_jominy_min_10: Optional[int] = None
    other_jominy_max_10: Optional[int] = None
    other_jominy_pos_11: Optional[int] = None
    other_jominy_min_11: Optional[int] = None
    other_jominy_max_11: Optional[int] = None
    sdist_min: Optional[int] = None
    sdist_max: Optional[int] = None
    filler: Optional[str] = None 
    
    
# SpecJominy Response
class SpecJominyCreate(SpecJominyResponse):
    pass

class SpecJominyUpdate(SpecJominyResponse):
    pass

class SpecJominyRead(SpecJominyResponse):
    id: int

class SpecJominyPagination(DispatchBase):
    total: int
    items: List[SpecJominyRead] = []
    itemsPerPage: int
    page: int


class SpecJominyBySpecCode(DispatchBase):
    spec_code: str
    page: int
    itemsPerPage: int


class SpecJominyCopyToCode(DispatchBase):
    before_code: str
    after_code: str