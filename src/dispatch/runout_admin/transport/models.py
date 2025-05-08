from typing import List, Optional
from enum import Enum
from sqlalchemy import (
    Column,
    Float,
    ForeignKey,
    String,
    BigInteger,
    Integer,
    DateTime, Numeric
)

from typing import  Optional

from sqlalchemy.sql.schema import UniqueConstraint
from sqlalchemy_utils import TSVectorType

from dispatch.database import Base
from dispatch.mill.models import MillRead
from dispatch.models import TimeStampMixin, DispatchBase,BaseResponseModel

from sqlalchemy.orm import relationship
from dispatch.site.models import SiteRead


class Transport(Base,TimeStampMixin):
    __tablename__ = 'transport'
    
    id = Column(BigInteger, primary_key=True,autoincrement=True)
    code = Column(String, nullable=False)
    type = Column(String)
    road_type = Column(String)
    desc = Column(String)
    site_id = Column(BigInteger, ForeignKey("site.id"), nullable=True)
    site = relationship("Site", backref="site_transport")
    length_mm = Column(Numeric(20, 10))
    weight_kg = Column(Numeric(20, 10))
    status = Column(String)
    mill_id = Column(BigInteger, ForeignKey("mill.id"), nullable=True)
    mill = relationship("Mill", backref="mill_transport")

    search_vector = Column(
        TSVectorType(
            "code",
            weights={"code": "A"},
        )
    )

    __table_args__ = (
        UniqueConstraint('code', name='unique_key_transport_code'),
    )


class TransportBase(BaseResponseModel):
    code: Optional[str] = None
    type: Optional[str] = None
    road_type: Optional[str] = None
    desc: Optional[str] = None
    site_id: Optional[int] = None
    length_mm: Optional[float] = None
    weight_kg: Optional[float] = None
    status: Optional[str] = None
    mill_id: Optional[int] = None


class TransportCreate(TransportBase):
    pass


class TransportUpdate(TransportBase):
    ids: List[int] = []


class TransportRead(TransportBase,BaseResponseModel):
    id: int
    site: Optional[SiteRead] = None
    mill: Optional[MillRead] = None


class TransportPagination(DispatchBase):
    total: int
    items: List[TransportRead] = []
    itemsPerPage: int
    page : int


class TransportStatusEnum(str,Enum):
    DELOAD = "Available"
    ONLOAD = "Transport"