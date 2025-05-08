from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from dispatch.semi_admin.semi_move_history.models import SemiMoveHistory, SemiMoveHistoryPagination
from dispatch.database_util.service import common_parameters, search_filter_sort_paginate
from dispatch.database import get_db
from dispatch.semi_admin.semi_move_history.service import bulk_get_area_code, search_semi_code, block_time_max
from datetime import datetime

router = APIRouter()


@router.get("/", response_model=SemiMoveHistoryPagination)
def get_semi_history(*,db_session: Session = Depends(get_db), common: dict = Depends(common_parameters),
    start_date:str, end_date:str, change_type:str = Query(None)):

    query = db_session.query(SemiMoveHistory).filter(SemiMoveHistory.created_at >= start_date).filter(SemiMoveHistory.created_at <= end_date)
    if change_type:
        query = query.filter(SemiMoveHistory.change_type == change_type)
    common["query"] = query

    if common['query_str']:
        q = common['query_str']
        common["filter_type"]  = "or"
        semi_ids = search_semi_code(db_session=common["db_session"], semi_code=q)
        common["fields"] = ["semi_id", "uuid"]
        common["ops"] = ["in", "like"]
        common["values"] = [semi_ids ,f'%{q}%', f'%{q}%']
        common['query_str'] = ''
    return search_filter_sort_paginate(model="SemiMoveHistory", **common)


@router.post("/get_code")
def add_code_in_semi_history(request_data: dict, db_session=Depends(get_db)):
    items = request_data["items"]
    print(request_data)
    area_ids = []
    for i in items:
        dic = {"from_area_id": i["from_area_id"], "to_area_id": i["to_area_id"]}
        area_ids.append(dic)
    result = bulk_get_area_code(db_session=db_session, ids=area_ids)
    for idx, item in enumerate(request_data["items"]):
        if idx < len(result):
            item.update(result[idx])  # 添加 from_area_code 和 to_area_code
    return request_data

@router.get("/max_time")
def max_time(db_session=Depends(get_db)):
    block_time = None
    formatted_date = None
    if block_time_max(db_session):
        block_time = block_time_max(db_session).created_at
        date_obj = datetime.fromisoformat(str(block_time))
        formatted_date = date_obj.strftime("%Y-%m-%d %H:%M:%S")
    return {"data": formatted_date}