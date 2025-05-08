from sqlalchemy import desc
from dispatch.database import get_db, get_class_by_tablename
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from dispatch.system_admin.auth.models import DispatchUser
from dispatch.system_admin.auth.service import get_current_user

from dispatch.database_util.service import common_parameters, search_filter_sort_paginate
from .models import (
    TestBend,
    TestBendCreate,
    TestBendUpdate,
    TestBendRead,
    TestBendPagination,
    TestBendBase
)
from .service import create, delete, get, update
from datetime import datetime, timezone
from dispatch.spec_admin.inspector import service as inspector_service

router = APIRouter()


@router.get("/", response_model=TestBendPagination)
def get_bend_test_cards(*, common: dict = Depends(common_parameters)):

    return search_filter_sort_paginate(model="TestBend", **common)


@router.get("/{bend_test_card_id}", response_model=TestBendRead)
def get_bend_test_card(*, db_session: Session = Depends(get_db), bend_test_card_id: int):
    """
    Get a bend test card contact.
    """
    bend_test_card = get(db_session=db_session, id=bend_test_card_id)
    if not bend_test_card:
        raise HTTPException(status_code=400, detail="The bend test card with this id does not exist.")
    return bend_test_card

@router.post("/", response_model=TestBendRead)
def create_bend_test_card(
    *,
    db_session: Session = Depends(get_db),
    bend_test_card_in: TestBendCreate,
    current_user: DispatchUser = Depends(get_current_user)
):
    """
    Create a new bend test card contact.
    """
    
    bend_test_card_in.created_by = current_user.email
    bend_test_card_in.updated_by = current_user.email
    bend_test_card = create(db_session=db_session, bend_test_card_in=bend_test_card_in)

    db_session.add(bend_test_card)
    db_session.commit()   
    return bend_test_card



@router.put("/{bend_test_card_id}", response_model=TestBendRead)
def update_bend_test_card(
    *,
    db_session: Session = Depends(get_db),
    bend_test_card_id: int,
    bend_test_card_in: TestBendUpdate,
    current_user: DispatchUser = Depends(get_current_user)
):
    """
    Update a bend test card contact.
    """
    bend_test_card = get(db_session=db_session, id=bend_test_card_id)
    if not bend_test_card:
        raise HTTPException(status_code=400, detail="The bend test card with this id does not exist.")
    
    bend_test_card_in.updated_by = current_user.email
    bend_test_card_in.updated_at = datetime.now(timezone.utc)
    bend_test_card = update(
        db_session=db_session,
        bend_test_card=bend_test_card,
        bend_test_card_in=bend_test_card_in,
    )
    return bend_test_card


@router.delete("/{bend_test_card_id}", response_model=TestBendRead)
def delete_bend_test_card(*, db_session: Session = Depends(get_db), bend_test_card_id: int):
    """
    Delete a bend test card contact.
    """
    bend_test_card = get(db_session=db_session, id=bend_test_card_id)
    if not bend_test_card:
        raise HTTPException(status_code=400, detail="The spec with this id does not exist.")

    return delete(db_session=db_session, id=bend_test_card_id)

