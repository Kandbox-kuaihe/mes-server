from sqlalchemy import desc
from dispatch.database import get_db
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from dispatch.system_admin.auth.models import DispatchUser
from dispatch.system_admin.auth.service import get_current_user

from dispatch.database_util.service import common_parameters, search_filter_sort_paginate
from .models import (
    TestResistivityCreate,
    TestResistivityUpdate,
    TestResistivityRead,
    TestResistivityPagination,
 
)
from .service import create, delete, get, update
from datetime import datetime, timezone

router = APIRouter()


@router.get("/", response_model=TestResistivityPagination)
def get_resistivitytest_cards(*, common: dict = Depends(common_parameters)):

    return search_filter_sort_paginate(model="TestResistivity", **common)


@router.get("/{resistivity_test_card_id}", response_model=TestResistivityRead)
def get_resistivitytest_card(*, db_session: Session = Depends(get_db), resistivity_test_card_id: int):
    """
    Get a resistivity test card contact.
    """
    resistivity_test_card = get(db_session=db_session, id=resistivity_test_card_id)
    if not resistivity_test_card:
        raise HTTPException(status_code=400, detail="The resistivity test card with this id does not exist.")
    return resistivity_test_card

@router.post("/", response_model=TestResistivityRead)
def create_resistivitytest_card(
    *,
    db_session: Session = Depends(get_db),
    resistivity_test_card_in: TestResistivityCreate,
    current_user: DispatchUser = Depends(get_current_user)
):
    """
    Create a new resistivity test card contact.
    """
    
    resistivity_test_card_in.created_by = current_user.email
    resistivity_test_card_in.updated_by = current_user.email
    resistivity_test_card = create(db_session=db_session, resistivity_test_card_in=resistivity_test_card_in)

    return resistivity_test_card



@router.put("/{resistivity_test_card_id}", response_model=TestResistivityRead)
def update_resistivitytest_card(
    *,
    db_session: Session = Depends(get_db),
    resistivity_test_card_id: int,
    resistivity_test_card_in: TestResistivityUpdate,
    current_user: DispatchUser = Depends(get_current_user)
):
    """
    Update a resistivitytest test card contact.
    """
    resistivitytest_card = get(db_session=db_session, id=resistivity_test_card_id)
    if not resistivitytest_card:
        raise HTTPException(status_code=400, detail="The resistivitytest test card with this id does not exist.")
    
    resistivity_test_card_in.updated_by = current_user.email
    resistivity_test_card_in.updated_at = datetime.now(timezone.utc)
    resistivitytest_card = update(
        db_session=db_session,
        resistivity_test_card=resistivitytest_card,
        resistivity_test_card_in=resistivity_test_card_in,
    )
    return resistivitytest_card


@router.delete("/{resistivity_test_card_id}", response_model=TestResistivityRead)
def delete_resistivitytest_card(*, db_session: Session = Depends(get_db), resistivity_test_card_id: int):
    """
    Delete a resistivitytest test card contact.
    """
    resistivitytest_card = get(db_session=db_session, id=resistivity_test_card_id)
    if not resistivitytest_card:
        raise HTTPException(status_code=400, detail="The spec with this id does not exist.")

    return delete(db_session=db_session, id=resistivity_test_card_id)

