from typing import List, Optional
from datetime import datetime
from sqlalchemy import Column, Integer, String, JSON, BigInteger
from sqlalchemy_utils import TSVectorType

from dispatch.database import Base
from dispatch.mill.models import MillRead
from dispatch.models import DispatchBase, TimeStampMixin
from sqlalchemy import  ForeignKey
from sqlalchemy.orm import relationship

class MessageLog(Base, TimeStampMixin):
    """
    system message log model
    """

    __tablename__ = "message_log"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    message_id = Column(Integer, nullable=True, index=True)
    msg = Column(String, nullable=True)  # 消息主体
    message_json = Column(String, nullable=True)
    message_status = Column(String, nullable=True)  # 发送状态
    type = Column(String, nullable=True)
    interact = Column(String, nullable=True)  # "MES to FECC"/"FECC to MES"
    interact_from = Column(String, nullable=True)  # 发送方
    interact_to = Column(String, nullable=True)  # 接收方
    msg_type = Column(Integer, nullable=True)  # 0 - sending, 1 - receiving
    mill_id = Column(BigInteger, ForeignKey("mill.id"), nullable=True)
    mill = relationship("Mill", backref="mill_MessageLog")
    repeat_flag = Column(Integer, nullable=True, default=0, comment="first: 0, repeat: 1")
    # search_vector = Column(
    #     TSVectorType(
    #         "message_status",
    #         "type",
    #         "msg",
    #         "interact",
    #     )
    # )


# Pydantic models...


class MessageLogBase(DispatchBase):
    id: Optional[int] = None
    message_id: Optional[int] = None
    type: Optional[str] = None
    message_json: Optional[str] = None
    message_status: Optional[str] = None
    msg: Optional[str] = None
    interact: Optional[str] = None
    interact_from: Optional[str] = None
    interact_to: Optional[str] = None
    msg_type: Optional[int] = None
    mill_id: Optional[int] = None
    mill: Optional[MillRead] = None
    repeat_flag: Optional[int] = None

class MessageLogCreate(MessageLogBase):
    updated_by: str = "MES"
    created_by: str = "MES"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class MessageLogUpdate(MessageLogBase):
    updated_by: str = None


class MessagetionLogRead(MessageLogBase):
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    updated_by: str
    created_by: str


class MessageLogPagination(DispatchBase):
    total: int
    items: List[MessagetionLogRead] = []
    itemsPerPage: int
    page: int