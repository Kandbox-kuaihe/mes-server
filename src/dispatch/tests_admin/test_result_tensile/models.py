from typing import List, Optional

from sqlalchemy import BigInteger, Column, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship

from dispatch.database import Base
from dispatch.mill.models import MillRead
from dispatch.models import BaseResponseModel, DispatchBase, TimeStampMixin
from dispatch.tests_admin.test_sample.models import TestSampleRead

# (Base,TimeStampMixin):




class TestResultTensile(Base,TimeStampMixin):
    __tablename__ = 'test_result_tensile' 

    id = Column(BigInteger, primary_key=True,autoincrement=True)
    mill_id = Column(BigInteger, ForeignKey("mill.id"), nullable=False, )
    mill = relationship("Mill", backref="mill_TestResultTensile")
    test_sample_id = Column(BigInteger, ForeignKey("test_sample.id"), nullable=False, )
    test_sample = relationship("TestSample", backref="test_result_tensile_test_sample")
    sample_shape = Column(String(1))
    orientation = Column(String(1))
    tested_thickness = Column(Numeric(20, 10))
    tested_width = Column(Numeric(20, 10))
    tested_diameter = Column(Numeric(20, 10))
    retest_seq = Column(Integer, nullable=True)
    standard = Column(String)
    insp_code = Column(String)
    # Assuming 'value_mpa' represents Ultimate Tensile Strength or similar
    value_mpa = Column(Numeric(20, 10))
    
    # Yield points at different criteria
    yield_tt0_5 = Column(Numeric(20, 10))
    yield_high = Column(Numeric(20, 10))
    yield_rp0_2 = Column(Numeric(20, 10))
    yield_low = Column(Numeric(20, 10))
    
    elongation_code = Column(String(1))
    elongation_a565 = Column(Numeric(20, 10))
    elongation_a200 = Column(Numeric(20, 10))
    elongation_a50 = Column(Numeric(20, 10))
    elongation_8 = Column(Numeric(20, 10))
    elongation_2 = Column(Numeric(20, 10))
    elongation_a80 = Column(Numeric(20, 10))

    
    # inspector1_id = Column(BigInteger, ForeignKey("inspector1.id"), nullable=True, )
    # inspector1 = relationship("Inspector", backref="test_result_tensile_Inspector1")
    # inspector2_id = Column(BigInteger, ForeignKey("inspector2.id"), nullable=True, )
    # inspector2 = relationship("Inspector", backref="test_result_tensile_Inspector2")
    # inspector3_id = Column(BigInteger, ForeignKey("inspector3.id"), nullable=True, )
    # inspector3 = relationship("Inspector", backref="test_result_tensile_Inspector3")
    # inspector4_id = Column(BigInteger, ForeignKey("inspector4.id"), nullable=True, )
    # inspector4 = relationship("Inspector", backref="test_result_tensile_Inspector4")


    min_ys = Column(Numeric(20, 10))
    max_ys = Column(Numeric(20, 10))
    ys_nominal = Column(Numeric(20, 10))
    ys_alternative = Column(Numeric(20, 10))
    min_uts = Column(Numeric(20, 10))
    max_uts = Column(Numeric(20, 10))
    min_ysuts = Column(Numeric(20, 10))
    max_ysuts = Column(Numeric(20, 10))
    min_elong = Column(String, nullable=True)
    elong_unit = Column(Numeric(20, 10))
    thickmin = Column(Numeric(20, 10))
    thickmax = Column(Numeric(20, 10))
    nominal_thick = Column(Numeric(20, 10))
    further_test = Column(Numeric(20, 10))
    tspr_code = Column(String, nullable=True)

    test_id = Column(BigInteger, ForeignKey('test.id'), nullable=False, unique=True)
    test = relationship("Test", backref="test_test_result_tensile")

    # created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # test_sample = relationship('TestSample', back_populates='tensile_results')
    # search_vector = Column(
    #     TSVectorType(
    #         "test_sample_id",
    #         weights={"test_sample_id": "A" },
    #     )
    # )

    
    
    
  

class TestResultTensileBase(BaseResponseModel):
    test_sample_id: Optional[int] = None
    test_sample: Optional[TestSampleRead] = None
    mill_id: Optional[int] = None
    mill: Optional[MillRead] = None
    test_id: Optional[int] = None
    sample_shape: Optional[str] = None
    retest_seq: Optional[int] = None
    orientation: Optional[str] = None
    tested_thickness: Optional[float] = None
    tested_width: Optional[float] = None
    tested_diameter: Optional[float] = None
    value_mpa: Optional[float] = None
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

    min_ys: Optional[float] = None
    max_ys: Optional[float] = None
    ys_nominal: Optional[float] = None
    ys_alternative: Optional[float] = None
    min_uts: Optional[float] = None
    max_uts: Optional[float] = None
    min_ysuts: Optional[float] = None
    max_ysuts: Optional[float] = None
    min_elong: Optional[float] = None
    elong_unit: Optional[str] = None
    thickmin: Optional[float] = None
    thickmax: Optional[float] = None
    nominal_thick: Optional[float] = None
    further_test: Optional[float] = None
    tspr_code: Optional[str] = None
    standard : Optional[str] = None
    insp_code : Optional[str] = None






class TestResultTensileCreate(TestResultTensileBase):
    pass


class TestResultTensileUpdate(TestResultTensileBase):
    pass


class TestResultTensileRead(TestResultTensileBase,BaseResponseModel):
    id: int


class TestResultTensilePagination(DispatchBase):
    total: int
    items: List[TestResultTensileRead] = []
    itemsPerPage: int
    page : int