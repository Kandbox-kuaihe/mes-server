from pydantic import root_validator
from dispatch.database import Base
from sqlalchemy import (
    Column,
    BigInteger,
    String,
    ForeignKey,
    UniqueConstraint,
)
from dispatch.models import DispatchBase, TimeStampMixin, BaseResponseModel
from typing import Optional, List
from sqlalchemy_utils import TSVectorType
from sqlalchemy.orm import relationship
from dispatch.mill.models import MillRead
from dispatch.runout_admin.holdreason.models_secondary import finished_product_hold


class HoldReason(Base, TimeStampMixin):
    __tablename__ = "hold_reason"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    mill_id = Column(BigInteger, ForeignKey("mill.id"), nullable=False)
    mill = relationship("Mill", backref="mill_hold_item")

    code = Column(String, nullable=False)
    type = Column(String, nullable=True)
    name = Column(String, nullable=True)
    desc = Column(String, nullable=True)
    
    comment = Column(String, nullable=True)
    finished_product = relationship("FinishedProduct", secondary=finished_product_hold, back_populates="hold_reason")


    search_vector = Column(
        TSVectorType(
            "code",
            "name",
            weights={"code": "A", "name": "B"},
        )
    )

    __table_args__ = (
        UniqueConstraint('mill_id','code', name='unique_hold_reason_code'),
    )




class HoldreasonBase(BaseResponseModel):
    mill_id: Optional[int] = None
    mill:Optional[MillRead] = None
    code: str = ""
    type: Optional[str] = ""
    name: Optional[str] = ""
    desc: Optional[str] = ""


class HoldreasonCreate(HoldreasonBase):
    pass


class HoldreasonUpdate(HoldreasonBase):
    pass


class HoldreasonRead(HoldreasonBase,BaseResponseModel):
    id: int
    comment: Optional[str] = None


class HoldreasonPagination(DispatchBase):
    total: int
    items: List[HoldreasonRead] = []
    itemsPerPage: int
    page: int
    

