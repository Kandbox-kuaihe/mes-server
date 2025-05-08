from typing import List, Optional

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
from sqlalchemy import Column, Integer, String, BigInteger, Numeric, ForeignKey
from sqlalchemy import Column, Integer, CHAR, Text
from pydantic import BaseModel, Field, conint
from typing import Optional, List



class SpmainelOtherElement(Base,TimeStampMixin):
    __tablename__ = 'spmainel_other_element'
    id = Column(Integer, primary_key=True)
    spmainel_id = Column(Integer, ForeignKey('spmainel.id'), nullable=False)
    spmainel = relationship("Spmainel", backref="spmainel_other_element")
    code = Column(String(255), nullable=False)
    min_value = Column(Numeric(20,10), nullable=False)
    max_value = Column(Numeric(20,10), nullable=False)
    precision = Column(Integer)
    element_abbr = Column(String)
    uom = Column(String)


class SpmainelOtherElementBase(BaseResponseModel):
    spmainel_id: Optional[int] = None
    # spmainel = Optional[SpMainElRead]
    code: Optional[str] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    precision: Optional[int] = None
    element_abbr: Optional[str] = None
    uom: Optional[str] = None


class SpmainelOtherElementUpdate(SpmainelOtherElementBase):
    pass

class SpmainelOtherElementRead(SpmainelOtherElementBase):
    id: Optional[int] = None

class SpmainelOtherElementCreate(SpmainelOtherElementBase):
    other_element: List[SpmainelOtherElementRead]

class SpmainelOtherElementPagination(DispatchBase):
    total: int
    items: List[SpmainelOtherElementRead] = []
    itemsPerPage: int
    page: int

