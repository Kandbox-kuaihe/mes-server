from typing import Optional
from sqlalchemy import (
    Column,
    ForeignKey,
    String,
    BigInteger,
    Integer,
)


from sqlalchemy.orm import relationship
from dispatch.database import Base
from dispatch.models import BaseResponseModel, DispatchBase, TimeStampMixin

from sqlalchemy import Column, Integer, String, BigInteger, ForeignKey
from sqlalchemy import Column, Integer

from dispatch.spec_admin.spec.models import SpecRead


class SpObs(Base, TimeStampMixin):

    __tablename__ = "sp_obs"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    spec_id = Column(
        BigInteger,
        ForeignKey("spec.id"),
        nullable=True,
    )
    display_seq = Column(Integer, nullable=False)
    spec_product_type = Column(Integer, nullable=False)
    nb_ext_spec = Column(Integer, nullable=False)
    cd_oper = Column(String, nullable=False)
    tx_obs = Column(String, nullable=False)

    spec = relationship("Spec")


class SpObsRead(BaseResponseModel):
    id: Optional[int] = None
    spec_id: Optional[int] = None
    display_seq: Optional[int] = None
    spec_product_type: Optional[int] = None
    nb_ext_spec: Optional[int] = None
    cd_oper: Optional[str] = None
    tx_obs: Optional[str] = None
    spec: Optional[SpecRead] = None


class SpObsPagination(DispatchBase):
    total: int
    items: list[SpObsRead] = []
    itemsPerPage: int
    page: int
