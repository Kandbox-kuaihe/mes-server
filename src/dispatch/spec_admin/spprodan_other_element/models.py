from sqlalchemy import (
    Column,
    Float,
    ForeignKey,
    String,
    BigInteger,
    Integer,
    Boolean
)
from datetime import datetime
from typing import Dict, Optional

from dispatch.database import Base
from dispatch.mill.models import MillRead
from dispatch.models import TimeStampMixin, DispatchBase,BaseResponseModel

from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, BigInteger, Numeric, ForeignKey, CHAR, Text
from pydantic import BaseModel, Field, conint
from typing import Optional, List

# from dispatch.spec_admin.spprodan.models import SpprodanRead



class SpprodanOtherElement(Base,TimeStampMixin):
    __tablename__ = 'spprodan_other_element'
    id = Column(Integer, primary_key=True)
    spprodan_id = Column(Integer, ForeignKey('spprodan.id'), nullable=False)
    spprodan = relationship("Spprodan", backref="spprodan_other_element")
    code = Column(String, nullable=False)
    min_value = Column(Numeric(20,10), nullable=False)
    max_value = Column(Numeric(20,10), nullable=False)
    precision = Column(Integer, nullable=False)


class SpprodanOtherElementBase(BaseResponseModel):
    spprodan_id: Optional[int] = None
    # spprodan = Optional[SpprodanRead]
    code: Optional[str] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    precision: Optional[int] = None



class SpprodanOtherElementUpdate(SpprodanOtherElementBase):
    pass

class SpprodanOtherElementRead(SpprodanOtherElementBase):
    id: Optional[int] = None

class SpprodanOtherElementCreate(SpprodanOtherElementBase):
    other_element: List[SpprodanOtherElementRead]

class SpprodanOtherElementPagination(DispatchBase):
    total: int
    items: List[SpprodanOtherElementRead] = []
    itemsPerPage: int
    page: int

