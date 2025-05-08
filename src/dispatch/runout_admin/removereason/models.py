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


class RemoveReason(Base, TimeStampMixin):
    __tablename__ = "remove_reason"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    mill_id = Column(BigInteger, ForeignKey("mill.id"), nullable=False)
    mill = relationship("Mill", backref="mill_remove_item")

    code = Column(String, nullable=False)
    type = Column(String, nullable=True)
    name = Column(String, nullable=False)
    desc = Column(String, nullable=True)
    
    comment = Column(String, nullable=True)
    


    search_vector = Column(
        TSVectorType(
            "code",
            "name",
            weights={"code": "A", "name": "B"},
        )
    )

    __table_args__ = (
        UniqueConstraint('code', name='uix_remove_reason_code'),
    )




class RemoveReasonBase(BaseResponseModel):
    mill_id: Optional[int] = None
    mill:Optional[MillRead] = None
    code: str = ""
    type: Optional[str] = ""
    name: Optional[str] = ""
    desc: Optional[str] = ""


class RemoveReasonCreate(RemoveReasonBase):
    pass


class RemoveReasonUpdate(RemoveReasonBase):
    pass


class RemoveReasonRead(RemoveReasonBase,BaseResponseModel):
    id: int
    comment: Optional[str] = None


class RemoveReasonPagination(DispatchBase):
    total: int
    items: List[RemoveReasonRead] = []
    itemsPerPage: int
    page: int
    

