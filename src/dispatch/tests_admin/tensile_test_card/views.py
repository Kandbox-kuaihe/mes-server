from dispatch.database import get_db
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from dispatch.system_admin.auth.models import DispatchUser
from dispatch.system_admin.auth.service import get_current_user

from dispatch.database_util.service import common_parameters, search_filter_sort_paginate
from .models import (
    TestTensile,
    TestTensileCreate,
    TestTensilePagination,
    TestTensileRead,
    TestTensileUpdate,
)
from .service import create, delete, get, update

router = APIRouter()


@router.get("/", response_model=TestTensilePagination)
def get_TestTensiles(*, common: dict = Depends(common_parameters)):

    return search_filter_sort_paginate(model="TestTensile", **common)


@router.post("/", response_model=TestTensileRead)
def create_TestTensile(*, db_session: Session = Depends(get_db), TestTensile_in: TestTensileCreate,
                 current_user: DispatchUser = Depends(get_current_user)):
    """
    Create a new TestTensile contact.
    """
    
    # TestTensile = get_by_code(db_session=db_session,code=TestTensile_in.test_code)
    
    
    # if TestTensile:
    #     raise HTTPException(status_code=400, detail="The TestTensile with this code already exists.")
    
    TestTensile_in.created_by = current_user.email
    TestTensile_in.updated_by = current_user.email
    TestTensile = create(db_session=db_session, TestTensile_in=TestTensile_in)
    return TestTensile


@router.get("/{TestTensile_id}", response_model=TestTensileRead)
def get_TestTensile(*, db_session: Session = Depends(get_db), TestTensile_id: int):
    """
    Get a TestTensile contact.
    """
    TestTensile = get(db_session=db_session, TestTensile_id=TestTensile_id)
    if not TestTensile:
        raise HTTPException(status_code=400, detail="The TestTensile with this id does not exist.")
    return TestTensile


@router.put("/{TestTensile_id}", response_model=TestTensileRead)
def update_TestTensile(
    *,
    db_session: Session = Depends(get_db),
    TestTensile_id: int,
    TestTensile_in: TestTensileUpdate, current_user: DispatchUser = Depends(get_current_user)
):
    """
    Update a TestTensile contact.
    """
    TestTensile = get(db_session=db_session, TestTensile_id=TestTensile_id)
    if not TestTensile:
        raise HTTPException(status_code=400, detail="The TestTensile with this id does not exist.")

    TestTensile = update(
        db_session=db_session,
        TestTensile=TestTensile,
        TestTensile_in=TestTensile_in,
    )
    return TestTensile


# @router.put("/TestTensile_code/{TestTensile_code}", response_model=TestTensileRead)
# def update_TestTensile_by_code(
#     *,
#     db_session: Session = Depends(get_db),
#     TestTensile_code: str,
#     TestTensile_in: TestTensileUpdate, current_user: DispatchUser = Depends(get_current_user)
# ):
#     """
#     Update a TestTensile contact.
#     """
#     TestTensile = get_by_code(db_session=db_session,code=TestTensile_in.test_code)

#     if not TestTensile:
#         raise HTTPException(status_code=400, detail="The TestTensile with this id does not exist.")

#     TestTensile_in.updated_by = current_user.email
#     TestTensile = update(
#         db_session=db_session,
#         TestTensile=TestTensile,
#         TestTensile_in=TestTensile_in,
#     )

#     return TestTensile


@router.delete("/{TestTensile_id}", response_model=TestTensileRead)
def delete_TestTensile(*, db_session: Session = Depends(get_db), TestTensile_id: int):
    """
    Delete a TestTensile contact.
    """
    TestTensile = get(db_session=db_session, TestTensile_id=TestTensile_id)
    if not TestTensile:
        raise HTTPException(status_code=400, detail="The TestTensile with this id does not exist.")

    return delete(db_session=db_session, TestTensile_id=TestTensile_id)
