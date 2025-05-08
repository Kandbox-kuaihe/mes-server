from datetime import datetime
from enum import Enum
from typing import List, Optional

from sqlalchemy import Column, Integer, String, DateTime, BigInteger, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy_utils import TSVectorType

from dispatch.database import Base
from dispatch.mill.models import MillRead
from dispatch.models import DispatchBase, TimeStampMixin, BaseResponseModel
from dispatch.semi_admin.semi.models import SemiRead


class SemiMoveHistory(Base, TimeStampMixin):
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    semi_id = Column(BigInteger, ForeignKey("semi.id"), nullable=False)
    rolling_id = Column(BigInteger, ForeignKey("rolling.id"))
    order_group_id = Column(BigInteger, ForeignKey("order_group.id"))
    area_id = Column(BigInteger, ForeignKey("area.id"), nullable=True)
    semi_load_id = Column(BigInteger, ForeignKey("semi_load.id"))
    cast_id = Column(BigInteger, ForeignKey("cast.id"))
    semi_type = Column(String, nullable=True)
    skelp_code = Column(String, nullable=True)
    semi_charge_seq = Column(Integer, nullable=True)
    semi_code = Column(String, nullable=True)
    weight_flag = Column(String, nullable=True)
    furnace_seq = Column(Integer, nullable=True)
    charge_time = Column(DateTime)
    comment = Column(String)
    quantity = Column(Integer)
    charge_seq = Column(Integer)
    stock_in_date = Column(DateTime)
    semi_cut_seq = Column(Integer)
    quality_code = Column(String)
    width_mm = Column(Numeric(20, 10))
    length_mm = Column(Numeric(20, 10))
    orig_length_mm = Column(Numeric(20, 10))
    thickness_mm = Column(Numeric(20, 10))
    estimated_weight_kg = Column(Numeric(20, 10))
    scarfed_status = Column(String)

    mill_id = Column(
        BigInteger,
        ForeignKey("mill.id"),
        nullable=True,
    )
    mill = relationship("Mill", backref="mill_SemiMoveHistory")
    uuid = Column(String, index=True, nullable=False)
    change_type = Column(String)
    code = Column(String, nullable=True)
    site_no = Column(String)
    area_no = Column(String)
    location = Column(String, nullable=True)

    rolling_code = Column(String)
    cast_no = Column(String)
    order_group_code = Column(String)
    defect_reason = Column(String)
    defect_quantity = Column(Integer)
    rework_type = Column(String)
    rework_status = Column(String)
    rework_comment = Column(String)

    search_vector = Column(
        TSVectorType(
            "location",
            weights={"location": "A"},
        )
    )


class SemiMoveHistoryBase(BaseResponseModel):
    change_type: Optional[str] = None
    mill_id: Optional[int] = None
    mill: Optional[MillRead] = None
    uuid: Optional[str] = None
    code: Optional[str] = None
    site_no : Optional[str] = None
    area_no : Optional[str] = None
    location: Optional[str] = None
    rolling_code : Optional[str] = None
    cast_no : Optional[str] = None
    order_group_code : Optional[str] = None

    semi: Optional[SemiRead] = None
    semi_type: Optional[str] = None
    quantity: Optional[int] = None
    charge_seq: Optional[int] = None
    stock_in_date: Optional[datetime] = None
    semi_charge_seq: Optional[int] = None
    semi_code: Optional[str] = None
    weight_flag: Optional[str] = None
    furnace_seq: Optional[int] = None
    charge_time: Optional[datetime] = None
    comment: Optional[str] = None
    semi_cut_seq: Optional[int] = None
    quality_code: Optional[str] = None
    width_mm: Optional[float]
    length_mm: Optional[float]
    orig_length_mm: Optional[float]
    thickness_mm: Optional[float]
    estimated_weight_kg: Optional[float]
    scarfed_status: Optional[str]
    defect_reason: Optional[str] = None
    defect_quantity: Optional[int] = None
    rework_type: Optional[str] = None
    rework_status: Optional[str] = None
    rework_comment: Optional[str] = None




class SemiMoveHistoryCreate(SemiMoveHistoryBase):
    updated_by: Optional[str] = None


class SemiMoveHistoryUpdate(SemiMoveHistoryBase):
    updated_by: Optional[str] = None


class SemiMoveHistoryRead(SemiMoveHistoryBase):
    id: int


class SemiMoveHistoryPagination(DispatchBase):
    total: int
    items: List[SemiMoveHistoryRead] = []
    itemsPerPage: int
    page: int


class SemiMoveHistoryChangTypeEnum(str, Enum):
    MOVE = "move"
    BLOCK = "block"
    UNBLOCK = "unblock"
    DELETE = "delete"
    CREATE = "create"
    UPDATE = 'update'
    REWORK = 'rework'
    REWORK_COMPLETE = 'rework_complete'
    DEFECT = 'defect'
    RESERVE = 'reserve'
    UNRESERVE = 'unreserve'
    HOLD= 'hold'
    UNHOLD= 'unhold'