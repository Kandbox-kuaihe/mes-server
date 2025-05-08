from datetime import datetime
from typing import List

from typing import Optional

from dispatch.cast.models import CastRead
from dispatch.database import Base
from dispatch.mill.models import MillRead
from dispatch.models import TimeStampMixin, DispatchBase, BaseResponseModel

from sqlalchemy import Column, String, BigInteger, Numeric, ForeignKey, Date, DateTime
from sqlalchemy.orm import relationship


class TestJob(Base, TimeStampMixin):
    __tablename__ = 'test_job'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    mill_id = Column(BigInteger, ForeignKey("mill.id"), nullable=False)
    mill = relationship("Mill", backref="mill_test_job")

    code = Column(String, nullable=True)
    investigator = Column(String, nullable=True)
    state = Column(String, nullable=True)
    cast = Column(String, nullable=True)
    customer = Column(String, nullable=True)
    initiated_date = Column(DateTime, nullable=True)
    completed_date = Column(DateTime, nullable=True)
    quality = Column(String, nullable=True)
    grade = Column(String, nullable=True)
    size = Column(String, nullable=True)
    investigation = Column(String, nullable=True)
    job_category = Column(String, nullable=True)
    product = Column(String, nullable=True)


class TestJobBase(BaseResponseModel):
    mill_id: Optional[int] = None
    code: Optional[str] = None
    investigator: Optional[str] = None
    state: Optional[str] = None
    cast: Optional[str] = None
    customer: Optional[str] = None
    initiated_date: Optional[datetime] = None
    completed_date: Optional[datetime] = None
    quality: Optional[str] = None
    grade: Optional[str] = None
    size: Optional[str] = None
    investigation: Optional[str] = None
    job_category: Optional[str] = None
    product: Optional[str] = None


class TestJobCreate(TestJobBase):
    pass


class TestJobUpdate(TestJobBase):
    id: Optional[int] = None


class TestJobRead(TestJobBase, BaseResponseModel):
    id: int
    mill: Optional[MillRead] = None


class TestJobPagination(DispatchBase):
    total: int
    items: List[TestJobRead] = []
    itemsPerPage: int
    page: int