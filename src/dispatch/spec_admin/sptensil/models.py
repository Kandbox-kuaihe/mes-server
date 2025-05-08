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



class Sptensil(Base,TimeStampMixin):

    __tablename__ = 'sptensil'

    id = Column(BigInteger, primary_key=True,autoincrement=True)

    
    mill_id = Column(BigInteger, ForeignKey("mill.id"), nullable=False, )
    mill = relationship("Mill", backref="mill_Sptensil")   
    spec_id = Column(BigInteger, ForeignKey("spec.id"), nullable=False, )
    spec = relationship("Spec", backref="spec_sptensil")
    
    thick_from = Column(Numeric(20, 10)) #Thickness From
    thick_to = Column(Numeric(20, 10)) #Thickness To
    location = Column(String(1)) #Sample Location
    tensile_min = Column(Integer) #Tensile Min
    tensile_max = Column(Integer) #Tensile Max
    stress_units = Column(String(1)) #Units
    heat_code = Column(String(14))
    filler = Column(String(14))
    
    # Product_Analysis_Flag
    elong_code_1_min = Column(Integer) #Elongation Min
    elong_code_2_min = Column(Integer) #Elongation Min
    elong_code_3_min = Column(Integer) #Elongation Min
    elong_code_4_min = Column(Integer) #Elongation Min
    elong_code_5_min = Column(Integer) #Elongation Min
    elong_code_6_min = Column(Integer) #Elongation Min
    tensile_units = Column(String) #Tensile Units
    yield_min = Column(Integer) #Yield Min
    yield_max = Column(Integer) #Yield Max
    yield_units = Column(String) #Yield Units
    y_t_ratio_min = Column(Integer) #Y/T Ratio Min
    y_t_ratio_max = Column(Integer) #Y/T Ratio Max
    
    # srsm spec 
    elgge = Column(String) #Elgge
    freq = Column(String) #Freq
    std = Column(String) #Std
    sequence = Column(Integer)
    fio = Column(String)
    pt = Column(String)
    pred = Column(String)
    tpsr = Column(String)

 

    product_analysis_flag = Column(String(1))
    elong_code_1_min = Column(Numeric(20, 10))
    elong_code_2_min = Column(Numeric(20, 10))
    elong_code_3_min = Column(Numeric(20, 10))
    elong_code_4_min = Column(Numeric(20, 10))
    elong_code_5_min = Column(Numeric(20, 10))
    elong_code_6_min = Column(Numeric(20, 10))
    tensile_units = Column(String(1)) #Tensile_units
    yield_min = Column(Numeric(20, 10)) #Yield_min
    yield_max = Column(Numeric(20, 10)) #Yield_max
    yield_units = Column(String(1)) #Yield_units
    y_t_ratio_min = Column(Numeric(20, 10)) #Y_T_ratio_min
    y_t_ratio_max = Column(Numeric(20, 10)) #Y_T_ratio_max

    orientation = Column(String)
    reduction_in_area = Column(Numeric(20, 10)) #reduction_in_area


    __table_args__ = (UniqueConstraint('spec_id', 'thick_from', 'thick_to','mill_id', 'sequence', name='sptensil_uix_spec_thick_from_to'),)



# BaseResponseModel

class SptensilResponse(BaseResponseModel):
    spec: Optional[SpecRead] = None
    spec_id:  Optional[int]=None 

    mill_id: Optional[int] = None
    mill: Optional[MillRead] = None

    thick_from: Optional[float] = None
    thick_to: Optional[float] = None
    location: Optional[str] = None
    tensile_min: Optional[int] = None
    tensile_max: Optional[int] = None
    stress_units: Optional[str] = None
    heat_code: Optional[str] = None
    filler: Optional[str] = None
    product_analysis_flag: Optional[str] = None
    elong_code_1_min: Optional[float] = None
    elong_code_2_min: Optional[float] = None
    elong_code_3_min: Optional[float] = None
    elong_code_4_min: Optional[float] = None
    elong_code_5_min: Optional[float] = None
    elong_code_6_min: Optional[float] = None
    tensile_units: Optional[str] = None
    yield_min: Optional[float] = None
    yield_max: Optional[float] = None
    yield_units: Optional[str] = None
    y_t_ratio_min: Optional[float] = None
    y_t_ratio_max: Optional[float] = None

    orientation: Optional[str] = None
    
    elong_code_1_min: Optional[int] = None
    elong_code_2_min: Optional[int] = None
    elong_code_3_min: Optional[int] = None
    elong_code_4_min: Optional[int] = None
    elong_code_5_min: Optional[int] = None
    elong_code_6_min: Optional[int] = None
    tensile_units: Optional[str] = None
    yield_min: Optional[int] = None
    yield_max: Optional[int] = None
    yield_units: Optional[str] = None
    y_t_ratio_min: Optional[int] = None
    y_t_ratio_max: Optional[int] = None
    
    elgge: Optional[str] = None
    freq: Optional[str] = None
    std: Optional[str] = None

    reduction_in_area: Optional[float] = None

    #srsm spec tensile 新增
    fio: Optional[str] = None
    pt: Optional[str] = None
    pred: Optional[str] = None
    tpsr: Optional[str] = None
    

# Sptensil Response
class SptensilCreate(SptensilResponse):
    pass

class SptensilUpdate(SptensilResponse):
    pass

class SptensilRead(SptensilResponse):
    id: int

class SptensilPagination(DispatchBase):
    total: int
    items: List[SptensilRead] = []
    itemsPerPage: int
    page: int

class SptensilUpdateNew(DispatchBase):
    id: int
    data: dict


class SptensilBySpecCode(DispatchBase):
    spec_code: str
    page: int
    itemsPerPage: int

class SptensilCopyToCode(DispatchBase):
    before_code: str
    after_code: str