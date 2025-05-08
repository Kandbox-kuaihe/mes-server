from datetime import datetime

from dispatch.database import get_db
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from dispatch.system_admin.auth.models import DispatchUser
from dispatch.system_admin.auth.service import get_current_user

from dispatch.database_util.service import common_parameters, search_filter_sort_paginate
from .models import (
    TestJominy,
    TestJominyCreate,
    TestJominyPagination,
    TestJominyRead,
    TestJominyUpdate,
)
from .service import create, delete, get, update

router = APIRouter()


@router.get("/", response_model=TestJominyPagination)
def get_test_jominys(*, common: dict = Depends(common_parameters)):

    return search_filter_sort_paginate(model="TestJominy", **common)


@router.post("/", response_model=TestJominyRead)
def create_test_jominy(*, db_session: Session = Depends(get_db), test_jominy_in: TestJominyCreate,
                 current_user: DispatchUser = Depends(get_current_user)):
    """
    Create a new TestJominy contact.
    """

    test_jominy_in.created_by = current_user.email
    test_jominy_in.updated_by = current_user.email
    test_jominy_in.mill_id = current_user.current_mill_id
    test_jominy = create(db_session=db_session, test_jominy_in=test_jominy_in)
    db_session.commit()
    return test_jominy


@router.get("/{test_jominy_id}", response_model=TestJominyRead)
def get_test_jominy(*, db_session: Session = Depends(get_db), test_jominy_id: int):
    """
    Get a TestJominy contact.
    """
    test_jominy = get(db_session=db_session, test_jominy_id=test_jominy_id)
    if not test_jominy:
        raise HTTPException(status_code=400, detail="The TestJominy with this id does not exist.")
    return test_jominy


@router.put("/{test_jominy_id}", response_model=TestJominyRead)
def update_TestJominy(
    *,
    db_session: Session = Depends(get_db),
    test_jominy_id: int,
    test_jominy_in: TestJominyUpdate,
    current_user: DispatchUser = Depends(get_current_user)
):
    """
    Update a TestJominy contact.
    """
    test_jominy = get(db_session=db_session, test_jominy_id=test_jominy_id)
    if not test_jominy:
        raise HTTPException(status_code=400, detail="The TestJominy with this id does not exist.")
    test_jominy_in.updated_at = datetime.now()
    test_jominy_in.updated_by = current_user.email
    test_jominy_in.mill_id = current_user.current_mill_id
    test_jominy = update(
        db_session=db_session,
        test_jominy=test_jominy,
        test_jominy_in=test_jominy_in,
    )
    return test_jominy


@router.delete("/{test_jominy_id}", response_model=TestJominyRead)
def delete_TestJominy(*, db_session: Session = Depends(get_db), test_jominy_id: int):
    """
    Delete a TestJominy contact.
    """
    test_jominy = get(db_session=db_session, test_jominy_id=test_jominy_id)
    if not test_jominy:
        raise HTTPException(status_code=400, detail="The TestJominy with this id does not exist.")

    return delete(db_session=db_session, test_jominy_id=test_jominy_id)
