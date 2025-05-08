import uuid
from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import Field
from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Index, Date
)

from dispatch.database import Base
from dispatch.models import BaseResponseModel, DispatchBase, TimeStampMixin


class FinishedProductHistory(Base, TimeStampMixin):
    __tablename__ = "finished_product_history"

    runout_id = Column(BigInteger, ForeignKey("runout.id"))
    finished_product_id = Column(BigInteger, ForeignKey("finished_product.id"))
    area_id = Column(BigInteger, ForeignKey("area.id"))
    adviced_id = Column(BigInteger, ForeignKey("advice.id"))
    order_item_id = Column(BigInteger, ForeignKey("order_item.id"))

    cut_seq = Column(Integer)
    spec_id = Column(BigInteger, ForeignKey("spec.id"))
    width_mm = Column(Numeric(20, 10))
    thickness_mm = Column(Numeric(20, 10))
    estimated_weight_kg = Column(Numeric(20, 10))

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    uuid = Column(String, default=uuid.uuid4)
    change_type = Column(String)
    mill_id = Column(BigInteger, ForeignKey("mill.id"), nullable=True,)

    code = Column(String)
    cut_code = Column(String)
    sawn_by = Column(String)
    rolling_code = Column(String)
    kg = Column(String)
    length_mm = Column(Numeric(20, 10))
    cast_no = Column(String)
    spec_code = Column(String)
    pass_tests = Column(String)
    location = Column(String)
    multed_with = Column(String)
    runout_code = Column(String)
    order_num = Column(String)
    product_type = Column(String)
    order_item_num = Column(String)
    onward = Column(Integer)
    bundle = Column(Integer)
    alt_spec = Column(String)

    stock_type = Column(String)
    area_code = Column(String)
    site_code = Column(String)
    site_type_code = Column(String)

    rework_status = Column(String)
    rework_initial = Column(String)
    rework_due_date = Column(Date)
    rework_finish_date = Column(Date)

    status_change_reason = Column(String)
    defect_reason = Column(String)
    allocate_reason = Column(String)
    comment = Column(String)

    from_allocation_status = Column(String)
    allocation_status = Column(String)
    exist_flag = Column(String)
    mult_code = Column(String)
    mult_type = Column(String)
    waste_length = Column(Numeric(20, 10))
    quantity = Column(Integer)

    reserve_status = Column(String)
    status = Column(String)
    advice_no = Column(String)

    __table_args__ = (
        Index('ix_finished_product_history_created_at_change_type', 'created_at', 'change_type'),
    )

class FinishedProductHistoryBase(BaseResponseModel):
    uuid: Optional[str]
    change_type: Optional[str]
    mill_id: Optional[int]
    code: Optional[str]
    cut_code: Optional[str]
    sawn_by: Optional[str]
    rolling_code: Optional[str]
    kg: Optional[str]
    length_mm: Optional[float]
    cast_no: Optional[str]
    spec_code: Optional[str]
    pass_tests: Optional[str]
    location: Optional[str]
    multed_with: Optional[str]
    runout_code: Optional[str]
    order_num: Optional[str]
    product_type: Optional[str]
    order_item_num: Optional[str]
    onward: Optional[int]
    bundle: Optional[int]
    alt_spec: Optional[str]

    stock_type: Optional[str]
    area_code: Optional[str]
    site_code: Optional[str]
    site_type_code: Optional[str]

    rework_status: Optional[str]
    rework_initial: Optional[str]
    rework_due_date: Optional[datetime]
    rework_finish_date: Optional[datetime]

    status_change_reason: Optional[str]
    comment: Optional[str]
    defect_reason: Optional[str]
    allocate_reason: Optional[str]

    from_allocation_status: Optional[str]
    allocation_status: Optional[str]
    exist_flag: Optional[str]
    mult_code: Optional[str]
    mult_type: Optional[str]
    waste_length: Optional[float]
    quantity: Optional[int]

    reserve_status: Optional[str] = None

    status : Optional[str] = None
    advice_no: Optional[str] = None


class FinishedProductHistoryCreate(FinishedProductHistoryBase):
    pass


class FinishedProductHistoryRead(FinishedProductHistoryBase):
    id: int



class FinishedProductHistoryPagination(DispatchBase):
    total: int
    items: List[FinishedProductHistoryRead] = Field(default_factory=list)
    total_weight: Optional[float] = 0
    total_bars: Optional[float] = 0


class FinishedProductHistoryChangeTypeEnum(str, Enum):
    """
    Enum for finished product history change type
    """

    HOLD = "hold"
    UNHOLD = "unhold"
    REWORK = "rework"
    REWORK_COMPLETE = "rework_complete"
    MOVE = "move"
    CREATE = "create"
    ALLOCATE = "allocate"
    REGRADE = "regrade"
    UNCOVER = "uncover"
    MULT = "mult"
    MULT_COMPLETE = "mult_complete"
    RESERVE = "reserve"
    DELETE = "delete"
    EDIT = "edit"
    RETRIEVE = "retrieve"
    RETURN = "return"
    LOAD_TIP = "load_tip"
    LOAD_CREATE = "load_create"
    ADVICE_TIP = "advice_tip"
    ADVICE_CREATE = "advice_create"
    ADVICE_MOVE = "advice_move"
    ADVICE_RETURN = "advice_return"
