from typing import List, Optional

from sqlalchemy import (
    Column,
    ForeignKey,
    BigInteger,
    Integer,
    String,
    Numeric
)
from sqlalchemy.orm import relationship
from dispatch.database import Base
from dispatch.models import TimeStampMixin, DispatchBase, BaseResponseModel


class TestMsgImpact(Base, TimeStampMixin):
    __tablename__ = 'test_msg_impact'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    test_id = Column(BigInteger, ForeignKey("test.id"), nullable=False)
    retest_seq = Column(Integer, default=0, nullable=False)
    check_digit = Column(Integer, nullable=True)
    trans_code = Column(String, nullable=True)
    testing_machine = Column(String, nullable=True)
    set_name = Column(String, nullable=True)
    machine_setting = Column(String, nullable=True)
    result_1 = Column(Numeric(20, 10), nullable=True)
    result_2 = Column(Numeric(20, 10), nullable=True)
    result_3 = Column(Numeric(20, 10), nullable=True)
    test = relationship("Test", foreign_keys=[test_id])


class TestMsgImpactBase(BaseResponseModel):
    test_id: Optional[int] = None
    retest_seq: Optional[int] = None
    check_digit: Optional[int] = None
    trans_code: Optional[str] = None
    testing_machine: Optional[str] = None
    set_name: Optional[str] = None
    machine_setting: Optional[str] = None
    result_1: Optional[float] = None
    result_2: Optional[float] = None
    result_3: Optional[float] = None


class TestMsgImpactCreate(TestMsgImpactBase):
    pass


class TestMsgImpactUpdate(TestMsgImpactBase):
    pass


class TestMsgImpactRead(TestMsgImpactBase, BaseResponseModel):
    id: Optional[int] = None


class TestMsgImpactPagination(DispatchBase):
    total: int
    items: List[TestMsgImpactRead] = []
    itemsPerPage: int
    page: int
