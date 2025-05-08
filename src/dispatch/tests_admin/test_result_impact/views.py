from dispatch.database import get_db
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from dispatch.system_admin.auth.models import DispatchUser
from dispatch.system_admin.auth.service import get_current_user

from dispatch.database_util.service import common_parameters, search_filter_sort_paginate
from .models import (
    TestResultImpactBase,
    TestResultImpactBaseCreate,
    TestResultImpactBasePagination,
    TestResultImpactBaseRead,
    TestResultImpactBaseUpdate,
)
from .service import create, delete, get, update

router = APIRouter()


@router.get("/", response_model=TestResultImpactBasePagination)
def get_testResultImpactBases(*, common: dict = Depends(common_parameters)):

    return search_filter_sort_paginate(model="TestResultImpact", **common)


@router.post("/", response_model=TestResultImpactBaseRead)
def create_testResultImpactBase(*, db_session: Session = Depends(get_db), testResultImpactBase_in: TestResultImpactBaseCreate,
                 current_user: DispatchUser = Depends(get_current_user)):
    """
    Create a new testResultImpactBase contact.
    """
 
    testResultImpactBase_in.created_by = current_user.email
    testResultImpactBase_in.updated_by = current_user.email
    testResultImpactBase = create(db_session=db_session, request_in=testResultImpactBase_in)
    return testResultImpactBase


@router.get("/{testResultImpactBase_id}", response_model=TestResultImpactBaseRead)
def get_testResultImpactBase(*, db_session: Session = Depends(get_db), testResultImpactBase_id: int):
    """
    Get a testResultImpactBase contact.
    """
    testResultImpactBase = get(db_session=db_session, testResultImpactBase_id=testResultImpactBase_id)
    if not testResultImpactBase:
        raise HTTPException(status_code=400, detail="The testResultImpactBase with this id does not exist.")
    return testResultImpactBase


@router.put("/{testResultImpactBase_id}", response_model=TestResultImpactBaseRead)
def update_testResultImpactBase(
    *,
    db_session: Session = Depends(get_db),
    testResultImpactBase_id: int,
    testResultImpactBase_in: TestResultImpactBaseUpdate, current_user: DispatchUser = Depends(get_current_user)
):
    """
    Update a testResultImpactBase contact.
    """
    testResultImpactBase = get(db_session=db_session, testResultImpactBase_id=testResultImpactBase_id)
    if not testResultImpactBase:
        raise HTTPException(status_code=400, detail="The testResultImpactBase with this id does not exist.")

    testResultImpactBase = update(
        db_session=db_session,
        testResultImpactBase=testResultImpactBase,
        testResultImpactBase_in=testResultImpactBase_in,
    )
    return testResultImpactBase


 

@router.delete("/{testResultImpactBase_id}", response_model=TestResultImpactBaseRead)
def delete_testResultImpactBase(*, db_session: Session = Depends(get_db), testResultImpactBase_id: int):
    """
    Delete a testResultImpactBase contact.
    """
    testResultImpactBase = get(db_session=db_session, testResultImpactBase_id=testResultImpactBase_id)
    if not testResultImpactBase:
        raise HTTPException(status_code=400, detail="The testResultImpactBase with this id does not exist.")

    return delete(db_session=db_session, testResultImpactBase_id=testResultImpactBase_id)
