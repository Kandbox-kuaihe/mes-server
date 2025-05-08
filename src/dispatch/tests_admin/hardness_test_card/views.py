from dispatch.database import get_db
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from dispatch.system_admin.auth.models import DispatchUser
from dispatch.system_admin.auth.service import get_current_user

from dispatch.database_util.service import common_parameters, search_filter_sort_paginate
from .models import (
    TestHardness,
    TestHardnessCreate,
    TestHardnessPagination,
    TestHardnessRead,
    TestHardnessUpdate,
)
from .service import create, delete, get, update

router = APIRouter()


@router.get("/", response_model=TestHardnessPagination)
def get_TestHardnesss(*, common: dict = Depends(common_parameters)):

    return search_filter_sort_paginate(model="TestHardness", **common)


@router.post("/", response_model=TestHardnessRead)
def create_TestHardness(*, db_session: Session = Depends(get_db), TestHardness_in: TestHardnessCreate,
                 current_user: DispatchUser = Depends(get_current_user)):
    """
    Create a new TestHardness contact.
    """
    
    # TestHardness = get_by_code(db_session=db_session,code=TestHardness_in.test_code)
    
    
    # if TestHardness:
    #     raise HTTPException(status_code=400, detail="The TestHardness with this code already exists.")
    
    TestHardness_in.created_by = current_user.email
    TestHardness_in.updated_by = current_user.email
    TestHardness = create(db_session=db_session, TestHardness_in=TestHardness_in)
    return TestHardness


@router.get("/{TestHardness_id}", response_model=TestHardnessRead)
def get_TestHardness(*, db_session: Session = Depends(get_db), TestHardness_id: int):
    """
    Get a TestHardness contact.
    """
    TestHardness = get(db_session=db_session, TestHardness_id=TestHardness_id)
    if not TestHardness:
        raise HTTPException(status_code=400, detail="The TestHardness with this id does not exist.")
    return TestHardness


@router.put("/{TestHardness_id}", response_model=TestHardnessRead)
def update_TestHardness(
    *,
    db_session: Session = Depends(get_db),
    TestHardness_id: int,
    TestHardness_in: TestHardnessUpdate, current_user: DispatchUser = Depends(get_current_user)
):
    """
    Update a TestHardness contact.
    """
    TestHardness = get(db_session=db_session, TestHardness_id=TestHardness_id)
    if not TestHardness:
        raise HTTPException(status_code=400, detail="The TestHardness with this id does not exist.")

    TestHardness = update(
        db_session=db_session,
        TestHardness=TestHardness,
        TestHardness_in=TestHardness_in,
    )
    return TestHardness


# @router.put("/TestHardness_code/{TestHardness_code}", response_model=TestHardnessRead)
# def update_TestHardness_by_code(
#     *,
#     db_session: Session = Depends(get_db),
#     TestHardness_code: str,
#     TestHardness_in: TestHardnessUpdate, current_user: DispatchUser = Depends(get_current_user)
# ):
#     """
#     Update a TestHardness contact.
#     """
#     TestHardness = get_by_code(db_session=db_session,code=TestHardness_in.test_code)

#     if not TestHardness:
#         raise HTTPException(status_code=400, detail="The TestHardness with this id does not exist.")

#     TestHardness_in.updated_by = current_user.email
#     TestHardness = update(
#         db_session=db_session,
#         TestHardness=TestHardness,
#         TestHardness_in=TestHardness_in,
#     )

#     return TestHardness


@router.delete("/{TestHardness_id}", response_model=TestHardnessRead)
def delete_TestHardness(*, db_session: Session = Depends(get_db), TestHardness_id: int):
    """
    Delete a TestHardness contact.
    """
    TestHardness = get(db_session=db_session, TestHardness_id=TestHardness_id)
    if not TestHardness:
        raise HTTPException(status_code=400, detail="The TestHardness with this id does not exist.")

    return delete(db_session=db_session, TestHardness_id=TestHardness_id)
