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
from dispatch.spec_admin.quality.models import QualityRead

from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, BigInteger, Numeric, ForeignKey
from sqlalchemy import Column, Integer, CHAR, Text
from pydantic import BaseModel, Field, conint
from typing import Optional, List, Dict

class AltQualityCode(Base, TimeStampMixin):
    __tablename__ = "alt_quality_code"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    quality_code = Column(String, nullable=False)
    alt_quality_code = Column(String, nullable=True)
    preference = Column(String, nullable=True)
    rank = Column(Integer, nullable=True)  
    quality_id = Column(Integer, ForeignKey('quality.id'))
    quality = relationship("Quality", backref="alt_quality_code_quality")

    __table_args__ = (
        UniqueConstraint("quality_code", "alt_quality_code", name="alt_quality_code_uix_quality_alt"),
    )

class AltQualityCodeBaseResponse(BaseResponseModel):
    quality_code: Optional[str] = None
    alt_quality_code: Optional[str] = None
    preference: Optional[str] = None
    rank: Optional[int] = None
    quality_id: Optional[int] = None
    
class AltQualityCodeUpdate(AltQualityCodeBaseResponse):
    quality_code: Optional[str] = None
    alt_quality_code: Optional[str] = None
    rank: Optional[int] = None
    quality_id: Optional[int] = None

class AltQualityCodeCreate(AltQualityCodeBaseResponse):
    pass


class AltQualityCodeRead(AltQualityCodeBaseResponse, BaseResponseModel):
    id: int
    flex_form_data: Optional[dict]
    quality: Optional[QualityRead]

class AltQualityCodePagination(DispatchBase):
    total: int
    items: List[AltQualityCodeRead] = []
    itemsPerPage: int
    page: int
