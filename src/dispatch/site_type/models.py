from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    Column,
    Float,
    String,
    BigInteger,
    Integer,
    ForeignKey
)
# from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import UniqueConstraint
from sqlalchemy_utils import TSVectorType

from dispatch.database import Base
from dispatch.models import TimeStampMixin, DispatchBase
from sqlalchemy.orm import relationship
from dispatch.mill.models import MillRead


# from dispatch.database import registry
# @registry.mapped
class SiteType(Base, TimeStampMixin):
    __tablename__ = 'site_type'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    code = Column(String, nullable=False)
    type = Column(String, nullable=True)
    name = Column(String, nullable=False)
    desc = Column(String, nullable=True)
    longitude = Column(Float, nullable=True)
    latitude = Column(Float, nullable=True)
    mill_id = Column(Integer, ForeignKey("mill.id"), nullable=False) # 外键，指向 Mill 表
    business_type = Column(String, nullable=True)

    mill = relationship("Mill", foreign_keys=[mill_id])

    search_vector = Column(
        TSVectorType(
            "code",
            "name",
            weights={"code": "A", "name": "B"},
        )
    )

    __table_args__ = (UniqueConstraint('code', 'mill_id', 'type', name='uix_type_mill_id_site_type_code'),)


class SiteTypeBase(DispatchBase):
    code: Optional[str] = None
    name: Optional[str] = None
    desc: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    business_type: Optional[str] = None
    mill_id: Optional[int] = None
    mill_code: Optional[str] = None
    mill: Optional[MillRead] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    flex_form_data: Optional[dict] = None
    is_deleted: Optional[int] = None


class SiteTypeCreate(SiteTypeBase):
    pass

class SiteTypeUpdate(SiteTypeBase):
    pass


class SiteTypeRead(SiteTypeBase):
    id: int


class SiteTypePagination(DispatchBase):
    total: int
    items: List[SiteTypeRead] = []
    itemsPerPage: int
    page: int
