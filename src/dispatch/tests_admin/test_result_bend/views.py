from dispatch.database import get_db
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from dispatch.system_admin.auth.models import DispatchUser
from dispatch.system_admin.auth.service import get_current_user

from dispatch.database_util.service import common_parameters, search_filter_sort_paginate
from .models import (
    TestResultBend,
    TestResultBendCreate,
    TestResultBendPagination,
    TestResultBendRead,
    TestResultBendUpdate,
)
from .service import create, delete, get, update

router = APIRouter()


@router.get("/", response_model=TestResultBendPagination)
def get_TestResultBends(*, common: dict = Depends(common_parameters)):

    return search_filter_sort_paginate(model="TestResultBend", **common)


@router.post("/", response_model=TestResultBendRead)
def create_TestResultBend(*, db_session: Session = Depends(get_db), TestResultBend_in: TestResultBendCreate,
                 current_user: DispatchUser = Depends(get_current_user)):
    """
    Create a new TestResultBend contact.
    """
    
    
    TestResultBend = create(db_session=db_session, test_result_tensile_in=TestResultBend_in)
    return TestResultBend


@router.get("/{TestResultBend_id}", response_model=TestResultBendRead)
def get_TestResultBend(*, db_session: Session = Depends(get_db), TestResultBend_id: int):
    """
    Get a TestResultBend contact.
    """
    TestResultBend = get(db_session=db_session, id=TestResultBend_id)
    if not TestResultBend:
        raise HTTPException(status_code=404, detail="The TestResultBend with this id does not exist.")
    return TestResultBend


@router.put("/{TestResultBend_id}", response_model=TestResultBendRead)
def update_TestResultBend(
    *,
    db_session: Session = Depends(get_db),
    TestResultBend_id: int,
    TestResultBend_in: TestResultBendUpdate, current_user: DispatchUser = Depends(get_current_user)
):
    """
    Update a TestResultBend contact.
    """
    TestResultBend = get(db_session=db_session, id=TestResultBend_id)
    if not TestResultBend:
        raise HTTPException(status_code=404, detail="The TestResultBend with this id does not exist.")

    TestResultBend = update(
        db_session=db_session,
        test_result_tensile=TestResultBend,
        test_result_tensile_in=TestResultBend_in,
    )
    return TestResultBend


 

@router.delete("/{TestResultBend_id}", response_model=TestResultBendRead)
def delete_TestResultBend(*, db_session: Session = Depends(get_db), TestResultBend_id: int):
    """
    Delete a TestResultBend contact.
    """
    TestResultBend = get(db_session=db_session, id=TestResultBend_id)
    if not TestResultBend:
        raise HTTPException(status_code=404, detail="The TestResultBend with this id does not exist.")

    return delete(db_session=db_session, id=TestResultBend_id)
