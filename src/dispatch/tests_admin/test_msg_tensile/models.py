from typing import List, Optional
from datetime import datetime, date, time

from sqlalchemy import (
    Column,
    ForeignKey,
    BigInteger,
    Integer,
    String,
    Numeric,
    DateTime,
    Date,
    Time,
)
from sqlalchemy.orm import relationship
from dispatch.database import Base
from dispatch.models import TimeStampMixin, DispatchBase, BaseResponseModel


class TestMsgTensile(Base, TimeStampMixin):
    __tablename__ = 'test_msg_tensile'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    test_id = Column(BigInteger, ForeignKey("test.id"), nullable=False)
    test = relationship("Test")

    testing_machine = Column(String, nullable=False)
    testing_date = Column(Date, nullable=False)
    testing_time = Column(Time, nullable=False)
    test_code = Column(String, nullable=False)
    test_standard = Column(String, nullable=False)
    retest_seq = Column(Integer, nullable=False)
    check_digit = Column(String, default=0, nullable=False)
    test_number = Column(String, nullable=False)
    thickness = Column(Numeric(20, 10), nullable=False)
    width = Column(Numeric(20, 10), nullable=False)
    diameter = Column(Numeric(20, 10), nullable=False)
    inner_diameter = Column(Numeric(20, 10), nullable=False)
    area = Column(Numeric(20, 10), nullable=False)
    pl_length = Column(Numeric(20, 10), nullable=False)
    initial_gauge_length = Column(Numeric(20, 10), nullable=False)
    calculated_area = Column(Numeric(20, 10), nullable=False)
    uts_kn = Column(String, nullable=False)
    yield_a = Column(String, nullable=False)
    lower_yield = Column(String, nullable=False)
    rp1 = Column(String, nullable=False)
    rp2 = Column(String, nullable=False)
    rt5 = Column(String, nullable=False)
    final_gauge_length = Column(Numeric(20, 10), nullable=False)
    z = Column(Numeric(20, 10), nullable=False)
    elongation = Column(Numeric(20, 10), nullable=False)
    a565 = Column(String, nullable=False)
    uts_load = Column(String, nullable=False)
    yield_load = Column(String, nullable=False)
    lower_yield_load = Column(String, nullable=False)
    rp1_load = Column(String, nullable=False)
    rp2_load = Column(String, nullable=False)
    rt5_load = Column(String, nullable=False)
    prompt1 = Column(String, nullable=False)
    prompt2 = Column(String, nullable=False)
    prompt3 = Column(String, nullable=False)
    prompt4 = Column(String, nullable=False)
    prompt5 = Column(String, nullable=False)
    reply1 = Column(String, nullable=False)
    reply2 = Column(String, nullable=False)
    reply3 = Column(String, nullable=False)
    reply4 = Column(String, nullable=False)
    reply5 = Column(String, nullable=False)
    at = Column(Numeric(20, 10), nullable=False)
    ae = Column(Numeric(20, 10), nullable=False)
    ag = Column(Numeric(20, 10), nullable=False)
    agt = Column(Numeric(20, 10), nullable=False)
    weight = Column(Numeric(20, 10), nullable=False)
    length = Column(Numeric(20, 10), nullable=False)
    density = Column(Numeric(20, 10), nullable=False)
    initial_agt = Column(Numeric(20, 10), nullable=False)
    final_agt = Column(Numeric(20, 10), nullable=False)
    final_diameter = Column(Numeric(20, 10), nullable=False)
    e_rate = Column(Numeric(20, 10), nullable=False)
    p_rate1 = Column(Numeric(20, 10), nullable=False)
    p_rate2 = Column(Numeric(20, 10), nullable=False)
    p_rate3 = Column(Numeric(20, 10), nullable=False)
    status = Column(String, nullable=False)
    prompt6 = Column(String, nullable=False)
    reply6 = Column(String, nullable=False)
    config_file = Column(String, nullable=False)
    ra2 = Column(Numeric(20, 10))
    ra3 = Column(Numeric(20, 10))
    ra4 = Column(Numeric(20, 10))
    ra5 = Column(Numeric(20, 10))
    ra6 = Column(Numeric(20, 10))
    uts2 = Column(String)
    uts3 = Column(String)
    uts4 = Column(String)
    uts5 = Column(String)
    uts6 = Column(String)
    ys2 = Column(String)
    ys3 = Column(String)
    ys4 = Column(String)
    ys5 = Column(String)
    ys6 = Column(String)


class TestMsgTensileBase(BaseResponseModel):
    test_id: Optional[int] = None

    testing_machine: Optional[str] = None
    testing_date: Optional[date] = None
    testing_time: Optional[time] = None
    test_code: Optional[str] = None
    test_standard: Optional[str] = None
    retest_seq: Optional[int] = None
    check_digit: Optional[str] = None
    test_number: Optional[str] = None
    thickness: Optional[float] = None
    width: Optional[float] = None
    diameter: Optional[float] = None
    inner_diameter: Optional[float] = None
    area: Optional[float] = None
    pl_length: Optional[float] = None
    initial_gauge_length: Optional[float] = None
    calculated_area: Optional[float] = None
    uts_kn: Optional[str] = None
    yield_a: Optional[str] = None
    lower_yield: Optional[str] = None
    rp1: Optional[str] = None
    rp2: Optional[str] = None
    rt5: Optional[str] = None
    final_gauge_length: Optional[float] = None
    z: Optional[float] = None
    elongation: Optional[float] = None
    a565: Optional[str] = None
    uts_load: Optional[str] = None
    yield_load: Optional[str] = None
    lower_yield_load: Optional[str] = None
    rp1_load: Optional[str] = None
    rp2_load: Optional[str] = None
    rt5_load: Optional[str] = None
    prompt1: Optional[str] = None
    prompt2: Optional[str] = None
    prompt3: Optional[str] = None
    prompt4: Optional[str] = None
    prompt5: Optional[str] = None
    reply1: Optional[str] = None
    reply2: Optional[str] = None
    reply3: Optional[str] = None
    reply4: Optional[str] = None
    reply5: Optional[str] = None
    at: Optional[float] = None
    ae: Optional[float] = None
    ag: Optional[float] = None
    agt: Optional[float] = None
    weight: Optional[float] = None
    length: Optional[float] = None
    density: Optional[float] = None
    initial_agt: Optional[float] = None
    final_agt: Optional[float] = None
    final_diameter: Optional[float] = None
    e_rate: Optional[float] = None
    p_rate1: Optional[float] = None
    p_rate2: Optional[float] = None
    p_rate3: Optional[float] = None
    status: Optional[str] = None
    prompt6: Optional[str] = None
    reply6: Optional[str] = None
    config_file: Optional[str] = None
    ra2: Optional[float] = None
    ra3: Optional[float] = None
    ra4: Optional[float] = None
    ra5: Optional[float] = None
    ra6: Optional[float] = None
    uts2: Optional[str] = None
    uts3: Optional[str] = None
    uts4: Optional[str] = None
    uts5: Optional[str] = None
    uts6: Optional[str] = None
    ys2: Optional[str] = None
    ys3: Optional[str] = None
    ys4: Optional[str] = None
    ys5: Optional[str] = None
    ys6: Optional[str] = None


class TestMsgTensileCreate(TestMsgTensileBase):
    pass


class TestMsgTensileUpdate(TestMsgTensileBase):
    pass


class TestMsgTensileRead(TestMsgTensileBase):
    id: Optional[int] = None


class TestMsgTensilePagination(DispatchBase):
    total: int
    items: List[TestMsgTensileRead] = []
    itemsPerPage: int
    page: int
