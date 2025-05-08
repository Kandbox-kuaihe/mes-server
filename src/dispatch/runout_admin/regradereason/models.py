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


class RegradeReason(Base, TimeStampMixin):
    __tablename__ = "regrade_reason"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    mill_id = Column(BigInteger, ForeignKey("mill.id"), nullable=False)
    mill = relationship("Mill", backref="mill_regrade_item")

    code = Column(String, nullable=False, unique=True)
    type = Column(String, nullable=True)
    desc = Column(String, nullable=True)
    supp_recalc = Column(String, nullable=True)
    search_vector = Column(
        TSVectorType(
            "code",
            "type",
            weights={"code": "A", "type": "B"},
        )
    )




class RegradereasonBase(BaseResponseModel):
    mill_id: Optional[int] = None
    mill:Optional[MillRead] = None
    code: str = ""
    type: Optional[str] = ""
    desc: Optional[str] = ""
    supp_recalc: Optional[str] = ""


class RegradereasonCreate(RegradereasonBase):
    pass


class RegradereasonUpdate(RegradereasonBase):
    pass


class RegradereasonRead(RegradereasonBase,BaseResponseModel):
    id: int


class RegradereasonPagination(DispatchBase):
    total: int
    items: List[RegradereasonRead] = []
    itemsPerPage: int
    page: int
    

