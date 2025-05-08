from typing import List

from typing import  Optional

from dispatch.database import Base
from dispatch.mill.models import MillRead
from dispatch.models import TimeStampMixin, DispatchBase,BaseResponseModel

from sqlalchemy import Column, Integer, String, BigInteger, Numeric, ForeignKey
from sqlalchemy.orm import relationship




class TestMicrostructure(Base,TimeStampMixin):
    __tablename__ = 'test_microstructure'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    mill_id = Column(BigInteger, ForeignKey("mill.id"), nullable=False, )
    mill = relationship("Mill", backref="mill_test_microstructure")
    check_digit = Column(Integer, nullable=True)
    trans_code = Column(String, nullable=True)
    status = Column(String, nullable=False)
    test_standard = Column(Integer, nullable=False)
    testing_machine = Column(String, nullable=True)
    test_id = Column(BigInteger, ForeignKey("test.id"), nullable=False, )

    ustructure_pass_fail = Column(String, nullable=True)
    code = Column(String, nullable=True)


class TestMicrostructureBase(BaseResponseModel):
    mill_id: Optional[int] = None
    check_digit: Optional[int] = None
    trans_code: Optional[str] = None
    status: Optional[str] = None
    test_standard: Optional[int] = None
    testing_machine: Optional[str] = None
    test_id: Optional[int] = None
    ustructure_pass_fail: Optional[str] = None
    code: Optional[str] = None



class TestMicrostructureCreate(TestMicrostructureBase):
    pass


class TestMicrostructureRead(TestMicrostructureBase, BaseResponseModel):
    id: int
 