from typing import List, Optional,Any
from pydantic import  Field

from sqlalchemy import (
    Column,
    Float,
    ForeignKey,
    String,
    BigInteger,
    Integer,
    Boolean, UniqueConstraint
)
from typing import Dict, Optional

from dispatch.database import Base
from dispatch.mill.models import MillRead
from dispatch.models import TimeStampMixin, DispatchBase,BaseResponseModel

from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, BigInteger, Numeric, ForeignKey,Date
from sqlalchemy import Column, Integer, CHAR, Text
from pydantic import BaseModel, Field, conint
from typing import Optional, List
from sqlalchemy_utils import TSVectorType



class Quality(Base, TimeStampMixin):
    __tablename__ = 'quality'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    
    mill_id = Column(
        BigInteger,
        ForeignKey("mill.id"),
        nullable=True,
    )
    mill = relationship("Mill", backref="mill_quality")
    code = Column(String, nullable=False)
    name = Column(String, nullable=True)
    version = Column(Integer, nullable=True)
    version_status = Column(String, nullable=True)
    type = Column(String, nullable=True)
    standard = Column(String, nullable=True)
    release_date = Column(Date, nullable=True)
    archive_date = Column(Date, nullable=True)
    quality_group = Column(String, nullable=True)
    desc = Column(String, nullable=True)
    spec_units = Column(String, nullable=True)
    source_type = Column(String, nullable=True)
    require_dressing = Column(String, nullable=True)

    __table_args__ = (UniqueConstraint('code', 'mill_id', name='uix_quality_code_mill_id'),)

    search_vector = Column(
        TSVectorType(
            "code",
            "name",
            weights={"code": "A", "name": "B"},
        )
    )


class QualityResponse(BaseResponseModel):
    id : Optional[int] = None
    mill_id : Optional[int] = None
    code : Optional[str] = None
    name : Optional[str] = None
    version : Optional[int] = None
    version_status : Optional[str] = None
    standard : Optional[str] = None
    release_date : Optional[Any] = None
    archive_date : Optional[Any] = None
    quality_group : Optional[str] = None
    desc : Optional[str] = None
    spec_units : Optional[str] = None
    source_type : Optional[str] = None
    require_dressing: Optional[str] = None

class QualityRead(QualityResponse):
    id : int
    mill: Optional[MillRead] = None
    type: Optional[str] = None
    
class QualityUpdate(QualityResponse):
    pass

class QualityCreate(QualityResponse):
    pass
    # other_element: List[QualityElementRead] = []
    
    
class QualityPagination(DispatchBase):
    total: int
    items: List[QualityRead] = []
    itemsPerPage: int
    page: int
    quality_num: List[int] = []
