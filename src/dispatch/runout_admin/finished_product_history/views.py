import logging

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from dispatch.database import get_db
from dispatch.database_util.service import (
    common_parameters,
    search_filter_sort_paginate,
)
from .models import (
    FinishedProductHistoryPagination, FinishedProductHistory,
)

router = APIRouter()

logging.basicConfig(level=logging.INFO)
from dispatch.log import getLogger
log = getLogger(__name__)


@router.get("/", response_model=FinishedProductHistoryPagination)
def get_finished_product_history(
    *, db_session: Session = Depends(get_db), common: dict = Depends(common_parameters),
    start_date:str, end_date:str, 
    change_type:list[str] = Query([], alias="change_type[]"),
    show_totla_fields:bool = Query(False),
    from_allocation_status:list[str] = Query([], alias="from_allocation_status[]"),
    to_allocation_status:list[str] = Query([], alias="to_allocation_status[]")
):

    query = db_session.query(FinishedProductHistory).filter(FinishedProductHistory.created_at >= start_date).filter(FinishedProductHistory.created_at <= end_date)
    if change_type:
        query = query.filter(FinishedProductHistory.change_type.in_(change_type))

    if from_allocation_status:
        query = query.filter(FinishedProductHistory.from_allocation_status.in_(from_allocation_status))
    if to_allocation_status:
        query = query.filter(FinishedProductHistory.allocation_status.in_(to_allocation_status))
    common["query"] = query

    q = common["query_str"]

    if q:
        common["filter_type"]  = "or"
        common["fields"] = ["uuid", "code", "area_code", "cast_no", "spec_code", "product_type", "order_num", "order_item_num", "runout_code", "rolling_code"]
        common["ops"] = ["like"] * len(common["fields"])
        common["values"] = [f'%{q}%'] * len(common["fields"])
        common['query_str'] = ''
    finished_product = search_filter_sort_paginate(
        model="FinishedProductHistory", **common
    )

    if show_totla_fields:
        common["items_per_page"] = None
        finished_product_total = search_filter_sort_paginate(
            model="FinishedProductHistory", **common
        )

        if len(finished_product_total["items"]) > 0:
            finished_product["total_weight"] = sum([item.estimated_weight_kg if item.estimated_weight_kg else 0 for item in finished_product_total["items"]])
            finished_product["total_bars"] = sum([item.quantity if item.quantity else 0 for item in finished_product_total["items"]])

    return finished_product