from typing import Optional
from sqlalchemy import (
    Column,
    String,
    BigInteger,
    Integer,
)

from sqlalchemy.orm import relationship
from dispatch.database import Base
from dispatch.models import DispatchBase, TimeStampMixin, BaseResponseModel
from sqlalchemy import Column, Integer, String, BigInteger, Numeric, ForeignKey
from sqlalchemy import Column, Integer
from dispatch.spec_admin.spec.models import SpecRead



class SpOtherTest(Base, TimeStampMixin):

    __tablename__ = "sp_other_test"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    spec_id = Column(
        BigInteger,
        ForeignKey("spec.id"),
        nullable=True,
    )
    display_seq = Column(Integer, nullable=False)
    quality_code = Column(Integer, nullable=False)
    quality_suff = Column(String, nullable=False)
    cd_oper = Column(String, nullable=False)
    cd_vari = Column(String, nullable=False)
    vl_ql = Column(String, nullable=False)
    vl_min = Column(Numeric(20, 10), nullable=False)
    vl_max = Column(Numeric(20, 10), nullable=False)
    vl_fix = Column(Numeric(20, 10), nullable=False)
    cd_uom = Column(String, nullable=False)
    nb_seq_oper_vari = Column(Integer, nullable=False)
    st_qc = Column(String, nullable=False)
    vl_min_orig = Column(Numeric(20, 10), nullable=False)
    vl_max_orig = Column(Numeric(20, 10), nullable=False)
    vl_fix_orig = Column(Numeric(20, 10), nullable=False)
    cd_uom_orig = Column(String, nullable=False)
    spec = relationship("Spec", backref="spec_sp_other_test")


class SpOtherTestRead(BaseResponseModel):
    id: Optional[int] = None
    spec_id: Optional[int] = None
    quality_code: Optional[int] = None
    display_seq: Optional[int] = None
    quality_suff: Optional[str] = None
    cd_oper: Optional[str] = None
    cd_vari: Optional[str] = None
    vl_ql: Optional[str] = None
    vl_min: Optional[float] = None
    vl_max: Optional[float] = None
    vl_fix: Optional[float] = None
    cd_uom: Optional[str] = None
    nb_seq_oper_vari: Optional[int] = None
    st_qc: Optional[str] = None
    vl_min_orig: Optional[float] = None
    vl_max_orig: Optional[float] = None
    vl_fix_orig: Optional[float] = None
    cd_uom_orig: Optional[str] = None
    spec: Optional[SpecRead] = None
    
    


class SpOtherTestPagination(DispatchBase):
    total: int
    items: list[SpOtherTestRead] = []
    itemsPerPage: int
    page: int