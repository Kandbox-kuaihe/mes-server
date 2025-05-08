from dispatch.database import get_db
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from dispatch.system_admin.auth.models import DispatchUser
from dispatch.system_admin.auth.service import get_current_user

from dispatch.database_util.service import common_parameters, search_filter_sort_paginate
from .models import (
    SpprodanOtherElement,
    SpprodanOtherElementCreate,
    SpprodanOtherElementPagination,
    SpprodanOtherElementRead,
    SpprodanOtherElementUpdate,
)
from .service import create, delete, get, get_by_code, update
from datetime import datetime, timezone

router = APIRouter()


@router.get("/", response_model=SpprodanOtherElementPagination)
def get_spprodans(*, common: dict = Depends(common_parameters)):

    return search_filter_sort_paginate(model="SpprodanOtherElement", **common)



@router.post("/{spprodan_id}", response_model=SpprodanOtherElementRead)
def create_spprodan(
    *, 
    db_session: Session = Depends(get_db), 
    spprodan_id: int,
    spprodan_in: SpprodanOtherElementCreate,
    current_user: DispatchUser = Depends(get_current_user)
):
    """
    Create a new specMainEl contact.
    """
    
    # spprodan = get_by_code(db_session=db_session,code=spprodan_in.code)
    
    
    # if spprodan:
    #     raise HTTPException(status_code=400, detail="The specMainEl with this code already exists.")
    
    
    spprodan = create(db_session=db_session, spprodan_id=spprodan_id, spprodan_other_element_in=spprodan_in, current_user=current_user)
    return spprodan


@router.get("/{spprodan_id}", response_model=SpprodanOtherElementRead)
def get_spprodan(*, db_session: Session = Depends(get_db), spprodan_id: int):
    """
    Get a specMainEl contact.
    """
    spprodan = get(db_session=db_session, id=spprodan_id)
    if not spprodan:
        raise HTTPException(status_code=400, detail="The spprodan with this id does not exist.")
    return spprodan


@router.put("/{spprodan_id}", response_model=SpprodanOtherElementRead)
def update_spprodan(
    *,
    db_session: Session = Depends(get_db),
    spprodan_id: int,
    spprodan_in: SpprodanOtherElementUpdate, current_user: DispatchUser = Depends(get_current_user)
):
    """
    Update a spprodan contact.
    """
    spprodan = get(db_session=db_session, id=spprodan_id)
    if not spprodan:
        raise HTTPException(status_code=400, detail="The spprodan with this id does not exist.")

    spprodan_in.updated_by = current_user.email
    spprodan_in.updated_at = datetime.now(timezone.utc)
    spprodan = update(
        db_session=db_session,
        spprodan_other_element=spprodan,
        spprodan_other_element_in=spprodan_in,
    )
    return spprodan



@router.delete("/{spprodan_id}", response_model=SpprodanOtherElementRead)
def delete_spprodan(*, db_session: Session = Depends(get_db), spprodan_id: int):
    """
    Delete a specMainEl contact.
    """
    spprodan = get(db_session=db_session, id=spprodan_id)
    if not spprodan:
        raise HTTPException(status_code=400, detail="The specMainEl with this id does not exist.")

    return delete(db_session=db_session, id=spprodan_id)

