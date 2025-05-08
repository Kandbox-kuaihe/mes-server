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


class TestDecarburisation(Base,TimeStampMixin):
    __tablename__ = 'test_decarburisation'
    id = Column(BigInteger, primary_key=True,autoincrement=True)

    retest_seq = Column(BigInteger, default=0, nullable=False)
    section = Column(String(20))
    section_size_code = Column(String(20))
    bloom = Column(BigInteger)
    cast_id = Column(BigInteger, ForeignKey("cast.id"), nullable=True, )
    cast = relationship("Cast", backref="cast_decarburisation_test_card")
    inspection_authority_code = Column(String(20))
    kg = Column(Numeric(20, 10))
    spec_id = Column(BigInteger, ForeignKey("spec.id"), nullable=True, )
    spec = relationship("Spec", backref="spec_decarburisation_test_card")
    test_id = Column(BigInteger, ForeignKey("test.id"), nullable=False)
    max = Column(Numeric(20, 10))
    status = Column(String(20), nullable=True)
    test_standard = Column(Integer, nullable=True)
    testing_machine = Column(String, nullable=True)

    decarburisation_min = Column(Numeric(20, 10))
    decarburisation_max = Column(Numeric(20, 10))
    decarburisation = Column(Numeric(20, 10))
    result = Column(String, nullable=True)

    check_digit_1 = Column(Integer, nullable=True)
    check_digit_2 = Column(Integer, nullable=True)
    check_digit_3 = Column(Integer, nullable=True)
    code = Column(String, nullable=True)
    decard = Column(Numeric(20, 10), nullable=True)


class TestDecarburisationBase(BaseResponseModel):
    test_id: Optional[int] = None
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

    decarburisation_min: Optional[float] = None
    decarburisation_max: Optional[float] = None
    decarburisation: Optional[float] = None
    result: Optional[str] = None
    check_digit_1: Optional[int] = None
    code: Optional[str] = None
    decard: Optional[float] = None


class TestDecarburisationCreate(TestDecarburisationBase):
    mill_id: Optional[int] = None
    pass


class TestDecarburisationUpdate(TestDecarburisationBase):
    id: Optional[int] = None
    check_digit_1_1: Optional[int] = None
    check_digit_2_2: Optional[int] = None
    check_digit_3_3: Optional[int] = None


class TestDecarburisationRead(TestDecarburisationBase,BaseResponseModel):
    id: int


class TestDecarburisationPagination(DispatchBase):
    total: int
    items: List[TestDecarburisationRead] = []
    itemsPerPage: int
    page: int