from datetime import datetime
from typing import List, Optional

from sqlalchemy import BigInteger, Column, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import UniqueConstraint
from sqlalchemy_utils import TSVectorType

from dispatch.database import Base
from dispatch.mill.models import MillRead
from dispatch.models import DispatchBase, TimeStampMixin, BaseResponseModel
from dispatch.shiftAdmin.shift.models import ShiftRead
from dispatch.rolling.rolling_list.models import RollingRead


class ShiftDelay(Base, TimeStampMixin):
    __tablename__ = 'shift_delay'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    delay_no = Column(String, nullable=False) 
    delay_code = Column(String, nullable=False) 
    delay_start = Column(String, nullable=True) 
    delay_end = Column(String, nullable=True) 
    delay_cause = Column(String, nullable=True) 
    product_type_code = Column(String, nullable=True) 
    
    delay_duration = Column(Float, nullable=True)  

    other_source_total_discharge_weight = Column(Float, nullable=True) 
    total_slit_discharge_weight = Column(Float, nullable=True) 
    caster4_discharge_weight = Column(Float, nullable=True) 
    caster5_discharge_weight = Column(Float, nullable=True) 
    no_of_delay_record_send = Column(String, nullable=True) 
    area_code = Column(String, nullable=True) 
 
    shift_id = Column(BigInteger, ForeignKey("shift.id"), nullable=False)
    shift = relationship("Shift", backref="shift_Shift_delay")
    mill_id = Column(BigInteger, ForeignKey("mill.id"), nullable=False)
    mill = relationship("Mill", backref="mill_Shift_delay")
    rolling_id = Column(BigInteger, ForeignKey('rolling.id'), nullable=True)
    rolling = relationship("Rolling", backref="rolling_shift_delay")

    search_vector = Column(
        TSVectorType(
            "delay_no",
            "delay_code",
            weights={"delay_no": "A", "delay_code": "B"},
        )
    )

    __table_args__ = (UniqueConstraint('delay_no', 'id', name='uix_id_delay_no'), )


class ShiftDelayBase(DispatchBase):
    """Base Pydantic model for Shift operations"""
    delay_no: Optional[str] = None
    delay_code: Optional[str] = None
    delay_start: Optional[str] = None
    delay_end: Optional[str] = None
    delay_cause: Optional[str] = None
    product_type_code: Optional[str] = None
    delay_duration: Optional[float] = None 
    other_source_total_discharge_weight: Optional[float] = None
    total_slit_discharge_weight: Optional[float] = None
    caster4_discharge_weight: Optional[float] = None
    caster5_discharge_weight: Optional[float] = None
    no_of_delay_record_send: Optional[str] = None
    area_code: Optional[str] = None
    shift_id: Optional[int] = None
    shift: Optional[ShiftRead] = None
    mill_id: Optional[int] = None
    mill: Optional[MillRead] = None

class ShiftDelayCreate(ShiftDelayBase):
    pass


class ShiftDelayUpdate(ShiftDelayBase):
    pass


class ShiftDelayRead(ShiftDelayBase, BaseResponseModel):
    id: int
    rolling: Optional[RollingRead] = None
    flex_form_data: Optional[dict]


class ShiftDelayPagination(DispatchBase):
    total: int
    items: List[ShiftDelayRead] = []
    itemsPerPage: int
    page: int
