from datetime import datetime
from typing import List, Optional

from sqlalchemy import BigInteger, Column, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import UniqueConstraint
from sqlalchemy_utils import TSVectorType

from dispatch.database import Base
from dispatch.mill.models import MillRead
from dispatch.models import DispatchBase, TimeStampMixin, BaseResponseModel


class Shift(Base, TimeStampMixin):
    __tablename__ = 'shift'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    code = Column(String, nullable=True)
    name = Column(String, nullable=True)
    desc = Column(String, nullable=True)
    track_code = Column(String, nullable=True)
    defective_weight = Column(String, nullable=True)
    defect_quantity = Column(String, nullable=True)
    shift_week = Column(String, nullable=True)
    product_type_code = Column(String, nullable=True) 

    shift_day = Column(String, nullable=True)
    shift_no = Column(String, nullable=True)
    shift_start = Column(String, nullable=True)
    shift_end = Column(String, nullable=True)
    shift_month = Column(String, nullable=True)
    shift_year = Column(String, nullable=True)
    weight1 = Column(Float, nullable=True)
    weight2 = Column(Float, nullable=True)
    record_type = Column(String, nullable=True)
    record_date = Column(String, nullable=True)
    total_weight_semi_discharge = Column(String, nullable=True)
    total_weight_semi_send_mill = Column(String, nullable=True)
    total_weight_cobbies_hot_rejection = Column(String, nullable=True)
    total_weight_semi_part_rolled = Column(String, nullable=True)
    gross_roll_minutes = Column(String, nullable=True)
    cast_supplier_code = Column(String, nullable=True)
    no_of_summarys = Column(String, nullable=True)
    shift_manager = Column(String, nullable=True)
    roller_code = Column(String, nullable=True)
    controller_code = Column(String, nullable=True)
 
    mill_id = Column(BigInteger, ForeignKey("mill.id"), nullable=False, )
    mill = relationship("Mill", backref="mill_Shift")

    search_vector = Column(
        TSVectorType(
            "code",
            "name",
            weights={"code": "A", "name": "B"},
        )
    )

    __table_args__ = (UniqueConstraint('code', 'id', name='uix_id_Shift_code'),)


class ShiftBase(BaseResponseModel):
    """Base Pydantic model for Shift operations"""
    code: Optional[str] = None
    name: Optional[str] = None
    desc: Optional[str] = None
    track_code: Optional[str] = None
    defective_weight: Optional[str] = None
    defect_quantity: Optional[str] = None
    product_type_code: Optional[str] = None

    shift_day: Optional[str] = None
    shift_no: Optional[str] = None
    shift_start: Optional[str] = None
    shift_end: Optional[str] = None
    shift_month: Optional[str] = None
    shift_week :  Optional[str] = None
    shift_year: Optional[str] = None
    weight1: Optional[float] = None
    weight2: Optional[float] = None
    record_type: Optional[str] = None
    record_date: Optional[str] = None
    total_weight_semi_discharge: Optional[str] = None
    total_weight_semi_send_mill: Optional[str] = None
    total_weight_cobbies_hot_rejection: Optional[str] = None
    total_weight_semi_part_rolled: Optional[str] = None
    gross_roll_minutes: Optional[str] = None
    cast_supplier_code: Optional[str] = None
    no_of_summarys: Optional[str] = None
    shift_manager: Optional[str] = None
    roller_code: Optional[str] = None
    controller_code: Optional[str] = None
    mill_id: Optional[int] = None


class ShiftCreate(ShiftBase):
    pass


class ShiftUpdate(ShiftBase):
    pass


class ShiftRead(ShiftBase, BaseResponseModel):
    id: int
    mill: Optional[MillRead] = None



class ShiftPagination(DispatchBase):
    total: int
    items: List[ShiftRead] = []
    itemsPerPage: int
    page: int
