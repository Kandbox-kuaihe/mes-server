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

class Spcevan(Base,TimeStampMixin):
    __tablename__ = 'spcevan'
    id = Column(BigInteger, primary_key=True,autoincrement=True)

    # spif_spec_code = Column(CHAR(5), nullable=True)
    spec_id = Column(BigInteger, ForeignKey("spec.id"), nullable=False, )
    spec = relationship("Spec", backref="spec_spcevan")
    mill_id = Column(BigInteger, ForeignKey("mill.id"), nullable=False, )
    mill = relationship("Mill", backref="mill_Spcevan")
    
    ## TODO 确认
    # delete 
    # spif_variation_no = Column(Integer, nullable=True)
    # spdk_mill = Column(Integer, nullable=True)
    # spdk_type = Column(CHAR(2), nullable=True)
    # spdk_sub_type = Column(CHAR(3), nullable=True)
    
    
    thick_from = Column(Numeric(20, 10), nullable=False) #Thickness From
    thick_to = Column(Numeric(20, 10), nullable=False) #Thickness TO
    cev_location = Column(String(255), nullable=False) #CEV location
    cev_formula = Column(String(255), nullable=False) #CEV from Opt
    cev_max_value = Column(Float, nullable=False) #CEV Value
    cev_rec_type = Column(CHAR(1), nullable=True)
    pcm_location = Column(String(255), nullable=False) #PCM Location
    pcm_formula = Column(String(255), nullable=False) #PCM From
    pcm_max_value = Column(Float, nullable=False) #PCM Max Value
    opt_ind = Column(CHAR(1), nullable=True)
    filler = Column(CHAR(20), nullable=True)

    __table_args__ = (UniqueConstraint('spec_id', 'thick_from', 'thick_to', name='spcevan_uix_spec_thick_from_to'),)



from dispatch.spec_admin.spec.models import SpecRead
class SpcevanBaseResponse(BaseResponseModel):
    # spif_spec_code: Optional[str] = None
    # spif_variation_no: Optional[int] = None
    spec: Optional[SpecRead] = None
    spec_id:  Optional[int]=None 
    mill_id: Optional[int] = None
    mill: Optional[MillRead] = None

    thick_from:Optional[float] = None
    thick_to: Optional[float] = None
    cev_location: Optional[str] = None
    cev_formula: Optional[str] = None
    cev_max_value: Optional[float] = None
    cev_rec_type: Optional[str] = None
    pcm_location: Optional[str] = None
    pcm_formula: Optional[str] = None
    pcm_max_value: Optional[float] = None
    opt_ind: Optional[str] = None
    filler: Optional[str] = None

class SpcevanCreate(SpcevanBaseResponse):
    pass

class SpcevanUpdate(SpcevanBaseResponse):
    pass

class SpcevanRead(SpcevanBaseResponse):
    id: int

class SpcevanPagination(DispatchBase):
    total: int
    items: List[SpcevanRead] = []
    itemsPerPage: int
    page: int

class SpcevanUpdateNew(DispatchBase):
    id: int
    data: dict

class SpcevanBySpecCode(DispatchBase):
    spec_code: str
    page: int
    itemsPerPage: int


class SpcevanCopyToCode(DispatchBase):
    before_code: str
    after_code: str