from sqlalchemy import desc
from dispatch.database import get_db, get_class_by_tablename
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from dispatch.system_admin.auth.models import DispatchUser
from dispatch.system_admin.auth.service import get_current_user

from dispatch.database_util.service import common_parameters, search_filter_sort_paginate
from .models import (
    TestDecarburisation,
    TestDecarburisationCreate,
    TestDecarburisationUpdate,
    TestDecarburisationRead,
    TestDecarburisationPagination,
    TestDecarburisationBase
)
from .service import create, delete, get, update
from datetime import datetime, timezone
from dispatch.spec_admin.inspector import service as inspector_service

router = APIRouter()


@router.get("/", response_model=TestDecarburisationPagination)
def get_decarburisation_test_cards(*, common: dict = Depends(common_parameters)):

    return search_filter_sort_paginate(model="TestDecarburisation", **common)


@router.get("/{decarburisation_test_card_id}", response_model=TestDecarburisationRead)
def get_decarburisation_test_card(*, db_session: Session = Depends(get_db), decarburisation_test_card_id: int):
    """
    Get a decarburisation test card contact.
    """
    decarburisation_test_card = get(db_session=db_session, id=decarburisation_test_card_id)
    if not decarburisation_test_card:
        raise HTTPException(status_code=400, detail="The decarburisation test card with this id does not exist.")
    return decarburisation_test_card

@router.post("/", response_model=TestDecarburisationRead)
def create_decarburisation_test_card(
    *,
    db_session: Session = Depends(get_db),
    decarburisation_test_card_in: TestDecarburisationCreate,
    current_user: DispatchUser = Depends(get_current_user)
):
    """
    Create a new decarburisation test card contact.
    """
    
    decarburisation_test_card_in.created_by = current_user.email
    decarburisation_test_card_in.updated_by = current_user.email
    decarburisation_test_card = create(db_session=db_session, decarburisation_test_card_in=decarburisation_test_card_in)

    db_session.add(decarburisation_test_card)
    db_session.commit()   
    return decarburisation_test_card



@router.put("/{decarburisation_test_card_id}", response_model=TestDecarburisationRead)
def update_decarburisation_test_card(
    *,
    db_session: Session = Depends(get_db),
    decarburisation_test_card_id: int,
    decarburisation_test_card_in: TestDecarburisationUpdate,
    current_user: DispatchUser = Depends(get_current_user)
):
    """
    Update a decarburisation test card contact.
    """
    decarburisation_test_card = get(db_session=db_session, id=decarburisation_test_card_id)
    if not decarburisation_test_card:
        raise HTTPException(status_code=400, detail="The decarburisation test card with this id does not exist.")
    
    decarburisation_test_card_in.updated_by = current_user.email
    decarburisation_test_card_in.updated_at = datetime.now(timezone.utc)
    decarburisation_test_card = update(
        db_session=db_session,
        decarburisation_test_card=decarburisation_test_card,
        decarburisation_test_card_in=decarburisation_test_card_in,
    )
    return decarburisation_test_card


@router.delete("/{decarburisation_test_card_id}", response_model=TestDecarburisationRead)
def delete_decarburisation_test_card(*, db_session: Session = Depends(get_db), decarburisation_test_card_id: int):
    """
    Delete a decarburisation test card contact.
    """
    decarburisation_test_card = get(db_session=db_session, id=decarburisation_test_card_id)
    if not decarburisation_test_card:
        raise HTTPException(status_code=400, detail="The spec with this id does not exist.")

    return delete(db_session=db_session, id=decarburisation_test_card_id)

