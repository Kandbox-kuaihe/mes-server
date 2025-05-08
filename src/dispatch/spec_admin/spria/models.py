from typing import Optional, List

from pydantic import Field
from sqlalchemy import Column, Integer, UniqueConstraint
from sqlalchemy import String, BigInteger, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, BigInteger, Numeric, ForeignKey

from dispatch.database import Base
from dispatch.mill.models import MillRead
from dispatch.models import TimeStampMixin, DispatchBase, BaseResponseModel
from dispatch.spec_admin.spec.models import SpecRead


class Spria(Base, TimeStampMixin):

    __tablename__ = 'spria'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    mill_id = Column(
        BigInteger,
        ForeignKey("mill.id"),
        nullable=True,
    )
    mill = relationship("Mill", backref="mill_Spria")

    spec_id = Column(
        BigInteger,
        ForeignKey("spec.id"),
        nullable=False,
    )
    spec = relationship("Spec", backref="spec_spria")

    thick_from = Column(Numeric(20, 10), nullable=False)
    thick_to = Column(Numeric(20, 10), nullable=False)
    location = Column(String(1), nullable=False)
    ria_min_value = Column(Integer, nullable=False)
    ria_ave_value = Column(Integer, nullable=False)
    uts_min = Column(Integer, nullable=False)
    filler = Column(String(100), nullable=True)

    __table_args__ = (
        UniqueConstraint('spec_id', 'thick_from', 'thick_to', 'mill_id', name='spria_uix_spec_thick_from_to'),
    )


# BaseResponseModel


class SpriaResponse(BaseResponseModel):
    # spif_spec_code: Optional[str] = None
    # spif_variation_no: Optional[int] = None
    spec: Optional[SpecRead] = None
    spec_id: Optional[int] = None

    mill_id: Optional[int] = None
    mill: Optional[MillRead] = None
    thick_from: Optional[float] = None
    thick_to: Optional[float] = None
    location: Optional[str] = None
    ria_min_value: Optional[int] = None
    ria_ave_value: Optional[int] = None
    uts_min: Optional[int] = None
    filler: Optional[str] = None


# Spria Response
class SpriaCreate(SpriaResponse):
    pass


class SpriaUpdate(SpriaResponse):
    pass


class SpriaRead(SpriaResponse):
    id: int


class SpriaPagination(DispatchBase):
    total: int
    items: List[SpriaRead] = Field(default_factory=list)
    itemsPerPage: int
    page: int


class SpriaCopyToCode(DispatchBase):
    before_code: str
    after_code: str
