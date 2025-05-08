from typing import List, Optional
from datetime import datetime, date
from sqlalchemy import Column, Float, ForeignKey, String, BigInteger, Integer, DateTime, Date, Boolean
from typing import Optional
from sqlalchemy.orm import relationship

from sqlalchemy.sql.schema import UniqueConstraint
from sqlalchemy_utils import TSVectorType
from dispatch.defect_reason.models import DefectReasonRead

from dispatch.area.models import AreaCreate, AreaRead
from dispatch.cast.models import CastRead
from dispatch.database import Base,Any
from dispatch.mill.models import MillRead
from dispatch.models import TimeStampMixin, DispatchBase, BaseResponseModel

from sqlalchemy import Column, Integer, String, BigInteger, Numeric, ForeignKey

from dispatch.order_admin.order_group.models import OrderGroupRead, OrderSpecGroupRead
from dispatch.rolling.rolling_list.models import RollingCreate, RollingRead
from dispatch.semi_admin.semi_load.models import SemiLoadRead
from dispatch.site.models import SiteCreate, SiteRead
from dispatch.area.models import AreaRead
from dispatch.product_type.models import ProductTypeBase, ProductTypeRead
from dispatch.label_template.models import LabelTemplateRead
from dispatch.semi_admin.semi_hold_reason.models import SemiHoldReasonRead
from dispatch.semi_admin.semi_hold_reason.models_secondary import semi_hold
from dispatch.spec_admin.quality.models import QualityRead

class Semi(Base, TimeStampMixin):
    __tablename__ = "semi"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    rolling_id = Column(
        BigInteger,
        ForeignKey("rolling.id"),
        nullable=True,
    )
    rolling = relationship("Rolling", backref="rolling_semi")

    order_group_id = Column(
        BigInteger,
        ForeignKey("order_group.id"),
        nullable=True,
    )
    reserved_order_group_id = Column(
        BigInteger,
        ForeignKey("order_group.id"),
        nullable=True,
    )
    order_group = relationship(
        "OrderGroup",
        foreign_keys=[order_group_id],
        backref="order_group_semi"
        )
    reserved_order_group = relationship(
        "OrderGroup",
        foreign_keys=[reserved_order_group_id],
        backref="reserved_order_group_semi"
        )
    site_id = Column(
        BigInteger,
        ForeignKey("site.id"),
        nullable=True,
    )
    site = relationship("Site", backref="site_semi")

    product_type_id = Column(
        BigInteger,
        ForeignKey("product_type.id"),
        nullable=True,
    )
    product_type = relationship("ProductType", backref="product_type_semi")

    mill_id = Column(BigInteger, ForeignKey("mill.id"), nullable=True, )
    mill = relationship("Mill", backref="mill_Semi")

    area_id = Column(BigInteger, ForeignKey("area.id"), nullable=True, )
    area = relationship("Area", backref="area_semi")
    semi_load_id = Column(
        BigInteger,
        ForeignKey("semi_load.id"),
        nullable=True,
    )
    semi_load = relationship("SemiLoad", backref="semi_load_semi")
    spec_id = Column(BigInteger, ForeignKey("spec.id"), nullable=True, )
    spec = relationship("Spec", backref="spec_semi")

    semi_type = Column(String, nullable=True)
    block_quantity = Column(Integer, nullable=True)
    semi_charge_seq = Column(Integer, nullable=True)
    # cast_code = Column(String, nullable=False)
    
    # cast_id =
    cast_id = Column(BigInteger, ForeignKey("cast.id"), nullable=False, )
    cast = relationship("Cast", backref="cast_semi")

    semi_code = Column(String, nullable=False)
    stock_in_date = Column(DateTime, nullable=True)
    quantity = Column(Integer, nullable=True, default=1)
    charge_seq = Column(Integer, nullable=True, default=1)
    location = Column(String, nullable=True, default="DESPATCHED")
    skelp_code = Column(String, nullable=True)

    semi_cut_seq = Column(Integer, nullable=True)
    semi_code_1 = Column(String, nullable=True)
    quality_code = Column(String, nullable=False)
    length_mm = Column(Numeric(20, 10), nullable=True)
    width_mm = Column(Numeric(20, 10), nullable=True)
    thickness_mm = Column(Numeric(20, 10), nullable=True)
    estimated_weight_kg = Column(Numeric(20, 10), nullable=True)
    scarfed_status = Column(String, nullable=True)
    weight = Column(Numeric(20, 10), nullable=True)
    fit = Column(Numeric(20, 10), nullable=True)
    dim1 = Column(Numeric(20, 10), nullable=True)
    dim2 = Column(Numeric(20, 10), nullable=True)

    semi_status = Column(String, nullable=True)

    hold_reason = Column(String)
    semi_hold_reason = relationship("SemiHoldReason", secondary=semi_hold, back_populates="semi")
    comment = Column(String)
    defect_reason_id = Column(BigInteger, ForeignKey("defect_reason.id"))
    defect_reason = relationship("DefectReason",backref="defect_reason_semi")
    rework_type = Column(String)
    rework_status = Column(String)
    rework_due_date = Column(Date)
    rework_finish_date = Column(Date)

    rework_comment = Column(String)
    furnace_sequence_number = Column(String)

    De_Hydrogenise_Flag = Column(Boolean, nullable=True)
    defs = Column(String, nullable=True)
    bloom_size_code = Column(String, nullable=True)
    supplier_code = Column(String, nullable=True)
    semi_supplier_code = Column(String, nullable=True)
    label_template_id = Column(Integer, ForeignKey("label_template.id"), nullable=True)
    label_tempalte = relationship("LabelTemplate")
    defect_quantity = Column(Integer, nullable=True)

    furnace_sequence_number = Column(String, nullable=True)
    section_code = Column(String, nullable=True)
    return_type = Column(String, nullable=True)
    track_code = Column(String, nullable=True)
    cast_code = Column(String, nullable=True)
    cast_suffix = Column(String, nullable=True)
    direction = Column(String, nullable=True)  # 0 - from pen to grid |  1 - from grid to pen
    replacement_ind = Column(String, nullable=True)
    scrap_quantity = Column(Integer, nullable=True)

    quality_id = Column(BigInteger, ForeignKey("quality.id"), nullable=False)
    quality = relationship("Quality", backref="quality_semi")

    generate_code = Column(Integer)
    long_semi_code = Column(String)
    cast_time = Column(DateTime, nullable=True)

    search_vector = Column(
        TSVectorType(
            # "cast_code",
            "semi_code",
            # weights={"cast_code": "A", "semi_code": "B"},
            weights={"semi_code": "A"},
        )
    )

    __table_args__ = (UniqueConstraint("semi_code", name="unique_key_semi_code"),)


class SemiBase(BaseResponseModel):
    semi_load_id: Optional[int] = None
    rolling: Optional[RollingRead] = None
    order_group: Optional[OrderGroupRead] = None
    reserved_order_group: Optional[OrderGroupRead] = None
    rolling_id: Optional[int] = None
    order_group_id: Optional[int] = None
    reserved_order_group_id: Optional[int] = None
    site: Optional[SiteRead] = None
    area: Optional[AreaRead] = None
    semi_load: Optional[SemiLoadRead] = None
    area_id: Optional[int] = None
    area_code: Optional[str] = None
    location: Optional[str] = None
    block_quantity: Optional[int] = None
    semi_charge_seq: Optional[int] = None
    # cast_code: str
    semi_code: Optional[str] = None
    rolling_code: Optional[str] = None
    stock_in_date: Optional[datetime] = None
    cast: Optional[CastRead] = None
    cast_code: Optional[str] = None
    cast_suffix: Optional[str] = None
    cast_id: Optional[int] = None
    skelp_code: Optional[str] = None
    semi_type: Optional[str] = None
    hold_reason: Optional[str] = None
    comment: Optional[str] = None
    semi_status: Optional[str] = None
    quantity: Optional[int] = None
    charge_seq: Optional[int] = None
    semi_cut_seq: Optional[int] = None
    semi_code_1: Optional[str] = None
    product_type: Optional[ProductTypeRead] = None
    quality_code: Optional[str] = None
    length_mm: Optional[float] = None
    width_mm: Optional[float] = None
    thickness_mm: Optional[float] = None
    estimated_weight_kg: Optional[float] = None
    scarfed_status: Optional[str] = None
    weight: Optional[float] = None
    fit: Optional[float] = None
    mill_id: Optional[int] = None
    mill: Optional[MillRead] = None
    label_template_id: Optional[int] = None
    label_template: Optional[LabelTemplateRead] = None
    dim1: Optional[float] = None
    dim2: Optional[float] = None

    defect_reason_id: Optional[int] = None
    defect_reason: Optional[DefectReasonRead] = None

    rework_type: Optional[str] = None
    rework_status: Optional[str] = None
    rework_due_date: Optional[date] = None
    rework_finish_date: Optional[date] = None

    rework_comment: Optional[str] = None
    furnace_sequence_number: Optional[str] = None

    De_Hydrogenise_Flag: Optional[bool] = None
    defs: Optional[str] = None
    bloom_size_code: Optional[str] = None
    supplier_code: Optional[str] = None
    defect_quantity: Optional[int] = None
    scrap_quantity: Optional[int] = None

    furnace_sequence_number: Optional[str] = None
    section_code: Optional[str] = None
    return_type: Optional[str] = None
    track_code: Optional[str] = None

    quality_id: Optional[int] = None
    quality: Optional[QualityRead] = None

    direction: Optional[str] = None

    generate_code: Optional[int] = None
    long_semi_code: Optional[str] = None
    cast_time: Optional[datetime] = None

class SemiCreate(SemiBase):
    pass

class SemiTLM(SemiBase):
    runout_code: Optional[int] = None
    runout_length: Optional[int] = None

class SemiUpdate(SemiBase):
    ids: List[int] = []


class SemiBatchUpdate(DispatchBase):
    id: Optional[int]
    rolling_id: Optional[int] = None
    order_group_id: Optional[int] = None
    block_quantity: Optional[int] = None
    semi_charge_seq: Optional[int] = None
    reserved_order_group_id: Optional[int] = None
    
    semi_code: Optional[str] = None
    comment: Optional[str] = None



class SemiRead(SemiBase, BaseResponseModel):
    id: int
    flex_form_data: Optional[dict]
    semi_hold_reason: Optional[List['SemiHoldReasonRead']] = []
    runout_code: Optional[str] = None
    runout_length: Optional[int] = None


class SemiPagination(DispatchBase):
    total: int
    items: List[SemiRead] = []
    itemsPerPage: int
    page: int
    


    
class ReworkBase(DispatchBase):
    rework_type: Optional[str] = None
    area_id: Optional[int] = None
    rework_comment: Optional[str] = None
    defect_reason_id: Optional[int] = None
    
class ReworkRead(ReworkBase):
    id: int

class ReworkUpdate(ReworkBase):
    ids: List[int]

class ReworkComplete(DispatchBase):
    ids: List[int]

class FinishedProductDefectCreate(DispatchBase):
    finished_ids: List[Any]
    comment: Optional[str] = None

class SemiHoldReason(DispatchBase):
    semi_ids: List[Any]
    hold_list: List[Any]
    