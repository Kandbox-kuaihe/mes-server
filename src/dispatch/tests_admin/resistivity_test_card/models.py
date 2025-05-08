from typing import List, Optional

from sqlalchemy import Column, ForeignKey, String, BigInteger, Integer

from typing import Optional

from sqlalchemy.orm import relationship

from dispatch.database import Base
from dispatch.models import TimeStampMixin, DispatchBase, BaseResponseModel
from sqlalchemy import Column, String, BigInteger, Numeric, ForeignKey
from typing import Optional
from dispatch.cast.models import CastRead
from dispatch.spec_admin.spec.models import SpecRead


class TestResistivity(Base, TimeStampMixin):
    __tablename__ = "test_resistivity"
    id = Column(BigInteger, primary_key=True, autoincrement=True)

    section = Column(String(20))
    section_size_code = Column(String(20))
    bloom = Column(BigInteger)
    cast_id = Column(
        BigInteger,
        ForeignKey("cast.id"), nullable=True
    )
    cast = relationship("Cast", backref="cast_resistivity_test_card")
    inspection_authority_code = Column(String(20))
    kg = Column(Numeric(20, 10))
    spec_id = Column(
        BigInteger,
        ForeignKey("spec.id"), nullable=True
    )
    spec = relationship("Spec", backref="spec_resistivity_test_card")
    max = Column(Numeric(20, 10))
    status = Column(String(20), nullable=True)

    max_resistivity = Column(Numeric(20, 10))
    temperature = Column(Numeric(20, 10))

    temp = Column(Numeric(20, 10))
    humidity = Column(Numeric(20, 10))
    distance = Column(Numeric(20, 10))
    volt = Column(Numeric(20, 10))
    current = Column(Numeric(20, 10))
    resistivity = Column(Numeric(20, 10))
    test_id = Column(BigInteger, ForeignKey("test.id"), nullable=False)

    check_digit_1 = Column(Integer, nullable=True)
    check_digit_2 = Column(Integer, nullable=True)
    check_digit_3 = Column(Integer, nullable=True)
    code = Column(String, nullable=True)

class TestResistivityBase(BaseResponseModel):
    id: Optional[int] = None
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

    max_resistivity: Optional[float] = None
    temperature: Optional[float] = None
    temp: Optional[float] = None
    humidity: Optional[float] = None
    distance: Optional[float] = None
    volt: Optional[float] = None
    current: Optional[float] = None
    resistivity: Optional[float] = None
    test_id: Optional[int] = None
    check_digit_1: Optional[int] = None
    code: Optional[str] = None


class TestResistivityCreate(TestResistivityBase):
    pass


class TestResistivityUpdate(TestResistivityBase):
    check_digit_1_1: Optional[int] = None
    check_digit_2_2: Optional[int] = None
    check_digit_3_3: Optional[int] = None


class TestResistivityRead(TestResistivityBase, BaseResponseModel):
    id: int


class TestResistivityPagination(DispatchBase):
    total: int
    items: List[TestResistivityRead] = []
    itemsPerPage: int
    page: int
