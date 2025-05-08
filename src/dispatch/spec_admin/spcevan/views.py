from dispatch.database import get_db
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from dispatch.system_admin.auth.models import DispatchUser
from dispatch.system_admin.auth.service import get_current_user

from dispatch.database_util.service import common_parameters, search_filter_sort_paginate
from .models import (
    Spcevan,
    SpcevanCreate,
    SpcevanPagination,
    SpcevanRead,
    SpcevanUpdate,
    SpcevanUpdateNew,
    SpcevanBySpecCode,
    SpcevanCopyToCode
)
from .service import create, delete, get, get_by_code, update, update_new, get_by_spec_code, create_by_copy_spec_code
from datetime import datetime, timezone

router = APIRouter()


@router.get("/", response_model=SpcevanPagination)
def get_spcevans(*, common: dict = Depends(common_parameters)):

    return search_filter_sort_paginate(model="Spcevan", **common)


@router.post("/search_data/", response_model=SpcevanPagination)
def getBySpecCode(*, db_session: Session = Depends(get_db), search_dict: SpcevanBySpecCode):
    spcevan = get_by_spec_code(db_session=db_session,search_dict=search_dict)
    return spcevan


@router.post("/", response_model=SpcevanRead)
def create_spcevan(*, db_session: Session = Depends(get_db), spcevan_in: SpcevanCreate,
                 current_user: DispatchUser = Depends(get_current_user)):
    """
    Create a new spcevan contact.
    """
    
    # spcevan = get_by_code(db_session=db_session,code=spcevan_in.code)
    
    
    # if spcevan:
    #     raise HTTPException(status_code=400, detail="The spcevan with this code already exists.")
    
    spcevan_in.created_by = current_user.email
    spcevan_in.updated_by = current_user.email
    try:
        spcevan = create(db_session=db_session, spcevan_in=spcevan_in)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return spcevan


@router.get("/{spcevan_id}", response_model=SpcevanRead)
def get_spcevan(*, db_session: Session = Depends(get_db), spcevan_id: int):
    """
    Get a spcevan contact.
    """
    spcevan = get(db_session=db_session, id=spcevan_id)
    if not spcevan:
        raise HTTPException(status_code=400, detail="The spcevan with this id does not exist.")
    return spcevan


@router.put("/{spcevan_id}", response_model=SpcevanRead)
def update_spcevan(
    *,
    db_session: Session = Depends(get_db),
    spcevan_id: int,
    spcevan_in: SpcevanUpdate, current_user: DispatchUser = Depends(get_current_user)
):
    """
    Update a spcevan contact.
    """
    spcevan = get(db_session=db_session, id=spcevan_id)
    if not spcevan:
        raise HTTPException(status_code=400, detail="The spcevan with this id does not exist.")

    spcevan = update(
        db_session=db_session,
        spcevan=spcevan,
        spcevan_in=spcevan_in,
    )
    return spcevan

@router.post("/update/", response_model=SpcevanRead)
def update_spcevan_new(
    *, 
    db_session: Session = Depends(get_db), 
    spcevan_in: SpcevanUpdateNew, 
    current_user: DispatchUser = Depends(get_current_user)
):
    spcevan_id = spcevan_in.id
    spcevan = get(db_session=db_session, id=spcevan_id)
    if not spcevan:
        raise HTTPException(status_code=400, detail="The spcevan with this id does not exist.")
    spcevan_in.data["updated_at"] = datetime.now(timezone.utc)
    spcevan_in.data["updated_by"] = current_user.email
    spcevan = update_new(
        db_session=db_session,
        spcevan=spcevan,
        spcevan_in=spcevan_in.data,
    )
    return spcevan


@router.put("/spcevan_code/{spcevan_code}", response_model=SpcevanRead)
def update_spcevan_by_code(
    *,
    db_session: Session = Depends(get_db),
    spcevan_code: str,
    spcevan_in: SpcevanUpdate, current_user: DispatchUser = Depends(get_current_user)
):
    """
    Update a spcevan contact.
    """
    spcevan = get_by_code(db_session=db_session, code=spcevan_code)
    if not spcevan:
        raise HTTPException(status_code=400, detail="The spcevan with this id does not exist.")

    spcevan_in.updated_by = current_user.email
    spcevan = update(
        db_session=db_session,
        spcevan=spcevan,
        spcevan_in=spcevan_in,
    )

    return spcevan


@router.delete("/{spcevan_id}", response_model=SpcevanRead)
def delete_spcevan(*, db_session: Session = Depends(get_db), spcevan_id: int):
    """
    Delete a spcevan contact.
    """
    spcevan = get(db_session=db_session, id=spcevan_id)
    if not spcevan:
        raise HTTPException(status_code=400, detail="The spcevan with this id does not exist.")

    return delete(db_session=db_session, spcevan_id=spcevan_id)



@router.post("/copy_to")
def create_by_copy_to(*, db_session: Session = Depends(get_db), copy_dict: SpcevanCopyToCode, current_user: DispatchUser = Depends(get_current_user)):
    spimpact = create_by_copy_spec_code(db_session=db_session, copy_dict=copy_dict, current_user=current_user)
    return spimpact