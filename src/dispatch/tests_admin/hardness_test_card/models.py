from typing import List

from typing import  Optional

from dispatch.database import Base
from dispatch.mill.models import MillRead
from dispatch.models import TimeStampMixin, DispatchBase,BaseResponseModel

from sqlalchemy import Column, Integer, String, BigInteger, Numeric, ForeignKey
from sqlalchemy.orm import relationship




class TestHardness(Base,TimeStampMixin):
    __tablename__ = 'test_hardness'
    
    id = Column(BigInteger, primary_key=True,autoincrement=True)
    mill_id = Column(BigInteger, ForeignKey("mill.id"), nullable=False, )
    mill = relationship("Mill", backref="mill_test_hardness")
    retest_seq = Column(Integer, default=0, nullable=False)
    trans_code = Column(String, nullable=True)
    status = Column(String, nullable=True)
    test_standard = Column(Integer, nullable=True)
    testing_machine = Column(String, nullable=True)
    test_id = Column(BigInteger, ForeignKey("test.id"), nullable=False)


    bhn_min_max = Column(String, nullable=True)
    ball_size_mm = Column(Numeric(20, 10), nullable=True)
    load_kg = Column(Numeric(20, 10), nullable=True)
    hardness_1 = Column(Numeric(20, 10), nullable=True)
    hardness_2 = Column(Numeric(20, 10), nullable=True)
    hardness_3 = Column(Numeric(20, 10), nullable=True)
    hardness_4 = Column(Numeric(20, 10), nullable=True)
    hardness_5 = Column(Numeric(20, 10), nullable=True)
    hardness_av = Column(Numeric(20, 10), nullable=True)

    check_digit_1 = Column(Integer, nullable=True)
    check_digit_2 = Column(Integer, nullable=True)
    check_digit_3 = Column(Integer, nullable=True)
    code = Column(String, nullable=True)
    result = Column(String, nullable=True)


    # search_vector = Column(
    #     TSVectorType(
    #         "test_code",
    #         weights={"test_code": "A"},
    #     )
    # )


class TestHardnessBase(BaseResponseModel):
    mill_id: Optional[int] = None
    mill: Optional[MillRead] = None
    retest_seq: Optional[int] = None
    trans_code: Optional[str] = None
    status: Optional[str] = None
    test_standard: Optional[int] = None
    testing_machine: Optional[str] = None
    test_id: Optional[int] = None

    bhn_min_max: Optional[str] = None
    ball_size_mm: Optional[float] = None
    load_kg: Optional[float] = None
    hardness_1: Optional[float] = None
    hardness_2: Optional[float] = None
    hardness_3: Optional[float] = None
    hardness_4: Optional[float] = None
    hardness_5: Optional[float] = None
    hardness_av: Optional[float] = None
    check_digit_1: Optional[int] = None
    code: Optional[str] = None
    result: Optional[str] = None


class TestHardnessCreate(TestHardnessBase):
    pass


class TestHardnessUpdate(TestHardnessBase):
    id: Optional[int] = None
    check_digit_1_1: Optional[int] = None
    check_digit_2_2: Optional[int] = None
    check_digit_3_3: Optional[int] = None


class TestHardnessRead(TestHardnessBase,BaseResponseModel):
    id: int


class TestHardnessPagination(DispatchBase):
    total: int
    items: List[TestHardnessRead] = []
    itemsPerPage: int
    page : int