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
from sqlalchemy import Column, Integer, String, BigInteger, Numeric, ForeignKey, CHAR, Text
from pydantic import BaseModel, Field, conint
from typing import Optional, List

from dispatch.product_category.models import ProductCategoryRead
from dispatch.spec_admin.spec.models import SpecRead
from dispatch.cast.models import CastRead
from dispatch.product_type.models import ProductTypeRead


# (Base,TimeStampMixin):



class SemiEndUseManual(Base,TimeStampMixin):

    __tablename__ = 'semi_end_use_manual'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    weight_min = Column( Numeric(precision=20,scale=2),  nullable=False)
    weight_max = Column( Numeric(precision=20,scale=2), nullable=False)
    product_category_id = Column(Integer, ForeignKey("product_category.id"), nullable=False)  # 外键，指向 ProductCategory 表
    product_category = relationship("ProductCategory", foreign_keys=[product_category_id])  # 设置外键关系
    
    spec_id = Column(BigInteger, ForeignKey("spec.id"), nullable=False, )
    spec = relationship("Spec", backref="spec_semi_end_use_manual")

    cast_id = Column( BigInteger,ForeignKey("cast.id"),   nullable=False)
    cast = relationship("Cast", backref="cast_semi_end_use_manual")

    short_name = Column( String, nullable=False)
    note = Column( String, nullable=True)
    mill_id = Column(BigInteger, ForeignKey("mill.id"), nullable=False, )
    mill = relationship("Mill", backref="mill_SemiEndUseManual")
    
    search_vector = Column(
        TSVectorType( 
            "short_name",
            weights={"code": "A" },
        )
    )
    
    # __table_args__ = (UniqueConstraint('mill_id', 'product_category_id', 'weight_min', 'weight_max','spec_id', 'cast_id', name='spec_id_product_category_weight_min_max_semi_end_use_manual'),)


class SemiEndUseManualResponse(BaseResponseModel):

    weight_min: Optional[float] = None
    weight_max: Optional[float] = None
    product_category_id: Optional[int] = None
    spec_id: Optional[int] = None
    cast_id: Optional[int] = None
    short_name: Optional[str] = None
    note: Optional[str] = None
    spec: Optional[SpecRead] = None 
    cast: Optional[CastRead] = None
    mill_id: Optional[int] = None
    mill: Optional[MillRead] = None
    

# SemiEndUseManual Response
class SemiEndUseManualCreate(SemiEndUseManualResponse):
    
    # virtual field
    flange_min: Optional[float] = None
    flange_max: Optional[float] = None

class SemiEndUseManualUpdate(SemiEndUseManualResponse):
    force: bool = False

    # virtual field
    flange_min: Optional[float] = None
    flange_max: Optional[float] = None

class SemiEndUseManualRead(SemiEndUseManualResponse):
    id: int
    product_category: Optional[ProductCategoryRead] = None

class SemiEndUseManualPagination(DispatchBase):
    total: int
    items: List[SemiEndUseManualRead] = []
    itemsPerPage: int
    page: int

class SemiEndUseManualNew(DispatchBase):
    id: int
    data: dict

class GetByCastSpec(DispatchBase):
    cast_no: Optional[str]
    section_code: Optional[str]
    page: int
    itemsPerPage: int


class SemiEndUseManualBlukCrreate(DispatchBase):
    product_category_id: Optional[int] = None
    mill_id: Optional[int] = None
    cast_id: Optional[int] = None

    items: List[SemiEndUseManualCreate] = Field(default_factory=list)

    force: bool = False

