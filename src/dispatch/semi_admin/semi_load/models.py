from typing import List, Optional
from datetime import datetime
from sqlalchemy import (
    Column,
    ForeignKey,
    String,
    BigInteger,
    Integer,
    DateTime
)
from typing import  Optional
from sqlalchemy.orm import relationship

from sqlalchemy.sql.schema import UniqueConstraint
from sqlalchemy_utils import TSVectorType

from dispatch.area.models import AreaRead
from dispatch.site.models import SiteRead
from dispatch.database import Base
from dispatch.mill.models import MillRead
from dispatch.models import TimeStampMixin, DispatchBase,BaseResponseModel

from sqlalchemy import Column, Integer, String, BigInteger, ForeignKey, Numeric

from dispatch.site.models import SiteRead
 

class SemiLoad(Base,TimeStampMixin):
    __tablename__ = 'semi_load'

    id = Column(BigInteger, primary_key=True,autoincrement=True)
     
    destination_site_id = Column(BigInteger, ForeignKey("site.id"), nullable=True, )
    site_id = Column(BigInteger, ForeignKey("site.id"), nullable=True, )
    site = relationship("Site", backref="site_semi_load", foreign_keys=[site_id]) 
    mill_id = Column(BigInteger, ForeignKey("mill.id"), nullable=False, )
    mill = relationship("Mill", backref="mill_SemiLoad")
    semi_load_code = Column(String, nullable=False)
    vehicle_code = Column(String, nullable=True)
    vehicle_type = Column(String, nullable=True)
    consignment_code = Column(String, nullable=True)
    dispatch_date =  Column(DateTime, nullable=True)
    stock_in_date =  Column(DateTime, nullable=True) 

    location = Column(String, nullable=True, default="Default Location")
    semi_count = Column(BigInteger)
    total_weight_ton = Column(Numeric(20, 10))
    supplier_code = Column(String, nullable=False)
    status = Column(String)

    to_area_id = Column(BigInteger, ForeignKey("area.id"), nullable=True)
    area = relationship("Area", backref="area_semi_load")

    comment = Column(String)

    order_number = Column(String, nullable=True)
    line_item_number = Column(String, nullable=True)

    search_vector = Column(
        TSVectorType(
            "semi_load_code",
            "vehicle_code",
            "consignment_code",
            weights={"semi_load_code": "A", "vehicle_code": "B", "consignment_code": "C"},
        )
    )

    __table_args__ = (
        UniqueConstraint('semi_load_code', name='unique_key_semi_load_code'),
    )



class SemiLoadBase(BaseResponseModel):
      
    site_id: Optional[int] = None
    site: Optional[SiteRead] = None 
    mill_id: Optional[int] = None
    mill: Optional[MillRead] = None
    semi_load_code: Optional[str] = None
    vehicle_code:  Optional[str] = None
    vehicle_type:  Optional[str] = None
    consignment_code: Optional[str] = None
    dispatch_date:  Optional[datetime] = None
    stock_in_date:  Optional[datetime] = None 

    semi_count: Optional[int] = None
    total_weight_ton: Optional[float] = None
    supplier_code: Optional[str] = None
    status: Optional[str] = None
    location: Optional[str] = None

    to_area_id: Optional[int] = None
    comment: Optional[str] = None
    order_number: Optional[str] = None
    line_item_number: Optional[str] = None

    
class SemiLoadCreate(SemiLoadBase):
    semi_ids: Optional[List[int]] = None

class SemiLoadUpdate(SemiLoadBase):
    semi_ids: Optional[List[int]] = None


class SemiLoadRead(SemiLoadBase,BaseResponseModel):
    id: int
    area: Optional[AreaRead] = None
    site: Optional[SiteRead] = None


class SemiLoadPagination(DispatchBase):
    total: int
    items: List[SemiLoadRead] = []
    itemsPerPage: int
    page : int

class SemiLoadReceiving(DispatchBase):
    ids: List[int] = []
    is_overwrite: Optional[bool] = False

class SemiLoadTip(DispatchBase):
    ids: List[int] = []
    to_area_id: int
    comment: Optional[str] = None
    is_overwrite: Optional[bool] = False

class SemiLoadDespatch(DispatchBase):
    ids: List[int] = []
    is_overwrite: Optional[bool] = False
