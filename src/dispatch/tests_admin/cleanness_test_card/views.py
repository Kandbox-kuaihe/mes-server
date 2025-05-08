from dispatch.database import get_db
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from dispatch.system_admin.auth.models import DispatchUser
from dispatch.system_admin.auth.service import get_current_user

from dispatch.database_util.service import common_parameters, search_filter_sort_paginate
from .models import (
    TestCleanness,
    TestCleannessCreate,
    TestCleannessPagination,
    TestCleannessRead,
    TestCleannessUpdate,
)
from .service import create, delete, get, get_by_code, update

router = APIRouter()


@router.get("/", response_model=TestCleannessPagination)
def get_TestCleannesss(*, common: dict = Depends(common_parameters)):

    return search_filter_sort_paginate(model="TestCleanness", **common)


@router.post("/", response_model=TestCleannessRead)
def create_TestCleanness(*, db_session: Session = Depends(get_db), TestCleanness_in: TestCleannessCreate,
                 current_user: DispatchUser = Depends(get_current_user)):
    """
    Create a new TestCleanness contact.
    """
    
    # TestCleanness = get_by_code(db_session=db_session,code=TestCleanness_in.test_code)
    
    
    # if TestCleanness:
    #     raise HTTPException(status_code=400, detail="The TestCleanness with this code already exists.")
    
    TestCleanness_in.created_by = current_user.email
    TestCleanness_in.updated_by = current_user.email
    TestCleanness = create(db_session=db_session, TestCleanness_in=TestCleanness_in)
    return TestCleanness


@router.get("/{TestCleanness_id}", response_model=TestCleannessRead)
def get_TestCleanness(*, db_session: Session = Depends(get_db), TestCleanness_id: int):
    """
    Get a TestCleanness contact.
    """
    TestCleanness = get(db_session=db_session, TestCleanness_id=TestCleanness_id)
    if not TestCleanness:
        raise HTTPException(status_code=400, detail="The TestCleanness with this id does not exist.")
    return TestCleanness


@router.put("/{TestCleanness_id}", response_model=TestCleannessRead)
def update_TestCleanness(
    *,
    db_session: Session = Depends(get_db),
    TestCleanness_id: int,
    TestCleanness_in: TestCleannessUpdate, current_user: DispatchUser = Depends(get_current_user)
):
    """
    Update a TestCleanness contact.
    """
    TestCleanness = get(db_session=db_session, TestCleanness_id=TestCleanness_id)
    if not TestCleanness:
        raise HTTPException(status_code=400, detail="The TestCleanness with this id does not exist.")

    TestCleanness = update(
        db_session=db_session,
        TestCleanness=TestCleanness,
        TestCleanness_in=TestCleanness_in,
    )
    return TestCleanness


# @router.put("/TestCleanness_code/{TestCleanness_code}", response_model=TestCleannessRead)
# def update_TestCleanness_by_code(
#     *,
#     db_session: Session = Depends(get_db),
#     TestCleanness_code: str,
#     TestCleanness_in: TestCleannessUpdate, current_user: DispatchUser = Depends(get_current_user)
# ):
#     """
#     Update a TestCleanness contact.
#     """
#     TestCleanness = get_by_code(db_session=db_session,code=TestCleanness_in.test_code)

#     if not TestCleanness:
#         raise HTTPException(status_code=400, detail="The TestCleanness with this id does not exist.")

#     TestCleanness_in.updated_by = current_user.email
#     TestCleanness = update(
#         db_session=db_session,
#         TestCleanness=TestCleanness,
#         TestCleanness_in=TestCleanness_in,
#     )

#     return TestCleanness


@router.delete("/{TestCleanness_id}", response_model=TestCleannessRead)
def delete_TestCleanness(*, db_session: Session = Depends(get_db), TestCleanness_id: int):
    """
    Delete a TestCleanness contact.
    """
    TestCleanness = get(db_session=db_session, TestCleanness_id=TestCleanness_id)
    if not TestCleanness:
        raise HTTPException(status_code=400, detail="The TestCleanness with this id does not exist.")

    return delete(db_session=db_session, TestCleanness_id=TestCleanness_id)
