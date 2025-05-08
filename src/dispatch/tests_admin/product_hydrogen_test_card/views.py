from sqlalchemy import desc
from dispatch.database import get_db, get_class_by_tablename
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from dispatch.system_admin.auth.models import DispatchUser
from dispatch.system_admin.auth.service import get_current_user

from dispatch.database_util.service import common_parameters, search_filter_sort_paginate
from .models import (
    TestHydrogen,
    TestHydrogenCreate,
    TestHydrogenUpdate,
    TestHydrogenRead,
    TestHydrogenPagination,
    TestHydrogenBase
)
from .service import create, delete, get, update
from datetime import datetime, timezone
from dispatch.spec_admin.inspector import service as inspector_service

router = APIRouter()


@router.get("/", response_model=TestHydrogenPagination)
def get_product_hydrogen_test_cards(*, common: dict = Depends(common_parameters)):

    return search_filter_sort_paginate(model="TestHydrogen", **common)


@router.get("/{product_hydrogen_test_card_id}", response_model=TestHydrogenRead)
def get_product_hydrogen_test_card(*, db_session: Session = Depends(get_db), product_hydrogen_test_card_id: int):
    """
    Get a product hydrogen test card contact.
    """
    product_hydrogen_test_card = get(db_session=db_session, id=product_hydrogen_test_card_id)
    if not product_hydrogen_test_card:
        raise HTTPException(status_code=400, detail="The product hydrogen test card with this id does not exist.")
    return product_hydrogen_test_card

@router.post("/", response_model=TestHydrogenRead)
def create_product_hydrogen_test_card(
    *,
    db_session: Session = Depends(get_db),
    product_hydrogen_test_card_in: TestHydrogenCreate,
    current_user: DispatchUser = Depends(get_current_user)
):
    """
    Create a new product hydrogen test card contact.
    """
    
    product_hydrogen_test_card_in.created_by = current_user.email
    product_hydrogen_test_card_in.updated_by = current_user.email
    product_hydrogen_test_card = create(db_session=db_session, product_hydrogen_test_card_in=product_hydrogen_test_card_in)

    db_session.add(product_hydrogen_test_card)
    db_session.commit()   
    return product_hydrogen_test_card



@router.put("/{product_hydrogen_test_card_id}", response_model=TestHydrogenRead)
def update_product_hydrogen_test_card(
    *,
    db_session: Session = Depends(get_db),
    product_hydrogen_test_card_id: int,
    product_hydrogen_test_card_in: TestHydrogenUpdate,
    current_user: DispatchUser = Depends(get_current_user)
):
    """
    Update a product hydrogen test card contact.
    """
    product_hydrogen_test_card = get(db_session=db_session, id=product_hydrogen_test_card_id)
    if not product_hydrogen_test_card:
        raise HTTPException(status_code=400, detail="The product hydrogen test card with this id does not exist.")
    
    product_hydrogen_test_card_in.updated_by = current_user.email
    product_hydrogen_test_card_in.updated_at = datetime.now(timezone.utc)
    product_hydrogen_test_card = update(
        db_session=db_session,
        product_hydrogen_test_card=product_hydrogen_test_card,
        product_hydrogen_test_card_in=product_hydrogen_test_card_in,
    )
    return product_hydrogen_test_card


@router.delete("/{product_hydrogen_test_card_id}", response_model=TestHydrogenRead)
def delete_product_hydrogen_test_card(*, db_session: Session = Depends(get_db), product_hydrogen_test_card_id: int):
    """
    Delete a product hydrogen test card contact.
    """
    product_hydrogen_test_card = get(db_session=db_session, id=product_hydrogen_test_card_id)
    if not product_hydrogen_test_card:
        raise HTTPException(status_code=400, detail="The spec with this id does not exist.")

    return delete(db_session=db_session, id=product_hydrogen_test_card_id)

