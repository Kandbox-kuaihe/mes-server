from dispatch.database import get_db
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from dispatch.system_admin.auth.models import DispatchUser
from dispatch.system_admin.auth.service import get_current_user

from dispatch.database_util.service import common_parameters, search_filter_sort_paginate
from .models import (
    TestHistory,
    TestHistoryPagination,
    TestHistoryRead
)
from .service import confirm_history
# from .service import create, delete, get, get_by_code, update, update_new, get_by_spec_code, create_by_copy_spec_code
from datetime import datetime, timezone

router = APIRouter()


@router.get("/", response_model=TestHistoryPagination)
def get_test_history(*, db_session: Session = Depends(get_db), common: dict = Depends(common_parameters), start_date:str = Query(None), end_date:str = Query(None), ):

    if start_date and end_date:
        query = db_session.query(TestHistory).filter(TestHistory.created_at >= start_date, TestHistory.created_at <= end_date)
    else:
        query = db_session.query(TestHistory)
    common["query"] = query
    q = common["query_str"]
    if q:
        common["filter_type"]  = "or"
        common["fields"] = ["uuid", "section_size_code"]
        common["ops"] = ["like"] * len(common["fields"])
        common["values"] = [f'%{q}%'] * len(common["fields"])
        common['query_str'] = ''

    return search_filter_sort_paginate(model="TestHistory", **common)


@router.put("/confirm/{test_history_id}", response_model=TestHistoryRead)
def confirm_test_history(*, db_session: Session = Depends(get_db), test_history_id: int, current_user: DispatchUser = Depends(get_current_user)):
    """Confirm TestHistory"""
    test_history = db_session.query(TestHistory).filter(TestHistory.id == test_history_id).first()
    if not test_history:
        raise HTTPException(status_code=404, detail="TestHistory not found")
    test_history = confirm_history(db_session=db_session, history_in=test_history, current_user=current_user)
    return test_history