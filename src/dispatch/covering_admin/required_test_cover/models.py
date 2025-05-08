from typing import List, Optional

from sqlalchemy import (
    Column,
    ForeignKey,
    String,
    BigInteger,
    Integer,
    DateTime, Numeric
)

from typing import Optional
from dispatch.database import Base
from dispatch.models import TimeStampMixin, DispatchBase, BaseResponseModel
from sqlalchemy.orm import relationship
from dispatch.runout_admin.finished_product.models import FinishedProductRead
from dispatch.tests_admin.test_list.models import TestRead


class RequiredTestCover(Base, TimeStampMixin):
    __tablename__ = 'required_test_cover'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    finished_product_id = Column(BigInteger, ForeignKey('finished_product.id'), nullable=False)
    finished_product = relationship("FinishedProduct", backref="finished_product_required_test_cover")
    test_id = Column(BigInteger, ForeignKey('test.id'), nullable=False)
    test = relationship("Test", backref="test_required_test_cover")
    inspector_id = Column(BigInteger, ForeignKey('inspector.id'), nullable=False)
    inspector = relationship("Inspector", backref="inspector_required_test_cover")
    requested_test_type = Column(String)
    requested_test_sub_type = Column(String)
    requested_test_desc = Column(String)
    mill_id = Column(BigInteger, ForeignKey('mill.id'))
    mill = relationship("Mill", backref="mill_required_test_cover")


class RequiredTestCoverBase(BaseResponseModel):
    finished_product_id: Optional[int] = None
    mill_id: Optional[int] = None
    inspector_id: Optional[int] = None
    requested_test_type: Optional[str] = None
    requested_test_sub_type: Optional[str] = None
    requested_test_desc: Optional[str] = None


class RequiredTestCoverCreate(RequiredTestCoverBase):
    pass


class RequiredTestCoverUpdate(RequiredTestCoverBase):
    pass


class RequiredTestCoverRead(RequiredTestCoverBase, BaseResponseModel):
    id: int
    finished_product: Optional[FinishedProductRead] = None
    test: Optional[TestRead] = None


class RequiredTestCoverPagination(DispatchBase):
    total: int
    items: List[RequiredTestCoverRead] = []
    itemsPerPage: int
    page: int
