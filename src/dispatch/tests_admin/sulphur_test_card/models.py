from typing import List

from typing import  Optional

from dispatch.database import Base
from dispatch.mill.models import MillRead
from dispatch.models import TimeStampMixin, DispatchBase,BaseResponseModel

from sqlalchemy import Column, Integer, String, BigInteger, Numeric, ForeignKey
from sqlalchemy.orm import relationship




class TestSulphur(Base,TimeStampMixin):
    __tablename__ = 'test_sulphur'
    
    id = Column(BigInteger, primary_key=True,autoincrement=True)
    mill_id = Column(BigInteger, ForeignKey("mill.id"), nullable=False, )
    mill = relationship("Mill", backref="mill_test_sulphur")
    retest_seq = Column(Integer, nullable=False, default=0)
    trans_code = Column(String, nullable=True)
    status = Column(String, nullable=True)
    test_standard = Column(Integer, nullable=True)
    testing_machine = Column(String, nullable=True)
    test_id = Column(BigInteger, ForeignKey("test.id"), nullable=False, )
    check_digit = Column(Integer, nullable=True)

    rail_grade = Column(Numeric(20, 10), nullable=True)
    max = Column(String, nullable=True)
    result = Column(String, nullable=True)

    check_digit_1 = Column(Integer, nullable=True)
    check_digit_2 = Column(Integer, nullable=True)
    check_digit_3 = Column(Integer, nullable=True)
    code = Column(String, nullable=True)
    d_val = Column(String, nullable=True)
    in_spec = Column(String, nullable=True)



class TestSulphurBase(BaseResponseModel):
    mill_id: Optional[int] = None
    mill: Optional[MillRead] = None
    retest_seq: Optional[int] = None
    trans_code: Optional[str] = None
    status: Optional[str] = None
    test_standard: Optional[int] = None
    testing_machine: Optional[str] = None
    test_id: Optional[int] = None
    check_digit: Optional[int] = None
    rail_grade: Optional[float] = None
    max: Optional[str] = None
    result: Optional[str] = None
    check_digit_1: Optional[int] = None
    code: Optional[str] = None
    d_val: Optional[str] = None
    in_spec: Optional[str] = None


class TestSulphurCreate(TestSulphurBase):
    pass


class TestSulphurUpdate(TestSulphurBase):
    id: Optional[int] = None
    check_digit_1_1: Optional[int] = None
    check_digit_2_2: Optional[int] = None
    check_digit_3_3: Optional[int] = None


class TestSulphurRead(TestSulphurBase,BaseResponseModel):
    id: int


class TestSulphurPagination(DispatchBase):
    total: int
    items: List[TestSulphurRead] = []
    itemsPerPage: int
    page : int