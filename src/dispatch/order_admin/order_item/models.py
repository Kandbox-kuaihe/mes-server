from typing import List, Optional

from datetime import datetime
from typing import Dict, Optional
from sqlalchemy_utils import TSVectorType
from pydantic import BaseModel, condecimal

from dispatch.database import Base
from dispatch.models import TimeStampMixin, DispatchBase,BaseResponseModel

from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, BigInteger, Numeric, ForeignKey, DateTime, text, Index, UniqueConstraint

from dispatch.rolling.rolling_list.models import  RollingRead

from dispatch.order_admin.order.models import OrderRead
from dispatch.order_admin.order_item_remark.models import OrderItemRemarkRead
from dispatch.order_admin.order_group.models import OrderGroupRead
from dispatch.mill.models import MillRead
from dispatch.product_type.models import ProductType, ProductTypeRead
from dispatch.product_code_trans.models import ProductCodeTrans

class OrderItem(Base,TimeStampMixin):
    __tablename__ = 'order_item'

    id = Column(BigInteger, primary_key=True,autoincrement=True)
    order_group_id = Column(BigInteger, ForeignKey("order_group.id"), nullable=True, )
    order_group = relationship("OrderGroup", backref="order_group_order_item")


    order_id = Column(BigInteger, ForeignKey("order.id"), nullable=False, )
    order = relationship("Order", backref="order_order_item")
    
    
    rolling_code = Column(String, nullable=False)
    rolling_id = Column(BigInteger, ForeignKey("rolling.id"), nullable=True)
    rolling = relationship("Rolling", backref="rolling_order")

    plant_id = Column(BigInteger, ForeignKey("mill.id"), nullable=False, )
    plant = relationship("Mill", backref="mill_order_item")
    mill_comment = Column(String)

    product_type_id = Column(BigInteger, ForeignKey("product_type.id"), nullable=False, )
    product_type = relationship("ProductType", backref="product_type_order_item")

    lr_ind = Column(String, nullable=True)
    line_item_code = Column(String, nullable=False)
    sap_line_item_code = Column(String)
    sub_item_code = Column(String)
    line_item_seq = Column(Integer)
    line_item_desc = Column(String)
    product_code = Column(String)
    spec_code = Column(String, nullable=False)

    spec_id = Column(BigInteger, ForeignKey("spec.id"), nullable=False)
    spec = relationship("Spec", backref="spec_order_item")

    quality_code = Column(String)
    # completion_status = Column(String)
    customer_spec_code = Column(String, nullable=True)
    quantity = Column(Numeric, default=0, nullable=False)
    quantity_pc = Column(Numeric, default=0, nullable=True)
    quantity_tonnage = Column(Numeric)
    stocked_quantity = Column(Numeric, default=0, nullable=False)
    tonnage = Column(Numeric)
    tonnage_tolerance_min_percent = Column(Numeric)
    tonnage_tolerance_max_percent = Column(Numeric)
    length_mm = Column(Numeric)
    length_1_mm = Column(Numeric)
    length_2_mm = Column(Numeric)
    length_feet = Column(Numeric)
    length_inch = Column(Numeric)
    product_dim1 = Column(String)
    product_dim2 = Column(String)
    product_dim3 = Column(String)
    product_dim4 = Column(String)
    product_dim_unit = Column(String)
    product_form = Column(String)
    product_form_type = Column(String)

    product_code_trans_code = Column(String)
    product_code_trans_id = Column(BigInteger, ForeignKey("product_code_trans.id"))
    product_code_trans = relationship("ProductCodeTrans", backref="product_code_trans_order_item")

    bws_store = Column(String)
    astm_dim1 = Column(String)
    astm_dim2 = Column(String)
    astm_dim3 = Column(String)
    sales_order_unit = Column(String)
    semi_width = Column(Numeric)
    semi_thickness = Column(Numeric)
    prime_type = Column(String)
    im_type = Column(String)
    weight_per_pc = Column(Numeric)
    outside_inspection_required = Column(String)
    transport_type = Column(String)
    destination_port = Column(String)
    loading_port = Column(String)
    clear_remark_type = Column(String)
    clear_remark_sequence = Column(Integer)
    clear_remark = Column(String)

    general_remark_1 = Column(String)
    general_remark_2 = Column(String)
    general_remark_3 = Column(String)
    general_remark_4 = Column(String)
    general_remark_5 = Column(String)
    general_remark_6 = Column(String)
    marking_requirements = Column(String)
    processing_remark_1 = Column(String)
    processing_remark_2 = Column(String)
    processing_remark_3 = Column(String)
    processing_remark_4 = Column(String)
    processing_remark_5 = Column(String)
    delivery_date = Column(DateTime)
    delivery_address_id = Column(String)
    caster = Column(String)
    surface_grade = Column(String)
    coating_type = Column(String)
    cut_margin_min = Column(Numeric)
    cut_margin_max = Column(Numeric)
    cut_margin_unit = Column(String)
    color_code = Column(Numeric)
    carbon_min = Column(Numeric)
    carbon_max = Column(Numeric)
    manganese_range_min = Column(Numeric)
    manganese_range_max = Column(Numeric)
    secondary_length_1_min = Column(Numeric)
    secondary_length_1_max = Column(Numeric)
    secondary_length_2_min = Column(Numeric)
    secondary_length_2_max = Column(Numeric)
    secondary_length_volume = Column(Numeric)
    section_width_min = Column(Numeric)
    section_thickness_min = Column(Numeric)
    section_width_max = Column(Numeric)
    section_thickness_max = Column(Numeric)
    inspector_code_1 = Column(String)
    inspector_code_2 = Column(String)
    inspector_code_3 = Column(String)
    spec_inspector_1 = Column(String)
    spec_inspector_2 = Column(String)
    spec_inspector_3 = Column(String)
    inspection_spec_name = Column(String)
    late_arrival = Column(String)

    label_template_id = Column(Integer, ForeignKey('label_template.id'))
    label_template = relationship("LabelTemplate", backref="label_template_order_item")
    
    label_data = Column(String)
    rejection = Column(String)
    rejection_desc = Column(String)
    condition_record_per_unit = Column(String)
    qual_prefix = Column(String)
    qual_suffix = Column(String)
    shorts_min = Column(Numeric)
    shorts_max = Column(Numeric)
    cover_order_weight = Column(Numeric)
    cover_order_no1 = Column(String)
    cover_order_no2 = Column(String)
    amended_quantity = Column(BigInteger)
    consignment_code = Column(String)# add the decoding when recieved
    v_voyage_no = Column(String)
    v_port_of_loading = Column(String)
    v_port_of_destination = Column(String)
    sr_voyage_no = Column(String)
    sr_port_of_loading = Column(String)
    sr_port_of_destination = Column(String)
    sp_voyage_no = Column(String)
    sp_port_of_loading = Column(String)
    sp_port_of_destination = Column(String)
    amend_status = Column(String)


    search_vector = Column(
        TSVectorType(
            "line_item_code",
            weights={"line_item_code": "A"},
        )
    )

    __table_args__ = (
        UniqueConstraint('order_id', 'line_item_code', 'sap_line_item_code', name='unique_key_order_item'),
        Index('idx_order_item_active_updated', 'updated_at', postgresql_where=(text("is_deleted IS NULL OR is_deleted = 0"))),
    )



    
class OrderItemBase(BaseResponseModel):

    v_voyage_no: Optional[str] = None
    v_port_of_loading: Optional[str] = None
    v_port_of_destination: Optional[str] = None
    sr_voyage_no: Optional[str] = None
    sr_port_of_loading: Optional[str] = None
    sr_port_of_destination: Optional[str] = None
    sp_voyage_no: Optional[str] = None
    sp_port_of_loading: Optional[str] = None
    sp_port_of_destination: Optional[str] = None

    order_id: Optional[int] = None
    order_group_id: Optional[int] = None
    
    plant_id: Optional[int] = None
    plant: Optional[MillRead] = None
    
    rolling_code: Optional[str] = None
    rolling_id: Optional[int] = None
    rolling: Optional[RollingRead] = None

    lr_ind: Optional[str] = None
    mill_comment: Optional[str] = None
    line_item_code: Optional[str] = None
    sap_line_item_code: Optional[str] = None
    sub_item_code: Optional[str] = None
    line_item_seq: Optional[int] = None
    line_item_desc: Optional[str] = None
    product_code: Optional[str] = None
    spec_code: Optional[str] = None

    spec_id: Optional[int] = None
    late_arrival: Optional[str] = None
    quality_code: Optional[str] = None
    # completion_status: Optional[str] = None
    customer_spec_code: Optional[str] = None
    quantity: Optional[condecimal(max_digits=20, decimal_places=10)] = None
    quantity_pc: Optional[condecimal(max_digits=20, decimal_places=10)] = None
    quantity_tonnage: Optional[condecimal(max_digits=20, decimal_places=10)] = None
    stocked_quantity: Optional[condecimal(max_digits=20, decimal_places=10)] = None
    tonnage: Optional[condecimal(max_digits=20, decimal_places=10)] = None
    tonnage_tolerance_min_percent: Optional[condecimal(max_digits=20, decimal_places=10)] = None
    tonnage_tolerance_max_percent: Optional[condecimal(max_digits=20, decimal_places=10)] = None
    length_mm: Optional[condecimal(max_digits=20, decimal_places=10)] = None
    length_1_mm: Optional[condecimal(max_digits=20, decimal_places=10)] = None
    length_2_mm: Optional[condecimal(max_digits=20, decimal_places=10)] = None
    length_feet: Optional[condecimal(max_digits=20, decimal_places=10)] = None
    length_inch: Optional[condecimal(max_digits=20, decimal_places=10)] = None
    product_dim1: Optional[str] = None
    product_dim2: Optional[str] = None
    product_dim3: Optional[str] = None
    product_dim4: Optional[str] = None
    product_dim_unit: Optional[str] = None
    product_form: Optional[str] = None
    product_form_type: Optional[str] = None
    bws_store: Optional[str] = None
    astm_dim1: Optional[str] = None
    astm_dim2: Optional[str] = None
    astm_dim3: Optional[str] = None
    sales_order_unit: Optional[str] = None
    semi_width: Optional[condecimal(max_digits=20, decimal_places=10)] = None
    semi_thickness: Optional[condecimal(max_digits=20, decimal_places=10)] = None
    prime_type: Optional[str] = None
    im_type: Optional[str] = None
    weight_per_pc: Optional[condecimal(max_digits=20, decimal_places=10)] = None
    outside_inspection_required: Optional[str] = None
    transport_type: Optional[str] = None
    destination_port: Optional[str] = None
    loading_port: Optional[str] = None
    clear_remark_type: Optional[str] = None
    clear_remark_sequence: Optional[int] = None
    clear_remark: Optional[str] = None
    general_remark_1: Optional[str] = None
    general_remark_2: Optional[str] = None
    general_remark_3: Optional[str] = None
    general_remark_4: Optional[str] = None
    general_remark_5: Optional[str] = None
    general_remark_6: Optional[str] = None
    marking_requirements: Optional[str] = None
    processing_remark_1: Optional[str] = None
    processing_remark_2: Optional[str] = None
    processing_remark_3: Optional[str] = None
    processing_remark_4: Optional[str] = None
    processing_remark_5: Optional[str] = None
    delivery_date: Optional[datetime] = None
    delivery_address_id: Optional[str] = None
    caster: Optional[str] = None
    surface_grade: Optional[str] = None
    coating_type: Optional[str] = None
    cut_margin_min: Optional[condecimal(max_digits=20, decimal_places=10)] = None
    cut_margin_max: Optional[condecimal(max_digits=20, decimal_places=10)] = None
    cut_margin_unit :Optional[str] = None
    color_code: Optional[condecimal(max_digits=20, decimal_places=10)] = None
    carbon_min: Optional[condecimal(max_digits=20, decimal_places=10)] = None
    carbon_max: Optional[condecimal(max_digits=20, decimal_places=10)] = None
    manganese_range_min: Optional[condecimal(max_digits=20, decimal_places=10)] = None
    manganese_range_max: Optional[condecimal(max_digits=20, decimal_places=10)] = None
    secondary_length_1_min: Optional[condecimal(max_digits=20, decimal_places=10)] = None
    secondary_length_1_max: Optional[condecimal(max_digits=20, decimal_places=10)] = None
    secondary_length_2_min: Optional[condecimal(max_digits=20, decimal_places=10)] = None
    secondary_length_2_max: Optional[condecimal(max_digits=20, decimal_places=10)] = None
    secondary_length_volume: Optional[condecimal(max_digits=20, decimal_places=10)] = None
    section_width_min: Optional[condecimal(max_digits=20, decimal_places=10)] = None
    section_thickness_min: Optional[condecimal(max_digits=20, decimal_places=10)] = None
    section_width_max: Optional[condecimal(max_digits=20, decimal_places=10)] = None
    section_thickness_max: Optional[condecimal(max_digits=20, decimal_places=10)] = None
    inspector_code_1: Optional[str] = None
    inspector_code_2: Optional[str] = None
    inspector_code_3: Optional[str] = None
    spec_inspector_1: Optional[str] = None
    spec_inspector_2: Optional[str] = None
    spec_inspector_3: Optional[str] = None
    label_template_id: Optional[int] = None
    label_data: Optional[str] = None
    rejection: Optional[str] = None
    rejection_desc: Optional[str] = None
    condition_record_per_unit: Optional[str] = None
    qual_prefix: Optional[str] = None
    qual_suffix: Optional[str] = None
    shorts_min: Optional[condecimal(max_digits=20, decimal_places=10)] = None
    shorts_max: Optional[condecimal(max_digits=20, decimal_places=10)] = None
    cover_order_weight: Optional[condecimal(max_digits=20, decimal_places=10)] = None
    cover_order_no1: Optional[str] = None
    cover_order_no2: Optional[str] = None
    amended_quantity: Optional[int] = None
    amend_status:  Optional[str] = None



    order: Optional[OrderRead] = None
    order_group: Optional[OrderGroupRead] = None

    product_type_id: Optional[int] = None

class OrderItemCreate(OrderItemBase):
    pass


class OrderItemUpdate(OrderItemBase):
    pass

class SpecRelatedRead(BaseResponseModel):
    id: int
    spec_code: Optional[str] = None
    mill_id: Optional[int] = None
    version: Optional[int] = None
    version_status: Optional[str] = None

class OrderItemRead(OrderItemBase,BaseResponseModel):
    id: int
    
    finished_bars: Optional[int] = 0
    completion_status: Optional[str] = "incomplete"
    despatched_bars: Optional[int] = 0
    allocate_bars: Optional[int] = 0
    rolling_bars: Optional[int] = 0
    advice_bars: Optional[int] = 0
    advice_tip_bars: Optional[int] = 0
    returned_bars: Optional[int] = 0
    product_type: Optional[ProductTypeRead] = None
    order_item_remarks: Optional[List[OrderItemRemarkRead]] = []
    total_weight: Optional[float] = None
    max_length: Optional[int] = None
    spec_short_name: Optional[str] = None
    spec: Optional[SpecRelatedRead] = None


class OrderItemPagination(DispatchBase):
    total: int
    items: List[OrderItemRead] = []
    itemsPerPage: int
    page : int

class OrderItemRollingPagination(DispatchBase):
    total: int
    items: List[OrderItemRead] = []
    itemsPerPage: int
    page : int
    product_num: list[int] = []

class OrderItemByRemarkRead(OrderItemBase):
    pass


class OrderItemStatistics(OrderItemBase):
    line_item_desc: Optional[str] = None
    product_code: Optional[str] = None
    caster: Optional[str] = None
    spec_code: Optional[str] = None
    delivery_date: Optional[datetime] = None
    total_quantity_tonnage: Optional[float] = None


class OrderItemStatisticsPagination(DispatchBase):
    total: int
    items: List[OrderItemStatistics] = []
    itemsPerPage: int
    page : int