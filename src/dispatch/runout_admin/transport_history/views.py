import logging

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from dispatch.database import get_db
from dispatch.database_util.service import (
    common_parameters,
    search_filter_sort_paginate,
)
from .models import (
    TransportHistoryPagination, TransportHistory,
)

router = APIRouter()

logging.basicConfig(level=logging.INFO)
from dispatch.log import getLogger
log = getLogger(__name__)


# @router.get("/", response_model=FinishedProductHistoryPagination)
# def get_finished_product_history(
#     *, db_session: Session = Depends(get_db), common: dict = Depends(common_parameters),
#     start_date:str, end_date:str, change_type:str = Query(None)
# ):
#
#     query = db_session.query(FinishedProductHistory).filter(FinishedProductHistory.created_at >= start_date).filter(FinishedProductHistory.created_at <= end_date)
#     if change_type:
#         query = query.filter(FinishedProductHistory.change_type == change_type)
#     common["query"] = query
#
#     q = common["query_str"]
#     if q:
#         common["filter_type"]  = "or"
#         common["fields"] = ["uuid", "code", "area_code", "cast_no", "spec_code", "product_type", "order_num", "order_item_num", "runout_code", "rolling_code"]
#         common["ops"] = ["like"] * len(common["fields"])
#         common["values"] = [f'%{q}%'] * len(common["fields"])
#         common['query_str'] = ''
#     finished_product = search_filter_sort_paginate(
#         model="FinishedProductHistory", **common
#     )
#     return finished_product


@router.get('/', response_model=TransportHistoryPagination)
def get_transport_history(
        *,
        db_session: Session = Depends(get_db),
        common: dict = Depends(common_parameters)
):
    if common["query_str"]:
        common["fields"].append("transport.code")
        common["ops"].append("like")
        common["values"].append(f'%{common["query_str"]}%')
    return search_filter_sort_paginate(model="TransportHistory", **common)