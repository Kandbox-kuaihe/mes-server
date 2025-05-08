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



class Sprem(Base,TimeStampMixin):

    __tablename__ = 'sprem'

    id = Column(BigInteger, primary_key=True,autoincrement=True)
    mill_id = Column(BigInteger, ForeignKey("mill.id"), nullable=True, )
    mill = relationship("Mill", backref="mill_Sprem")
    
    
    spec_id = Column(BigInteger, ForeignKey("spec.id"), nullable=False)
    spec = relationship("Spec", backref="spec_sprem")

    rem_type_1 = Column(String(5), nullable=False)
    rem_type_2 = Column(String(5), nullable=False)
    rem_type_3 = Column(String(5), nullable=False)
    rem_type_4 = Column(String(5), nullable=False)
    rem_type_5 = Column(String(5), nullable=False)
    rem_type_6 = Column(String(5), nullable=False)
    rem_type_7 = Column(String(5), nullable=False)
    rem_type_8 = Column(String(5), nullable=False)
    rem_type_9 = Column(String(5), nullable=False)
    rem_type_10 = Column(String(5), nullable=False)
    rem_type_11 = Column(String(5), nullable=False)
    rem_type_12 = Column(String(5), nullable=False)
    rem_type_13 = Column(String(5), nullable=False)
    rem_type_14 = Column(String(5), nullable=False)
    rem_type_15 = Column(String(5), nullable=False)
    filler = Column(String(20), nullable=False)


# BaseResponseModel

class SpremResponse(BaseResponseModel):
    # spif_spec_code: Optional[str] = None
    # spif_variation_no: Optional[int] = None
    spec: Optional[SpecRead] = None
    spec_id:  Optional[int]=None 

    mill_id: Optional[int] = None
    mill: Optional[MillRead] = None
    rem_type_1: Optional[str] = None
    rem_type_2: Optional[str] = None
    rem_type_3: Optional[str] = None
    rem_type_4: Optional[str] = None
    rem_type_5: Optional[str] = None
    rem_type_6: Optional[str] = None
    rem_type_7: Optional[str] = None
    rem_type_8: Optional[str] = None
    rem_type_9: Optional[str] = None
    rem_type_10: Optional[str] = None
    rem_type_11: Optional[str] = None
    rem_type_12: Optional[str] = None
    rem_type_13: Optional[str] = None
    rem_type_14: Optional[str] = None
    rem_type_15: Optional[str] = None
    filler: Optional[str] = None

# Sprem Response
class SpremCreate(SpremResponse):
    pass

class SpremUpdate(SpremResponse):
    pass

class SpremRead(SpremResponse):
    id: int

class SpremPagination(DispatchBase):
    total: int
    items: List[SpremRead] = []
    itemsPerPage: int
    page: int