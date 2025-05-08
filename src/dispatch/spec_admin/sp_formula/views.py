from fastapi import APIRouter, Depends

from dispatch.database_util.service import (
    common_parameters,
    search_filter_sort_paginate,
)
from .models import SpFormulaPagination

router = APIRouter()


@router.get("/", response_model=SpFormulaPagination)
def get_filters(*, common: dict = Depends(common_parameters)):
    if common["query_str"]:
        common["fields"] = ["formula_code"]
        common["ops"] = ["like"]
        common["values"] = [f"%{common['query_str']}%"]
        common["query_str"] = ""
    return search_filter_sort_paginate(model="SpFormula", **common)
