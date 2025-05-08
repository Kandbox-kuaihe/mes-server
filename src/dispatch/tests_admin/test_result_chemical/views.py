from dispatch.database import get_db
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from dispatch.system_admin.auth.models import DispatchUser
from dispatch.system_admin.auth.service import get_current_user

from dispatch.database_util.service import common_parameters, search_filter_sort_paginate
from .models import (
    TestResultChemical,
    TestResultChemicalCreate,
    TestResultChemicalPagination,
    TestResultChemicalRead,
    TestResultChemicalUpdate,
)
from .service import create, create_form_mq, delete, get, update

router = APIRouter()


@router.get("/", response_model=TestResultChemicalPagination)
def get_testResultChemicals(*, common: dict = Depends(common_parameters)):

    result_list = search_filter_sort_paginate(model="TestResultChemical", **common)
    return result_list


@router.post("/", response_model=TestResultChemicalRead)
def create_testResultChemical(*, db_session: Session = Depends(get_db), testResultChemical_in: TestResultChemicalCreate,
                 current_user: DispatchUser = Depends(get_current_user)):
    """
    Create a new testResultChemical contact.
    """
 
    testResultChemical_in.created_by = current_user.email
    testResultChemical_in.updated_by = current_user.email
    testResultChemical = create(db_session=db_session, testResultChemical_in=testResultChemical_in)
    return testResultChemical


@router.get("/{testResultChemical_id}", response_model=TestResultChemicalRead)
def get_testResultChemical(*, db_session: Session = Depends(get_db), testResultChemical_id: int):
    """
    Get a testResultChemical contact.
    """
    testResultChemical = get(db_session=db_session, testResultChemical_id=testResultChemical_id)
    if not testResultChemical:
        raise HTTPException(status_code=400, detail="The testResultChemical with this id does not exist.")
    return testResultChemical


@router.put("/{testResultChemical_id}", response_model=TestResultChemicalRead)
def update_testResultChemical(
    *,
    db_session: Session = Depends(get_db),
    testResultChemical_id: int,
    testResultChemical_in: TestResultChemicalUpdate, current_user: DispatchUser = Depends(get_current_user)
):
    """
    Update a testResultChemical contact.
    """
    testResultChemical = get(db_session=db_session, testResultChemical_id=testResultChemical_id)
    if not testResultChemical:
        raise HTTPException(status_code=400, detail="The testResultChemical with this id does not exist.")

    testResultChemical = update(
        db_session=db_session,
        testResultChemical=testResultChemical,
        testResultChemical_in=testResultChemical_in,
    )
    return testResultChemical


 


@router.delete("/{testResultChemical_id}", response_model=TestResultChemicalRead)
def delete_testResultChemical(*, db_session: Session = Depends(get_db), testResultChemical_id: int):
    """
    Delete a testResultChemical contact.
    """
    testResultChemical = get(db_session=db_session, testResultChemical_id=testResultChemical_id)
    if not testResultChemical:
        raise HTTPException(status_code=400, detail="The testResultChemical with this id does not exist.")

    return delete(db_session=db_session, testResultChemical_id=testResultChemical_id)



@router.post("/create_testResultChemical_mq", response_model=TestResultChemicalRead)
def create_testResultChemical_mq(*, db_session: Session = Depends(get_db), testResultChemical_in,
                 current_user: DispatchUser = Depends(get_current_user)):
    """
    Create a new testResultChemical contact.
    """
     
    testResultChemical = create_form_mq(db_session=db_session, testResultChemical_in=testResultChemical_in)
    return testResultChemical