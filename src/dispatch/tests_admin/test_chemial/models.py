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

from sqlalchemy import Column, Integer, BigInteger, Numeric, ForeignKey,String

from dispatch.tests_admin.test_sample.models import TestSampleRead




class TestChemial(Base,TimeStampMixin):
    __tablename__ = 'test_chemial'
    id = Column(BigInteger, primary_key=True,autoincrement=True)
    cast_id = Column(BigInteger, ForeignKey("cast.id"), nullable=False, )
    test_type = Column(String, nullable=False)

    ch_c = Column(Numeric(20, 10))
    ch_si = Column(Numeric(20, 10))
    ch_mn = Column(Numeric(20, 10))
    ch_p = Column(Numeric(20, 10))
    ch_s = Column(Numeric(20, 10))
    ch_cr = Column(Numeric(20, 10))
    ch_mo = Column(Numeric(20, 10))
    ch_ni = Column(Numeric(20, 10))
    ch_al = Column(Numeric(20, 10))
    ch_b = Column(Numeric(20, 10))
    ch_co = Column(Numeric(20, 10))
    ch_cu = Column(Numeric(20, 10))
    ch_nb = Column(Numeric(20, 10))
    ch_sn = Column(Numeric(20, 10))
    ch_ti = Column(Numeric(20, 10))
    ch_v = Column(Numeric(20, 10))
    ch_ca = Column(Numeric(20, 10))
    ch_n = Column(Numeric(20, 10))
    ch_o = Column(Numeric(20, 10))
    ch_h = Column(Numeric(20, 10))
    ch_solal = Column(Numeric(20, 10))
    ch_as = Column(Numeric(20, 10))
    ch_bi = Column(Numeric(20, 10))
    ch_ce = Column(Numeric(20, 10))
    ch_pb = Column(Numeric(20, 10))
    ch_sb = Column(Numeric(20, 10))
    ch_w = Column(Numeric(20, 10))
    ch_zn = Column(Numeric(20, 10))
    ch_zr = Column(Numeric(20, 10))
    ch_s_p = Column(Numeric(20, 10))
    ch_te = Column(Numeric(20, 10))
    ch_rad = Column(Numeric(20, 10))

    test_sample_id = Column(BigInteger)
    
    # search_vector = Column(
    #     TSVectorType(
    #         "test_sample_id",
    #         "mill_id",
    #         weights={"test_sample_id": "A", "mill_id": "B" },
    #     )
    # )  

class TestChemialBase(BaseResponseModel):
    cast_id: Optional[int] = None
    test_type: Optional[str] = None

    ch_c: Optional[float] = None
    ch_si: Optional[float] = None
    ch_mn: Optional[float] = None
    ch_p: Optional[float] = None
    ch_s: Optional[float] = None
    ch_cr: Optional[float] = None
    ch_mo: Optional[float] = None
    ch_ni: Optional[float] = None
    ch_al: Optional[float] = None
    ch_b: Optional[float] = None
    ch_co: Optional[float] = None
    ch_cu: Optional[float] = None
    ch_nb: Optional[float] = None
    ch_sn: Optional[float] = None
    ch_ti: Optional[float] = None
    ch_v: Optional[float] = None
    ch_ca: Optional[float] = None
    ch_n: Optional[float] = None
    ch_o: Optional[float] = None
    ch_h: Optional[float] = None
    ch_solal: Optional[float] = None
    ch_as: Optional[float] = None
    ch_bi: Optional[float] = None
    ch_ce: Optional[float] = None
    ch_pb: Optional[float] = None
    ch_sb: Optional[float] = None
    ch_w: Optional[float] = None
    ch_zn: Optional[float] = None
    ch_zr: Optional[float] = None
    ch_s_p: Optional[float] = None
    ch_te: Optional[float] = None
    ch_rad: Optional[float] = None
    
    test_sample_id: Optional[int] = None

class TestChemialCreate(TestChemialBase):
    pass


class TestChemialUpdate(TestChemialBase):
    id: Optional[int] = None



class TestChemialRead(TestChemialBase,BaseResponseModel):
    id: Optional[int] = None


class TestChemialPagination(DispatchBase):
    total: int
    items: List[TestChemialRead] = []
    itemsPerPage: int
    page : int