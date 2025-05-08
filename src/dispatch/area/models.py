from typing import List, Optional

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
from dispatch.mill.models import MillRead
from dispatch.models import TimeStampMixin, DispatchBase, BaseResponseModel
# Association tables for many to many relationships

from sqlalchemy.orm import relationship

from dispatch.site.models import SiteRead


#  material part product  asset  Area
class Area(Base, TimeStampMixin):
    __tablename__ = 'area'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    code = Column(String, nullable=False, )
    type = Column(String, nullable=False)
    desc = Column(String)
    # site_id = Column(BigInteger, ForeignKey("site.id"))
    # site = relationship("Site", backref="area_to_site_id")

    site_id = Column(Integer, ForeignKey("site.id"), nullable=False)
    longitude = Column(Float, nullable=True)
    latitude = Column(Float, nullable=True)
    charge_status = Column(String, nullable=True)
    processing_type = Column(String, nullable=True)

    site = relationship("Site", foreign_keys=[site_id])
    mill_id = Column(BigInteger, ForeignKey("mill.id"), nullable=False, )
    mill = relationship("Mill", backref="mill_Area")

    row = Column(Integer, nullable=True)
    slot = Column(Integer, nullable=True)

    search_vector = Column(
        TSVectorType(
            "code",
            "type",
            weights={"code": "A", "type": "B"},
        )
    )

    __table_args__ = (UniqueConstraint('code', 'mill_id', 'type', name='uix_type_mill_id_area_code'),)


class AreaBase(BaseResponseModel):
    code: str = ""
    type: Optional[str] = None
    desc: Optional[str] = None
    site_id: Optional[int] = None
    site: Optional[SiteRead] = None
    site_code: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    charge_status: Optional[str] = None
    processing_type: Optional[str] = None
    mill_id: Optional[int] = None
    mill: Optional[MillRead] = None
    row: Optional[int] = None
    slot: Optional[int] = None


class AreaCreate(AreaBase):
    site_id: Optional[int] = None


class AreaUpdate(AreaBase):
    pass


class AreaRead(AreaBase, BaseResponseModel):
    id: int
    flex_form_data: Optional[dict]


class AreaPagination(DispatchBase):
    total: int
    items: List[AreaRead] = []
    itemsPerPage: int
    page: int