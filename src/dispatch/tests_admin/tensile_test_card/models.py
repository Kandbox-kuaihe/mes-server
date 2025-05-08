from typing import List, Optional

from sqlalchemy import BigInteger, Column, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship

from dispatch.cast.models import CastRead
from dispatch.database import Base
from dispatch.mill.models import MillRead
from dispatch.models import BaseResponseModel, DispatchBase, TimeStampMixin


class TestTensile(Base,TimeStampMixin):
    __tablename__ = 'test_tensile'
    
    id = Column(BigInteger, primary_key=True,autoincrement=True)
    code = Column(String, nullable=True)
    mill_id = Column(BigInteger, ForeignKey("mill.id"), nullable=False, )
    mill = relationship("Mill", backref="mill_test_tensile")
    cast_id = Column(BigInteger, ForeignKey("cast.id"), nullable=True)
    test_sample_id = Column(BigInteger, ForeignKey("test_sample.id"), nullable=True, )
    test_sample = relationship("TestSample", backref="test_tensile_test_sample")
    value_mpa = Column(Numeric(20, 10))
    cast_code = Column(String, nullable=True)
    retest_seq = Column(Integer, nullable=True)
    standard = Column(String, nullable=True)
    insp_code = Column(String, nullable=True)
    status = Column(String, nullable=True)
    check_digit_1 = Column(Integer, nullable=True)
    check_digit_2 = Column(Integer, nullable=True)
    check_digit_3 = Column(Integer, nullable=True)
    test_standard = Column(Integer, nullable=True)
    susp = Column(String(1), nullable=True)
    testing_machine = Column(String, nullable=True)
    test_id = Column(BigInteger, ForeignKey("test.id"), nullable=False, unique=True)
    test = relationship("Test", back_populates="tensile_object")
    sample_shape = Column(String, nullable=True)
    tested_thickness = Column(Numeric(20, 10), nullable=True)
    tested_width = Column(Numeric(20, 10), nullable=True)
    tested_diameter = Column(Numeric(20, 10), nullable=True)
    tensile_uts_mpa = Column(Numeric(20, 10), nullable=True)
    yield_tt0_5 = Column(Numeric(20, 10), nullable=True)
    yield_high = Column(Numeric(20, 10), nullable=True)
    yield_rp0_2 = Column(Numeric(20, 10), nullable=True)
    yield_low = Column(Numeric(20, 10), nullable=True)
    elongation_code = Column(String, nullable=True)
    elongation = Column(Numeric(20, 10), nullable=True)
    elongation_a565 = Column(Numeric(20, 10), nullable=True)
    elongation_a200 = Column(Numeric(20, 10), nullable=True)
    elongation_a50 = Column(Numeric(20, 10), nullable=True)
    elongation_8 = Column(Numeric(20, 10), nullable=True)
    elongation_2 = Column(Numeric(20, 10), nullable=True)
    elongation_a80 = Column(Numeric(20, 10), nullable=True)
    condition_code = Column(Numeric(20, 10), nullable=True)
    relieved_code = Column(Numeric(20, 10), nullable=True)
    yield_ = Column(Numeric(20, 10), nullable=True)
    rp1 = Column(Numeric(20, 10), nullable=True)
    rp2 = Column(Numeric(20, 10), nullable=True)
    rp5 = Column(Numeric(20, 10), nullable=True)
    reduction_of_area = Column(Numeric(20, 10), nullable=True)
    cross_sectional_area = Column(Numeric(20, 10), nullable=True)
    area = Column(Numeric(20, 10), nullable=True)

    r1_value_mpa = Column(Numeric(20, 10), nullable=True)
    r1_tested_thickness = Column(Numeric(20, 10), nullable=True)
    r1_tested_width = Column(Numeric(20, 10), nullable=True)
    r1_tested_diameter = Column(Numeric(20, 10), nullable=True)
    r1_tensile_uts_mpa = Column(Numeric(20, 10), nullable=True)
    r1_yield_tt0_5 = Column(Numeric(20, 10), nullable=True)
    r1_yield_high = Column(Numeric(20, 10), nullable=True)
    r1_yield_rp0_2 = Column(Numeric(20, 10), nullable=True)
    r1_yield_low = Column(Numeric(20, 10), nullable=True)
    r1_elongation_code = Column(String, nullable=True)
    r1_elongation = Column(Numeric(20, 10), nullable=True)
    r1_elongation_a565 = Column(Numeric(20, 10), nullable=True)
    r1_elongation_a200 = Column(Numeric(20, 10), nullable=True)
    r1_elongation_a50 = Column(Numeric(20, 10), nullable=True)
    r1_elongation_8 = Column(Numeric(20, 10), nullable=True)
    r1_elongation_2 = Column(Numeric(20, 10), nullable=True)
    r1_elongation_a80 = Column(Numeric(20, 10), nullable=True)
    r1_yield_ = Column(Numeric(20, 10), nullable=True)
    r1_rp1 = Column(Numeric(20, 10), nullable=True)
    r1_rp2 = Column(Numeric(20, 10), nullable=True)
    r1_rp5 = Column(Numeric(20, 10), nullable=True)
    r1_reduction_of_area = Column(Numeric(20, 10), nullable=True)
    r1_cross_sectional_area = Column(Numeric(20, 10), nullable=True)
    r1_testing_machine = Column(String, nullable=True)
    r1_susp = Column(String(1), nullable=True)
    r1_area = Column(Numeric(20, 10), nullable=True)
    r1_tester = Column(String, nullable=True)

    r2_value_mpa = Column(Numeric(20, 10), nullable=True)
    r2_tested_thickness = Column(Numeric(20, 10), nullable=True)
    r2_tested_width = Column(Numeric(20, 10), nullable=True)
    r2_tested_diameter = Column(Numeric(20, 10), nullable=True)
    r2_tensile_uts_mpa = Column(Numeric(20, 10), nullable=True)
    r2_yield_tt0_5 = Column(Numeric(20, 10), nullable=True)
    r2_yield_high = Column(Numeric(20, 10), nullable=True)
    r2_yield_rp0_2 = Column(Numeric(20, 10), nullable=True)
    r2_yield_low = Column(Numeric(20, 10), nullable=True)
    r2_elongation_code = Column(String, nullable=True)
    r2_elongation = Column(Numeric(20, 10), nullable=True)
    r2_elongation_a565 = Column(Numeric(20, 10), nullable=True)
    r2_elongation_a200 = Column(Numeric(20, 10), nullable=True)
    r2_elongation_a50 = Column(Numeric(20, 10), nullable=True)
    r2_elongation_8 = Column(Numeric(20, 10), nullable=True)
    r2_elongation_2 = Column(Numeric(20, 10), nullable=True)
    r2_elongation_a80 = Column(Numeric(20, 10), nullable=True)
    r2_yield_ = Column(Numeric(20, 10), nullable=True)
    r2_rp1 = Column(Numeric(20, 10), nullable=True)
    r2_rp2 = Column(Numeric(20, 10), nullable=True)
    r2_rp5 = Column(Numeric(20, 10), nullable=True)
    r2_reduction_of_area = Column(Numeric(20, 10), nullable=True)
    r2_cross_sectional_area = Column(Numeric(20, 10), nullable=True)
    r2_testing_machine = Column(String, nullable=True)
    r2_test_ref = Column(String, nullable=True)
    r2_susp = Column(String(1), nullable=True)
    r2_area = Column(Numeric(20, 10), nullable=True)
    r2_tester = Column(String, nullable=True)

    inspector_id_1 = Column(BigInteger, ForeignKey("inspector.id"), nullable=True, )
    inspector_id_2 = Column(BigInteger, ForeignKey("inspector.id"), nullable=True, )
    inspector_id_3 = Column(BigInteger, ForeignKey("inspector.id"), nullable=True, )
    inspector_id_4 = Column(BigInteger, ForeignKey("inspector.id"), nullable=True, )

    orientation = Column(String(1), nullable=True)
    srsm_relieved_code = Column(String(3), nullable=True)
    srsm_uts = Column(String(4), nullable=True)
    srsm_pl_length = Column(Numeric(20, 10), nullable=True)
    srsm_rp1 = Column(Numeric(20, 10), nullable=True)
    srsm_tested_inner_diameter = Column(Numeric(20, 10), nullable=True)
    srsm_area = Column(Numeric(20, 10), nullable=True)
    comment = Column(String)

    
    yield_min = Column(Numeric(20, 10), nullable=True)
    yield_max = Column(Numeric(20, 10), nullable=True)
    tensile_min = Column(Numeric(20, 10), nullable=True)
    tensile_max = Column(Numeric(20, 10), nullable=True)
    elong_min_value = Column(Numeric(20, 10), nullable=True)
    location = Column(String(1), nullable=True)
    tensile_units = Column(String(1), nullable=True)
    yield_units = Column(String(1), nullable=True)
    y_t_ratio_min = Column(Numeric(20, 10), nullable=True)
    y_t_ratio_max = Column(Numeric(20, 10), nullable=True)
    # search_vector = Column(
    #     TSVectorType(
    #         "test_code",
    #         weights={"test_code": "A"},
    #     )
    # )



class TestTensileBase(BaseResponseModel):
    id: Optional[int] = None
    test_sample_id: Optional[int] = None
    
    mill_id: Optional[int] = None
    mill: Optional[MillRead] = None
    code: Optional[str] = None
    cast_id: Optional[int] = None
    cast_code: Optional[str] = None
    retest_seq: Optional[int] = None
    standard: Optional[str] = None
    insp_code: Optional[str] = None
    value_mpa: Optional[float] = None
    check_digit_1: Optional[int] = None
    check_digit_2: Optional[int] = None
    check_digit_3: Optional[int] = None
    test_standard: Optional[int] = None
    testing_machine: Optional[str] = None
    status: Optional[str] = None
    test_id: Optional[int] = None
    sample_shape: Optional[str] = None
    tested_thickness: Optional[float] = None
    tested_width: Optional[float] = None
    tested_diameter: Optional[float] = None
    tensile_uts_mpa: Optional[float] = None
    yield_tt0_5: Optional[float] = None
    yield_high: Optional[float] = None
    yield_rp0_2: Optional[float] = None
    yield_low: Optional[float] = None
    elongation_code: Optional[str] = None
    elongation_a565: Optional[float] = None
    elongation_a200: Optional[float] = None
    elongation_a50: Optional[float] = None
    elongation_8: Optional[float] = None
    elongation_2: Optional[float] = None
    elongation_a80: Optional[float] = None
    condition_code: Optional[float] = None
    relieved_code: Optional[float] = None
    yield_: Optional[float] = None
    elongation: Optional[float] = None
    rp1: Optional[float] = None
    rp2: Optional[float] = None
    rp5: Optional[float] = None
    reduction_of_area: Optional[float] = None
    cross_sectional_area: Optional[float] = None
    area: Optional[float] = None

    r1_value_mpa: Optional[float] = None
    r1_tested_thickness: Optional[float] = None
    r1_tested_width: Optional[float] = None
    r1_tested_diameter: Optional[float] = None
    r1_tensile_uts_mpa: Optional[float] = None
    r1_yield_tt0_5: Optional[float] = None
    r1_yield_high: Optional[float] = None
    r1_yield_rp0_2: Optional[float] = None
    r1_yield_low: Optional[float] = None
    r1_elongation_code: Optional[str] = None
    r1_elongation_a565: Optional[float] = None
    r1_elongation_a200: Optional[float] = None
    r1_elongation_a50: Optional[float] = None
    r1_elongation_8: Optional[float] = None
    r1_elongation_2: Optional[float] = None
    r1_elongation_a80: Optional[float] = None
    r1_yield_: Optional[float] = None
    r1_elongation: Optional[float] = None
    r1_rp1: Optional[float] = None
    r1_rp2: Optional[float] = None
    r1_rp5: Optional[float] = None
    r1_reduction_of_area: Optional[float] = None
    r1_cross_sectional_area: Optional[float] = None
    r1_area: Optional[float] = None
    r1_tester: Optional[str] = None

    r2_value_mpa: Optional[float] = None
    r2_tested_thickness: Optional[float] = None
    r2_tested_width: Optional[float] = None
    r2_tested_diameter: Optional[float] = None
    r2_tensile_uts_mpa: Optional[float] = None
    r2_yield_tt0_5: Optional[float] = None
    r2_yield_high: Optional[float] = None
    r2_yield_rp0_2: Optional[float] = None
    r2_yield_low: Optional[float] = None
    r2_elongation_code: Optional[str] = None
    r2_elongation_a565: Optional[float] = None
    r2_elongation_a200: Optional[float] = None
    r2_elongation_a50: Optional[float] = None
    r2_elongation_8: Optional[float] = None
    r2_elongation_2: Optional[float] = None
    r2_elongation_a80: Optional[float] = None
    r2_yield_: Optional[float] = None
    r2_elongation: Optional[float] = None
    r2_rp1: Optional[float] = None
    r2_rp2: Optional[float] = None
    r2_rp5: Optional[float] = None
    r2_reduction_of_area: Optional[float] = None
    r2_cross_sectional_area: Optional[float] = None
    r2_area: Optional[float] = None
    r2_test_ref: Optional[str] = None
    r2_tester: Optional[str] = None

    inspector_id_1: Optional[int] = None
    inspector_id_2: Optional[int] = None
    inspector_id_3: Optional[int] = None
    inspector_id_4: Optional[int] = None
    orientation: Optional[str] = None
    srsm_relieved_code: Optional[str] = None
    srsm_uts: Optional[str] = None
    srsm_pl_length: Optional[float] = None
    srsm_rp1: Optional[float] = None
    srsm_tested_inner_diameter: Optional[float] = None
    srsm_area: Optional[float] = None
    comment: Optional[str] = None

    susp: Optional[str] = None

    yield_min: Optional[float] = None
    yield_max: Optional[float] = None
    tensile_min: Optional[float] = None
    tensile_max: Optional[float] = None
    elong_min_value: Optional[float] = None

    location: Optional[str] = None
    tensile_units: Optional[str] = None
    yield_units: Optional[str] = None
    y_t_ratio_min: Optional[float] = None
    y_t_ratio_max: Optional[float] = None
    



class TestTensileCreate(TestTensileBase):
    pass


class TestSampleRead(DispatchBase):
    id: int
    test_sample_code: Optional[str] = None
    test_sample_part: Optional[str] = None


class TestRead(DispatchBase):
    id: Optional[int] = None
    test_sample: Optional[TestSampleRead] = None


class TestTensileUpdate(TestTensileBase):
    check_digit_1_1: Optional[int] = None
    check_digit_2_2: Optional[int] = None
    check_digit_3_3: Optional[int] = None
    pass


class TestTensileRead(TestTensileBase,BaseResponseModel):
    id: int
#test_sample: Optional['TestSampleRead'] = None
    #virtual
    covered_weight_kg: Optional[float] = None
    test: Optional[TestRead] = None


class TestTensilePagination(DispatchBase):
    total: int
    items: List[TestTensileRead] = []
    itemsPerPage: int
    page : int