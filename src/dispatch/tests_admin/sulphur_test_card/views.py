from dispatch.database import get_db
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from dispatch.system_admin.auth.models import DispatchUser
from dispatch.system_admin.auth.service import get_current_user

from dispatch.database_util.service import common_parameters, search_filter_sort_paginate
from .models import (
    TestSulphur,
    TestSulphurCreate,
    TestSulphurPagination,
    TestSulphurRead,
    TestSulphurUpdate,
)
from .service import create, delete, get, get_by_code, update

router = APIRouter()


@router.get("/", response_model=TestSulphurPagination)
def get_TestSulphurs(*, common: dict = Depends(common_parameters)):

    return search_filter_sort_paginate(model="TestSulphur", **common)


@router.post("/", response_model=TestSulphurRead)
def create_TestSulphur(*, db_session: Session = Depends(get_db), TestSulphur_in: TestSulphurCreate,
                 current_user: DispatchUser = Depends(get_current_user)):
    """
    Create a new TestSulphur contact.
    """
    
    # TestSulphur = get_by_code(db_session=db_session,code=TestSulphur_in.test_code)
    
    
    # if TestSulphur:
    #     raise HTTPException(status_code=400, detail="The TestSulphur with this code already exists.")
    
    TestSulphur_in.created_by = current_user.email
    TestSulphur_in.updated_by = current_user.email
    TestSulphur = create(db_session=db_session, TestSulphur_in=TestSulphur_in)
    return TestSulphur


@router.get("/{TestSulphur_id}", response_model=TestSulphurRead)
def get_TestSulphur(*, db_session: Session = Depends(get_db), TestSulphur_id: int):
    """
    Get a TestSulphur contact.
    """
    TestSulphur = get(db_session=db_session, TestSulphur_id=TestSulphur_id)
    if not TestSulphur:
        raise HTTPException(status_code=400, detail="The TestSulphur with this id does not exist.")
    return TestSulphur


@router.put("/{TestSulphur_id}", response_model=TestSulphurRead)
def update_TestSulphur(
    *,
    db_session: Session = Depends(get_db),
    TestSulphur_id: int,
    TestSulphur_in: TestSulphurUpdate, current_user: DispatchUser = Depends(get_current_user)
):
    """
    Update a TestSulphur contact.
    """
    TestSulphur = get(db_session=db_session, TestSulphur_id=TestSulphur_id)
    if not TestSulphur:
        raise HTTPException(status_code=400, detail="The TestSulphur with this id does not exist.")

    TestSulphur = update(
        db_session=db_session,
        TestSulphur=TestSulphur,
        TestSulphur_in=TestSulphur_in,
    )
    return TestSulphur


# @router.put("/TestSulphur_code/{TestSulphur_code}", response_model=TestSulphurRead)
# def update_TestSulphur_by_code(
#     *,
#     db_session: Session = Depends(get_db),
#     TestSulphur_code: str,
#     TestSulphur_in: TestSulphurUpdate, current_user: DispatchUser = Depends(get_current_user)
# ):
#     """
#     Update a TestSulphur contact.
#     """
#     TestSulphur = get_by_code(db_session=db_session,code=TestSulphur_in.test_code)

#     if not TestSulphur:
#         raise HTTPException(status_code=400, detail="The TestSulphur with this id does not exist.")

#     TestSulphur_in.updated_by = current_user.email
#     TestSulphur = update(
#         db_session=db_session,
#         TestSulphur=TestSulphur,
#         TestSulphur_in=TestSulphur_in,
#     )

#     return TestSulphur


@router.delete("/{TestSulphur_id}", response_model=TestSulphurRead)
def delete_TestSulphur(*, db_session: Session = Depends(get_db), TestSulphur_id: int):
    """
    Delete a TestSulphur contact.
    """
    TestSulphur = get(db_session=db_session, TestSulphur_id=TestSulphur_id)
    if not TestSulphur:
        raise HTTPException(status_code=400, detail="The TestSulphur with this id does not exist.")

    return delete(db_session=db_session, TestSulphur_id=TestSulphur_id)
