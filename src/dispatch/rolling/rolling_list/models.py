from datetime import datetime
from typing import List, Optional

from sqlalchemy import BigInteger, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import UniqueConstraint
from sqlalchemy_utils import TSVectorType

from dispatch.database import Base
from dispatch.mill.models import MillRead
from dispatch.models import DispatchBase, TimeStampMixin
from dispatch.product_category.models import ProductCategory, ProductCategoryRead  # 导入 ProductCategory
from dispatch.product_class.models import ProductClass, ProductClassRead
from dispatch.product_size.models import ProductSizeRead
from dispatch.product_type.models import ProductType


class Rolling(Base, TimeStampMixin):
    """
    mill_code
    section_type
    section_code
    roll_no
    Programmed Date
    Duration_minutes
    Programmed Total Tons
    """

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    mill_code = Column(String, nullable=False)
    mill_id = Column(BigInteger, ForeignKey("mill.id"), nullable=False, )
    mill = relationship("Mill", backref="mill_Rolling")

    rolling_code = Column(String, nullable=False)
    product_class_id = Column(Integer, ForeignKey("product_class.id"), nullable=True)
    product_class = relationship("ProductClass", foreign_keys=[product_class_id])
    product_type_id = Column(Integer, ForeignKey("product_type.id"), nullable=True)
    product_type_info = relationship("ProductType", foreign_keys=[product_type_id])
    product_category_id = Column(Integer, ForeignKey("product_category.id"), nullable=True)
    product_category = relationship("ProductCategory", foreign_keys=[product_category_id])

    product_size_id = Column(BigInteger, ForeignKey("product_size.id"), nullable=False)
    product_size =  relationship("ProductSize", backref="rolling_product_size")

    rolling_dim1 = Column(String, nullable=False)
    rolling_dim2 = Column(String, nullable=False)
    rolling_dim3 = Column(String, nullable=True)
    rolling_dim4 = Column(String, nullable=True)

    short_code = Column(String, nullable=False)
    galvanise = Column(String, nullable=True)

    product_type = Column(String, nullable=True)
    semi_size = Column(String, nullable=True)
    rolling_status = Column(String, nullable=False)
    rolling_rate = Column(BigInteger, nullable=True)
    std_time_75_pct = Column(Float, nullable=True)
    rolling_time_total = Column(Float, nullable=False)

    programmed_start_date = Column(DateTime, nullable=False)
    duration_minutes = Column(BigInteger, nullable=False)
    programmed_tonnage = Column(Float, nullable=True)

    quality_code = Column(Integer, nullable=True)
    quantity = Column(Integer, nullable=False, default=0)
    close_date = Column(DateTime, nullable=True)
    comment = Column(String, nullable=True)
    rolling_complete = Column(Integer, nullable=True)
    charged_tonnage = Column(Float, nullable=True)
    additional_minutes = Column(Integer, nullable=True)
    week_number = Column(String, nullable=False)
    year = Column(String, nullable=True)
    open_time = Column(DateTime, nullable=True)
    complete_time = Column(DateTime, nullable=True)

    weight = Column(String, nullable=True)
    thick = Column(String, nullable=True)

    programme_id = Column(BigInteger, nullable=True)
    orig_rolling_id = Column(BigInteger, nullable=True)
    pc_id = Column(Integer, nullable=True)

    rolling_seq = Column(BigInteger, nullable=False, default=0)

    search_vector = Column(
        TSVectorType(
            "mill_code",
            "rolling_code",
            weights={"mill_code": "A", "rolling_code": "B"},
        )
    )
    __table_args__ = (
        UniqueConstraint("rolling_dim1", "rolling_dim2", "rolling_dim3", "rolling_dim4", name="unique_key_rolling"),
        UniqueConstraint("rolling_code", "mill_id", "year", name="unique_key_rolling_code_mill_id_year"),
    )


# Pydantic models...


class RollingBase(DispatchBase):
    mill_code: Optional[str] = None
    mill_id: Optional[int] = None
    mill: Optional[MillRead] = None
    rolling_code: Optional[str] = None
    rolling_dim1: Optional[str] = None
    rolling_dim2: Optional[str] = None
    rolling_dim3: Optional[str] = None
    rolling_dim4: Optional[str] = None

    short_code: Optional[str] = None
    product_category_id: Optional[int] = None
    product_class_id: Optional[int] = None
    # product_class_code: Optional[str] = None
    product_type_id: Optional[int] = None

    product_size_id: Optional[int] = None
    

    product_type: Optional[str] = None
    semi_size: Optional[str] = None
    rolling_status: Optional[str] = None
    rolling_rate: Optional[int] = None
    std_time_75_pct: Optional[float] = None
    rolling_time_total: Optional[float] = None

    programmed_start_date: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    # additional_minutes: Optional[int] = None
    programmed_tonnage: Optional[float] = None
    week_number: Optional[str] = None
    year: Optional[str] = None
    weight: Optional[str] = None
    thick: Optional[str] = None

    product_category_code: Optional[str] = None
    product_class_code: Optional[str] = None
    comment: Optional[str] = None

    rolling_seq: Optional[int] = None
    quality_code: Optional[int] = None

class RollingCreate(RollingBase):
    updated_by: Optional[str] = None
    created_by: Optional[str] = None


class RollingUpdate(RollingBase):
    updated_by: Optional[str] = None
    updated_at: Optional[datetime] = None
    product_category_code: Optional[str] = None
    product_class_code: Optional[str] = None
    open_time: Optional[datetime] = None
    complete_time: Optional[datetime] = None


class RollingUpdateStatus(DispatchBase):
    rolling_status: str = None
    updated_by: str = None
    open_time: Optional[datetime] = None
    complete_time: Optional[datetime] = None


class RollingRead(RollingBase):
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    updated_by: Optional[str] = None
    open_time: Optional[datetime] = None
    complete_time: Optional[datetime] = None

    product_class: Optional[ProductClassRead] = None
    product_category: Optional[ProductCategoryRead] = None
    start_datetime: Optional[datetime] = None
    end_datetime: Optional[datetime] = None
    runout_from: Optional[str] = None
    runout_to: Optional[str] = None
    no_bars_rolled: Optional[int] = None
    ordered_tons: Optional[float] = None

    product_size: Optional[ProductSizeRead] = None
    additional_minutes: Optional[int] = None

class RollingPagination(DispatchBase):
    total: int
    items: List[RollingRead] = []


class RollingStatistics(DispatchBase):
    total: int
    items: List[RollingRead] = []
