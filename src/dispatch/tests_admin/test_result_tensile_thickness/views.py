from dispatch.database import get_db
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from dispatch.system_admin.auth.models import DispatchUser
from dispatch.system_admin.auth.service import get_current_user

from dispatch.database_util.service import common_parameters, search_filter_sort_paginate
from .models import (
    TestResultTensileThickness,
    TestResultTensileThicknessCreate,
    TestResultTensileThicknessPagination,
    TestResultTensileThicknessRead,
    TestResultTensileThicknessUpdate,
)
from .service import create, delete, get,  update

router = APIRouter()


@router.get("/", response_model=TestResultTensileThicknessPagination)
def get_testResultTensileThicknesss(*, common: dict = Depends(common_parameters)):

    return search_filter_sort_paginate(model="TestResultTensileThickness", **common)


@router.post("/", response_model=TestResultTensileThicknessRead)
def create_testResultTensileThickness(*, db_session: Session = Depends(get_db), testResultTensileThickness_in: TestResultTensileThicknessCreate,
                 current_user: DispatchUser = Depends(get_current_user)):
    """
    Create a new testResultTensileThickness contact.
    """
 
    testResultTensileThickness_in.created_by = current_user.email
    testResultTensileThickness_in.updated_by = current_user.email
    testResultTensileThickness = create(db_session=db_session, testResultTensileThickness_in=testResultTensileThickness_in)
    return testResultTensileThickness


@router.get("/{testResultTensileThickness_id}", response_model=TestResultTensileThicknessRead)
def get_testResultTensileThickness(*, db_session: Session = Depends(get_db), testResultTensileThickness_id: int):
    """
    Get a testResultTensileThickness contact.
    """
    testResultTensileThickness = get(db_session=db_session, testResultTensileThickness_id=testResultTensileThickness_id)
    if not testResultTensileThickness:
        raise HTTPException(status_code=400, detail="The testResultTensileThickness with this id does not exist.")
    return testResultTensileThickness


@router.put("/{testResultTensileThickness_id}", response_model=TestResultTensileThicknessRead)
def update_testResultTensileThickness(
    *,
    db_session: Session = Depends(get_db),
    testResultTensileThickness_id: int,
    testResultTensileThickness_in: TestResultTensileThicknessUpdate, current_user: DispatchUser = Depends(get_current_user)
):
    """
    Update a testResultTensileThickness contact.
    """
    testResultTensileThickness = get(db_session=db_session, testResultTensileThickness_id=testResultTensileThickness_id)
    if not testResultTensileThickness:
        raise HTTPException(status_code=400, detail="The testResultTensileThickness with this id does not exist.")

    testResultTensileThickness = update(
        db_session=db_session,
        testResultTensileThickness=testResultTensileThickness,
        testResultTensileThickness_in=testResultTensileThickness_in,
    )
    return testResultTensileThickness

 

@router.delete("/{testResultTensileThickness_id}", response_model=TestResultTensileThicknessRead)
def delete_testResultTensileThickness(*, db_session: Session = Depends(get_db), testResultTensileThickness_id: int):
    """
    Delete a testResultTensileThickness contact.
    """
    testResultTensileThickness = get(db_session=db_session, testResultTensileThickness_id=testResultTensileThickness_id)
    if not testResultTensileThickness:
        raise HTTPException(status_code=400, detail="The testResultTensileThickness with this id does not exist.")

    return delete(db_session=db_session, testResultTensile_id=testResultTensileThickness_id)
