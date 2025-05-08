from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey,Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from typing import List, Optional
from dispatch.models import TimeStampMixin, DispatchBase,BaseResponseModel
from dispatch.models import TimeStampMixin, DispatchBase,BaseResponseModel
from dispatch.database import Base

class QualityOtherElement(Base, TimeStampMixin):
    __tablename__ = 'quality_other_element'

    id = Column(Integer, primary_key=True)
    code = Column(String, nullable=False)
    min_value = Column(Numeric(20, 10), default=0, nullable=False)
    max_value = Column(Numeric(20, 10), default=0, nullable=False)
    precision = Column(Integer)
    quality_element_id = Column(Integer, ForeignKey('quality_element.id'), nullable=False)
    quality_element = relationship("QualityElement", backref="quality_other_element_quality")
    element_abbr = Column(String)
    
    
    
class QualityOtherElementResponse(BaseResponseModel):
    id: Optional[int] = None
    code: Optional[str] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    precision: Optional[int] = None
    quality_element_id: Optional[int] = None
    other_element: Optional[List[QualityOtherElement]] = None
    element_abbr: Optional[str] = None   
    
    
class QualityOtherElementBase(BaseResponseModel):
    code: Optional[str] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    precision: Optional[int] = None



class QualityOtherElementUpdate(QualityOtherElementBase):
    pass

class QualityOtherElementRead(QualityOtherElementBase):
    id: Optional[int] = None
    
    
class QualityOtherElementCreate(QualityOtherElementBase):
    quality_other_element: List[QualityOtherElementRead]
    
    
class QualityOtherElementPagination(DispatchBase):
    total: int
    items: List[QualityOtherElementResponse] = []
    itemsPerPage: int
    page: int
    quality_element_num: List[int] = []