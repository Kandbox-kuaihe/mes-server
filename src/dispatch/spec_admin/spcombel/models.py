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



# comb_
class Spcombel(Base,TimeStampMixin):
    __tablename__ = 'spcombel'
    
    # SP_combined_element
    id = Column(BigInteger, primary_key=True,autoincrement=True)

    # spif_spec_code = Column(String(5))
    # spif_variation_no = Column(Integer)
    spec_id = Column(BigInteger, ForeignKey("spec.id"), nullable=True, )
    spec = relationship("Spec", backref="spec_spcombel")

    mill_id = Column(BigInteger, ForeignKey("mill.id"), nullable=True, )
    mill = relationship("Mill", backref="mill_Spcombel") 
    # mill_id 
    # spdk_mill = Column(Integer)  
    # spdk_type = Column(String(2))
    # spdk_sub_type = Column(String(3))
    
    
    ln_no = Column(Integer)
    
    thick_from = Column(Numeric(20, 10), nullable=False) #Thickness From
    thick_to = Column(Numeric(20, 10), nullable=False) #Thickness To
    comb_el_sign_1 = Column(String(1), nullable=False) #sign-1
    comb_el_symbol_1 = Column(String(2), nullable=False) #EL1
    comb_el_sign_2 = Column(String(1), nullable=False) #sign-2
    comb_el_symbol_2 = Column(String(2)) #EL2
    comb_el_sign_3 = Column(String(1)) #sign-3
    comb_el_symbol_3 = Column(String(2)) #EL3
    comb_el_sign_4 = Column(String(1)) #sign-4
    comb_el_symbol_4 = Column(String(1)) #EL4
    comb_el_sign_5 = Column(String(1)) #sign-5
    comb_el_symbol_5 = Column(String(2)) #EL5
    comb_min_red_1 = Column(Integer)
    comb_min_1 = Column(String(5)) #min
    comb_max_1 = Column(String(5)) #max
    comb_max_red_1 = Column(Integer)
    comb_min_red_2 = Column(Integer)
    comb_min_2 = Column(String(5))
    comb_max_2 = Column(String(5))
    comb_max_red_2 = Column(Integer)
    comb_min_red_3 = Column(Integer)
    comb_min_3 = Column(String(5))
    comb_max_3 = Column(String(5))
    comb_max_red_3 = Column(Integer)
    comb_min_red_4 = Column(Integer)
    comb_min_4 = Column(String(5))
    comb_max_4 = Column(String(5))
    comb_max_red_4 = Column(Integer)
    filler = Column(String(30))

    __table_args__ = (UniqueConstraint('spec_id', 'thick_from', 'thick_to', name='spcombel_uix_spec_thick_from_to'),)




class SpComBelResponse(BaseResponseModel):
    # spif_spec_code: Optional[str] = None
    # spif_variation_no: Optional[int] = None
    spec: Optional[SpecRead] = None
    spec_id:  Optional[int]=None 
    mill_id: Optional[int] = None
    mill: Optional[MillRead] = None
    # spdk_mill: Optional[int] = None
    # spdk_type: Optional[str] = None
    # spdk_sub_type: Optional[str] = None
    ln_no: Optional[int] = None
    
    thick_from: Optional[float] = None
    thick_to: Optional[float] = None
    comb_el_sign_1: Optional[str] = None
    comb_el_symbol_1: Optional[str] = None
    comb_el_sign_2: Optional[str] = None
    comb_el_symbol_2: Optional[str] = None
    comb_el_sign_3: Optional[str] = None
    comb_el_symbol_3: Optional[str] = None
    comb_el_sign_4: Optional[str] = None
    comb_el_symbol_4: Optional[str] = None
    comb_el_sign_5: Optional[str] = None
    comb_el_symbol_5: Optional[str] = None
    comb_min_red_1: Optional[int] = None
    comb_min_1: Optional[str] = None
    comb_max_1: Optional[str] = None
    comb_max_red_1: Optional[int] = None
    comb_min_red_2: Optional[int] = None
    comb_min_2: Optional[str] = None
    comb_max_2: Optional[str] = None
    comb_max_red_2: Optional[int] = None
    comb_min_red_3: Optional[int] = None
    comb_min_3: Optional[str] = None
    comb_max_3: Optional[str] = None
    comb_max_red_3: Optional[int] = None
    comb_min_red_4: Optional[int] = None
    comb_min_4: Optional[str] = None
    comb_max_4: Optional[str] = None
    comb_max_red_4: Optional[int] = None
    filler: Optional[str] = None


class SpComBelCreate(SpComBelResponse):
    pass

class SpComBelUpdate(SpComBelResponse):
    pass

class SpComBelRead(SpComBelResponse):
    id: int

class SpComBelPagination(DispatchBase):
    total: int
    items: List[SpComBelRead] = []
    itemsPerPage: int
    page: int

class SpComBelUpdateNew(DispatchBase):
    id: int
    data: dict

class SpComBelBySpecCode(DispatchBase):
    spec_code: str
    page: int
    itemsPerPage: int

class SpComBelCopyToCode(DispatchBase):
    before_code: str
    after_code: str