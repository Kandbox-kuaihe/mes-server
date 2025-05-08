from typing import List
from datetime import datetime

from sqlalchemy import (
    Column,
    ForeignKey,
    BigInteger,
    Integer,
    Numeric,
    DateTime,
    String
)

from typing import  Optional

from dispatch.database import Base
from dispatch.models import TimeStampMixin, DispatchBase,BaseResponseModel

from sqlalchemy.orm import relationship

from dispatch.runout_admin.finished_product.models import FinishedProductRead
from dispatch.tests_admin.test_list.models import TestRead


class TestCoverage(Base,TimeStampMixin):
    __tablename__ = 'test_coverage'

    id = Column(BigInteger, primary_key=True,autoincrement=True)
    finished_product_id = Column(BigInteger, ForeignKey('finished_product.id'))
    finished_product = relationship("FinishedProduct", backref="finished_product_test_coverage")
    test_id = Column(BigInteger, ForeignKey('test.id'))
    test = relationship("Test", backref="test_test_coverage")
    cast_id = Column(BigInteger, ForeignKey('cast.id'), nullable=True)
    cast = relationship("Cast", backref="cast_test_coverage")
    bundle_code = Column(String, nullable=True)
    cast_code = Column(String, nullable=True)
    test_code = Column(String, nullable=True)
    test_date = Column(DateTime, nullable=True)
    covered_weight_kg = Column(Numeric(precision=20, scale=10))
    covered_quantity = Column(Integer)
    orphan_date = Column(DateTime, nullable=True)
    orphan_batch = Column(String, nullable=True)
    ass_test_number = Column(String, nullable=True)
    ass_test_date = Column(DateTime, nullable=True)
    occurrence = Column(String, nullable=True)
    operate = Column(String, nullable=True)
    test_type = Column(String, nullable=True)
    temp = Column(Integer)
    temp_units = Column(String)
    part = Column(String)
    mill_id = Column(BigInteger, ForeignKey('mill.id'))
    mill = relationship("Mill", backref="mill_test_coverage")
    
    result = Column(Integer, nullable=True)


class TestCoverageBase(BaseResponseModel):
    finished_product_id: Optional[int] = None
    test_id: Optional[int] = None
    mill_id: Optional[int] = None
    cast_id: Optional[int] = None
    bundle_code: Optional[str] = None
    test_code: Optional[str] = None
    cast_code: Optional[str] = None
    test_date: Optional[datetime] = None
    covered_weight_kg: Optional[float] = None
    covered_quantity: Optional[int] = None
    orphan_date: Optional[datetime] = None
    orphan_batch: Optional[str] = None
    ass_test_number: Optional[str] = None
    ass_test_date: Optional[datetime] = None
    occurrence: Optional[str] = None
    operate: Optional[str] = None
    test_type: Optional[str] = None
    temp: Optional[int] = None
    temp_units: Optional[str] = None
    part: Optional[str] = None

    result: Optional[int] = None

class TestCoverageCreate(TestCoverageBase):
    pass


class TestCoverageUpdate(TestCoverageBase):
    pass


class TestCoverageRead(TestCoverageBase,BaseResponseModel):
    id: int
    finished_product: Optional[FinishedProductRead] = None
    test: Optional[TestRead] = None


class TestCoveragePagination(DispatchBase):
    total: int
    items: List[TestCoverageRead] = []
    itemsPerPage: int
    page : int