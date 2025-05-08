from typing import List, Optional

from sqlalchemy import (
    Column,
    ForeignKey,
    BigInteger
)

from typing import  Optional


from dispatch.database import Base
from dispatch.mill.models import MillRead
from dispatch.models import TimeStampMixin, DispatchBase,BaseResponseModel

from sqlalchemy import Column, BigInteger, Numeric, ForeignKey, Integer, String

# (Base,TimeStampMixin):

from typing import Optional
from sqlalchemy.orm import relationship

from dispatch.tests_admin.test_sample.models import TestSampleRead


class TestResultTensileThickness(Base,TimeStampMixin):
    __tablename__ = 'test_result_tensile_thickness' 
    id = Column(BigInteger, primary_key=True,autoincrement=True)
    # test_sample_id = Column(Integer, nullable=False)#, ForeignKey('test_sample.id')

    mill_id = Column(BigInteger, ForeignKey("mill.id"), nullable=False)
    mill = relationship("Mill", backref="mill_TestResultTensileThickness")   
    test_sample_id = Column(BigInteger, ForeignKey("test_sample.id"), nullable=False, )
    test_sample = relationship("TestSample", backref="test_result_tensile_thickness_test_sample")
    retest_seq = Column(Integer, default=0, nullable=False)
    insp_code = Column(String)
    # Tested diameters
    tested_diameter_1 = Column(Numeric(20, 10))
    tested_diameter_2 = Column(Numeric(20, 10))
    tested_diameter_3 = Column(Numeric(20, 10))
    
    # Ultimate tensile strength at different diameters
    value_mpa_1 = Column(Numeric(20, 10))
    value_mpa_2 = Column(Numeric(20, 10))
    value_mpa_3 = Column(Numeric(20, 10))
    
    # Yield strengths at different diameters
    yield_rt0_5_1 = Column(Numeric(20, 10))
    yield_rt0_5_2 = Column(Numeric(20, 10))
    yield_rt0_5_3 = Column(Numeric(20, 10))
    
    # Reduction in area measurements
    reduction_in_area_1 = Column(Numeric(20, 10))
    reduction_in_area_2 = Column(Numeric(20, 10))
    reduction_in_area_3 = Column(Numeric(20, 10))
    ria_average = Column(Numeric(20, 10))
    test_id = Column(BigInteger, ForeignKey('test.id'), nullable=True)
    test = relationship("Test", backref="test_test_result_through_thickness")
 

class TestResultTensileThicknessBase(BaseResponseModel):

    test_sample_id: Optional[int] = None
    test_sample: Optional[TestSampleRead] = None
    mill_id: Optional[int] = None
    mill: Optional[MillRead] = None
    retest_seq: Optional[int] = None
    tested_diameter_1: Optional[float] = None
    tested_diameter_2: Optional[float] = None
    tested_diameter_3: Optional[float] = None
    value_mpa_1: Optional[float] = None
    value_mpa_2: Optional[float] = None
    value_mpa_3: Optional[float] = None
    yield_rt0_5_1: Optional[float] = None
    yield_rt0_5_2: Optional[float] = None
    yield_rt0_5_3: Optional[float] = None
    reduction_in_area_1: Optional[float] = None
    reduction_in_area_2: Optional[float] = None
    reduction_in_area_3: Optional[float] = None
    ria_average: Optional[float] = None
    insp_code: Optional[str] = None






class TestResultTensileThicknessCreate(TestResultTensileThicknessBase):
    pass


class TestResultTensileThicknessUpdate(TestResultTensileThicknessBase):
    test_sample_part: Optional[str] = None


class TestResultTensileThicknessRead(TestResultTensileThicknessBase,BaseResponseModel):
    id: int


class TestResultTensileThicknessPagination(DispatchBase):
    total: int
    items: List[TestResultTensileThicknessRead] = []
    itemsPerPage: int
    page : int