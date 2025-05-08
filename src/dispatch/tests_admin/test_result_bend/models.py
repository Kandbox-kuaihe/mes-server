from typing import List, Optional

from sqlalchemy import (
    Column,
    ForeignKey,
    String,
    BigInteger
)

from typing import  Optional


from dispatch.database import Base
from dispatch.models import TimeStampMixin, DispatchBase,BaseResponseModel

from sqlalchemy import Column, String, BigInteger, Numeric, ForeignKey
from sqlalchemy import Column, Integer, String, ForeignKey

# (Base,TimeStampMixin):

from typing import Optional
from sqlalchemy.orm import relationship

from dispatch.tests_admin.test_sample.models import TestSampleRead


class TestResultBend(Base,TimeStampMixin):
    __tablename__ = 'test_result_bend' 

    id = Column(BigInteger, primary_key=True,autoincrement=True)
    # 定义表中的各个字段
    test_id = Column(BigInteger, ForeignKey('test.id'), nullable=False)
    test = relationship("Test", backref="test_test_result_bend")
    
    code = Column(String, nullable=False)
    test_sample_id = Column(BigInteger, ForeignKey("test_sample.id"), nullable=False)
    test_sample = relationship("TestSample", backref="test_result_bend_test_sample")


    test_standard = Column(Integer)
    check_digit_0 = Column(Integer)
    check_digit_1 = Column(Integer)
    # cast_id = Column(Integer, ForeignKey('cast.id'))
    # cast_code = Column(String)
    heat_treated_by = Column(String)
    tested_by = Column(String)
    result_1 = Column(String)
    result_2 = Column(String)
    
    
    cast_id = Column(BigInteger, ForeignKey("cast.id"), nullable=False)
    cast = relationship("Cast", backref="test_result_bend_cast")
        
    
    
  

class TestResultBendBase(BaseResponseModel):

    code: Optional[str] = None
    test_sample_id: Optional[int] = None
    test_standard: Optional[int] = None
    check_digit_0: Optional[int] = None
    check_digit_1: Optional[int] = None
    heat_treated_by: Optional[str] = None
    tested_by: Optional[str] = None
    result_1: Optional[str] = None
    result_2: Optional[str] = None
    cast_id: Optional[int] = None





class TestResultBendCreate(TestResultBendBase):
    pass


class TestResultBendUpdate(TestResultBendBase):
    pass


class TestResultBendRead(TestResultBendBase,BaseResponseModel):
    id: int


class TestResultBendPagination(DispatchBase):
    total: int
    items: List[TestResultBendRead] = []
    itemsPerPage: int
    page : int