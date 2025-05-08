from typing import List, Optional, Any
from datetime import datetime
from typing import Dict, Optional

from pydantic import Field
from sqlalchemy.orm import relationship
from sqlalchemy_utils import TSVectorType
from sqlalchemy.sql.schema import UniqueConstraint
from sqlalchemy import Column, Integer, String, BigInteger, Numeric, ForeignKey

from dispatch.database import Base

# from dispatch.location.models import LocationCreate, LocationRead
from dispatch.mill.models import MillRead
from dispatch.models import TimeStampMixin, DispatchBase, BaseResponseModel
from dispatch.rolling.rolling_list.models import RollingRead
from dispatch.spec_admin.spec.models import SpecRead
from dispatch.product_type.models import ProductTypeRead
from dispatch.semi_admin.alternative_semi_size.models import AlternativeSemiSizeRead


class OrderGroup(Base, TimeStampMixin):
    __tablename__ = "order_group"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    rolling_id = Column(
        BigInteger,
        ForeignKey("rolling.id"),
        nullable=False,
    )
    rolling = relationship("Rolling", backref="rolling_order_group")
    product_id = Column(
        BigInteger,
        ForeignKey("product_type.id"),
        nullable=False,
    )
    product_type = relationship("ProductType", backref="product_order_group")
    alternative_semi_size_id = Column(
        BigInteger,
        ForeignKey("alternative_semi_size.id"),
        nullable=True,
    )
    alternative_semi_size = relationship("AlternativeSemiSize", backref="alternative_semi_order_group")
    spec_id = Column(
        BigInteger,
        ForeignKey("spec.id"),
        nullable=True,
    )
    spec = relationship("Spec", backref="spec_order_group")

    plan_tonnes = Column(Numeric(20,10), nullable=True)  # 允许为空
    semi_order_code = Column(String, nullable=True)  # 允许为空
    group_charge_seq = Column(Integer, nullable=False)
    group_code = Column(String, nullable=False)
    mill_id = Column(BigInteger, ForeignKey("mill.id"), nullable=False, )
    mill = relationship("Mill", backref="mill_OrderGroup")
    galvanisation = Column(String, nullable=True)
    search_vector = Column(
        TSVectorType(
            "semi_order_code",
            weights={"semi_order_code": "A"},
        )
    )

    dim1 = Column(Numeric(20,10))
    dim2 = Column(Numeric(20,10))
    dim3 = Column(Numeric(20,10))

    __table_args__ = (UniqueConstraint("rolling_id", "group_charge_seq", name="unique_key_order_group"),)


class OrderSpecGroup(Base, TimeStampMixin):
    """
    length, weight, fit字段临时加入，后续需要进行逻辑判断后导入，每次block更新
    """

    __tablename__ = "order_spec_group"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    spec_id = Column(
        BigInteger,
        ForeignKey("spec.id"),
        nullable=False,
    )
    spec = relationship("Spec", backref="spec_order_spec_group")

    order_group_id = Column(
        BigInteger,
        ForeignKey("order_group.id"),
        nullable=False,
    )
    order_group = relationship("OrderGroup", backref="order_spec_group_order_group")
    quality_code = Column(String, default=999999999, nullable=False)
    spec_charge_seq = Column(Integer, nullable=False)
    semi_order_code = Column(String, nullable=True)
    spec_group_code = Column(String, nullable=False)
    multing_code = Column(String, nullable=True)
    length = Column(Numeric(20, 10), default=0, nullable=False)
    weight = Column(Numeric(20, 10), default=0, nullable=False)
    fit = Column(Numeric(20, 10), nullable=True)
    requested_tonnes = Column(Numeric(20, 10), nullable=True)
    allocation_tonnes = Column(Numeric(20, 10), nullable=True)
    mill_id = Column(BigInteger, ForeignKey("mill.id"), nullable=False, )
    mill = relationship("Mill", backref="mill_OrderSpecGroup")
    project_tonnes = Column(Numeric(20, 10), nullable=True)
    search_vector = Column(
        TSVectorType(
            "semi_order_code",
            "multing_code",
            weights={"semi_order_code": "A", "multing_code": "B"},
        )
    )


class OrderGroupBase(BaseResponseModel):
    rolling_id: Optional[int] = None
    product_id: Optional[int] = None
    alternative_semi_size_id: Optional[int] = None
    spec_id: Optional[int] = None
    alternative_semi_id: Optional[int] = None
    group_charge_seq: Optional[int] = None
    group_code: Optional[str] = None
    semi_order_code: Optional[str] = None  # 或者使用Optional[str]来明确表示可选字符串
    plan_tonnes: Optional[float] = None
    rolling: Optional[RollingRead] = None
    product_type: Optional[ProductTypeRead] = None
    mill_id: Optional[int] = None
    mill: Optional[MillRead] = None
    dim1: Optional[float] = None
    dim2: Optional[float] = None
    dim3: Optional[float] = None


class OrderSpecGroupBase(BaseResponseModel):
    id: Optional[int] = None
    quality_code: Optional[str] = None
    order_group_id: Optional[int] = None
    spec_id: Optional[int] = None
    spec_charge_seq: Optional[int] = None
    semi_order_code: Optional[str] = None  # 或者使用Optional[str]来明确表示可选字符串
    spec_group_code: Optional[str] = None  # 同上，可选字符串
    multing_code: Optional[str] = None
    spec: Optional[SpecRead] = None
    length: Optional[float] = None
    weight: Optional[float] = None
    fit: Optional[float] = None
    requested_tonnes: Optional[float] = None
    allocation_tonnes: Optional[float] = None
    mill_id: Optional[int] = None
    mill: Optional[MillRead] = None
    project_tonnes: Optional[float] = None

class OrderSpecGroupUpdate(BaseResponseModel):
    order_group_id: Optional[int] = None
    spec_id: Optional[int] = None
    spec_charge_seq: Optional[int] = None
    semi_order_code: Optional[str] = None
    spec_group_code: Optional[str] = None
    quality_code: Optional[str] = None
    multing_code: Optional[str] = None
    length: Optional[float] = None
    weight: Optional[float] = None
    fit: Optional[float] = None
    requested_tonnes: Optional[float] = None
    allocation_tonnes: Optional[float] = None


class OrderSpecGroupCreate(BaseResponseModel):
    order_group_id: Optional[int] = None
    # alternative_semi_size_id: Optional[int] = None
    spec_id: Optional[int] = None
    spec_charge_seq: Optional[int] = None
    semi_order_code: Optional[str] = None
    spec_group_code: Optional[str] = None
    quality_code: Optional[str] = None
    multing_code: Optional[str] = None
    length: Optional[float] = None
    weight: Optional[float] = None
    fit: Optional[float] = None
    requested_tonnes: Optional[float] = None
    allocation_tonnes: Optional[float] = None
    mill_id: Optional[int] = None

class QualityKG(BaseResponseModel):
    quality_code: str
    kg: float


class OrderGroupListBase(OrderGroupBase):
    id: int
    order_spec_group: Optional[List[OrderSpecGroupBase]] = []
    alternative_semi_size: Optional[AlternativeSemiSizeRead] = None
    blocked_semi_tonnes: Optional[float] = None
    quality_kg: List[QualityKG] = Field(default_factory=list)
    galvanisation: Optional[str] = None
    charged_tonnes: Optional[float] = None


class OrderGroupCreate(BaseResponseModel):
    mill_id: Optional[int] = None
    rolling_id: Optional[int] = None
    product_id: Optional[int] = None
    group_charge_seq: Optional[int] = None
    group_code: Optional[str] = None
    semi_order_code: Optional[str] = None


class OrderGroupSplit(OrderGroupCreate):
    order_spec_group_ids: Optional[list] = []
    pass


class OrderGroupUpdate(OrderGroupBase):
    pass

class OrderSpecGroupUpdateBase(OrderGroupBase):
    id: Optional[int]
    project_tonnes: Optional[float] = None

class OrderGroupBatchUpdate(BaseResponseModel):
    id: Optional[int]
    group_charge_seq: Optional[int] = None
    group_code: Optional[str] = None
    plan_tonnes: Optional[float] = None
    requested_tonnes: Optional[float] = None
    galvanisation: Optional[str] = None
    alternative_semi_size_id: Optional[int] = None


class OrderGroupRead(OrderGroupBase):
    id: int
    order_spec_group: Optional[List[OrderSpecGroupBase]] = []


class OrderGroupPagination(DispatchBase):
    total: int
    items: List[OrderGroupRead] = []
    itemsPerPage: int
    page: int


class OrderSpecGroupRead(OrderSpecGroupBase):
    pass


class OrderSpecGroupPagination(DispatchBase):
    total: int
    items: List[OrderSpecGroupRead] = []
    itemsPerPage: int
    page: int
