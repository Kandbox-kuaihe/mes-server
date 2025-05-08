
from typing import Optional
from sqlalchemy import (
    Column,
    ForeignKey,
    String,
    BigInteger,
    Integer,
)


from dispatch.database import Base
from dispatch.models import BaseResponseModel, DispatchBase, TimeStampMixin

from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, BigInteger, Numeric, ForeignKey
from sqlalchemy import Column, Integer

from dispatch.spec_admin.spec.models import SpecRead


class SpVarious(Base, TimeStampMixin):

    __tablename__ = "sp_various"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    spec_id = Column(
        BigInteger,
        ForeignKey("spec.id"),
        nullable=True,
    )
    display_seq = Column(Integer, nullable=False)

    spec_product_type = Column(String)
    nb_ext_spec = Column(Integer)
    quality_code = Column(String, nullable=False)
    cd_char = Column(String, nullable=False)
    cd_param = Column(String, nullable=False)
    cd_source = Column(String, nullable=False)
    ds_param = Column(String, nullable=False)
    nm_param = Column(String, nullable=False)
    vl_min = Column(Numeric(20, 10), nullable=False)
    vl_max = Column(Numeric(20, 10), nullable=False)
    vl_fix = Column(Numeric(20, 10), nullable=False)
    cd_uom = Column(String, nullable=False)
    tx_obs = Column(String, nullable=False)

    spec = relationship("Spec", backref="spec_sp_various")




class SpObsRead(BaseResponseModel):
    id: Optional[int] = None
    spec_id: Optional[int] = None
    display_seq: Optional[int] = None
    spec_product_type: Optional[int] = None
    nb_ext_spec: Optional[int] = None
    quality_code: Optional[str] = None
    cd_char: Optional[str] = None
    cd_param: Optional[str] = None
    cd_source: Optional[str] = None
    ds_param: Optional[str] = None
    nm_param: Optional[str] = None
    vl_min: Optional[float] = None
    vl_max: Optional[float] = None
    vl_fix: Optional[float] = None
    cd_uom: Optional[str] = None
    tx_obs: Optional[str] = None
    spec: Optional[SpecRead] = None

class SpObsPagination(DispatchBase):
    total: int
    items: list[SpObsRead] = []
    itemsPerPage: int
    page: int
