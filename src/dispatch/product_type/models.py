from datetime import datetime
from typing import List, Optional

from sqlalchemy import Column, Integer, String, Float, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import UniqueConstraint
from sqlalchemy_utils import TSVectorType

from dispatch.database import Base
from dispatch.mill.models import Mill, MillRead
from dispatch.models import DispatchBase, BaseResponseModel, TimeStampMixin
from dispatch.product_category.models import ProductCategoryRead  # 导入 ProductCategory
from dispatch.product_class.models import ProductClassRead
from dispatch.product_size.models import ProductSizeRead
from dispatch.spec_admin.tolerance.models import ToleranceRead


class ProductType(Base, TimeStampMixin):
    __tablename__ = "product_type"
    __table_args__ = (
        UniqueConstraint('code', 'mill_id', name='product_type_code_mill_id'),
    )
    id = Column(Integer, primary_key=True)
    mill_id = Column(Integer, ForeignKey("mill.id"), nullable=False)  # 外键，指向 Mill 表
    product_category_id = Column(Integer, ForeignKey("product_category.id"), nullable=False)  # 外键，指向 ProductCategory 表
    product_class_id = Column(Integer, ForeignKey("product_class.id"), nullable=True)
    tolerance_id = Column(Integer, ForeignKey("tolerance.id"), nullable=True)
    product_size_id = Column(Integer, ForeignKey("product_size.id"), nullable=True)
    code = Column(String, nullable=False)  # 唯一键
    type = Column(String, nullable=True)
    desc = Column(String, nullable=True)
    longitude = Column(Float, nullable=True)
    latitude = Column(Float, nullable=True)
    product_type_yield = Column(Float, nullable=True)
    dim1 = Column(Numeric(20, 10),default=0, nullable=False)
    dim2 = Column(Numeric(20, 10),default=0, nullable=False)
    dim3 = Column(Numeric(20, 10),default=0, nullable=False)
    dim4 = Column(Numeric(20, 10), nullable=True)

    # PRSZFLTH
    flange_thickness = Column(Numeric(20, 10), nullable=True)
    flange_thickness_1 = Column(Numeric(20, 10), nullable=True)
    flange_thickness_2 = Column(Numeric(20, 10), nullable=True)
    flange_thickness_3 = Column(Numeric(20, 10), nullable=True)
    flange_thickness_4 = Column(Numeric(20, 10), nullable=True)
    flange_height = Column(Numeric(20, 10), nullable=True)
    flange_height_1 = Column(Numeric(20, 10), nullable=True)
    flange_height_2 = Column(Numeric(20, 10), nullable=True)
    flange_height_3 = Column(Numeric(20, 10), nullable=True)
    flange_height_4 = Column(Numeric(20, 10), nullable=True)
    web_thickness = Column(Numeric(20, 10), nullable=True)
    # PRSWBTH
    depth_d = Column(Numeric(20, 10), nullable=True)
    width_b = Column(Numeric(20, 10), nullable=True)
    width_b_1 = Column(Numeric(20, 10), nullable=True)
    width_b_2 = Column(Numeric(20, 10), nullable=True)
    mass = Column(Numeric(20, 10), nullable=True)
    root_radius = Column(Numeric(20, 10), nullable=True)

    tolerance = relationship("Tolerance", foreign_keys=[tolerance_id])
    mill = relationship("Mill", foreign_keys=[mill_id])
    product_category = relationship("ProductCategory", foreign_keys=[product_category_id])  # 设置外键关系
    product_class = relationship("ProductClass", foreign_keys=[product_class_id])
    product_size = relationship("ProductSize", foreign_keys=[product_size_id])

    roughing_xsect = Column(String, nullable=True)
    cogging_xsect = Column(Integer, nullable=True)
    cogging_web = Column(Integer, nullable=True)
    saw_crops_front = Column(Numeric(20, 10), nullable=True)
    shear_loss = Column(Numeric(20, 10), nullable=True)
    max_shear_length = Column(Numeric(20, 10), nullable=True)
    control_roll = Column(Numeric(20, 10), nullable=True)

    search_vector = Column(
        TSVectorType(
            "code",
            "type",
            weights={"code": "A", "type": "B"},
        )
    )

    # __table_args__ = (UniqueConstraint("code", name="unique_key_code"),)


class ProductTypeBase(BaseResponseModel):
    mill_id: Optional[int] = None  # mill_id 必填项
    mill: Optional[MillRead] = None
    tolerance: Optional[ToleranceRead] = None
    tolerance_id: Optional[int] = None
    tolerance_code: Optional[str] = None
    product_category_id: Optional[int] = None  # 新增的 product_category_id
    product_category_code: Optional[str] = None
    product_category: Optional[ProductCategoryRead] = None
    product_class_id: Optional[int] = None
    product_class_code: Optional[str] = None
    product_class: Optional[ProductClassRead] = None
    code: Optional[str]
    type: Optional[str] = None
    desc: Optional[str] = None
    longitude: Optional[float] = None
    latitude: Optional[float] = None
    product_type_yield: Optional[float] = None
    dim1: Optional[float] = None
    dim2: Optional[float] = None
    dim3: Optional[float] = None
    dim4: Optional[float] = None
    mill_code: Optional[str] = None
    flange_thickness: Optional[float] = None
    flange_thickness_1: Optional[float] = None
    flange_thickness_2: Optional[float] = None
    flange_thickness_3: Optional[float] = None
    flange_thickness_4: Optional[float] = None
    flange_height: Optional[float] = None
    flange_height_1: Optional[float] = None
    flange_height_2: Optional[float] = None
    flange_height_3: Optional[float] = None
    flange_height_4: Optional[float] = None

    web_thickness: Optional[float] = None
    
    depth_d: Optional[float] = None
    width_b: Optional[float] = None
    width_b_1: Optional[float] = None
    width_b_2: Optional[float] = None
    mass: Optional[float] = None
    root_radius: Optional[float] = None


    roughing_xsect: Optional[str] = None
    cogging_xsect: Optional[int] = None
    cogging_web: Optional[int] = None
    saw_crops_front: Optional[float] = None
    shear_loss: Optional[float] = None
    max_shear_length: Optional[float] = None
    control_roll: Optional[float] = None


class ProductTypeCreate(ProductTypeBase):
    pass



class ProductTypeUpdate(ProductTypeBase):
    id: int


class ProductTypeRead(ProductTypeBase):
    id: int
    product_size: Optional[ProductSizeRead]



class ProductTypePagination(DispatchBase):
    total: int
    items: List[ProductTypeRead] = []
    itemsPerPage: int
    page: int
