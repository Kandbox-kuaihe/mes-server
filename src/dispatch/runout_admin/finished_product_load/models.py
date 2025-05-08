from typing import List, Optional
from datetime import datetime, date

from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    BigInteger,
    Numeric,
    String,
    Date,
    DateTime,
)
from sqlalchemy.orm import relationship

from sqlalchemy.sql.schema import UniqueConstraint
from sqlalchemy_utils import TSVectorType

from dispatch.database import Base
from dispatch.models import TimeStampMixin, DispatchBase, BaseResponseModel

from dispatch.mill.models import MillRead
from dispatch.area.models import AreaRead
from dispatch.order_admin.order_item.models import OrderItemRead
from dispatch.rolling.rolling_list.models import RollingRead
from dispatch.runout_admin.finished_product.models_secondary_load import finished_product_load
from dispatch.runout_admin.finished_product_load.models_secondary_cut_sequence import finished_product_load_cut_sequence_plan
from dispatch.runout_admin.transport.models import TransportRead
from dispatch.rolling.cut_sequence_plan.models import CutSequencePlanRead

# from dispatch.runout_admin.advice.models import AdviceRead


class FinishedProductLoad(Base,TimeStampMixin):
    __tablename__ = 'load'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    code = Column(String)
    
    mill_id = Column(BigInteger, ForeignKey("mill.id"), nullable=True)
    mill = relationship("Mill", backref="mill_finished_product_load")

    order_item_id = Column(BigInteger, ForeignKey("order_item.id"))
    order_item = relationship("OrderItem", backref="order_item_finished_product_load")

    rolling_id = Column(BigInteger, ForeignKey("rolling.id"), nullable=True)
    rolling = relationship("Rolling", backref="rolling_finished_product_load")

    to_area_id = Column(BigInteger, ForeignKey("area.id"), nullable=True)
    area = relationship("Area", backref="area_finished_product_load")

    # advice_id = Column(BigInteger, ForeignKey("advice.id"), nullable=True)
    # advice = relationship("Advice", backref="advice_finished_product_load")

    business_type = Column(String)
    transport_id = Column(BigInteger, ForeignKey("transport.id"), nullable=True)
    transport = relationship("Transport", backref="transport_finished_product_load")
    transport_code = Column(String)
    transport_type = Column(String)
    dispatch_date = Column(DateTime)
    stock_in_date = Column(DateTime)
    piece_count = Column(Integer)
    bundle_size = Column(String)
    total_weight_ton = Column(Numeric(20, 10))
    customer_code = Column(String)

    load_type = Column(String)
    load_status = Column(String)
    transport_restrict = Column(String)
    comment = Column(String, nullable=True)
    pilling_bogie = Column(String)
    actual_weight = Column(Numeric(20, 10))
    cut_seq_load_no = Column(String)

    finished_products = relationship("FinishedProduct", secondary=finished_product_load, back_populates="loads")
    cut_sequences = relationship("CutSequencePlan", secondary=finished_product_load_cut_sequence_plan, back_populates="cut_seq_loads")

    search_vector = Column(
        TSVectorType(
            "code",
            weights={"code": "A"},
        )
    )

    __table_args__ = (
        UniqueConstraint('code', name='unique_key_code'),
    )


class FinishedProductLoadBase(BaseResponseModel):
    mill_id: Optional[int] = None
    order_item_id: Optional[int] = None
    rolling_id: Optional[int] = None
    to_area_id: Optional[int] = None
    # advice_id: Optional[int] = None
    business_type: Optional[str] = None
    transport_code: Optional[str] = None
    transport_type: Optional[str] = None
    dispatch_date: Optional[datetime] = None
    stock_in_date: Optional[datetime] = None
    piece_count: Optional[int] = None
    bundle_size: Optional[str] = None
    total_weight_ton: Optional[float] = None
    customer_code: Optional[str] = None
    load_type: Optional[str] = None
    load_status: Optional[str] = None
    transport_restrict: Optional[str] = None
    comment: Optional[str] = None
    transport_id: Optional[int] = None
    actual_weight: Optional[float] = None

    pilling_bogie: Optional[str] = None
    cut_seq_load_no: Optional[str] = None


class FinishedProductLoadCreate(FinishedProductLoadBase):
    code: Optional[str] = None
    bind_finished_product_ids: Optional[List[int]] = None
    is_create_advice: Optional[bool] = None
    create_advice_order_item_ids: Optional[List[int]] = None


class FinishedProductLoadUpdate(FinishedProductLoadBase):
    bind_finished_product_ids: Optional[List[int]] = None
    is_create_advice: Optional[bool] = None
    create_advice_order_item_ids: Optional[List[int]] = None


class FinishedProductCutSeqLoadCreate(FinishedProductLoadBase):
    cut_seq_id: Optional[int] = None
    pta_code: Optional[str] = None
    new_bars: Optional[int] = None
    length_mm: Optional[int] = None
    strps: Optional[int] = None
    remarks: Optional[str] = None
    weight: Optional[float] = None
    loads: Optional[List[FinishedProductLoadCreate]] = None
    update_loads: Optional[List[dict]] = None


class FinishedProductLoadRead(FinishedProductLoadBase):
    id: Optional[int] = None
    code: Optional[str] = None
    mill: Optional[MillRead] = None
    area: Optional[AreaRead] = None
    rolling: Optional[RollingRead] = None
    order_id: Optional[int] = None
    order_item: Optional[OrderItemRead] = None 
    advice_num: Optional[int] = None
    transport: Optional[TransportRead] = None
    max_weight_tonnage: Optional[float] = None
    cut_sequence: Optional[List[CutSequencePlanRead]] = []  
    cut_sequences: Optional[List[CutSequencePlanRead]] = []  
    # advice: Optional[AdviceRead] = None

class FinishedProductLoadPagination(DispatchBase):
    total: int
    items: List[FinishedProductLoadRead] = []
    itemsPerPage: int
    page : int

class FinishedProductLoadMove(FinishedProductLoadRead):
    codes: List[str] = []
    site_type_code: Optional[str] = None,
    site_code: Optional[str] = None,
    area_code: Optional[str] = None,
    area_id: Optional[int] = None
    comment: Optional[str] = None

class LoadAutoPlanCreate(DispatchBase):
    work_order_item_id: int
    auto_plan_type: str
    bundle_matrix_id: Optional[int] = None

class LoadAutoPlanFinishedProductRead(DispatchBase):
    id: int
    code: str
    estimated_weight_kg: Optional[float] = None

class LoadAutoPlanRead(FinishedProductLoadBase):
    id: Optional[int] = None
    code: Optional[str] = None
    max_weight_tonnage: Optional[float] = None
    finished_products: Optional[List[LoadAutoPlanFinishedProductRead]]

class LoadCarryoutCreate(DispatchBase):
    work_order_item_id: int

class CarryOutCreate(DispatchBase):
    load_in: list[int]
