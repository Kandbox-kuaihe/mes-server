from typing import List

from typing import  Optional

from dispatch.cast.models import CastRead
from dispatch.database import Base
from dispatch.mill.models import MillRead
from dispatch.models import TimeStampMixin, DispatchBase,BaseResponseModel

from sqlalchemy import Column, String, BigInteger, Numeric, ForeignKey
from sqlalchemy.orm import relationship




class TestJominy(Base,TimeStampMixin):
    __tablename__ = 'test_jominy'
    
    id = Column(BigInteger, primary_key=True,autoincrement=True)
    mill_id = Column(BigInteger, ForeignKey("mill.id"), nullable=False)
    mill = relationship("Mill", backref="mill_test_jominy")
    cast_id = Column(BigInteger, ForeignKey("cast.id"), nullable=False)
    cast = relationship("Cast", backref="cast_test_jominy")

    s_dst = Column(Numeric(20, 10), nullable=True)
    type = Column(String, nullable=False)
    j_1 = Column(Numeric(20, 10), nullable=True)
    j_1_5 = Column(Numeric(20, 10), nullable=True)
    j_2 = Column(Numeric(20, 10), nullable=True)
    j_3 = Column(Numeric(20, 10), nullable=True)
    j_4 = Column(Numeric(20, 10), nullable=True)
    j_5 = Column(Numeric(20, 10), nullable=True)
    j_6 = Column(Numeric(20, 10), nullable=True)
    j_7 = Column(Numeric(20, 10), nullable=True)
    j_8 = Column(Numeric(20, 10), nullable=True)
    j_9 = Column(Numeric(20, 10), nullable=True)
    j_10 = Column(Numeric(20, 10), nullable=True)
    j_11 = Column(Numeric(20, 10), nullable=True)
    j_12 = Column(Numeric(20, 10), nullable=True)
    j_13 = Column(Numeric(20, 10), nullable=True)
    j_14 = Column(Numeric(20, 10), nullable=True)
    j_15 = Column(Numeric(20, 10), nullable=True)
    j_16 = Column(Numeric(20, 10), nullable=True)
    j_18 = Column(Numeric(20, 10), nullable=True)
    j_20 = Column(Numeric(20, 10), nullable=True)
    j_22 = Column(Numeric(20, 10), nullable=True)
    j_24 = Column(Numeric(20, 10), nullable=True)
    j_25 = Column(Numeric(20, 10), nullable=True)
    j_28 = Column(Numeric(20, 10), nullable=True)
    j_30 = Column(Numeric(20, 10), nullable=True)
    j_32 = Column(Numeric(20, 10), nullable=True)
    j_35 = Column(Numeric(20, 10), nullable=True)
    j_40 = Column(Numeric(20, 10), nullable=True)
    j_45 = Column(Numeric(20, 10), nullable=True)
    j_50 = Column(Numeric(20, 10), nullable=True)


class TestJominyBase(BaseResponseModel):
    mill_id: Optional[int] = None
    cast_id: Optional[int] = None
    s_dst: Optional[float] = None
    type: Optional[str] = None
    j_1: Optional[float] = None
    j_1_5: Optional[float] = None
    j_2: Optional[float] = None
    j_3: Optional[float] = None
    j_4: Optional[float] = None
    j_5: Optional[float] = None
    j_6: Optional[float] = None
    j_7: Optional[float] = None
    j_8: Optional[float] = None
    j_9: Optional[float] = None
    j_10: Optional[float] = None
    j_11: Optional[float] = None
    j_12: Optional[float] = None
    j_13: Optional[float] = None
    j_14: Optional[float] = None
    j_15: Optional[float] = None
    j_16: Optional[float] = None
    j_18: Optional[float] = None
    j_20: Optional[float] = None
    j_22: Optional[float] = None
    j_24: Optional[float] = None
    j_25: Optional[float] = None
    j_28: Optional[float] = None
    j_30: Optional[float] = None
    j_32: Optional[float] = None
    j_35: Optional[float] = None
    j_40: Optional[float] = None
    j_45: Optional[float] = None
    j_50: Optional[float] = None



class TestJominyCreate(TestJominyBase):
    pass


class TestJominyUpdate(TestJominyBase):
    id: Optional[int] = None


class TestJominyRead(TestJominyBase,BaseResponseModel):
    id: int
    mill: Optional[MillRead] = None
    cast: Optional[CastRead] = None



class TestJominyPagination(DispatchBase):
    total: int
    items: List[TestJominyRead] = []
    itemsPerPage: int
    page : int