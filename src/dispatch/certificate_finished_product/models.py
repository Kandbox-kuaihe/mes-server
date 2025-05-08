from typing import List, Optional
from pydantic import  Field

from sqlalchemy import (
    Column,
    Float,
    ForeignKey,
    String,
    BigInteger,
    Integer,
)
from datetime import datetime
from typing import Dict, Optional

from sqlalchemy.sql.schema import UniqueConstraint
from sqlalchemy_utils import TSVectorType

from dispatch.database import Base
from dispatch.models import TimeStampMixin, DispatchBase,BaseResponseModel

from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, BigInteger, Numeric, ForeignKey
from sqlalchemy import Column, Integer, CHAR, Text
from pydantic import BaseModel, Field, conint
from typing import Optional, List

from dispatch.spec_admin.spec.models import SpecRead


# (Base,TimeStampMixin):



class CertificateFinishedProduct(Base,TimeStampMixin):

    __tablename__ = 'certificate_finished_product'  

    id = Column(BigInteger, primary_key=True,autoincrement=True)
    
    
    
    certificate_id = Column(Integer, ForeignKey("certificate.id"), nullable=False)
    certificate = relationship("certificate", foreign_keys=[certificate_id])

    finished_product_id = Column(Integer, ForeignKey("finished_product.id"), nullable=False)
    certificate = relationship("FinishedProduct", foreign_keys=[finished_product_id])
    
    

    __table_args__ = (
        UniqueConstraint('certificate_id','finished_product_id', name='unique_key_code_certificate_finished_product'),
    )

class CertificateFinishedProductResponse(BaseResponseModel):
    code : Optional[str] = None
    status : Optional[str] = None
    

# CertificateFinishedProduct Response
class CertificateFinishedProductCreate(CertificateFinishedProductResponse):
    pass

class CertificateFinishedProductUpdate(CertificateFinishedProductResponse):
    pass

class CertificateFinishedProductRead(CertificateFinishedProductResponse):
    id: int

class CertificateFinishedProductPagination(DispatchBase):
    total: int
    items: List[CertificateFinishedProductRead] = []
    itemsPerPage: int
    page: int