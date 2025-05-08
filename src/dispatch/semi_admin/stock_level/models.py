from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from dispatch.database import Base
from datetime import datetime
from dispatch.models import DispatchBase, BaseResponseModel
from typing import List, Optional
from dispatch.site.models import SiteRead
from dispatch.area.models import AreaRead
from pydantic import BaseModel


class StockLevelBase(BaseResponseModel):
    area_code: Optional[str] = None
    site_code: Optional[str] = None
    quantity: Optional[int] = None
    weight: Optional[float] = None
    bartype: Optional[str] = None
    good_blms: Optional[int] = None
    defect_blms: Optional[int] = None
    source: Optional[str] = None
    cast_code: Optional[str] = None
    quality_code: Optional[str] = None
    semi_size: Optional[str] = None
    weight_per_bloom: Optional[float] = None
    length_mm: Optional[float] = None


class StockLevelRead(StockLevelBase, BaseResponseModel):
    id: Optional[int] = None


class StockLevelPagination(DispatchBase):
    total: int
    items: List[StockLevelRead] = []
    itemsPerPage: int
    page: int
