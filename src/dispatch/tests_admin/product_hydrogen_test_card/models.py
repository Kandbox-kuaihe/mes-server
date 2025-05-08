from typing import List, Optional

from sqlalchemy import (
    Column,
    ForeignKey,
    String,
    BigInteger
)

from typing import  Optional

from sqlalchemy.orm import relationship

from dispatch.database import Base
from dispatch.models import TimeStampMixin, DispatchBase,BaseResponseModel
from sqlalchemy import Column, String, BigInteger, Numeric, ForeignKey, Integer
from typing import Optional
from dispatch.cast.models import CastRead
from dispatch.spec_admin.spec.models import SpecRead


class TestHydrogen(Base,TimeStampMixin):
    __tablename__ = 'test_hydrogen'
    id = Column(BigInteger, primary_key=True,autoincrement=True)
    mill_id = Column(BigInteger,ForeignKey('mill.id'), nullable=False)
    retest_seq = Column(BigInteger, nullable=False)
    section = Column(String(20))
    section_size_code = Column(String(20))
    bloom = Column(BigInteger)
    cast_id = Column(BigInteger, ForeignKey("cast.id"), nullable=True)
    cast = relationship("Cast", backref="cast_product_hydrogen_card")
    inspection_authority_code = Column(String(20))
    kg = Column(Numeric(20, 10))
    spec_id = Column(BigInteger, ForeignKey("spec.id"), nullable=True)
    spec = relationship("Spec", backref="spec_product_hydrogen_test_card")

    max = Column(Numeric(20, 10))
    status = Column(String(20), nullable=True)
    test_standard = Column(Integer, nullable=True)
    testing_machine = Column(String, nullable=True)

    spec_test = Column(String(20))
    rail_grade = Column(String(20))
    max_test = Column(Numeric(20, 10))
    result = Column(Numeric(20, 10))
    test_id = Column(BigInteger, ForeignKey("test.id"), nullable=False)

    check_digit_1 = Column(Integer, nullable=True)
    check_digit_2 = Column(Integer, nullable=True)
    check_digit_3 = Column(Integer, nullable=True)
    code = Column(String, nullable=True)


class TestHydrogenBase(BaseResponseModel):
    retest_seq: Optional[int] = None
    section: Optional[str] = None
    section_size_code: Optional[str] = None
    bloom: Optional[int] = None
    cast_id: Optional[int] = None
    cast: Optional[CastRead] = None
    inspection_authority_code: Optional[str] = None
    kg: Optional[float] = None
    spec_id: Optional[int] = None
    spec: Optional[SpecRead] = None
    max: Optional[float] = None
    status: Optional[str] = None
    test_standard: Optional[int] = None
    testing_machine: Optional[str] = None

    spec_test: Optional[str] = None
    rail_grade: Optional[str] = None
    max_test: Optional[float] = None
    result: Optional[float] = None
    mill_id: Optional[int] = None
    test_id: Optional[int] = None

    check_digit_1: Optional[int] = None
    code: Optional[str] = None

class TestHydrogenCreate(TestHydrogenBase):
    pass


class TestHydrogenUpdate(TestHydrogenBase):
    id: Optional[int] = None
    check_digit_1_1: Optional[int] = None
    check_digit_2_2: Optional[int] = None
    check_digit_3_3: Optional[int] = None


class TestHydrogenRead(TestHydrogenBase,BaseResponseModel):
    id: int


class TestHydrogenPagination(DispatchBase):
    total: int
    items: List[TestHydrogenRead] = []
    itemsPerPage: int
    page: int