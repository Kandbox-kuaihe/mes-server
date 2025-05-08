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



# (Base,TimeStampMixin):

from dispatch.spec_admin.spec.models import SpecRead


class Spsource(Base,TimeStampMixin):

    __tablename__ = 'spsource'

    id = Column(BigInteger, primary_key=True,autoincrement=True) 
    mill_id = Column(BigInteger, ForeignKey("mill.id"), nullable=True, )
    mill = relationship("Mill", backref="mill_Spsource")    
    spec_id = Column(BigInteger, ForeignKey("spec.id"), nullable=False, )
    spec = relationship("Spec", backref="spec_spsource")
    
    thick_from = Column(Numeric(20, 10), nullable=False) #Thickness From
    thick_to = Column(Numeric(20, 10), nullable=False) #Thickness To
    dim1 = Column(Integer, nullable=True)
    dim2 = Column(Integer, nullable=True)
    level = Column(String(2), nullable=True) #Degassing Level
    sub_type = Column(String(4), nullable=True) #subtype
    priority = Column(String(2), nullable=True)
    injection = Column(String(2), nullable=True) #Injection Level
    pouring_practice = Column(String(2), nullable=True) #Pouring Practice(1)
    shrouding = Column(String(2), nullable=True) #Shrouding
    slow_cooling = Column(Integer, nullable=True) #Slow Cooling
    hot_connecting = Column(String(1), nullable=True) #Hot Connecting
    sc_code = Column(String(2), nullable=True) #Scarfing Code 1
    sc_temp_min = Column(Integer, nullable=True)
    sc_temp_max = Column(Integer, nullable=True)
    sc_code_2 = Column(String(2), nullable=True) #Scarfing Code 2
    sc_temp_min_2 = Column(Integer, nullable=True)
    sc_temp_max_2 = Column(Integer, nullable=True)
    sl_practice = Column(String(2), nullable=True) #Slitting Practice 1
    sl_temp_min = Column(Integer, nullable=True)
    sl_temp_max = Column(Integer, nullable=True)
    sl_beard = Column(String(1), nullable=True)
    sd_practice = Column(String(2), nullable=True) #Subdividing Practice 1
    sd_temp_min = Column(Integer, nullable=True)
    sd_temp_max = Column(Integer, nullable=True)
    inspection = Column(String(2), nullable=True) #Inspection
    sulphur_printing = Column(String(2), nullable=True) #Sulphur Printing
    qual_code = Column(String(4), nullable=True) #Quality Code
    location = Column(String(1), nullable=True) #Location
    routing_input = Column(String(1), nullable=True)
    use_quality_1 = Column(String(4), nullable=True)
    use_quality_2 = Column(String(4), nullable=True)
    use_quality_3 = Column(String(4), nullable=True)
    use_quality_4 = Column(String(4), nullable=True)
    use_quality_5 = Column(String(4), nullable=True)
    use_quality_6 = Column(String(4), nullable=True)
    use_quality_7 = Column(String(4), nullable=True)
    steel_type = Column(String(1), nullable=True) # Steel Type
    filler_1 = Column(String(5), nullable=True)
    teeming = Column(String(2), nullable=True)
    filler = Column(String(31), nullable=True)

    other_quality_code = Column(String, nullable=True)

    __table_args__ = (UniqueConstraint('spec_id', 'thick_from', 'thick_to', 'mill_id','sub_type',name='spsource_uix_spec_thick_from_to'),)



# BaseResponseModel

class SpsourceResponse(BaseResponseModel): 
    spec: Optional[SpecRead] = None
    spec_id:  Optional[int]=None 
    mill_id: Optional[int] = None
    mill: Optional[MillRead] = None

    thick_from: Optional[float] = None
    thick_to: Optional[float] = None
    dim1: Optional[int] = None
    dim2: Optional[int] = None
    level: Optional[str] = None 
    sub_type: Optional[str] = None 
    priority: Optional[str] = None
    injection: Optional[str] = None 
    pouring_practice: Optional[str] = None 
    shrouding: Optional[str] = None 
    slow_cooling: Optional[int] = None 
    hot_connecting: Optional[str] = None 
    sc_code: Optional[str] = None 
    sc_temp_min: Optional[int] = None
    sc_temp_max: Optional[int] = None
    sc_code_2: Optional[str] = None 
    sc_temp_min_2: Optional[int] = None
    sc_temp_max_2: Optional[int] = None
    sl_practice: Optional[str] = None 
    sl_temp_min: Optional[int] = None
    sl_temp_max: Optional[int] = None
    sl_beard: Optional[str] = None
    sd_practice: Optional[str] = None
    sd_temp_min: Optional[int] = None
    sd_temp_max: Optional[int] = None
    inspection: Optional[str] = None
    sulphur_printing: Optional[str] = None
    qual_code: Optional[str] = None
    location: Optional[str] = None
    routing_input: Optional[str] = None
    use_quality_1: Optional[str] = None
    use_quality_2: Optional[str] = None
    use_quality_3: Optional[str] = None
    use_quality_4: Optional[str] = None
    use_quality_5: Optional[str] = None
    use_quality_6: Optional[str] = None
    use_quality_7: Optional[str] = None
    steel_type: Optional[str] = None
    filler_1: Optional[str] = None
    teeming: Optional[str] = None
    filler: Optional[str] = None

    other_quality_code: Optional[str] = None
    
    

# Spsource Response
class SpsourceCreate(SpsourceResponse):
    pass

class SpsourceUpdate(SpsourceResponse):
    pass

class SpsourceRead(SpsourceResponse):
    id: int

class SpsourcePagination(DispatchBase):
    total: int
    items: List[SpsourceRead] = []
    itemsPerPage: int
    page: int

class SpsourceUpdateNew(DispatchBase):
    id: int
    data: dict


class SpsourceBySpecCode(DispatchBase):
    spec_code: str
    page: int
    itemsPerPage: int


class SpsourceCopyToCode(DispatchBase):
    before_code: str
    after_code: str