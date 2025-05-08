from typing import List
from sqlalchemy import Column, BigInteger, String, Date, Time
from sqlalchemy.orm import relationship
from dispatch.database import Base
from dispatch.models import TimeStampMixin, DispatchBase, BaseResponseModel
from sqlalchemy_utils import TSVectorType

class RailDispatch(Base, TimeStampMixin):
    __tablename__ = 'rail_dispatch'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False)
    time = Column(Time, nullable=False)
    last_track_no = Column(String(50), nullable=True)
    works_order = Column(String(50), nullable=False)
    no_entries = Column(String(50), nullable=False)
    
    # Relationship with RailDispatchDetail
    #rail_dispatch_details = relationship("RailDispatchDetail", backref="rail_dispatch", cascade="all, delete-orphan")
    search_vector = Column(
        TSVectorType(
            "last_track_no",
            "works_order",
            weights={"last_track_no":"A","works_order":"B"}
        )
    )

class RailDispatchBase(BaseResponseModel):
    date: str
    time: str
    last_track_no: str
    works_order: str
    no_entries: str

class RailDispatchCreate(RailDispatchBase):
    pass

class RailDispatchUpdate(RailDispatchBase):
    pass

class RailDispatchRead(RailDispatchBase, BaseResponseModel):
    id: int

class RailDispatchPagination(DispatchBase):
    total: int
    items: List[RailDispatchRead] = []
    itemsPerPage: int
    page: int
