from datetime import datetime, date
from typing import List, Optional, Any, Dict

from pydantic import Field
from sqlalchemy import Column, Integer, String, BigInteger, Numeric, ForeignKey, Boolean, text
from sqlalchemy import (
    DateTime,
    Date,
    Index,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import UniqueConstraint
from sqlalchemy_utils import TSVectorType

from dispatch.area.models import AreaRead
from dispatch.cast.models import CastRead
from dispatch.database import Base
from dispatch.defect_reason.models import DefectReasonRead
from dispatch.runout_admin.finished_product.models_secondary_advice import finished_product_advice
from dispatch.runout_admin.finished_product.models_secondary_load import finished_product_load
from dispatch.runout_admin.finished_product.models_secondary_association import finished_product_association
from dispatch.runout_admin.regradereason.models import RegradereasonRead
from dispatch.mill.models import MillRead
from dispatch.models import TimeStampMixin, DispatchBase, BaseResponseModel
from dispatch.order_admin.order.models import OrderRead
from dispatch.order_admin.order_item.models import OrderItemRead
from dispatch.product_type.models import ProductTypeRead
from dispatch.product_size.models import ProductSizeRead
from dispatch.rolling.rolling_list.models import RollingRead
from dispatch.runout_admin.advice.models import AdviceRead
from dispatch.runout_admin.finished_product_load.models import FinishedProductLoadRead
from dispatch.runout_admin.holdreason.models import HoldreasonRead
from dispatch.runout_admin.holdreason.models_secondary import finished_product_hold
from dispatch.runout_admin.runout_list.models import RunoutRead
from dispatch.spec_admin.spec.models import SpecRead
from dispatch.rolling.cut_sequence_plan.models import CutSequencePlanRead
from dispatch.tests_admin.tensile_test_card.models import TestTensileRead
from dispatch.tests_admin.impact_test_card.models import TestImpactRead


class FinishedProduct(Base,TimeStampMixin):
    __tablename__ = 'finished_product'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    mill_id = Column(BigInteger, ForeignKey("mill.id"), nullable=False )
    mill = relationship("Mill", backref="mill_FinishedProduct")
    runout_id = Column(BigInteger, ForeignKey('runout.id'), nullable=False, index=True)
    runout = relationship('Runout')
    
    rolling_id = Column(BigInteger, ForeignKey('rolling.id'), index=True, nullable=True) # should be nullable=False
    rolling = relationship("Rolling", backref="rolling_finished_product")
    
    area_id = Column(BigInteger, ForeignKey('area.id'))
    area = relationship("Area", backref="area_finished_product")

    hold_reason = relationship("HoldReason", secondary=finished_product_hold, back_populates="finished_product")

    code = Column(String, nullable=False)
    # cast_code = Column(String)
    
    cast_id = Column(BigInteger, ForeignKey("cast.id"), nullable=True, index=True)
    cast = relationship("Cast",foreign_keys=[cast_id],backref="cast_finished_product")
    sec_cast_id = Column(BigInteger, ForeignKey("cast.id"), nullable=True, )
    sec_cast = relationship("Cast", foreign_keys=[sec_cast_id],backref="sec_cast_finished_product")
    
    location = Column(String)
    stock_in_date = Column(DateTime)
    cut_seq = Column(Integer)
    # product_type = Column(String)
    product_type_id = Column(BigInteger, ForeignKey("product_type.id"), nullable=False, index=True)
    product_type = relationship("ProductType", backref="product_type_finished_product")

    quality_code = Column(String)
    width_mm = Column(Numeric(precision=20, scale=10))
    length_mm = Column(Numeric(precision=20, scale=10), nullable=False)
    thickness_mm = Column(Numeric(precision=20, scale=10))
    estimated_weight_kg = Column(Numeric(precision=20, scale=10), nullable=False)
    orig_length_mm = Column(Numeric(precision=20, scale=10))
    scarfed_status = Column(String)
    allocation_status = Column(String)
    exist_flag = Column(String)
    mult_type = Column(String)
    mult_code = Column(String)
    mult_datetime = Column(DateTime)
    mult_confirm_datetime = Column(DateTime)
    waste_length = Column(Numeric(precision=20, scale=10))

    mult_id = Column(BigInteger, ForeignKey("finished_product.id"), nullable=True, )
    mult_regulars = relationship("FinishedProduct")

    status = Column(String, nullable=False)
    rework_type = Column(String)
    rework_status = Column(String)
    rework_due_date = Column(Date)
    rework_finish_date = Column(Date)
    reserve_status = Column(String)
    reserved_order_item_id = Column(BigInteger, ForeignKey('order_item.id'))
    reserved_order_item = relationship("OrderItem", foreign_keys=[reserved_order_item_id], backref="reserved_order_item_finished_product")

    estimated_cold_length_mm = Column(Numeric(precision=20, scale=10))
    nose_crop_flag = Column(String)
    tail_crop_flag = Column(String)
    cut_composition_count = Column(Integer)
    
    store_code = Column(String)

    cut_code = Column(String)
    sawn_by = Column(String)
    kg = Column(String)
    spec_id = Column(BigInteger, ForeignKey('spec.id'), index=True)
    spec = relationship("Spec")
    pass_tests = Column(String)
    multed_with = Column(String)
    order_id = Column(BigInteger, ForeignKey('order.id'), index=True)
    order = relationship("Order")
    order_item_id = Column(BigInteger, ForeignKey('order_item.id'), index=True)
    order_item = relationship("OrderItem", foreign_keys=[order_item_id], backref="order_item_finished_product")
    onward = Column(Integer)
    bundle = Column(Integer)
    alt_spec = Column(String)

    nominal_f1 = Column(Numeric(precision=20, scale=10))
    actual_f1 = Column(Numeric(precision=20, scale=10))
    nominal_f2 = Column(Numeric(precision=20, scale=10))
    actual_f2 = Column(Numeric(precision=20, scale=10))
    nominal_f3 = Column(Numeric(precision=20, scale=10))
    actual_f3 = Column(Numeric(precision=20, scale=10))
    nominal_f4 = Column(Numeric(precision=20, scale=10))
    actual_f4 = Column(Numeric(precision=20, scale=10))
    nominal_fh1 = Column(Numeric(precision=20, scale=10))
    actual_fh1 = Column(Numeric(precision=20, scale=10))
    nominal_fh2 = Column(Numeric(precision=20, scale=10))
    actual_fh2 = Column(Numeric(precision=20, scale=10))
    nominal_fh3 = Column(Numeric(precision=20, scale=10))
    actual_fh3 = Column(Numeric(precision=20, scale=10))
    nominal_fh4 = Column(Numeric(precision=20, scale=10))
    actual_fh4 = Column(Numeric(precision=20, scale=10))
    nominal_b1 = Column(Numeric(precision=20, scale=10))
    actual_b1 = Column(Numeric(precision=20, scale=10))
    nominal_b2 = Column(Numeric(precision=20, scale=10))
    actual_b2 = Column(Numeric(precision=20, scale=10))
    nominal_d = Column(Numeric(precision=20, scale=10))
    actual_d = Column(Numeric(precision=20, scale=10))
    nominal_weight = Column(Numeric(precision=20, scale=10))
    calculated_weight = Column(Numeric(precision=20, scale=10))
    difference = Column(Numeric(precision=20, scale=10))
    off_centre_web = Column(Numeric(precision=20, scale=10))
    flange_variation = Column(Numeric(precision=20, scale=10))
    information_to_banks = Column(String)
    comment = Column(String)
    stock_type = Column(String)
    status_change_reason = Column(String)
    # advice_id = Column(BigInteger, ForeignKey('advice.id'),nullable=True)
    # advice = relationship("Advice", backref="advice_finished_product")
    advice = relationship("Advice", secondary=finished_product_advice, back_populates="finished_product")
    loads = relationship("FinishedProductLoad", secondary=finished_product_load, back_populates="finished_products")
    association = relationship("FinishedProduct", secondary=finished_product_association,
                               primaryjoin=id == finished_product_association.c.finished_product_id,
                                secondaryjoin=id == finished_product_association.c.finished_product_association_id)

    # load_id = Column(BigInteger, ForeignKey('finished_product_load.id'),nullable=True)
    # load = relationship("FinishedProductLoad", backref="finished_product_load_finished_product")
    
    product_size_id = Column(BigInteger, ForeignKey("product_size.id"))
    product_size =  relationship("ProductSize", backref="finished_product_size_finished_product")
    
    defect_reason_id = Column(BigInteger, ForeignKey("defect_reason.id"), index=True)
    defect_reason = relationship("DefectReason",backref="defect_reason_finished_product")
    downgraded = Column(String)

    regrade_reason_id = Column(BigInteger, ForeignKey("regrade_reason.id"))
    regrade_reason = relationship("RegradeReason", backref="regrade_reason_finished_product")
    regrade_comment = Column(String)

    order_code = Column(String)
    order_item_code = Column(String)

    cut_sample_length_mm = Column(Numeric(precision=20, scale=10))
    quantity = Column(Integer, nullable=False)

    allocate_reason = Column(String)

    rework_comment = Column(String)

    defect_comment = Column(String)

    rework_initial = Column(String)


    defective_length = Column(Numeric(precision=20, scale=10))
    defect_type = Column(String)
    comment = Column(String)
    defect_quantity = Column(Integer)

    defect_level = Column(String)
    let_go_flag = Column(String)
    rectification_code = Column(String)
    

    
    advice_status = Column(String)

    adc_ind = Column(Boolean, default=False)
    piece_group_code = Column(String, nullable=True)

    label_template_id = Column(BigInteger, ForeignKey("label_template.id"), nullable=True)
    label_template = relationship("LabelTemplate", backref="label_template_item")
    minor_cast_code = Column(String, nullable=True)
    rework_complete_comment = Column(String, nullable = True)

    #covering
    t_runout = Column(Integer)
    t_result = Column(Integer)
    t_override = Column(String)
    tt_runout = Column(Integer)
    tt_result = Column(Integer)
    tt_override = Column(String)
    c_runout = Column(Integer)
    c_result = Column(Integer)
    c_override = Column(String)
    ct_runout = Column(Integer)
    ct_result = Column(Integer)
    ct_override = Column(String)
    sa_runout = Column(Integer)
    sa_result = Column(Integer)
    sa_override = Column(String)
    pa_runout = Column(Integer)
    pa_result = Column(Integer)
    pa_override = Column(String)
    bend_runout = Column(Integer)
    bend_result = Column(Integer)
    bend_override = Column(String)
    overall_imp_result = Column(Integer)
    overall_ten_result = Column(Integer)
    elong_code = Column(String)
    astm_cover_2nd = Column(String)
    cover_status = Column(String, default="W")
    srsmmonesixzero = Column(String)
    srsmmsixfourtwo = Column(String)

    type = Column(String, nullable=False)
    cover_date = Column(DateTime(timezone=True))
    auto_pass = Column(Integer, comment="srsm auto pass flag")
    
    remove_reason = Column(String) 

    scrap_quantity = Column(Integer)


    search_vector = Column(
        TSVectorType(
            "code",
            weights={"code": "A"}
        )
    )

    __table_args__ = (
        UniqueConstraint('code', name='unique_key_code_finished_product'),
        Index('idx_finished_active_updated', 'created_at', postgresql_where=(text("is_deleted IS NULL OR is_deleted = 0"))),
    )


class FinishedProductNoRelationshipBase(BaseResponseModel):
    mill_id: Optional[int] = None
    mill: Optional[MillRead] = None
    runout_id: Optional[int] = None
    rolling_id: Optional[int] = None
    area_id: Optional[int] = None
    # cast_code: Optional[str] = None
    cast_id: Optional[int]=None 
    sec_cast_id: Optional[int]=None 
    location: Optional[str] = None
    stock_in_date: Optional[datetime] = None
    cut_seq: Optional[int] = None
    product_type_id: Optional[int] = None
    product_type: Optional[ProductTypeRead] = None
    quality_code: Optional[str] = None
    width_mm: Optional[float] = None
    length_mm: Optional[float] = None
    thickness_mm: Optional[float] = None
    estimated_cold_length_mm: Optional[float] = None
    estimated_weight_kg: Optional[float] = None
    orig_length_mm: Optional[float] = None
    nose_crop_flag: Optional[str] = None
    tail_crop_flag: Optional[str] = None
    cut_composition_count: Optional[int] = None

    scarfed_status: Optional[str] = None
    allocation_status: Optional[str] = None
    exist_flag: Optional[str] = None
    mult_type: Optional[str] = None
    mult_code: Optional[str] = None
    mult_datetime: Optional[datetime] = None
    mult_confirm_datetime: Optional[datetime] = None
    waste_length: Optional[float] = None
    mult_id: Optional[int] = None
    # advice_id: Optional[int] = None
    # advice: Optional[AdviceRead] = None
    # load_id: Optional[int] = None
    # load: Optional[FinishedProductLoadRead] = None

    status: Optional[str] = None
    rework_type: Optional[str] = None
    rework_status: Optional[str] = None
    rework_due_date: Optional[date] = None
    rework_finish_date: Optional[date] = None
    reserve_status: Optional[str] = None
    reserved_order_item_id: Optional[int] = None
    rework_complete_comment: Optional[str] = None

    cut_code: Optional[str] = None
    sawn_by: Optional[str] = None
    kg: Optional[str] = None
    spec_id: Optional[int] = None
    pass_tests: Optional[str] = None
    multed_with: Optional[str] = None
    order_id: Optional[int] = None
    order_item_id: Optional[int] = None
    onward: Optional[int] = None
    bundle: Optional[int] = None
    alt_spec: Optional[str] = None

    nominal_f1: Optional[float] = None
    actual_f1: Optional[float] = None
    nominal_f2: Optional[float] = None
    actual_f2: Optional[float] = None
    nominal_f3: Optional[float] = None
    actual_f3: Optional[float] = None
    nominal_f4: Optional[float] = None
    actual_f4: Optional[float] = None
    nominal_fh1: Optional[float] = None
    actual_fh1: Optional[float] = None
    nominal_fh2: Optional[float] = None
    actual_fh2: Optional[float] = None
    nominal_fh3: Optional[float] = None
    actual_fh3: Optional[float] = None
    nominal_fh4: Optional[float] = None
    actual_fh4: Optional[float] = None
    nominal_b1: Optional[float] = None
    actual_b1: Optional[float] = None
    nominal_b2: Optional[float] = None
    actual_b2: Optional[float] = None
    nominal_d: Optional[float] = None
    actual_d: Optional[float] = None
    nominal_weight: Optional[float] = None
    calculated_weight: Optional[float] = None
    difference: Optional[float] = None
    off_centre_web: Optional[float] = None
    flange_variation: Optional[float] = None
    information_to_banks: Optional[str] = None

    store_code: Optional[str] = None
    stock_type: Optional[str] = None
    status_change_reason: Optional[str] = None

    defect_reason_id: Optional[int] = None

    regrade_comment: Optional[str] = None

    codes: Optional[List] = None
    site_type_code: Optional[str] = None
    site_code: Optional[str] = None
    area_code: Optional[str] = None
    is_generate_comsi: Optional[bool] = None
    comment: Optional[str] = None
    cut_sample_length_mm: Optional[float] = None
    quantity: Optional[int] = None

    allocate_reason: Optional[str] = None

    rework_comment: Optional[str] = None

    defect_comment: Optional[str] = None

    defective_length: Optional[float] = None
    defect_type: Optional[str] = None
    defect_quantity: Optional[int] = None

    comment: Optional[str] = None

    defect_level: Optional[str] = None
    let_go_flag: Optional[str] = None
    rectification_code: Optional[str] = None

    advice_status: Optional[str] = None

    adc_ind: Optional[bool] = False
    piece_group_code: Optional[str] = None
    label_template_id: Optional[int] = None
    minor_cast_code: Optional[str] = None

    #covering
    t_runout: Optional[int] = None
    t_result: Optional[int] = None
    t_override: Optional[str] = None
    tt_runout: Optional[int] = None
    tt_result: Optional[int] = None
    tt_override: Optional[str] = None
    c_runout: Optional[int] = None
    c_result: Optional[int] = None
    c_override: Optional[str] = None
    ct_runout: Optional[int] = None
    ct_result: Optional[int] = None
    ct_override: Optional[str] = None
    sa_runout: Optional[int] = None
    sa_result: Optional[int] = None
    sa_override: Optional[str] = None
    pa_runout: Optional[int] = None
    pa_result: Optional[int] = None
    pa_override: Optional[str] = None
    bend_runout: Optional[int] = None
    bend_result: Optional[int] = None
    bend_override: Optional[str] = None
    overall_imp_result: Optional[int] = None
    overall_ten_result: Optional[int] = None
    elong_code: Optional[str] = None
    astm_cover_2nd: Optional[str] = None
    cover_status: Optional[str] = None

    type: Optional[str] = None
    product_size_id: Optional[int] = None
    cover_date: Optional[datetime] = None
    auto_pass: Optional[int] = None

    scrap_quantity: Optional[int] = None
 
class FinishedProductRelationshipBase():

    rolling: Optional[RollingRead] = None 
    area: Optional[AreaRead] = None 
    spec: Optional[SpecRead] = None 
    order_item: Optional[OrderItemRead] = None 
    reserved_order_item: Optional[OrderItemRead] = None
    order: Optional[OrderRead] = None 
    cast: Optional[CastRead] = None 
    sec_cast: Optional[CastRead] = None
    advice: Optional[List["AdviceRead"]] = []
    loads: Optional[List["FinishedProductLoadRead"]] = []
    association: Optional[List["FinishedProductRead"]] = []
    # load: Optional[FinishedProductLoadRead] = None
    product_size: Optional[ProductSizeRead] = None


class FinishedProductBase(FinishedProductNoRelationshipBase,FinishedProductRelationshipBase):
    pass

class FinishedProductReadID(FinishedProductBase,FinishedProductRelationshipBase):
    id: int


class FinishedProductCreate(FinishedProductBase):
    code: Optional[str] = None
    hold_reason: Optional[List[Any]] = []
    # cast_code: Optional[str] = None
    # runout_code: Optional[str] = None
    # rolling_code: Optional[str] = None
    # area_code: Optional[str] = None
    # spec_code: Optional[str] = None
    order_code: Optional[str] = None
    order_item_code: Optional[str] = None

class FinishedProductRepeatCreate(FinishedProductBase):
    repeat_num: int
    
class FinishedProductTruncutCreate(BaseResponseModel):
    spec_id: Optional[int] = None
    runout_id: Optional[int] = None
    length_mm: Optional[float] = None

class FinishedProductUpdate(FinishedProductBase):
    pass
    # cast_code: Optional[int] = None
    # runout_code: Optional[int] = None
    # rolling_code: Optional[int] = None
    # area_code: Optional[int] = None
    # spec_code: Optional[int] = None
    # order_code: Optional[int] = None
    # order_item_code: Optional[int] = None


class FinishedProductRead(FinishedProductBase,BaseResponseModel):
    id: int
    code: Optional[str] = None
    runout: Optional[RunoutRead] = None
    hold_reason: Optional[List['HoldreasonRead']] = []
    test_result: Optional[int] = None
    t_result: Optional[int] = 0
    c_result: Optional[int] = 0
    defect_reason_no: Optional[int] = 0
    qualified_quantity: Optional[int] = 0
    defect_reason: Optional[DefectReasonRead] = None
    regrade_reason: Optional[RegradereasonRead] = None
    downgraded: Optional[str] = None
    roll_ref_code: Optional[str] = None

    # virtual fields
    t_runout_code: Optional[str] = None
    c_runout_code: Optional[str] = None

    cut_into: Optional[int] = None
    cut_codes: Optional[str] = None
    remove_reason: Optional[str] = None

    cut_sequence: Optional[List[CutSequencePlanRead]] = []
    test_tensile: Optional[List[TestTensileRead]] = []
    test_impact: Optional[List[TestImpactRead]] = []




class FinishedProductPagination(DispatchBase):
    total: int
    items: List[FinishedProductRead] = []
    itemsPerPage: int
    page : int

class FinishedProductAdviceSplit(DispatchBase):
    total: int
    items: List[FinishedProductRead] = []
    itemsPerPage: int
    page : int

class CombinedResponse(DispatchBase):
    advice: AdviceRead
    finished_product: List[FinishedProductRead]

class FinishedProductBatchHold(DispatchBase):
    total_count: Optional[int] = None
    success_count: Optional[int] = None
    failure_count: Optional[int] = None

class FinishedProductHoldReason(DispatchBase):
    finished_ids: List[Any]
    hold_list: List[Any]
    test_ids: List[int] = []
    

class FinishedProductBySearch(DispatchBase):
    cut_code: Optional[str] = None
    rolling_no: Optional[str] = None
    kg: Optional[str] = None
    
# class FinishedProductMultBase(DispatchBase):
#     runout_id: Optional[int] = None
#     mult_type: Optional[str] = None
#     mult_code: Optional[str] = None
#     exist_flag: Optional[str] = None
#     length_mm: Optional[float] = None
#     waste_length: Optional[float] = None
#     order_item_id: Optional[int] = None
#     cut_code: Optional[str] = None
#     mult_id: Optional[int] = None
    
class FinishedProductMultUpdate(DispatchBase):
    waste_length: Optional[float] = None
    order_item_id: Optional[int] = None
    order_id: Optional[int] = None
    length_mm: Optional[float] = None
    cut_sample_length_mm: Optional[float] = 0
    quantity: Optional[int] = None
    allocation_status: Optional[str] = None
    defect_reason_id: Optional[int] = None
    status_change_reason: Optional[str] = None
    stock_type: Optional[str] = None
    is_cover: Optional[bool] = False
    spec_code: Optional[str] = None
    defect_comment: Optional[str] = None
    defective_length: Optional[float] = None
    compliance: Optional[str] = None
    waste: Optional[float] = None
    scrap_quantity: Optional[int] = 0
    

class FinishedProductMultRegularCreate(DispatchBase):
    length_mm: Optional[float] = None
    order_item_id: Optional[int] = None
    order_id: Optional[int] = None
    cut_sample_length_mm: Optional[float] = 0
    quantity: Optional[int] = None
    allocation_status: Optional[str] = None
    defect_reason_id: Optional[int] = None
    status_change_reason: Optional[str] = None
    stock_type: Optional[str] = None
    spec_code: Optional[str] = None
    compliance: Optional[str] = None
    waste: Optional[float] = None
    

# class FinishedProductMultSingleCreate(FinishedProductMultBase):
#     pass
    
class FinishedProductMultCreate(DispatchBase):
    ids: List[int]
    is_cover: Optional[bool] = False
    mult: FinishedProductMultUpdate = None
    regulars: List[FinishedProductMultRegularCreate] = None


# class FinishedProductMultRead(DispatchBase):
#     id: int
#     runout_id: Optional[int] = None
#     mult_type: Optional[str] = None
#     mult_code: Optional[str] = None
#     exist_flag: Optional[str] = None
#     length_mm: Optional[float] = None
#     waste_length: Optional[float] = None
#     order_item_id: Optional[int] = None
#     cut_code: Optional[str] = None
#     mult_id: Optional[int] = None
#     runout: RunoutRead = None
#     order_item: OrderItemRead = None

class FinishedProductMultResponse(DispatchBase):
    mult: FinishedProductRead = None
    regulars: List[FinishedProductRead] = None
    message_triggered_result: str = None
    
class FinishedProductMultPagination(DispatchBase):
    total: int
    items: List[FinishedProductRead] = []
    itemsPerPage: int
    page : int
    
class ReworkBase(DispatchBase):
    rework_type: Optional[str] = None
    area_id: Optional[int] = None
    rework_comment: Optional[str] = None
    defect_reason_id: Optional[int] = None
    
    
class ReworkRead(ReworkBase):
    id: int

class ReworkUpdate(ReworkBase):
    ids: List[int]

class MultConfirm(DispatchBase):
    ids: List[int]

class LoadUpdate(ReworkBase):
    load_id: int


class RegradeUpdate(BaseResponseModel):
    id: int
    spec_id: Optional[int] = None
    regrade_reason_id: Optional[int] = None
    regrade_reason_code: Optional[str] = None
    regrade_reason: Dict[str, Any] = None
    regrade_comment: Optional[str] = None
    t_result: Optional[int] = None
    c_result: Optional[int] = None


class RegradeBase(BaseResponseModel):
    runout_id: Optional[int] = None
    spec_id: Optional[int] = None
    spec: Optional[SpecRead] = None
    rolling: Optional[RollingRead] = None 
    rolling_id: Optional[int] = None
    test_result: Optional[int] = None
    tensile_score: Optional[int] = None
    impact_score: Optional[int] = None
    comment: Optional[str] = None
    id: Optional[int] = None


class UnCoverUpdate(DispatchBase):
    id: int
    updated_at: Optional[datetime] = None
    updated_by: Optional[str] = None
    t_runout: Optional[int] = None
    t_result: Optional[int] = None
    t_override: Optional[str] = None
    tt_runout: Optional[int] = None
    tt_result: Optional[int] = None
    tt_override: Optional[str] = None
    c_runout: Optional[int] = None
    c_result: Optional[int] = None
    c_override: Optional[str] = None
    ct_runout: Optional[int] = None
    ct_result: Optional[int] = None
    ct_override: Optional[str] = None
    sa_runout: Optional[int] = None
    sa_result: Optional[int] = None
    sa_override: Optional[str] = None
    pa_runout: Optional[int] = None
    pa_result: Optional[int] = None
    pa_override: Optional[str] = None
    bend_runout: Optional[int] = None
    bend_result: Optional[int] = None
    bend_override: Optional[str] = None
    overall_imp_result: Optional[int] = None
    overall_ten_result: Optional[int] = None
    elong_code: Optional[str] = None
    astm_cover_2nd: Optional[str] = None
    cover_status: Optional[str] = "W"


class RegradePagination(DispatchBase):
    total: int
    items: List[RegradeBase] = []
    itemsPerPage: int
    page : int


class FinishedProductAllocate(DispatchBase):
    finished_ids: List[Any]
    select_type: str
    order_id: Optional[int] = None
    order_item_id: Optional[int] = None
    scrap_reason_id: Optional[int] = None
    status_change_reason: Optional[str] = None
    
class GetCompliance(DispatchBase):
    spec_code: str
    runout_id: int

class FinishedProductDefectCreate(DispatchBase):
    finished_ids: List[Any]
    comment: Optional[str] = None


class FinishedProductReworkComplete(DispatchBase):
    ids: List[int]
    rework_initial: Optional[str] = None
    rework_complete_comment : Optional[str] = None

class FinishedProductCreateLoad(BaseResponseModel):
    total_weight: Optional[float] = None
    max_length: Optional[float] = None
    transport_type: Optional[str] = None
    transport_id: Optional[int] = None
    load_no: Optional[str] = None
    cal_weight: Optional[float] = None
    length: Optional[float] = None
    comment: Optional[str] = None
    is_generate_load: Optional[bool] = None
    is_generate_advice: Optional[bool] = None
    is_carry_out:Optional[bool] = None
    ids: List[int] = None

class RetrieveUpdate(DispatchBase):
    finished_ids: List[int] = Field(default_factory=list)
    comment : Optional[str] = None


class ReturnUpdate(DispatchBase):
    id: int
    # kg: Optional[str] = None
    estimated_weight_kg: Optional[float] = None
    length_mm: Optional[float] = None
    code: Optional[str] = None
    advice_id: Optional[int] = None
    quantity: Optional[int] = None
    is_generate_new: Optional[bool] = None
    stock_type: Optional[str] = None
    status: Optional[str] = None
    area_id: Optional[int] = None


class CutTestSample(DispatchBase):
    finished_ids: List[int] = Field(default_factory=list)


class LabelPrint(FinishedProductNoRelationshipBase):
    finished_product_id: int
    printer: str
    format: str
    copies: str
    transaction_code: str