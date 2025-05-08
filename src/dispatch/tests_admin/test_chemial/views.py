from sqlalchemy import desc, case
from dispatch.database import get_db, get_class_by_tablename
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from dispatch.system_admin.auth.models import DispatchUser
from dispatch.system_admin.auth.service import get_current_user

from dispatch.database_util.service import common_parameters, search_filter_sort_paginate
from .models import (
    TestChemial,
    TestChemialCreate,
    TestChemialUpdate,
    TestChemialRead,
    TestChemialPagination,
    TestChemialBase
)
from .service import create, get, update, delete
from datetime import datetime, timezone
from dispatch.spec_admin.inspector import service as inspector_service
from ...cast.models import Cast

router = APIRouter()


@router.get("/", response_model=TestChemialPagination)
def get_test_chemials(*, db_session: Session = Depends(get_db), common: dict = Depends(common_parameters)):

    query = db_session.query(TestChemial).outerjoin(Cast, TestChemial.cast_id == Cast.id)
    sort_list = ["AVG", "MIN", "MAX", "L01", "A01", "T01", "T02", "T03", "T04"]
    sort_order = case(
        {test_type: index for index, test_type in enumerate(sort_list)},
        value=TestChemial.test_type,
        else_=len(sort_list)  # 将不在 sort_list 中的 test_type 排在最后
    )
    query = query.order_by(sort_order)
    common['query'] = query

    return search_filter_sort_paginate(model="TestChemial", **common)


@router.get("/{test_chemial_id}", response_model=TestChemialRead)
def get_test_chemial(*, db_session: Session = Depends(get_db), test_chemial_id: int):
    """
    Get a decarburisation test card contact.
    """
    test_chemial = get(db_session=db_session, id=test_chemial_id)
    if not test_chemial:
        raise HTTPException(status_code=400, detail="The decarburisation test card with this id does not exist.")
    return test_chemial

@router.post("/", response_model=TestChemialRead)
def create_test_chemial(
    *,
    db_session: Session = Depends(get_db),
    test_chemial_in: TestChemialCreate,
    current_user: DispatchUser = Depends(get_current_user)
):
    """
    Create a new test_chemial test card contact.
    """
    
    test_chemial_in.created_by = current_user.email
    test_chemial_in.updated_by = current_user.email
    test_chemial = create(db_session=db_session, test_chemial_in=test_chemial_in)

    db_session.add(test_chemial)
    db_session.commit()   
    return test_chemial


@router.put("/{test_chemial_id}", response_model=TestChemialRead)
def update_test_chemial(
    *,
    db_session: Session = Depends(get_db),
    test_chemial_id: int,
    test_chemial_in: TestChemialUpdate,
    current_user: DispatchUser = Depends(get_current_user)
):
    """
    Update a test_chemial test card contact.
    """
    test_chemial = get(db_session=db_session, id=test_chemial_id)
    if not test_chemial:
        raise HTTPException(status_code=400, detail="The test_chemial test card with this id does not exist.")
    
    test_chemial_in.updated_by = current_user.email
    test_chemial_in.updated_at = datetime.now(timezone.utc)
    test_chemial = update(
        db_session=db_session,
        test_chemial=test_chemial,
        test_chemial_in=test_chemial_in,
    )
    return test_chemial


@router.delete("/{test_chemial_id}", response_model=TestChemialRead)
def delete_cast(*, db_session: Session = Depends(get_db), cast_id: int):
    """
    Delete a cast contact.
    """
    test_chemial = get(db_session=db_session, id=cast_id)
    if not test_chemial:
        raise HTTPException(status_code=400, detail="The test_chemial with this id does not exist.")

    return delete(db_session=db_session, id=cast_id)