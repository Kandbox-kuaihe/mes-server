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



class Certificate(Base,TimeStampMixin):

    __tablename__ = 'certificate'  

    id = Column(BigInteger, primary_key=True,autoincrement=True)
    code = Column(String, nullable=False)
    status = Column(String, nullable=False)
    
    
    __table_args__ = (
        UniqueConstraint('code', name='unique_key_code_certificate'),
    )

class CertificateResponse(BaseResponseModel):
    code : Optional[str] = None
    status : Optional[str] = None
    

# Certificate Response
class CertificateCreate(CertificateResponse):
    pass

class CertificateUpdate(CertificateResponse):
    pass

class CertificateRead(CertificateResponse):
    id: int

class CertificatePagination(DispatchBase):
    total: int
    items: List[CertificateRead] = []
    itemsPerPage: int
    page: int