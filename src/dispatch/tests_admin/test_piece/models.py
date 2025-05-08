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
from dispatch.runout_admin.finished_product.models import FinishedProductRead
from dispatch.tests_admin.impact_test_card.models import TestSampleRead


class TestPiece(Base, TimeStampMixin):
    __tablename__ = 'test_piece'

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    # rolling_id = Column(BigInteger, ForeignKey("rolling.id"), nullable=False)
    # rolling = relationship("Rolling")

    cast_id = Column(BigInteger, ForeignKey("cast.id"), nullable=False)
    cast = relationship("Cast")

    trans_code = Column(String, nullable=False)
    bun_identity = Column(String, nullable=False)
    bundle_date = Column(String, nullable=False)

    operation = Column(String, nullable=False)
    occurrence = Column(String, nullable=False)
    test_number = Column(String, nullable=False)
    test_date = Column(String)
    orphan_batch = Column(String)
    orphan_date = Column(String)
    sec_test_number = Column(String)
    sec_test_date = Column(String)
    cast_number = Column(String, nullable=False)
    bars_covered = Column(String, nullable=False)
    bars_weight = Column(String, nullable=False)
    test_type = Column(String, nullable=False)
    finished_id = Column(BigInteger, ForeignKey("finished_product.id"), nullable=True)
    finished = relationship("FinishedProduct")
    test_sample_id = Column(BigInteger, ForeignKey("test_sample.id"), nullable=True)
    test_sample = relationship("TestSample")


class TestPieceBase(BaseResponseModel):
    rolling_id: int
    cast_id: int

    trans_code: str
    bun_identity: str
    bundle_date: str

    operation: str
    occurrence: str
    test_number: str
    test_date: Optional[str] = None
    orphan_batch: Optional[str] = None
    orphan_date: Optional[str] = None
    ass_test_number: Optional[str] = None
    ass_test_date: Optional[str] = None
    cast_number: str
    bars_covered: str
    bars_weight: str
    test_type: str
    finished_id: Optional[int] = None
    finished: Optional[FinishedProductRead] = None
    test_sample_id: Optional[int] = None
    test_sample: Optional[TestSampleRead] = None


class TestPieceCreate(TestPieceBase):
    pass


class TestPieceUpdate(TestPieceBase):
    pass


class TestPieceRead(TestPieceBase):
    id: int


class TestPiecePagination(DispatchBase):
    total: int
    items: List[TestPieceRead] = []
    itemsPerPage: int
    page: int
