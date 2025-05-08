from typing import List, Optional

from sqlalchemy import (
    Column,
    ForeignKey,
    String,
    BigInteger
)

from typing import  Optional

from sqlalchemy.orm import relationship

from dispatch.database import Base
from dispatch.models import TimeStampMixin, DispatchBase,BaseResponseModel
from sqlalchemy import Column, String, BigInteger, Numeric, ForeignKey
from typing import Optional
from dispatch.cast.models import CastRead
from dispatch.spec_admin.spec.models import SpecRead

class SpecDeoxidation(Base,TimeStampMixin):
    __tablename__ = 'spec_deoxidation'
    id = Column(BigInteger, primary_key=True,autoincrement=True)

    spec_id = Column(BigInteger, ForeignKey("spec.id"), nullable=False, )
    spec = relationship("Spec", backref="spec_decarburisation")
    thick_from = Column(Numeric(20, 10))  # Thickness From
    thick_to = Column(Numeric(20, 10))  # Thickness To
    location = Column(String())
    remarks = Column(String())



class SpecDeoxidationBase(BaseResponseModel):
    spec_id: Optional[int] = None
    spec: Optional[SpecRead] = None
    thick_from: Optional[float] = None
    thick_to: Optional[float] = None
    location: Optional[str] = None
    remarks: Optional[str] = None



class SpecDeoxidationCreate(SpecDeoxidationBase):
    pass


class SpecDeoxidationUpdate(SpecDeoxidationBase):
    pass


class SpecDeoxidationRead(SpecDeoxidationBase,BaseResponseModel):
    id: int


class SpecDeoxidationPagination(DispatchBase):
    total: int
    items: List[SpecDeoxidationRead] = []
    itemsPerPage: int
    page: int