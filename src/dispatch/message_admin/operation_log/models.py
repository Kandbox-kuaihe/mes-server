from typing import List, Optional
from datetime import datetime
from sqlalchemy import Column, Integer, String, JSON,BigInteger
from sqlalchemy_utils import TSVectorType

from dispatch.database import Base
from dispatch.models import (
    DispatchBase,
    TimeStampMixin
) 


class OperationLog(Base,TimeStampMixin):
    '''
    system operation log model 
    '''
    id = Column(BigInteger, primary_key=True,autoincrement=True)
    request_modular = Column(String,  nullable=True)
    request_path = Column(String,  nullable=True)
    request_body = Column(String,  nullable=True)
    request_method = Column(String,  nullable=True)
    request_msg = Column(String,  nullable=True)
    request_ip = Column(String,  nullable=True)
    response_code = Column(String,  nullable=True)
    response_json_result = Column(JSON, default={})
    response_status = Column(String,  nullable=True)
 


    # search_vector = Column(
    #     TSVectorType(
    #         "request_modular",
    #         "request_path",
    #         "request_body",
    #         "request_method",
    #         "request_ip",
    #         "response_code",
    #         "response_status"
    #     )
    # )

# Pydantic models...


class OperationLogBase(DispatchBase): 

    id: Optional[str] = None
    request_modular: str = None
    request_path: str = None
    request_body: str = None
    request_method: str = None
    request_msg: str = None
    request_ip: str = None
    response_code: str = None
    response_json_result: dict = None
    response_status: str = None
 


class OperationLogCreate(OperationLogBase):

    updated_by: str = None


class OperationLogUpdate(OperationLogBase):

    updated_by: str = None

class OperationLogRead(OperationLogBase):

    id: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    updated_by: str  

class OperationLogPagination(DispatchBase):
    total: int
    items: List[OperationLogRead] = []
 