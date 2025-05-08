from dispatch.database import get_db
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from dispatch.system_admin.auth.models import DispatchUser
from dispatch.system_admin.auth.service import get_current_user

from dispatch.database_util.service import common_parameters, search_filter_sort_paginate
from .models import (
    Sprem,
    SpremCreate,
    SpremPagination,
    SpremRead,
    SpremUpdate,
)
from .service import create, delete, get, get_by_code, update

router = APIRouter()


@router.get("/", response_model=SpremPagination)
def get_sprems(*, common: dict = Depends(common_parameters)):

    return search_filter_sort_paginate(model="Sprem", **common)


@router.post("/", response_model=SpremRead)
def create_sprem(*, db_session: Session = Depends(get_db), sprem_in: SpremCreate,
                 current_user: DispatchUser = Depends(get_current_user)):
    """
    Create a new sprem contact.
    """
    
    sprem = get_by_code(db_session=db_session,code=sprem_in.code)
    
    
    if sprem:
        raise HTTPException(status_code=400, detail="The sprem with this code already exists.")
    
    sprem_in.created_by = current_user.email
    sprem_in.updated_by = current_user.email
    try:
        sprem = create(db_session=db_session, sprem_in=sprem_in)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return sprem


@router.get("/{sprem_id}", response_model=SpremRead)
def get_sprem(*, db_session: Session = Depends(get_db), sprem_id: int):
    """
    Get a sprem contact.
    """
    sprem = get(db_session=db_session, sprem_id=sprem_id)
    if not sprem:
        raise HTTPException(status_code=400, detail="The sprem with this id does not exist.")
    return sprem


@router.put("/{sprem_id}", response_model=SpremRead)
def update_sprem(
    *,
    db_session: Session = Depends(get_db),
    sprem_id: int,
    sprem_in: SpremUpdate, current_user: DispatchUser = Depends(get_current_user)
):
    """
    Update a sprem contact.
    """
    sprem = get(db_session=db_session, sprem_id=sprem_id)
    if not sprem:
        raise HTTPException(status_code=400, detail="The sprem with this id does not exist.")

    sprem = update(
        db_session=db_session,
        sprem=sprem,
        sprem_in=sprem_in,
    )
    return sprem


@router.put("/sprem_code/{sprem_code}", response_model=SpremRead)
def update_sprem_by_code(
    *,
    db_session: Session = Depends(get_db),
    sprem_code: str,
    sprem_in: SpremUpdate, current_user: DispatchUser = Depends(get_current_user)
):
    """
    Update a sprem contact.
    """
    sprem = get_by_code(db_session=db_session, code=sprem_code)
    if not sprem:
        raise HTTPException(status_code=400, detail="The sprem with this id does not exist.")

    sprem_in.updated_by = current_user.email
    sprem = update(
        db_session=db_session,
        sprem=sprem,
        sprem_in=sprem_in,
    )

    return sprem


@router.delete("/{sprem_id}", response_model=SpremRead)
def delete_sprem(*, db_session: Session = Depends(get_db), sprem_id: int):
    """
    Delete a sprem contact.
    """
    sprem = get(db_session=db_session, sprem_id=sprem_id)
    if not sprem:
        raise HTTPException(status_code=400, detail="The sprem with this id does not exist.")

    return delete(db_session=db_session, sprem_id=sprem_id)
