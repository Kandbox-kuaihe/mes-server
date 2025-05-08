from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    Column,
    Float,
    String,
    BigInteger,
    ForeignKey
)
# from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import UniqueConstraint
from sqlalchemy_utils import TSVectorType

from dispatch.database import Base
from dispatch.mill.models import MillRead
from dispatch.models import TimeStampMixin, DispatchBase
from sqlalchemy.orm import relationship
from dispatch.site_type.models import SiteTypeRead


# from dispatch.database import registry
# @registry.mapped
class Site(Base, TimeStampMixin):
    __tablename__ = 'site'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    code = Column(String, nullable=False)
    name = Column(String, nullable=True)
    desc = Column(String, nullable=True)
    type = Column(String, nullable=True)
    site_type_id = Column(BigInteger, ForeignKey("site_type.id"), nullable=True)
    longitude = Column(Float, nullable=True)
    latitude = Column(Float, nullable=True)
    # areas = relationship("Area", back_populates="site")
    site_type = relationship("SiteType", foreign_keys=[site_type_id], backref="site_type_site")
    mill_id = Column(BigInteger, ForeignKey("mill.id"), nullable=True, )
    mill = relationship("Mill", backref="mill_Site")
    search_vector = Column(
        TSVectorType(
            "code",
            "name",
            weights={"code": "A", "name": "B"},
        )
    )

    __table_args__ = (UniqueConstraint('code', 'mill_id', 'type', name='uix_type_mill_id_site_code'),)


class SiteBase(DispatchBase):
    code: str = ""
    name: Optional[str] = None
    desc: Optional[str] = None
    site_type_id: Optional[int] = None
    site_type: Optional[SiteTypeRead] = None
    site_type_code: Optional[str] = None

    latitude: Optional[float] = None
    longitude: Optional[float] = None

    flex_form_data: Optional[dict] = None
    mill_id: Optional[int] = None
    mill: Optional[MillRead] = None
    is_deleted: Optional[int] = None

class SiteCreate(SiteBase):
    site_type_id: Optional[int] = None
    pass


class SiteUpdate(SiteBase):
    site_type_id: Optional[int] = None
    pass


class SiteRead(SiteBase):
    id: int
    flex_form_data: Optional[dict]


class SitePagination(DispatchBase):
    total: int
    items: List[SiteRead] = []
    itemsPerPage: int
    page: int
