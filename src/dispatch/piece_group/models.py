from typing import List, Optional
from datetime import datetime, date

from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    BigInteger,
    Numeric,
    String,
    Date,
    DateTime,
)
from sqlalchemy.orm import relationship

from sqlalchemy.sql.schema import UniqueConstraint
from sqlalchemy_utils import TSVectorType

from dispatch.database import Base
from dispatch.models import TimeStampMixin, DispatchBase, BaseResponseModel

from dispatch.mill.models import MillRead

class PieceGroup(Base,TimeStampMixin):
    __tablename__ = 'piece_group'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    code = Column(String, nullable=False)
    sawn_date = Column(DateTime)
    
    mill_id = Column(BigInteger, ForeignKey("mill.id"))
    mill = relationship("Mill", backref="mill_piece_group")

    product_type_id = Column(BigInteger, ForeignKey("product_type.id"))
    product_type = relationship("ProductType", backref="product_type_piece_group")

    rolling_id = Column(BigInteger, ForeignKey("rolling.id"))
    rolling = relationship("Rolling", backref="rolling_piece_group")

    search_vector = Column(
        TSVectorType(
            "code",
            weights={"code": "A"},
        )
    )


class PieceGroupBase(BaseResponseModel):
    code: Optional[str] = None
    sawn_date: Optional[datetime] = None
    mill_id: Optional[int] = None
    rolling_id: Optional[int] = None
    product_type_id: Optional[int] = None



class PieceGroupCreate(PieceGroupBase):
    pass


class PieceGroupUpdate(PieceGroupBase):
    pass


class PieceGroupRead(PieceGroupBase):
    id: int

class PieceGroupPagination(DispatchBase):
    total: int
    items: List[PieceGroupRead] = []
    itemsPerPage: int
    page : int