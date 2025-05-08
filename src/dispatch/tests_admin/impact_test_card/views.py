from dispatch.database import get_db
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from dispatch.system_admin.auth.models import DispatchUser
from dispatch.system_admin.auth.service import get_current_user

from dispatch.database_util.service import common_parameters, search_filter_sort_paginate
from .models import (
    TestImpact,
    TestImpactCreate,
    TestImpactPagination,
    TestImpactRead,
    TestImpactUpdate,
)
from .service import create, delete, get, get_by_code, update

router = APIRouter()


@router.get("/", response_model=TestImpactPagination)
def get_TestImpact(*, common: dict = Depends(common_parameters)):

    return search_filter_sort_paginate(model="TestImpact", **common)


@router.post("/", response_model=TestImpactRead)
def create_TestImpact(*, db_session: Session = Depends(get_db), TestImpact_in: TestImpactCreate,
                 current_user: DispatchUser = Depends(get_current_user)):
    """
    Create a new TestImapct contact.
    """
    
    # TestImapct = get_by_code(db_session=db_session,code=TestImpact_in.test_code)
    
    
    # if TestImapct:
    #     raise HTTPException(status_code=400, detail="The TestImapct with this code already exists.")
    
    TestImpact_in.created_by = current_user.email
    TestImpact_in.updated_by = current_user.email
    TestImpact = create(db_session=db_session, TestImpact_in=TestImpact_in)
    return TestImpact


@router.get("/{TestImpact_id}", response_model=TestImpactRead)
def get_TestImpact(*, db_session: Session = Depends(get_db), TestImpact_id: int):
    """
    Get a TestImpact contact.
    """
    TestImpact = get(db_session=db_session, TestImpact_id=TestImpact_id)
    if not TestImpact:
        raise HTTPException(status_code=400, detail="The TestImpact with this id does not exist.")
    return TestImpact


@router.put("/{TestImpact_id}", response_model=TestImpactRead)
def update_TestImpact(
    *,
    db_session: Session = Depends(get_db),
    TestImpact_id: int,
    TestImpact_in: TestImpactUpdate, current_user: DispatchUser = Depends(get_current_user)
):
    """
    Update a TestImpact contact.
    """
    TestImpact = get(db_session=db_session, TestImpact_id=TestImpact_id)
    if not TestImpact:
        raise HTTPException(status_code=400, detail="The TestImpact with this id does not exist.")

    TestImpact = update(
        db_session=db_session,
        TestImpact=TestImpact,
        TestImpact_in=TestImpact_in,
    )
    return TestImpact


# @router.put("/TestImpact_code/{TestImpact_code}", response_model=TestImpactRead)
# def update_TestImpact_by_code(
#     *,
#     db_session: Session = Depends(get_db),
#     TestImpact_code: str,
#     TestImpact_in: TestImpactUpdate, current_user: DispatchUser = Depends(get_current_user)
# ):
#     """
#     Update a TestImpact contact.
#     """
#     TestImpact = get_by_code(db_session=db_session,code=TestImpact_in.test_code)

#     if not TestImpact:
#         raise HTTPException(status_code=400, detail="The TestImpact with this id does not exist.")

#     TestImpact_in.updated_by = current_user.email
#     TestImpact = update(
#         db_session=db_session,
#         TestImpact=TestImpact_in,
#         TestImpact_in=TestImpact_in,
#     )

#     return TestImpact

@router.delete("/{TestImpact_id}", response_model=TestImpactRead)
def delete_TestImpact(*, db_session: Session = Depends(get_db), TestImpact_id: int):
    """
    Delete a TestImpact contact.
    """
    TestImpact = get(db_session=db_session, TestImpact_id=TestImpact_id)
    if not TestImpact:
        raise HTTPException(status_code=400, detail="The TestImpact with this id does not exist.")

    return delete(db_session=db_session, TestImpact_id=TestImpact_id)

