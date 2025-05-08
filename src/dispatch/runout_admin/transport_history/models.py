import uuid
from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import Field
from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Index, Date
)
from sqlalchemy.orm import relationship

from dispatch.database import Base
from dispatch.mill.models import MillRead
from dispatch.models import BaseResponseModel, DispatchBase, TimeStampMixin
from dispatch.runout_admin.transport.models import TransportRead


class TransportHistory(Base, TimeStampMixin):
    __tablename__ = "transport_history"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    transport_id = Column(Integer, ForeignKey("transport.id"), nullable=False)
    transport = relationship("Transport", backref="transport_transport_history")
    status = Column(String)
    action = Column(String, nullable=False)
    mill_id = Column(Integer, ForeignKey("mill.id"), nullable=False)
    mill = relationship("Mill", backref="mill_transport_history")
    week_number = Column(String, nullable=True)


class TransportHistoryBase(BaseResponseModel):
    transport_id: Optional[int] = None
    status: Optional[str] = None
    action: Optional[str] = None
    mill_id: Optional[int] = None
    week_number: Optional[int] = None


class TransportHistoryCreate(TransportHistoryBase):
    pass


class TransportHistoryRead(TransportHistoryBase):
    id: int
    transport: Optional[TransportRead] = None
    status: Optional[str] = None
    action: Optional[str] = None
    mill: Optional[MillRead] = None



class TransportHistoryPagination(DispatchBase):
    total: int
    items: List[TransportHistoryRead] = Field(default_factory=list)


class TransportHistoryActionEnum(str, Enum):
    """
    Enum for transport history action
    """

    CREATE = "create"
    DELOAD = "deload"
    ONLOAD = "onload"
    DELETE = "delete"
    EDIT = "edit"
