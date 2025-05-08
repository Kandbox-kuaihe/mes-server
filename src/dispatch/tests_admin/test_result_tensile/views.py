from dispatch.database import get_db
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from dispatch.system_admin.auth.models import DispatchUser
from dispatch.system_admin.auth.service import get_current_user

from dispatch.database_util.service import common_parameters, search_filter_sort_paginate
from .models import (
    TestResultTensile,
    TestResultTensileCreate,
    TestResultTensilePagination,
    TestResultTensileRead,
    TestResultTensileUpdate,
)
from .service import create, delete, get, update

router = APIRouter()


@router.get("/", response_model=TestResultTensilePagination)
def get_testResultTensiles(*, common: dict = Depends(common_parameters)):

    return search_filter_sort_paginate(model="TestResultTensile", **common)


@router.post("/", response_model=TestResultTensileRead)
def create_testResultTensile(*, db_session: Session = Depends(get_db), testResultTensile_in: TestResultTensileCreate,
                 current_user: DispatchUser = Depends(get_current_user)):
    """
    Create a new testResultTensile contact.
    """
    
    
    testResultTensile = create(db_session=db_session, test_result_tensile_in=testResultTensile_in)
    return testResultTensile


@router.get("/{testResultTensile_id}", response_model=TestResultTensileRead)
def get_testResultTensile(*, db_session: Session = Depends(get_db), testResultTensile_id: int):
    """
    Get a testResultTensile contact.
    """
    testResultTensile = get(db_session=db_session, id=testResultTensile_id)
    if not testResultTensile:
        raise HTTPException(status_code=400, detail="The testResultTensile with this id does not exist.")
    return testResultTensile


@router.put("/{testResultTensile_id}", response_model=TestResultTensileRead)
def update_testResultTensile(
    *,
    db_session: Session = Depends(get_db),
    testResultTensile_id: int,
    testResultTensile_in: TestResultTensileUpdate, current_user: DispatchUser = Depends(get_current_user)
):
    """
    Update a testResultTensile contact.
    """
    testResultTensile = get(db_session=db_session, id=testResultTensile_id)
    if not testResultTensile:
        raise HTTPException(status_code=400, detail="The testResultTensile with this id does not exist.")

    testResultTensile = update(
        db_session=db_session,
        test_result_tensile=testResultTensile,
        test_result_tensile_in=testResultTensile_in,
    )
    return testResultTensile


 

@router.delete("/{testResultTensile_id}", response_model=TestResultTensileRead)
def delete_testResultTensile(*, db_session: Session = Depends(get_db), testResultTensile_id: int):
    """
    Delete a testResultTensile contact.
    """
    testResultTensile = get(db_session=db_session, id=testResultTensile_id)
    if not testResultTensile:
        raise HTTPException(status_code=400, detail="The testResultTensile with this id does not exist.")

    return delete(db_session=db_session, id=testResultTensile_id)
