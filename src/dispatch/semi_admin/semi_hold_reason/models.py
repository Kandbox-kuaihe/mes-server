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
from dispatch.semi_admin.semi_hold_reason.models_secondary import semi_hold


class SemiHoldReason(Base, TimeStampMixin):
    __tablename__ = "semi_hold_reason"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    mill_id = Column(BigInteger, ForeignKey("mill.id"), nullable=False)
    mill = relationship("Mill", backref="mill_semi_hold_item")

    code = Column(String, nullable=False)
    type = Column(String, nullable=True)
    name = Column(String, nullable=False)
    desc = Column(String, nullable=True)
    
    comment = Column(String, nullable=True)
    
    semi = relationship("Semi", secondary=semi_hold, back_populates="semi_hold_reason")


    search_vector = Column(
        TSVectorType(
            "code",
            "name",
            weights={"code": "A", "name": "B"},
        )
    )

    __table_args__ = (
        UniqueConstraint('code', name='uix_semi_hold_reason_code'),
    )




class SemiHoldReasonBase(BaseResponseModel):
    mill_id: Optional[int] = None
    mill:Optional[MillRead] = None
    code: str = ""
    type: Optional[str] = ""
    name: Optional[str] = ""
    desc: Optional[str] = ""


class SemiHoldReasonCreate(SemiHoldReasonBase):
    pass


class SemiHoldReasonUpdate(SemiHoldReasonBase):
    pass


class SemiHoldReasonRead(SemiHoldReasonBase,BaseResponseModel):
    id: int
    comment: Optional[str] = None


class SemiHoldReasonPagination(DispatchBase):
    total: int
    items: List[SemiHoldReasonRead] = []
    itemsPerPage: int
    page: int
    

