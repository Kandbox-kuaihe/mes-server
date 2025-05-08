from typing import List

from typing import  Optional

from dispatch.database import Base
from dispatch.mill.models import MillRead
from dispatch.models import TimeStampMixin, DispatchBase,BaseResponseModel

from sqlalchemy import Column, Integer, String, BigInteger, Numeric, ForeignKey
from sqlalchemy.orm import relationship




class TestCleanness(Base,TimeStampMixin):
    __tablename__ = 'test_cleanness'
    
    id = Column(BigInteger, primary_key=True,autoincrement=True)
    mill_id = Column(BigInteger, ForeignKey("mill.id"), nullable=False, )
    mill = relationship("Mill", backref="mill_test_cleanness")
    retest_seq = Column(Integer, default=0, nullable=False)
    trans_code = Column(String, nullable=True)
    status = Column(String, nullable=True)
    test_standard = Column(Integer, nullable=True)
    testing_machine = Column(String, nullable=True)
    test_id = Column(BigInteger, ForeignKey("test.id"), nullable=False, )

    type = Column(String, nullable=True)
    k_number = Column(Numeric(20, 10), nullable=True)
    k_value = Column(Numeric(20, 10), nullable=True)

    check_digit_1 = Column(Integer, nullable=True)
    check_digit_2 = Column(Integer, nullable=True)
    check_digit_3 = Column(Integer, nullable=True)
    code = Column(String, nullable=True)

    # type_2 = Column(String, nullable=True)
    # k_number_2 = Column(String, nullable=True)
    # k_value_2 = Column(String, nullable=True)

    # search_vector = Column(
    #     TSVectorType(
    #         "test_code",
    #         weights={"test_code": "A"},
    #     )
    # )


class TestCleannessBase(BaseResponseModel):
    mill_id: Optional[int] = None
    mill: Optional[MillRead] = None
    retest_seq: Optional[int] = None
    trans_code: Optional[str] = None
    status: Optional[str] = None
    test_standard: Optional[int] = None
    testing_machine: Optional[str] = None
    test_id: Optional[int] = None


    type: Optional[str] = None
    k_number: Optional[float] = None
    k_value: Optional[float] = None

    # type_2: Optional[str] = None
    # k_number_2: Optional[str] = None
    # k_value_2: Optional[str] = None
    check_digit_1: Optional[int] = None
    code: Optional[str] = None


class TestCleannessCreate(TestCleannessBase):
    pass


class TestCleannessUpdate(TestCleannessBase):
    id: Optional[int] = None
    check_digit_1_1: Optional[int] = None
    check_digit_2_2: Optional[int] = None
    check_digit_3_3: Optional[int] = None


class TestCleannessRead(TestCleannessBase,BaseResponseModel):
    id: int


class TestCleannessPagination(DispatchBase):
    total: int
    items: List[TestCleannessRead] = []
    itemsPerPage: int
    page : int