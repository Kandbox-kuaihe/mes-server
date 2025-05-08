from typing import List, Optional
from sqlalchemy import DateTime
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

from dispatch.spec_admin.quality.models import QualityRead
from dispatch.spec_admin.spec.models import SpecRead


# (Base,TimeStampMixin):



class Cast(Base,TimeStampMixin):

    __tablename__ = 'cast'  

    id = Column(BigInteger, primary_key=True,autoincrement=True)
      
    mill_id = Column(BigInteger, ForeignKey("mill.id"), nullable=True, )
    mill = relationship("Mill", backref="mill_Cast")
    generate_code = Column(Integer, nullable=False)  
    cast_code = Column(String, nullable=False)  
    bos_cast_code = Column(String)  
    quality_code = Column(String, nullable=False)  
    cast_suffix = Column(String, nullable=True)
      
    ch_c = Column(Numeric(20, 10))
    ch_si = Column(Numeric(20, 10))  
    ch_mn = Column(Numeric(20, 10))  
    ch_p = Column(Numeric(20, 10))  
    ch_s = Column(Numeric(20, 10))  
    ch_s_p = Column(Numeric(20, 10))  
    ch_cr = Column(Numeric(20, 10))  
    ch_mo = Column(Numeric(20, 10))  
    ch_ni = Column(Numeric(20, 10))  
    ch_al = Column(Numeric(20, 10))  
    ch_b = Column(Numeric(20, 10))  
    ch_co = Column(Numeric(20, 10))  
    ch_cu = Column(Numeric(20, 10))  
    ch_nb = Column(Numeric(20, 10))  
    ch_sn = Column(Numeric(20, 10))  
    ch_ti = Column(Numeric(20, 10))  
    ch_v = Column(Numeric(20, 10))  
    ch_ca = Column(Numeric(20, 10))  
    ch_n = Column(Numeric(20, 10))  
    ch_o = Column(Numeric(20, 10))  
    ch_h = Column(Numeric(20, 10))  
    ch_solal = Column(Numeric(20, 10))  
    ch_as = Column(Numeric(20, 10))  
    ch_bi = Column(Numeric(20, 10))  
    ch_ce = Column(Numeric(20, 10))  
    ch_pb = Column(Numeric(20, 10))  
    ch_sb = Column(Numeric(20, 10))  
    ch_w = Column(Numeric(20, 10))  
    ch_zn = Column(Numeric(20, 10))  
    ch_zr = Column(Numeric(20, 10))  
    ch_te = Column(Numeric(20, 10))  
    ch_rad = Column(Numeric(20, 10))
    ch_insal = Column(Numeric(20, 10))
    ch_n2 = Column(Numeric(20, 10))
    ch_sal = Column(Numeric(20, 10))
    authorize_date = Column(DateTime)


    quality_id = Column(Integer, ForeignKey("quality.id"), nullable=True)
    quality = relationship("Quality", backref="cast_quality")

    long_cast_code = Column(String)
    
    search_vector = Column(
        TSVectorType(
            "cast_code",
            "bos_cast_code",
            weights={
                "cast_code": "A",
                "bos_cast_code": "B",
            },
        )
    )
    
    __table_args__ = (
        UniqueConstraint('cast_code', 'generate_code', name='unique_key_cast_generate_code'),
    )
# BaseResponseModel

class CastSemiRead(BaseResponseModel):
    id: int
    semi_code: str

class CastResponse(BaseResponseModel):
    cast_code : Optional[str] = None
    bos_cast_code : Optional[str] = None
    quality_code : Optional[str] = None    
    cast_suffix: Optional[str] = None
    generate_code: Optional[int] = None
    mill_id: Optional[int] = None
    mill: Optional[MillRead] = None
    ch_c: Optional[float] = None
    ch_si: Optional[float] = None
    ch_mn: Optional[float] = None
    ch_p: Optional[float] = None
    ch_s: Optional[float] = None
    ch_s_p: Optional[float] = None
    ch_cr: Optional[float] = None
    ch_mo: Optional[float] = None
    ch_ni: Optional[float] = None
    ch_al: Optional[float] = None
    ch_b: Optional[float] = None
    ch_co: Optional[float] = None
    ch_cu: Optional[float] = None
    ch_nb: Optional[float] = None
    ch_sn: Optional[float] = None
    ch_ti: Optional[float] = None
    ch_v: Optional[float] = None
    ch_ca: Optional[float] = None
    ch_n: Optional[float] = None
    ch_o: Optional[float] = None
    ch_h: Optional[float] = None
    ch_solal: Optional[float] = None
    ch_as: Optional[float] = None
    ch_bi: Optional[float] = None
    ch_ce: Optional[float] = None
    ch_pb: Optional[float] = None
    ch_sb: Optional[float] = None
    ch_w: Optional[float] = None
    ch_zn: Optional[float] = None
    ch_zr: Optional[float] = None
    ch_te: Optional[float] = None
    ch_rad: Optional[float] = None
    ch_insal: Optional[float] = None
    ch_n2: Optional[float] = None
    ch_sal: Optional[float] = None
    long_cast_code: Optional[str] = None
    authorize_date: Optional[datetime] = None

    quality_id: Optional[int] = None
    quality: Optional[QualityRead] = None



# Cast Response
class CastCreate(CastResponse):
    pass

class CastUpdate(CastResponse):
    pass

class CastRead(CastResponse):
    id: int
    cast_semis: Optional[List[CastSemiRead]] = []

class CastPagination(DispatchBase):
    total: int
    items: List[CastRead] = []
    itemsPerPage: int
    page: int


class CastQualityCompare(DispatchBase):
    semi_load_ids: List[int]
