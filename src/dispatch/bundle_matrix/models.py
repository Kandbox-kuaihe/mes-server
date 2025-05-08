from typing import List, Optional
from datetime import datetime, date

from sqlalchemy import (
    Column,
    Float,
    ForeignKey,
    String,
    BigInteger,
    Integer,
    Numeric,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import UniqueConstraint
from sqlalchemy_utils import TSVectorType

from dispatch.database import Base
from dispatch.models import TimeStampMixin, DispatchBase,BaseResponseModel

class BundleMatrix(Base,TimeStampMixin):
    __tablename__ = 'bundle_maxtrix'

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    cust_no = Column(Integer, nullable=True)
    add_no = Column(Integer, nullable=True)
    roll_ref = Column(Integer, nullable=True)
    kg_per_metre = Column(Numeric(20, 10), nullable=False)
    max_bar_length = Column(Integer, default=0, nullable=False)
    num_bars = Column(Integer, default=0, nullable=False)
    bars_wide = Column(Integer, default=0, nullable=False)
    bars_high = Column(Integer, default=0, nullable=False)
    max_bundle_weight = Column(Numeric(20, 10), default=0, nullable=False)
    spec_no = Column(Integer, nullable=True)
    form = Column(String, default=0, nullable=False)
    size = Column(String, default=0, nullable=False)
    pc_wt = Column(Numeric(20, 10), default=0, nullable=False)
    shortest_flange_length = Column(Numeric(20, 10), default=0, nullable=False)
    flange_max_tol = Column(Numeric(20, 10), default=0, nullable=False)
    shortest_flange_length_max = Column(Numeric(20, 10), default=0, nullable=False)
    web_thickness = Column(Numeric(20, 10), default=0, nullable=False)
    web_thick_max_tol = Column(Numeric(20, 10), default=0, nullable=False)
    web_thickness_max = Column(Numeric(20, 10), default=0, nullable=False)
    BC_height = Column(Integer, default=0, nullable=False)
    PFC_height = Column(Integer, default=0, nullable=False)
    angle_height = Column(Integer, default=0, nullable=False)


    # search_vector = Column(
    #     TSVectorType(
    #         "code",
    #         weights={"code": "A"},
    #     )
    # )

    __table_args__ = (
        UniqueConstraint('cust_no', 'add_no', 'roll_ref', 'kg_per_metre', 'max_bar_length', 'spec_no',  name='unique_key_bundle_matrix_multi'),
    )


class BundleMatrixBase(BaseResponseModel):
    cust_no: Optional[int] = None
    add_no: Optional[int] = None
    roll_ref: Optional[int] = None
    kg_per_metre: Optional[float] = None
    max_bar_length: Optional[int] = None
    num_bars: Optional[int] = None
    bars_wide: Optional[int] = None
    bars_high: Optional[int] = None
    max_bundle_weight: Optional[int] = None
    spec_no: Optional[int] = None


class BundleMatrixRead(BundleMatrixBase):
    id: int

class BundleMatrixCreate(BundleMatrixBase):
    pass

class BundleMatrixUpdate(BundleMatrixBase):
    pass

class BundleMatrixPagination(DispatchBase):
    total: int
    items: List[BundleMatrixRead] = []
    itemsPerPage: int
    page : int

class AutoPlanGet(DispatchBase):
    cust_no: Optional[int] = None
    add_no: Optional[int] = None
    roll_ref: Optional[int] = None
    kg_per_metre: Optional[float] = None
    max_bar_length: Optional[int] = None
    spec_no: Optional[int] = None