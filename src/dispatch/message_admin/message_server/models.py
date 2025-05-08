from typing import Any, List, Optional
from datetime import datetime
from sqlalchemy import Column, Integer, String, JSON
from sqlalchemy_utils import TSVectorType
from pydantic import BaseModel, Field

from dispatch.database import Base
from dispatch.models import (
    DispatchBase,
    TimeStampMixin
) 

 
 

class PushMessageData(DispatchBase):

    id: int = Field( default=None, title="id", description='Message ID, for example M11o')
    type: str = Field( default="", title="type", description='type of system. In TBM, it is PC=ProcessControl, LIMS, or SAP')
    msg: str = Field( default="", title="msg", description='The message content')

class PushMessageSemiData(DispatchBase):

    id: int = Field( default=None, title="id", description='Message ID, for example M11o')
    type: str = Field( default="", title="type", description='type of system. In TBM, it is PC=ProcessControl, LIMS, or SAP')
    data: dict[Any, Any] = Field( default="", title="data", description='The data content')

class PushMessage7xxxData(DispatchBase):
    data: dict[Any, Any] = Field( default="", title="data", description='The data content')


class MessageData(BaseModel):
    id: int = Field(default=None, title="id", description='Message ID, for example M11o')
    type: str = Field(default="", title="type", description='type of system. In TBM, it is PC=ProcessControl, LIMS, or SAP')
    msg: str = Field(default="", title="msg", description='The message content')
    need_send: bool = Field(default=False, title="need_send", description='Whether the message needs to be sent')

class PushMessageDataRead(DispatchBase):

    status: str  
    process: List[Any] = []


class PushMessage7xxxDataRead(DispatchBase):
    status: int
    detail: str