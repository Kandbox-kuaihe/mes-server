from typing import Optional, List

from pydantic import Field
from sqlalchemy import (
    Column,
    ForeignKey,
    String,
    BigInteger,
    Integer,
    Numeric,
)
from sqlalchemy.orm import relationship
from sqlalchemy_utils import TSVectorType

from dispatch.database import Base
from dispatch.models import TimeStampMixin, BaseResponseModel, DispatchBase
from dispatch.order_admin.order_group.models import OrderGroupRead
from dispatch.order_admin.order_item.models import OrderItemRead
from dispatch.rolling.rolling_list.models import RollingRead
from dispatch.runout_admin.finished_product_load.models_secondary_cut_sequence import finished_product_load_cut_sequence_plan


class CutSequencePlan(Base, TimeStampMixin):
    __tablename__ = "cut_sequence_plan"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    saw_route = Column(String, nullable=False)
    original_saw_route = Column(String, nullable=False)
    new_seq = Column(Integer, nullable=False)
    original_seq = Column(Integer, nullable=False)
    order_item_id = Column(BigInteger, ForeignKey("order_item.id"), nullable=True)
    order_item = relationship("OrderItem")
    order_id = Column(BigInteger, ForeignKey("order.id"), nullable=True)
    new_bars = Column(Integer, nullable=False)
    original_bars = Column(Integer, nullable=False)
    rd_ri = Column(String, default="ROAD", nullable=False)
    load_pen = Column(String, nullable=True)
    load_no = Column(String, nullable=True)
    pta_code = Column(String, default="PADC", nullable=False)
    rolling_id = Column(BigInteger, ForeignKey("rolling.id"), index=True, nullable=False)
    rolling = relationship("Rolling")
    weight = Column(Numeric(20, 10), default=0, nullable=False)
    order_group_id = Column(BigInteger, ForeignKey("order_group.id"), nullable=False)
    order_group = relationship("OrderGroup")
    strps = Column(Integer, nullable=False)
    length = Column(Integer, nullable=False, server_default="0")
    remarks = Column(String, nullable=True)

    cut_seq_loads = relationship(
        "FinishedProductLoad",
        secondary=finished_product_load_cut_sequence_plan,
        back_populates="cut_sequences",
    )

    search_vector = Column(
        TSVectorType(
            "saw_route",
            weights={
                "saw_route": "A",
            },
        )
    )


class CutSequencePlanBase(BaseResponseModel):
    saw_route: Optional[str] = None
    original_saw_route: Optional[str] = None
    new_seq: Optional[int] = None
    original_seq: Optional[int] = None
    order_item_id: Optional[int] = None
    new_bars: Optional[int] = None
    original_bars: Optional[int] = None
    rd_ri: Optional[str] = None
    load_pen: Optional[str] = None
    load_no: Optional[str] = None
    pta_code: Optional[str] = None
    rolling_id: Optional[int] = None
    weight: Optional[float] = None
    order_id: Optional[int] = None
    order_group_id: Optional[int] = None
    strps: Optional[int] = None
    length: Optional[int] = None
    remarks: Optional[str] = None


class CutSequencePlanCreate(BaseResponseModel):
    rolling_id: Optional[int] = None
    order_id: Optional[int] = None
    order_group_id: Optional[int] = None
    order_code: Optional[str] = None
    saw_route: Optional[str] = None
    order_item_id: Optional[int] = None
    pta_code: Optional[str] = None
    new_bars: Optional[int] = None
    length: Optional[int] = None


class CutSequencePlanRead(CutSequencePlanBase):
    id: Optional[int] = None
    rolling: Optional[RollingRead] = None
    order_item: Optional[OrderItemRead] = None
    order_group: Optional[OrderGroupRead] = None

class CutSequencePlanPagination(DispatchBase):
    total: int = 0
    items: List[CutSequencePlanRead] = Field(default_factory=list)


class CutSequencePlanMove(BaseResponseModel):
    ids: List[int] = Field(default_factory=list)
    saw_route: str = Field(...)
    move_to_id: Optional[int] = None


class CutSequencePlanSplit(BaseResponseModel):
    id: int
    items: List[CutSequencePlanBase] = Field(default_factory=list)


class AutoLoadPlanCreate(BaseResponseModel):
    rolling_id: Optional[int] = None
    order_group_id: Optional[int] = None
