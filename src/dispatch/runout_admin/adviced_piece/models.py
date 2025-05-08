# from dispatch.database import Base
# from sqlalchemy import (
#     Column,
#     BigInteger,
#     String,
#     ForeignKey,
#     UniqueConstraint,
#     DateTime
# )
# from dispatch.models import DispatchBase, TimeStampMixin, BaseResponseModel
# from typing import Optional, List
# from sqlalchemy_utils import TSVectorType
# from sqlalchemy.orm import relationship
# from datetime import datetime
# from dispatch.runout_admin.finished_product.models import FinishedProductRead
# from dispatch.semi_admin.semi.models import SemiRead



# class AdvicedPiece(Base, TimeStampMixin):
#     __tablename__ = "adviced_piece"
#     id = Column(BigInteger, primary_key=True, autoincrement=True)

#     semi_id = Column(BigInteger, ForeignKey("semi.id"), nullable=True)
#     semi = relationship("Semi", backref="semi_advice_item")
#     finished_product_id = Column(BigInteger, ForeignKey("finished_product.id"), nullable=True)
#     finished_product = relationship("FinishedProduct", backref="finished_product_advice_item")
#     load_no = Column(String, nullable=True)
#     move_date = Column(DateTime, default=datetime.utcnow)
#     move_by = Column(String, nullable=True)


#     # search_vector = Column(
#     #     TSVectorType(
#     #         # "code",
#     #         # "name",
#     #         # weights={"code": "A", "name": "B"},
#     #     )
#     # )




# class AdvicedPieceBase(BaseResponseModel):
#     semi_id: Optional[int] = None
#     semi: Optional[SemiRead] = None
#     finished_product_id: Optional[int] = None
#     finished_product: Optional[FinishedProductRead] = None
#     load_no: Optional[str] = None
#     move_date: Optional[datetime] = None
#     move_by: Optional[str] = None


# class AdvicedPieceCreate(AdvicedPieceBase):
#     pass


# class AdvicedPieceUpdate(AdvicedPieceBase):
#     pass


# class AdvicedPieceRead(AdvicedPieceBase):
#     id: int


# class AdvicedPiecePagination(DispatchBase):
#     total: int
#     items: List[AdvicedPieceRead] = []
#     itemsPerPage: int
#     page: int
    

