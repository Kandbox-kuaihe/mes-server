from typing import List

from typing import  Optional

from dispatch.database import Base
from dispatch.mill.models import MillRead
from dispatch.models import TimeStampMixin, DispatchBase,BaseResponseModel

from sqlalchemy import Column, Integer, String, BigInteger, Numeric, ForeignKey
from sqlalchemy.orm import relationship




class TestConductivity(Base,TimeStampMixin):
    __tablename__ = 'test_conductivity'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    mill_id = Column(BigInteger, ForeignKey("mill.id"), nullable=False, )
    mill = relationship("Mill", backref="mill_test_conductivity")
    check_digit = Column(Integer, nullable=True)
    trans_code = Column(String, nullable=False)
    status = Column(String, nullable=False)
    test_standard = Column(Integer, nullable=False)
    testing_machine = Column(String, nullable=True)
    test_id = Column(BigInteger, ForeignKey("test.id"), nullable=False, )

    temperature = Column(Numeric(20, 10), nullable=True)
    relative_humidity = Column(Numeric(20, 10), nullable=True)
    distance = Column(Numeric(20, 10), nullable=True)
    voltage = Column(Numeric(20, 10), nullable=True)
    current = Column(Numeric(20, 10), nullable=True)
    correction_factor = Column(Numeric(20, 10), nullable=True)
    conductivity_actual = Column(Numeric(20, 10), nullable=True)
    conductivity_corrected = Column(Numeric(20, 10), nullable=True)


class TestConductivityBase(BaseResponseModel):
    mill_id: Optional[int] = None
    check_digit: Optional[int] = None
    trans_code: Optional[str] = None
    status: Optional[str] = None
    test_standard: Optional[int] = None
    testing_machine: Optional[str] = None
    test_id: Optional[int] = None
    temperature: Optional[float] = None
    relative_humidity: Optional[float] = None
    distance: Optional[float] = None
    voltage: Optional[float] = None
    current: Optional[float] = None
    correction_factor: Optional[float] = None
    conductivity_actual: Optional[float] = None
    conductivity_corrected: Optional[float] = None


class TestConductivityCreate(TestConductivityBase):
    pass


class TestConductivityRead(TestConductivityBase, BaseResponseModel):
    id: int
