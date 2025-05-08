from typing import Optional
from sqlalchemy import Column, BigInteger, String, ForeignKey
from sqlalchemy.orm import relationship
from dispatch.database import Base
from dispatch.models import TimeStampMixin, BaseResponseModel

class RailDispatchDetail(Base, TimeStampMixin):
    __tablename__ = 'rail_dispatch_detail'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    rail_dispatch_id = Column(BigInteger, ForeignKey('rail_dispatch.id', ondelete="CASCADE"), nullable=False)
    item_no = Column(String(50), nullable=False)
    length = Column(String(50), nullable=False)
    cast_no = Column(String(50), nullable=False)
    no_bars = Column(String(50), nullable=False)
    
    # Relationship back to RailDispatch
    rail_dispatch = relationship("RailDispatch", backref="rail_dispatch_details")

class RailDispatchDetailCreate(BaseResponseModel):
    rail_dispatch_id: int
    item_no: Optional[str] = None
    length: Optional[str] = None
    cast_no: Optional[str] = None
    no_bars: Optional[str] = None

class RailDispatchDetailUpdate(RailDispatchDetailCreate):
    pass

class RailDispatchDetailRead(RailDispatchDetailCreate, BaseResponseModel):
    id: int
