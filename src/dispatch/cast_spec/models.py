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
from dispatch.models import TimeStampMixin, DispatchBase,BaseResponseModel

from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, BigInteger, Numeric, ForeignKey
from sqlalchemy import Column, Integer, CHAR, Text
from pydantic import BaseModel, Field, conint
from typing import Optional, List
from dispatch.semi_admin.alternative_semi_size.models import AlternativeSemiSizeRead
from dispatch.spec_admin.spec.models import SpecRead
from dispatch.product_type.models import ProductTypeRead
from dispatch.cast.models import CastRead




class CastSpec(Base,TimeStampMixin):

    __tablename__ = 'cast_spec'  

    id = Column(BigInteger, primary_key=True,autoincrement=True)
      
    cast_id = Column(BigInteger, ForeignKey("cast.id"), nullable=False, )
    cast = relationship("Cast", backref="cast_cast_spec")
    
    spec_id = Column(BigInteger, ForeignKey("spec.id"), nullable=False, )
    spec = relationship("Spec", backref="spec_cast_spec")

    product_type_id = Column(Integer, ForeignKey("product_type.id"), nullable=False)
    product_type = relationship("ProductType", backref="product_type_cast_spec")
    
          
    
# BaseResponseModel

class CastSpecResponse(BaseResponseModel):
    spec_id:  Optional[int]=None 
    spec: Optional[SpecRead] = None
    
    cast: Optional[CastRead] = None 
    cast_id: Optional[int]=None 

    product_type: Optional[ProductTypeRead] = None 
    product_type_id: Optional[int]=None 

    
    
# Cast Response
class CastSpecCreate(CastSpecResponse):
    pass

class CastSpecUpdate(CastSpecResponse):
    pass

class CastSpecRead(CastSpecResponse):
    id: int
    alt_semi_sizes: List[AlternativeSemiSizeRead] = []

class CastSpecPagination(DispatchBase):
    total: int
    items: List[CastSpecRead] = []
    itemsPerPage: int
    page: int