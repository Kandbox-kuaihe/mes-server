from typing import Optional
from sqlalchemy import (
    Column,
    String,
    BigInteger,
    Integer,
)


from dispatch.database import Base
from dispatch.models import DispatchBase, TimeStampMixin, BaseResponseModel
from sqlalchemy import Column, Integer, String, BigInteger
from sqlalchemy import Column, Integer


class SpFormula(Base, TimeStampMixin):

    __tablename__ = "sp_formula"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    display_seq = Column(Integer, nullable=False)
    nr_formula = Column(Integer, nullable=False)
    formula_code = Column(String, nullable=False)
    cd_unid_medida = Column(String, nullable=False)
    tx_formula = Column(String, nullable=False)
    tx_observeacao = Column(String, nullable=False)


class SpFormulaRead(BaseResponseModel):
    id: Optional[int] = None
    display_seq: Optional[int] = None
    nr_formula: Optional[int] = None
    formula_code: Optional[str] = None
    cd_unid_medida: Optional[str] = None
    tx_formula: Optional[str] = None
    tx_observeacao: Optional[str] = None


class SpFormulaPagination(DispatchBase):
    total: int
    items: list[SpFormulaRead] = []
    itemsPerPage: int
    page: int
