from typing import List, Optional

from sqlalchemy import (
    Column,
    ForeignKey,
    BigInteger,
    Integer
)

from typing import  Optional


from sqlalchemy.orm import relationship
from dispatch.database import Base
from dispatch.mill.models import MillRead
from dispatch.models import TimeStampMixin, DispatchBase,BaseResponseModel

from sqlalchemy import Column, Integer, BigInteger, Numeric, ForeignKey

from dispatch.tests_admin.test_sample.models import TestSampleRead




class TestResultChemical(Base,TimeStampMixin):
    __tablename__ = 'test_result_chemical'
    id = Column(BigInteger, primary_key=True,autoincrement=True)
    mill_id = Column(BigInteger, ForeignKey("mill.id"), nullable=False, )
    mill = relationship("Mill", backref="mill_TestResultChemical")    
    test_sample_id = Column(BigInteger, ForeignKey("test_sample.id"), nullable=False, )
    test_sample = relationship("TestSample", backref="test_result_chemical_test_sample")

    #, ForeignKey('mill.id')
    # mill_id = Column(Integer, comment="TBM = ‘B’, Skinningrove = ‘S’")
    result_c = Column(Numeric(20, 10))
    result_si = Column(Numeric(20, 10))
    result_mn = Column(Numeric(20, 10))
    result_p = Column(Numeric(20, 10))
    result_s = Column(Numeric(20, 10))
    result_cr = Column(Numeric(20, 10))
    result_mo = Column(Numeric(20, 10))
    result_ni = Column(Numeric(20, 10))
    result_al = Column(Numeric(20, 10))
    result_b = Column(Numeric(20, 10))
    result_co = Column(Numeric(20, 10))
    result_cu = Column(Numeric(20, 10))
    result_nb = Column(Numeric(20, 10))
    result_sn = Column(Numeric(20, 10))
    result_ti = Column(Numeric(20, 10))
    result_v = Column(Numeric(20, 10))
    result_ca = Column(Numeric(20, 10))
    result_n2 = Column(Numeric(20, 10))
    result_o = Column(Numeric(20, 10))
    result_h = Column(Numeric(20, 10))
    result_sal = Column(Numeric(20, 10))
    result_as = Column(Numeric(20, 10))
    result_bi = Column(Numeric(20, 10))
    result_ce = Column(Numeric(20, 10))
    result_pb = Column(Numeric(20, 10))
    result_sb = Column(Numeric(20, 10))
    result_w = Column(Numeric(20, 10))
    result_zn = Column(Numeric(20, 10))
    result_zr = Column(Numeric(20, 10))
    test_id = Column(BigInteger, ForeignKey('test.id'), nullable=False)
    test = relationship("Test", backref="test_test_result_chemical")

    # search_vector = Column(
    #     TSVectorType(
    #         "test_sample_id",
    #         "mill_id",
    #         weights={"test_sample_id": "A", "mill_id": "B" },
    #     )
    # )  

class TestResultChemicalBase(BaseResponseModel):

    test_sample_id: Optional[int] = None
    test_sample: Optional[TestSampleRead] = None
    mill_id: Optional[int] = None
    mill: Optional[MillRead] = None
    result_c: Optional[float] = None
    result_si: Optional[float] = None
    result_mn: Optional[float] = None
    result_p: Optional[float] = None
    result_s: Optional[float] = None
    result_cr: Optional[float] = None
    result_mo: Optional[float] = None
    result_ni: Optional[float] = None
    result_al: Optional[float] = None
    result_b: Optional[float] = None
    result_co: Optional[float] = None
    result_cu: Optional[float] = None
    result_nb: Optional[float] = None
    result_sn: Optional[float] = None
    result_ti: Optional[float] = None
    result_v: Optional[float] = None
    result_ca: Optional[float] = None
    result_n2: Optional[float] = None
    result_o: Optional[float] = None
    result_h: Optional[float] = None
    result_sal: Optional[float] = None
    result_as: Optional[float] = None
    result_bi: Optional[float] = None
    result_ce: Optional[float] = None
    result_pb: Optional[float] = None
    result_sb: Optional[float] = None
    result_w: Optional[float] = None
    result_zn: Optional[float] = None
    result_zr: Optional[float] = None





 
    


class TestResultChemicalCreate(TestResultChemicalBase):
    pass


class TestResultChemicalUpdate(TestResultChemicalBase):
    pass


class TestResultChemicalRead(TestResultChemicalBase,BaseResponseModel):
    id: int
    test_sample: Optional[TestSampleRead]


class TestResultChemicalPagination(DispatchBase):
    total: int
    items: List[TestResultChemicalRead] = []
    itemsPerPage: int
    page : int