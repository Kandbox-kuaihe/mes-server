from typing import Any, List, Optional
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
# from dispatch.location.models import LocationCreate, LocationRead
from dispatch.models import TimeStampMixin, DispatchBase,BaseResponseModel
# Association tables for many to many relationships

from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, BigInteger, Numeric, ForeignKey
from dispatch.system_admin.auth.models import UserRead
from dispatch.system_admin.auth.models_secondary import user_mill_table


class Mill(Base,TimeStampMixin):
    __tablename__ = 'mill'
    
    id = Column(BigInteger, primary_key=True,autoincrement=True)
    code = Column(String, unique=True, nullable=False)
    type = Column(String, nullable=False)
    desc = Column(String, nullable=False)

    dispatch_user = relationship("DispatchUser", secondary=user_mill_table, back_populates="mill")
    
    search_vector = Column(
        TSVectorType(
            "code",
            "type",
            weights={"code": "A", "type": "B"},
        )
    )

    __table_args__ = (
        UniqueConstraint('code', 'type', name='unique_key_mill_code_type'),
    )
    

    
class MillBase(BaseResponseModel):

    code: Optional[str] = ""
    type: Optional[str] = ""
    desc: Optional[str] = ""



class MillCreate(MillBase):
    dispatch_user: Optional[List[Any]] = []
    user_ids: Optional[List[int]] = []


class MillUpdate(MillBase):
    dispatch_user: Optional[List[Any]] = []
    user_ids: Optional[List[int]] = []


class MillRead(DispatchBase):
    # 其他地方引用Mill使用， 只保留基本元素
    id: int
    code: Optional[str] = ""
    type: Optional[str] = ""
    desc: Optional[str] = ""
    

class MillOwnerRead(MillBase):
    # Mill 增删改查使用
    id: int
    dispatch_user: Optional[List[UserRead]] = []


class MillPagination(DispatchBase):
    total: int
    items: List[MillOwnerRead] = []
    itemsPerPage: int
    page : int

class MillSelect(DispatchBase):
    id: int
    code: str

class MillSelectRespone(DispatchBase):
    options: Optional[List[MillSelect]] = []