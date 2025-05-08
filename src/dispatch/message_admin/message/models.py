from typing import List, Optional
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
    type: Optional[str] = Field( default="", title="type", description='type of system. In TBM, it is PC=ProcessControl, LIMS, or SAP')
    msg: Optional[str] = Field( default="", title="msg", description='The message content')
    tast_simple_id: Optional[int] = Field( default="", title="msg", description='The message content')
    interact: Optional[str] = Field( default="", title="interact", description='MES to FECC"/"FECC to MES')

class PushMessageDataRead(DispatchBase):

    status: str = Field( default="OK", title="status", description='OK or Error')
    msg: str = Field( default="", title="msg", description='The return msg')




class PushSemiMessageData(DispatchBase):

    wagon_no: str = Field( default=None, title="wagon_no", description='Wagon No ')
    consignment_code: str = Field( default="", title="consigi", description=' ')
    destination_site_code: str = Field( default="", title="destin", description=' ')
    dispatch_date: str = Field( default=None, title="dispatch_date", description=' ')

    cast_no: str = Field( default="", title="cast_no", description=' ')
    slabid: str = Field( default="", title="slabid", description=' ')
    slabnum: str = Field( default="", title="slabnum", description=' ')
    piece_no: str = Field( default="", title="piece_no", description=' ')
    piece_id: str = Field( default="", title="piece_id", description=' ')
    product_type: str = Field( default="", title="production", description=' ')
    quality_code: str = Field( default="", title="qualty", description=' ')
    thickness_mm: str = Field( default="", title="thickness_mm", description=' ')
    width_mm: int = Field( default=0, title="width_mm", description=' ')
    section: str = Field( default="", title="section", description=' ')
    length_mm: int = Field( default=0, title="length_mm", description=' ')
    estimated_weight_kg: int = Field( default=0, title="estimat", description=' ')
    scarfed_status: str = Field( default="", title="scarfed_status", description=' ')


class RequestSemiMessageData(DispatchBase):

    semi_data: List[PushSemiMessageData]  