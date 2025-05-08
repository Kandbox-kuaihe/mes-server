from dispatch.database import Base
from sqlalchemy import (
    Column,
    BigInteger,
    String,
    ForeignKey,
)
from dispatch.models import DispatchBase, TimeStampMixin, BaseResponseModel
from typing import Optional, List
from sqlalchemy.orm import relationship
from sqlalchemy_utils import TSVectorType
from dispatch.mill.models import MillRead
from sqlalchemy.sql.schema import UniqueConstraint


class Customer(Base, TimeStampMixin):
    __tablename__ = "customer"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    mill_id = Column(BigInteger, ForeignKey("mill.id"), nullable=True)
    mill = relationship("Mill", backref="mill_customer")


    code = Column(String, nullable=False, unique=True)
    address_line_1 = Column(String, nullable=True)
    address_line_2 = Column(String, nullable=True)
    address_line_3 = Column(String, nullable=True)
    address_line_4 = Column(String, nullable=True)
    address_line_5 = Column(String, nullable=True)
    customer_type = Column(String, nullable=True)
    group = Column(String, nullable=True)
    name = Column(String, nullable=True)
    desc = Column(String, nullable=True)
    coh_code = Column(String, nullable=True, unique=True)

    search_vector = Column(
        TSVectorType(
            "code",
            "name",
            weights={"code": "A", "name": "B"},
        )
    )
    __table_args__ = (
        UniqueConstraint('code', name='unique_customer_code'),
    )

class Cust_Attr(Base, TimeStampMixin):
    __tablename__ = "cust_attr"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    cust_id = Column(BigInteger, ForeignKey('customer.id'), nullable=False)
    customer = relationship("Customer", backref="cust_attr_customer")
    code = Column(String, nullable=False)
    value = Column(String, nullable=False)
    __table_args__ = (
        UniqueConstraint('code', name='unique_cust_attr_code'),
    )


class CustomerBase(BaseResponseModel):
    mill_id: Optional[int] = None
    mill: Optional[MillRead] = None
    code: Optional[str] = None
    address_line_1: Optional[str] = None
    address_line_2: Optional[str] = None
    address_line_3: Optional[str] = None
    address_line_4: Optional[str] = None
    address_line_5: Optional[str] = None
    customer_type: Optional[str] = None
    group: Optional[str] = None
    name: Optional[str] = None
    desc: Optional[str] = None
    coh_code: Optional[str] = None

class Cust_AttrBase(BaseResponseModel):
    code: Optional[str] = None
    value: Optional[str] = None
    cust_id: Optional[int] = None

class Cust_AttrRead(Cust_AttrBase):
    id: Optional[int] = None

class CustomerCreate(CustomerBase):
    cust_attr: Optional[List[Cust_AttrRead]] = []


class CustomerUpdate(CustomerBase):
    id: Optional[int] = None
    cust_attr: Optional[List[Cust_AttrRead]] = []


class CustomerRead(CustomerBase,BaseResponseModel):
    id: Optional[int] = None


class CustomerPagination(DispatchBase):
    total: int
    items: List[CustomerRead] = []
    itemsPerPage: int
    page: int
    

