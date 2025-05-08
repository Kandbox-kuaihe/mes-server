from typing import List, Optional

from sqlalchemy import BigInteger, Column, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship

from dispatch.database import Base
from dispatch.mill.models import MillRead
from dispatch.models import BaseResponseModel, DispatchBase, TimeStampMixin
from dispatch.tests_admin.test_sample.models import TestSampleRead

# (Base,TimeStampMixin):






class TestResultImpact(Base,TimeStampMixin):
    __tablename__ = 'test_result_impact' 
    id = Column(BigInteger, primary_key=True,autoincrement=True)
    mill_id = Column(BigInteger, ForeignKey("mill.id"), nullable=False, )
    mill = relationship("Mill", backref="mill_TestResultImpact")    
    test_sample_id = Column(BigInteger, ForeignKey("test_sample.id"), nullable=False, )
    test_sample = relationship("TestSample", backref="test_result_impact_test_sample")
    retest_seq = Column(Integer, nullable=True)
    size_code = Column(String(1))
    orientation = Column(String(1))
    standard = Column(String)
    insp_code = Column(String)
    charpy_temp_c = Column(Numeric(20, 10))
    charpy_temp_f = Column(Numeric(20, 10))
    charpy_energy_1_j = Column(Numeric(20, 10))
    charpy_energy_2_j = Column(Numeric(20, 10))
    charpy_energy_3_j = Column(Numeric(20, 10))
    charpy_energy_average_j = Column(Numeric(20, 10))
    charpy_energy_1_f = Column(Numeric(20, 10))
    charpy_energy_2_f = Column(Numeric(20, 10))
    charpy_energy_3_f = Column(Numeric(20, 10))
    charpy_energy_average_f = Column(Numeric(20, 10))
    charpy_shear_1 = Column(Numeric(20, 10))
    charpy_shear_2 = Column(Numeric(20, 10))
    charpy_shear_3 = Column(Numeric(20, 10))
    charpy_shear_average = Column(Numeric(20, 10))
    charpy_temp_units = Column(String(1))
    charpy_i_units = Column(String(1))

    test_id = Column(BigInteger, ForeignKey('test.id'), nullable=False, unique=True)
    test = relationship("Test", backref="test_test_result_impact")
    # search_vector = Column(
    #     TSVectorType(
    #         "test_sample_id",
    #         weights={"test_sample_id": "A" },
    #     )
    # )



class TestResultImpactBase(BaseResponseModel):
    test_sample_id: Optional[int] = None
    test_sample: Optional[TestSampleRead] = None
    test_id: Optional[int] = None
    mill_id: Optional[int] = None
    mill: Optional[MillRead] = None
    retest_seq: Optional[int] = None
    size_code: Optional[str] = None
    orientation: Optional[str] = None
    charpy_temp_c: Optional[float] = None
    charpy_temp_f: Optional[float] = None
    charpy_energy_1_j: Optional[float] = None
    charpy_energy_2_j: Optional[float] = None
    charpy_energy_3_j: Optional[float] = None
    charpy_energy_average_j: Optional[float] = None
    charpy_energy_1_f: Optional[float] = None
    charpy_energy_2_f: Optional[float] = None
    charpy_energy_3_f: Optional[float] = None
    charpy_energy_average_f: Optional[float] = None
    charpy_shear_1: Optional[float] = None
    charpy_shear_2: Optional[float] = None
    charpy_shear_3: Optional[float] = None
    charpy_shear_average: Optional[float] = None
    charpy_temp_units: Optional[str] = None
    charpy_i_units: Optional[str] = None
    standard : Optional[str] = None
    insp_code : Optional[str] = None





class TestResultImpactBaseCreate(TestResultImpactBase):
    pass


class TestResultImpactBaseUpdate(TestResultImpactBase):
    pass


class TestResultImpactBaseRead(TestResultImpactBase,BaseResponseModel):
    id: int


class TestResultImpactBasePagination(DispatchBase):
    total: int
    items: List[TestResultImpactBaseRead] = []
    itemsPerPage: int
    page : int