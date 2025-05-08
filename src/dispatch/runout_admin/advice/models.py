from enum import Enum

from dispatch.area.models import AreaRead
from dispatch.cast.models import CastRead
from dispatch.database import Base
from sqlalchemy import (
    Column,
    BigInteger,
    String,
    ForeignKey,
    UniqueConstraint,
    DateTime, Numeric
)
from dispatch.models import DispatchBase, TimeStampMixin, BaseResponseModel
from typing import Optional, List, ClassVar, Any
from sqlalchemy_utils import TSVectorType
from sqlalchemy.orm import relationship
from pydantic import Field
from dispatch.mill.models import MillRead
from datetime import datetime
from dispatch.order_admin.order.models import OrderRead
from dispatch.order_admin.order_item.models import OrderItemRead
from dispatch.product_type.models import ProductTypeRead
from dispatch.rolling.rolling_list.models import RollingRead
from dispatch.runout_admin.finished_product.models_secondary_advice import finished_product_advice
# from dispatch.runout_admin.finished_product.models import FinishedProductBase, FinishedProduct, FinishedProductReadID
from dispatch.runout_admin.finished_product_load.models import FinishedProductLoadRead
from dispatch.runout_admin.holdreason.models import HoldreasonRead
from dispatch.runout_admin.runout_list.models import RunoutRead
from dispatch.runout_admin.transport.models import TransportRead
from dispatch.shiftAdmin.shift.models import ShiftRead

class AdviceStatusEnum(str, Enum):
    """Defines the possible statuses of an Advice."""

    ENROUTE = "enroute"
    TIPPED = "tipped"
    CANCELLED = "cancelled"
    UNLOAD = "unload"
    DELOAD = "deload"
    RETURNED = "return"


class Advice(Base, TimeStampMixin):
    __tablename__ = "advice"
    id = Column(BigInteger, primary_key=True, autoincrement=True)

    advice_code = Column(String, nullable=False)
    type = Column(String, nullable=True)
    piece_type = Column(String, nullable=True)

    load_id = Column(BigInteger, ForeignKey("load.id"), nullable=True)
    load = relationship("FinishedProductLoad", backref="finished_product_load_advice")

    from_area_id = Column(BigInteger, ForeignKey("area.id"), nullable=True)
    from_area = relationship("Area", foreign_keys=[from_area_id], backref="from_area_advice_item")
    from_location = Column(String, nullable=True)
    to_area_id = Column(BigInteger, ForeignKey("area.id"), nullable=True)
    to_area = relationship("Area", foreign_keys=[to_area_id], backref="to_area_advice_item")
    to_location = Column(String, nullable=True)
    move_date = Column(DateTime, default=datetime.utcnow, nullable=True)
    move_by = Column(String, nullable=True)
    order_item_id = Column(BigInteger, ForeignKey("order_item.id"), nullable=True)
    order_item = relationship("OrderItem", backref="order_item_advice_item")
    order_id = Column(BigInteger, ForeignKey("order.id"), nullable=True)
    order = relationship("Order", backref="order_advice_item")
    tip_reason = Column(String, nullable=True)
    mill_id = Column(BigInteger, ForeignKey("mill.id"), nullable=False)
    mill = relationship("Mill", backref="mill_advice_item")

    comment = Column(String, nullable=True)
    date_load = Column(String, nullable=True)
    tran_from = Column(String, nullable=True)
    destination = Column(String, nullable=True)
    customer = Column(String, nullable=True)
    delivery_address = Column(String, nullable=True)
    haulier = Column(String, nullable=True)
    ship = Column(String, nullable=True)
    wagon_no = Column(String, nullable=True)
    rail_road = Column(String, nullable=True)
    corus_order_no = Column(String, nullable=True)
    customer_order_no = Column(String, nullable=True)
    item_no = Column(String, nullable=True)
    # no_of_bars = Column(String, nullable=True)
    length_mm = Column(String, nullable=True)
    section = Column(String, nullable=True)
    gauge = Column(String, nullable=True)
    specification = Column(String, nullable=True)
    rl_sht = Column(String, nullable=True)
    cust_item_mark = Column(String, nullable=True)
    calculated_weight = Column(Numeric(precision=20, scale=10))
    tip_location = Column(String, nullable=True)
    bar_number = Column(String, nullable=True)
    part = Column(String, nullable=True)
    total_bars = Column(String, nullable=True)
    last = Column(String, nullable=True)
    associated_advice = Column(String, nullable=True)
    # tot_bundles = Column(String, nullable=True)
    calc_weight = Column(Numeric(precision=20, scale=10))
    loose_bars = Column(String, nullable=True)
    weighted_weight = Column(String, nullable=True)
    # comments = Column(String, nullable=True)    # #####~~~~~~~~~~~~---------------
    general_remarks = Column(String, nullable=True)
    shift_id = Column(BigInteger, ForeignKey("shift.id"), nullable=True)
    shift = relationship("Shift", backref="shift_advice_item")
    stocktaker = Column(String, nullable=True)
    inspection = Column(String, nullable=True)
    journey = Column(String, nullable=True)
    message = Column(String, nullable=True)
    advice_no_c = Column(String, nullable=True)
    works_location = Column(String, nullable=True)
    # filler = Column(String, nullable=True)
    load_seg = Column(String, nullable=True)
    loaditem_seg = Column(String, nullable=True) 
    loaditem_ptr = Column(String, nullable=True)
    loadbar_seg = Column(String, nullable=True)
    
    status = Column(String, default=AdviceStatusEnum.ENROUTE, nullable=False)

    business_type = Column(String, nullable=False)

    transport_id = Column(BigInteger, ForeignKey("transport.id"), nullable=True)
    transport = relationship("Transport", backref="transport_advice_item")
    transport_type = Column(String, nullable=True)

    curr_area_id = Column(BigInteger, ForeignKey("area.id"), nullable=True)
    curr_area = relationship("Area", foreign_keys=[curr_area_id], backref="curr_area_advice_item")
    store = Column(String, nullable=True)
    port = Column(String, nullable=True)
    own_state = Column(String, nullable=True, default="mill")
    consignee = Column(String, nullable=True)

    finished_product = relationship("FinishedProduct", secondary=finished_product_advice, back_populates="advice")

    search_vector = Column(
        TSVectorType(
            "advice_code",
            weights={
                "advice_code": "A",
            }
        )
    )

    # __table_args__ = (
    #     UniqueConstraint('advice_code', name='unique_key_advice_code'),
    # )




class AdviceBase(BaseResponseModel):
    advice_code: Optional[str] = None
    type: Optional[str] = None
    piece_type: Optional[str] = None

    load_id: Optional[int] = None
    load: Optional[FinishedProductLoadRead] = None

    from_area_id: Optional[int] = None
    from_area: Optional[AreaRead] = None
    to_area_id: Optional[int] = None
    to_area: Optional[AreaRead] = None
    to_location: Optional[str] = None
    move_date: Optional[datetime] = None
    move_by: Optional[str] = None
    order_item_id: Optional[int] = None
    order_item: Optional[OrderItemRead] = None
    order_id: Optional[int] = None
    order: Optional[OrderRead] = None
    comment: Optional[str] = None
    tip_reason: Optional[str] = None
    mill_id: Optional[int] = None
    mill: Optional[MillRead] = None

    # advice_no: Optional[str] = None
    date_load: Optional[str] = None
    tran_from: Optional[str] = None
    destination: Optional[str] = None
    customer: Optional[str] = None
    delivery_address: Optional[str] = None
    haulier: Optional[str] = None
    ship: Optional[str] = None
    wagon_no: Optional[str] = None
    rail_road: Optional[str] = None
    corus_order_no: Optional[str] = None
    customer_order_no: Optional[str] = None
    item_no: Optional[str] = None
    length_mm: Optional[str] = None
    section: Optional[str] = None
    gauge: Optional[str] = None
    specification: Optional[str] = None
    rl_sht: Optional[str] = None
    cust_item_mark: Optional[str] = None
    calculated_weight: Optional[float] = None
    tip_location: Optional[str] = None
    bar_number: Optional[str] = None
    part: Optional[str] = None
    total_bars: Optional[str] = None
    last: Optional[str] = None
    associated_advice: Optional[str] = None
    calc_weight: Optional[float] = None
    weighted_weight: Optional[str] = None
    # comments: Optional[str] = None
    general_remarks: Optional[str] = None
    shift_id: Optional[int] = None
    shift: Optional[ShiftRead] = None
    stocktaker: Optional[str] = None
    inspection: Optional[str] = None
    journey: Optional[str] = None
    message: Optional[str] = None
    advice_no_c: Optional[str] = None
    works_location: Optional[str] = None
    load_seg: Optional[str] = None
    loaditem_seg: Optional[str] = None
    loaditem_ptr: Optional[str] = None
    loadbar_seg: Optional[str] = None
    status: Optional[str] = None
    business_type: Optional[str] = None
    transport_type: Optional[str] = None
    transport_id: Optional[int] = None
    transport: Optional[TransportRead] = None
    curr_area_id: Optional[int] = None
    curr_area: Optional[AreaRead] = None
    store: Optional[str] = None
    port: Optional[str] = None
    own_state: Optional[str] = None
    consignee: Optional[str] = None
    # finished_product: Optional[List[Any]] = []



class AdviceCreate(AdviceBase):
    finished_ids: List[int] = []
    is_load_status: Optional[bool] = None
    business_type: Optional[str] = None


class AdviceUpdate(AdviceBase):
    area_code: Optional[str] = None
    area_id: Optional[int] = None
    tipped_date: Optional[datetime] = None
    finished_ids: List[int] = []
    advice_ids: List[int] = []

class AdviceFinished(DispatchBase):
    id: int
    code: Optional[str] = None
    product_type: Optional[ProductTypeRead] = None
    cast: Optional[CastRead] = None
    order: Optional[OrderRead] = None
    order_item: Optional[OrderItemRead] = None
    length_mm: Optional[float] = None
    status: Optional[str] = None
    quality_code: Optional[str] = None
    quantity: Optional[int] = None
    rolling: Optional[RollingRead] = None
    runout: Optional[RunoutRead] = None
    cut_codes: Optional[str] = None
    estimated_weight_kg: Optional[float] = None
    exist_flag: Optional[str] = None
    mult_type: Optional[str] = None
    rework_type: Optional[str] = None

class AdviceRead(AdviceBase):
    id: Optional[int] = None
    total_weight: Optional[float] = None
    max_length: Optional[int] = None
    held: Optional[str] = None
    rework: Optional[List[str]] = []
    mult: Optional[str] = None
    # hold_reason: Optional[List[Any]] = []
    hold_reason: Optional[List[str]] = []
    cover: Optional[List[str]] = []
    finished_products: Optional[List[AdviceFinished]] = []
    mult_done: Optional[str] = None
    no_products: Optional[int] = None
    
    
class AdviceSplit(AdviceBase):
    item_ids: List[int] = []


class AdvicePagination(DispatchBase):
    total: int
    items: List[AdviceRead] = []
    itemsPerPage: int
    page: int
    
# class CombinedResponse(DispatchBase):
#     advice: AdviceBase
#     finished_product: List[FinishedProductReadID]

class AdviceIDPagination(DispatchBase):
    advice_id: Optional[int] = None
    itemsPerPage: Optional[int] = None
    page: int

class AdviceMove(AdviceRead):
    code: Optional[str] = None,
    site_type_code: Optional[str] = None,
    site_code: Optional[str] = None,
    area_code: Optional[str] = None,


class AdviceReturn(DispatchBase):
    ids: List[int] = Field(default_factory=list)
    area_id: int




