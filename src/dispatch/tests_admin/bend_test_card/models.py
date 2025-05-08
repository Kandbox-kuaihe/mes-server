from typing import List

from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, Session

from dispatch.database import Base
from dispatch.models import TimeStampMixin, DispatchBase,BaseResponseModel
from sqlalchemy import Column, String, BigInteger, ForeignKey, Integer
from typing import Optional
from dispatch.cast.models import CastRead
from dispatch.spec_admin.spbend.models import Spbend

from dispatch.tests_admin.test_sample.models import TestSampleRead


class TestBend(Base,TimeStampMixin):
    __tablename__ = 'test_bend'
    id = Column(BigInteger, primary_key=True,autoincrement=True)
    
    test_id = Column(BigInteger, ForeignKey("test.id"), nullable=False, )
    test = relationship("Test", backref="bend_test", viewonly=True)
    code = Column(String, nullable=True)
    test_sample_id = Column(BigInteger, ForeignKey("test_sample.id"), nullable=True,)
    test_sample = relationship("TestSample", backref="test_sample_bend_test_card")
    test_standard = Column(BigInteger)
    cast_id = Column(BigInteger, ForeignKey("cast.id"), nullable=True, )
    cast = relationship("Cast", backref="cast_bend_test_card")
    heat_treated_by = Column(String)
    tested_by = Column(String)

    check_digit_1 = Column(Integer, nullable=True)
    check_digit_2 = Column(Integer, nullable=True)
    check_digit_3 = Column(Integer, nullable=True)

    result_1 = Column(String)
    result_2 = Column(String)

    @hybrid_property
    def diameter_mm(self):
        if self.test and self.test.spec and self.test.product_type:
            flange_thickness = self.test.product_type.flange_thickness
            spec_id = self.test.spec_id
            spbend = (
                Session.object_session(self)
                .query(Spbend)
                .filter(
                    Spbend.spec_id == spec_id,
                    Spbend.thick_from <= flange_thickness,
                    Spbend.thick_to > flange_thickness
                )
                .first()
            )
            if spbend:
                return spbend.diameter_mm
        return None

class TestBendBase(BaseResponseModel):

    test_id: Optional[int] = None
    code: Optional[str] = None
    test_sample_id: Optional[int] = None
    test_sample: Optional[TestSampleRead] = None
    test_standard: Optional[int] = None
    cast_id: Optional[int] = None
    cast: Optional[CastRead] = None
    heat_treated_by: Optional[str] = None
    tested_by: Optional[str] = None
    result_1: Optional[str] = None
    result_2: Optional[str] = None

    check_digit_1: Optional[int] = None
    check_digit_2: Optional[int] = None
    check_digit_3: Optional[int] = None



class TestBendCreate(TestBendBase):
    pass


class TestBendUpdate(TestBendBase):
    id: Optional[int] = None
    check_digit_1_1: Optional[int] = None
    check_digit_2_2: Optional[int] = None
    check_digit_3_3: Optional[int] = None


class TestSampleRead(DispatchBase):
    id: int
    test_sample_code: Optional[str] = None
    test_sample_part: Optional[str] = None


class TestRead(DispatchBase):
    id: Optional[int] = None
    test_sample: Optional[TestSampleRead] = None


class TestBendRead(TestBendBase,BaseResponseModel):
    id: int
    test: Optional[TestRead] = None
    diameter_mm: Optional[float] = None


class TestBendPagination(DispatchBase):
    total: int
    items: List[TestBendRead] = []
    itemsPerPage: int
    page : int