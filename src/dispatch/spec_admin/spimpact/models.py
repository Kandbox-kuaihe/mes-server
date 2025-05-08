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



class Spimpact(Base,TimeStampMixin):
    __tablename__ = 'spimpact'
    # id = Column(Integer, primary_key=True)
    id = Column(Integer, primary_key=True, autoincrement=True)

 
    
    spec_id = Column(BigInteger, ForeignKey("spec.id"), nullable=False, )
    spec = relationship("Spec", backref="spec_spimpact")

    mill_id = Column(BigInteger, ForeignKey("mill.id"), nullable=False, )
    mill = relationship("Mill", backref="mill_Spimpact")
    
    
    thick_from = Column(Numeric(20, 10), nullable=False) #Thickness From
    thick_to = Column(Numeric(20, 10), nullable=False) #Thickness To
    location = Column(String(1)) #Sample Location

    summary_name = Column(String(10)) #Summary Name
    sub_type = Column(String(5)) #Sub Type

    ave_value_1 = Column(String(5), nullable=False) #Average 1
    min_value_1 = Column(String(5), nullable=False) #Min 1
    temp_sign_1 = Column(String(1)) 
    temp_value_1 = Column(String(3), nullable=False) #Temp 1
    ave_value_2 = Column(String(5), nullable=False) #Average 2
    min_value_2 = Column(String(5), nullable=False) #min 2
    temp_sign_2 = Column(String(1)) 
    temp_value_2 = Column(String(3), nullable=False) #Temp 2

    reduction_75 = Column(String(5)) # Sub-Size Reduction-7.5
    reduction_50 = Column(String(5)) # Sub-Size Reduction-5.0
    reduction_25 = Column(String(5)) # Sub-Size Reduction-2.5
    heat_code = Column(String(5)) #Heat Code


    ave_value_3 = Column(String(5), nullable=False)
    min_value_3 = Column(String(5), nullable=False)
    temp_sign_3 = Column(String(1))
    temp_value_3 = Column(String(3), nullable=False)
    ave_value_4 = Column(String(5))
    min_value_4 = Column(String(5))
    temp_sign_4 = Column(String(1))
    temp_value_4 = Column(String(3))
    ave_value_5 = Column(String(5))
    min_value_5 = Column(String(5))
    temp_sign_5 = Column(String(1))
    temp_value_5 = Column(String(3))
    ave_value_6 = Column(String(5))
    min_value_6 = Column(String(5))
    temp_sign_6 = Column(String(1))
    temp_value_6 = Column(String(3))
    impact_units = Column(String(1)) #I
    temp_units = Column(String(1)) # T
    acc_dev = Column(String(2))
    info_temp_sign_1 = Column(String(1)) 
    info_temp_value_1 = Column(String(3)) #Info Temp 1
    info_temp_sign_2 = Column(String(1))
    info_temp_value_2 = Column(String(3)) #Info Temp 2
    info_temp_sign_3 = Column(String(1))
    info_temp_value_3 = Column(String(3)) #Info Temp 3
    option = Column(String(1)) #opt
    std = Column(String(4)) # standard_astm_bsen
    ave_shear_1 = Column(String(3))
    min_shear_1 = Column(String(5))
    ave_shear_2 = Column(String(5))
    min_shear_2 = Column(String(5))
    ave_shear_3 = Column(String(5))
    min_shear_3 = Column(String(5))
    spaeter_certs = Column(String(1))  #spaeter_type_certification
    filler = Column(String(9))
    
    
    freq = Column(String)
    notch = Column(String)
 
    direction = Column(String) # l/x
    orientation = Column(String)
    sequence = Column(Integer) #srsm
    fio = Column(String)
    pt = Column(String)
    pred = Column(String) 
    tpsr = Column(String)
    crystallinity_shear = Column(String)
    crystallinity_avg = Column(Numeric(20, 10))
    crystallinity_ind = Column(Numeric(20, 10))

    # search_vector = Column(
    #     TSVectorType(
    #         "code",
    #         "type",
    #         weights={"code": "A", "type": "B"},
    #     )
    # )

    __table_args__ = (UniqueConstraint('spec_id', 'thick_from', 'thick_to','sequence', 'mill_id',  'direction','orientation', name='spimpact_uix_spec_thick_from_to'),)



class SpImpactBaseResponse(BaseResponseModel):
    # spif_spec_code: Optional[str] = None
    # spif_variation_no: Optional[int] = None
    spec: Optional[SpecRead] = None
    spec_id:  Optional[int]=None 

    mill_id: Optional[int] = None
    mill: Optional[MillRead] = None
    thick_from: Optional[float] = None
    thick_to: Optional[float] = None
    location: Optional[str] = None

    summary_name: Optional[str] = None
    sub_type: Optional[str] = None



    ave_value_1: Optional[str] = None
    min_value_1: Optional[str] = None
    temp_sign_1: Optional[str] = None
    temp_value_1: Optional[str] = None
    ave_value_2: Optional[str] = None
    min_value_2: Optional[str] = None
    temp_sign_2: Optional[str] = None
    temp_value_2: Optional[str] = None


    reduction_75: Optional[str] = None
    reduction_50: Optional[str] = None
    reduction_25: Optional[str] = None



    ave_value_3: Optional[str] = None
    min_value_3: Optional[str] = None
    temp_sign_3: Optional[str] = None
    temp_value_3: Optional[str] = None
    ave_value_4: Optional[str] = None
    min_value_4: Optional[str] = None
    temp_sign_4: Optional[str] = None
    temp_value_4: Optional[str] = None
    ave_value_5: Optional[str] = None
    min_value_5: Optional[str] = None
    temp_sign_5: Optional[str] = None
    temp_value_5: Optional[str] = None
    ave_value_6: Optional[str] = None
    min_value_6: Optional[str] = None
    temp_sign_6: Optional[str] = None
    temp_value_6: Optional[str] = None
    impact_units: Optional[str] = None
    temp_units: Optional[str] = None
    acc_dev: Optional[str] = None
    info_temp_sign_1: Optional[str] = None
    info_temp_value_1: Optional[str] = None
    info_temp_sign_2: Optional[str] = None
    info_temp_value_2: Optional[str] = None
    info_temp_sign_3: Optional[str] = None
    info_temp_value_3: Optional[str] = None
    option: Optional[str] = None
    std: Optional[str] = None 
    ave_shear_1: Optional[str] = None
    min_shear_1: Optional[str] = None
    ave_shear_2: Optional[str] = None
    min_shear_2: Optional[str] = None
    ave_shear_3: Optional[str] = None
    min_shear_3: Optional[str] = None
    spaeter_certs: Optional[str] = None
    filler: Optional[str] = None

    orientation: Optional[str] = None


    # srsm
    freq: Optional[str] = None
    notch: Optional[str] = None
    sequence: Optional[int] = None
    fio: Optional[str] = None
    pt: Optional[str] = None
    pred: Optional[str] = None
    tpsr: Optional[str] = None
    crystallinity_shear: Optional[str] = None
    crystallinity_avg: Optional[float] = None
    crystallinity_ind: Optional[float] = None


class SpImpactCreate(SpImpactBaseResponse):
    pass

class SpImpactUpdate(SpImpactBaseResponse):
    pass

class SpImpactRead(SpImpactBaseResponse):
    id: int

class SpImpactPagination(DispatchBase):
    total: int
    items: List[SpImpactRead] = []
    itemsPerPage: int
    page: int

class SpImapctBySpecCode(DispatchBase):
    spec_code: str
    page: int
    itemsPerPage: int

class SpImpactUpdateNew(DispatchBase):
    id: int
    data: dict

class SpImpactCopyToCode(DispatchBase):
    before_code: str
    after_code: str