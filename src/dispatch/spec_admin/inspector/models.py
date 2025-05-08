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
from typing import Optional, List



# (Base,TimeStampMixin):
from dispatch.mill.models import MillRead
from dispatch.spec_admin.inspector.models_secondary import spec_inspector_table


class Inspector(Base,TimeStampMixin):

    __tablename__ = 'inspector'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    mill_id = Column(BigInteger, ForeignKey("mill.id"), nullable=False)
    mill = relationship("Mill", backref="mill_inspector_item")

    code = Column(String, nullable=False)
    type = Column(String, nullable=True)
    name = Column(String, nullable=True)
    desc = Column(String, nullable=True)

    spec = relationship("Spec", secondary=spec_inspector_table, back_populates="inspector")


    search_vector = Column(
        TSVectorType(
            "code",
            "name",
            weights={"code": "A", "name": "B"},
        )
    )

    __table_args__ = (
        UniqueConstraint('code', name='unique_inspector_code'),
    )




# BaseResponseModel

class InspectorResponse(BaseResponseModel):
    mill_id: Optional[int] = None
    mill: Optional[MillRead] = None
    code: Optional[str] = None
    type: Optional[str] = None
    name: Optional[str] = None
    desc: Optional[str] = None
    
    

# Inspector Response
class InspectorCreate(InspectorResponse):
    pass
    id: Optional[int] = None

class InspectorUpdate(InspectorResponse):
    pass

class InspectorRead(InspectorResponse):
    id: int

class InspectorPagination(DispatchBase):
    total: int
    items: List[InspectorRead] = []
    itemsPerPage: int
    page: int


class InspectorSelect(DispatchBase):
    id: int
    code: str
    name: str

class InspectorSelectRespone(DispatchBase):
    options: Optional[List[InspectorSelect]] = []
