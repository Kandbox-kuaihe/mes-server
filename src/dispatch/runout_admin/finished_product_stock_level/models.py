from dispatch.models import DispatchBase, BaseResponseModel
from typing import List, Optional


class StockLevelBase(BaseResponseModel):
    area_code: Optional[str] = None
    site_code: Optional[str] = None
    quantity: Optional[int] = None
    weight: Optional[float] = None
    bartype: Optional[str] = None
    good_blms: Optional[int] = None
    defect_blms: Optional[int] = None
    source: Optional[str] = None
    no_of_finished_product: Optional[int] = None
    length_mm: Optional[float] = None
    weight_per_bloom: Optional[float] = None

class StockLevelRead(StockLevelBase, BaseResponseModel):
    id: Optional[int] = None


class StockLevelPagination(DispatchBase):
    total: int
    items: List[StockLevelRead] = []
    itemsPerPage: int
    page: int
