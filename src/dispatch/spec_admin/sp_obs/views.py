from fastapi import APIRouter, Depends

from dispatch.database_util.service import (
    common_parameters,
    search_filter_sort_paginate,
)
from .models import SpObsPagination

router = APIRouter()


@router.get("/", response_model=SpObsPagination)
def get_filters(*, common: dict = Depends(common_parameters), spec_id: int = None):
    if spec_id:
        common["fields"] = ["spec_id"]
        common["ops"] = ["=="]
        common["values"] = [spec_id]
        common["query_str"] = ""
    return search_filter_sort_paginate(model="SpObs", **common)
