from typing import List

from typing import  Optional

from dispatch.database import Base
from dispatch.mill.models import MillRead
from dispatch.models import TimeStampMixin, DispatchBase,BaseResponseModel

from sqlalchemy import Column, Integer, String, BigInteger, Numeric, ForeignKey
from sqlalchemy.orm import relationship




class TestImpact(Base, TimeStampMixin):
    __tablename__ = 'test_impact'

    id = Column(BigInteger, primary_key=True,autoincrement=True)
    mill_id = Column(BigInteger, ForeignKey("mill.id"), nullable=False)
    mill = relationship("Mill", backref="mill_test_impact")
    test_sample_id = Column(BigInteger, ForeignKey("test_sample.id"), nullable=True)
    test_sample = relationship("TestSample", backref="test_impact_test_sample")
    size_code = Column(String(1))
    retest_seq = Column(Integer, default=0, nullable=False)
    trans_code = Column(String, nullable=True)
    testing_machine = Column(String, nullable=True)
    test_id = Column(BigInteger, ForeignKey("test.id"), nullable=False, unique=True)
    test = relationship("Test", back_populates="impact_object")
    check_digit_1 = Column(Integer, nullable=True)
    check_digit_2 = Column(Integer, nullable=True)
    check_digit_3 = Column(Integer, nullable=True)
    orientation = Column(String, nullable=True)
    standard = Column(String, nullable=True)
    insp_code = Column(String, nullable=True)

    min_single = Column(Numeric(20, 10))
    min_average = Column(Numeric(20, 10))

    temp_c = Column(Numeric(20, 10))
    temp_f = Column(Numeric(20, 10))
    energy_1_j = Column(Numeric(20, 10))
    energy_2_j = Column(Numeric(20, 10))
    energy_3_j = Column(Numeric(20, 10))
    energy_average_j = Column(Numeric(20, 10))
    energy_1_f = Column(Numeric(20, 10))
    energy_2_f = Column(Numeric(20, 10))
    energy_3_f = Column(Numeric(20, 10))
    energy_average_f = Column(Numeric(20, 10))
    shear_1 = Column(Numeric(20, 10))
    shear_2 = Column(Numeric(20, 10))
    shear_3 = Column(Numeric(20, 10))
    shear_average = Column(Numeric(20, 10))
    temp_units = Column(String(1))
    impact_units = Column(String(1))
    energy_units = Column(String(1))

    r1_temp_c = Column(Numeric(20, 10))
    r1_temp_f = Column(Numeric(20, 10))
    r1_energy_1_j = Column(Numeric(20, 10))
    r1_energy_2_j = Column(Numeric(20, 10))
    r1_energy_3_j = Column(Numeric(20, 10))
    r1_energy_average_j = Column(Numeric(20, 10))
    r1_energy_1_f = Column(Numeric(20, 10))
    r1_energy_2_f = Column(Numeric(20, 10))
    r1_energy_3_f = Column(Numeric(20, 10))
    r1_energy_average_f = Column(Numeric(20, 10))
    r1_shear_1 = Column(Numeric(20, 10))
    r1_shear_2 = Column(Numeric(20, 10))
    r1_shear_3 = Column(Numeric(20, 10))
    r1_shear_average = Column(Numeric(20, 10))
    r1_temp_units = Column(String(1))
    r1_impact_units = Column(String(1))
    r1_energy_units = Column(String(1))
    r1_testing_machine = Column(String, nullable=True)
    r1_susp = Column(String(1)) # 是否暂停 cover
    r1_tester = Column(String, nullable=True)

    susp = Column(String(1)) # 是否暂停 cover
    notch = Column(String)
    code = Column(String, nullable=True)

    charpy_ave= Column(String(5), nullable=True)
    charpy_min= Column(String(5), nullable=True)
    shear_min= Column(String(5), nullable=True)
    shear_ave_min= Column(String(5), nullable=True)

    location = Column(String(1), nullable=True)

    ave_value_1 = Column(String(5), nullable=True)
    min_value_1 = Column(String(5), nullable=True)

    ave_value_2 = Column(String(5), nullable=True)
    min_value_2 = Column(String(5), nullable=True)

    ave_value_3 = Column(String(5), nullable=True)
    min_value_3 = Column(String(5), nullable=True)

    ave_value_4 = Column(String(5), nullable=True)
    min_value_4 = Column(String(5), nullable=True)

    ave_value_5 = Column(String(5), nullable=True)
    min_value_5 = Column(String(5), nullable=True)

    ave_value_6 = Column(String(5), nullable=True)
    min_value_6 = Column(String(5), nullable=True)

    ave_shear_1 = Column(String(3), nullable=True)
    min_shear_1 = Column(String(5), nullable=True)

    ave_shear_2 = Column(String(3), nullable=True)
    min_shear_2 = Column(String(5), nullable=True)

    ave_shear_3 = Column(String(3), nullable=True)
    min_shear_3 = Column(String(5), nullable=True)

    crystallinity_shear = Column(String, nullable=True)

    impact_size = Column(Numeric(20, 10))

    # search_vector = Column(
    #     TSVectorType(
    #         "test_code",
    #         weights={"test_code": "A"},
    #     )
    # )


class TestImpactBase(BaseResponseModel):
    test_sample_id: Optional[int] = None
    #test_sample: Optional['TestSampleRead'] = None
    size_code: Optional[str] = None
    mill_id: Optional[int] = None
    mill: Optional[MillRead] = None
    retest_seq: Optional[int] = None
    trans_code: Optional[str] = None
    testing_machine: Optional[str] = None
    test_id: Optional[int] = None
    orientation: Optional[str] = None
    standard: Optional[str] = None
    insp_code: Optional[str] = None

    check_digit_1: Optional[int] = None
    check_digit_2: Optional[int] = None
    check_digit_3: Optional[int] = None
   
    temp_c: Optional[float] = None
    temp_f: Optional[float] = None
    energy_1_j: Optional[float] = None
    energy_2_j: Optional[float] = None
    energy_3_j: Optional[float] = None
    energy_average_j: Optional[float] = None
    energy_1_f: Optional[float] = None
    energy_2_f: Optional[float] = None
    energy_3_f: Optional[float] = None
    energy_average_f: Optional[float] = None
    shear_1: Optional[float] = None
    shear_2: Optional[float] = None
    shear_3: Optional[float] = None
    shear_average: Optional[float] = None
    temp_units: Optional[str] = None
    impact_units: Optional[str] = None
    energy_units: Optional[str] = None

    min_single: Optional[float] = None
    min_average: Optional[float] = None

    r1_temp_c: Optional[float] = None
    r1_temp_f: Optional[float] = None
    r1_energy_1_j: Optional[float] = None
    r1_energy_2_j: Optional[float] = None
    r1_energy_3_j: Optional[float] = None
    r1_energy_average_j: Optional[float] = None
    r1_energy_1_f: Optional[float] = None
    r1_energy_2_f: Optional[float] = None
    r1_energy_3_f: Optional[float] = None
    r1_energy_average_f: Optional[float] = None
    r1_shear_1: Optional[float] = None
    r1_shear_2: Optional[float] = None
    r1_shear_3: Optional[float] = None
    r1_shear_average: Optional[float] = None
    r1_temp_units: Optional[str] = None
    r1_impact_units: Optional[str] = None
    r1_energy_units: Optional[str] = None
    r1_testing_machine: Optional[str] = None
    r1_susp: Optional[str] = None
    r1_tester: Optional[str] = None

    notch: Optional[str] = None
    min_single: Optional[float] = None
    min_average: Optional[float] = None
    
    susp: Optional[str] = None
    code: Optional[str] = None
    charpy_ave: Optional[str] = None
    charpy_min: Optional[str] = None
    shear_min: Optional[str] = None
    shear_ave_min: Optional[str] = None

    location : Optional[str] = None

    ave_value_1: Optional[str] = None
    min_value_1: Optional[str] = None

    ave_value_2: Optional[str] = None
    min_value_2: Optional[str] = None

    ave_value_3: Optional[str] = None
    min_value_3: Optional[str] = None

    ave_value_4: Optional[str] = None
    min_value_4: Optional[str] = None

    ave_value_5: Optional[str] = None
    min_value_5: Optional[str] = None

    ave_value_6: Optional[str] = None
    min_value_6: Optional[str] = None

    ave_shear_1: Optional[str] = None
    min_shear_1: Optional[str] = None

    ave_shear_2: Optional[str] = None
    min_shear_2: Optional[str] = None

    ave_shear_3: Optional[str] = None
    min_shear_3: Optional[str] = None
    crystallinity_shear:  Optional[str] = None

    impact_size: Optional[float] = None




class TestImpactCreate(TestImpactBase):
    pass


class TestImpactUpdate(TestImpactBase):
    id: Optional[int] = None
    check_digit_1_1: Optional[int] = None
    check_digit_2_2: Optional[int] = None
    check_digit_3_3: Optional[int] = None



class TestSampleRead(DispatchBase):
    id: int
    test_sample_code: Optional[str] = None
    test_sample_part: Optional[str] = None


class TestRead(DispatchBase):
    id: Optional[int] = None
    test_sample: Optional[TestSampleRead] = None


class TestImpactRead(TestImpactBase,BaseResponseModel):
    test: Optional[TestRead] = None
    id: int

    # virtual
    covered_weight_kg: Optional[float] = None


class TestImpactPagination(DispatchBase):
    total: int
    items: List[TestImpactRead] = []
    itemsPerPage: int
    page : int
