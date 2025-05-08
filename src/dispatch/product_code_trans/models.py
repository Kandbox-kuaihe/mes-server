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

from dispatch.database import Base
from dispatch.models import TimeStampMixin, DispatchBase, BaseResponseModel


class ProductCodeTrans(Base,TimeStampMixin):
    __tablename__ = 'product_code_trans'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    sap_product_code = Column(String, nullable=False)
    sap_dim_1 = Column(String, nullable=False)
    sap_dim_2 = Column(String, nullable=False)
    sap_dim_3 = Column(String, nullable=False)
    legacy_type = Column(String, nullable=False)
    leg_product_code = Column(String, nullable=False)
    leg_dim_1 = Column(String, nullable=False)
    leg_dim_2 = Column(String, nullable=False)
    leg_dim_3 = Column(String, nullable=False)

    mill_id = Column(BigInteger, ForeignKey("mill.id"), nullable=False)
    mill = relationship("Mill", backref="mill_product_code_trans")

    # search_vector = Column(
    #     TSVectorType(
    #         "code",
    #         weights={"code": "A"},
    #     )
    # )

    __table_args__ = (
        UniqueConstraint('sap_product_code', 'sap_dim_1', 'sap_dim_2', 'sap_dim_3', 'mill_id', name='product_code_trans_unique_key'),
    )


class ProductCodeTransBase(BaseResponseModel):
    sap_product_code: Optional[str] = None
    sap_dim_1: Optional[str] = None
    sap_dim_2: Optional[str] = None
    sap_dim_3: Optional[str] = None
    legacy_type: Optional[str] = None
    leg_product_code: Optional[str] = None
    leg_dim_1: Optional[str] = None
    leg_dim_2: Optional[str] = None
    leg_dim_3: Optional[str] = None
    mill_id: Optional[int] = None


class ProductCodeTransCreate(ProductCodeTransBase):
    pass


class ProductCodeTransUpdate(ProductCodeTransBase):
    pass


class ProductCodeTransRead(ProductCodeTransBase):
    id: int

class ProductCodeTransPagination(DispatchBase):
    total: int
    items: List[ProductCodeTransRead] = []
    itemsPerPage: int
    page : int