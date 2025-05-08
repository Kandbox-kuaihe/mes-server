from dispatch.database import get_db
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from dispatch.system_admin.auth.models import DispatchUser
from dispatch.system_admin.auth.service import get_current_user

from dispatch.database_util.service import common_parameters, search_filter_sort_paginate
from .models import Spelong as SpeLong
from .models import (
    SpeLongCreate,
    SpeLongPagination,
    SpeLongRead,
    SpeLongUpdate,
    SpeLongUpdateNew,
    SpeLongBySpecCode,
    SpeLongCopyToCode
)
from .service import create, delete, get, get_by_code, update, update_new, get_by_spec_code, create_by_copy_spec_code
from datetime import datetime, timezone

router = APIRouter()


@router.get("/", response_model=SpeLongPagination)
def get_speLongs(*, common: dict = Depends(common_parameters)):

    return search_filter_sort_paginate(model="Spelong", **common)


@router.post("/search_data/", response_model=SpeLongPagination)
def getBySpecCode(*, db_session: Session = Depends(get_db), search_dict: SpeLongBySpecCode):
    spimpact = get_by_spec_code(db_session=db_session,search_dict=search_dict)
    return spimpact


@router.post("/", response_model=SpeLongRead)
def create_speLong(*, db_session: Session = Depends(get_db), speLong_in: SpeLongCreate,
                 current_user: DispatchUser = Depends(get_current_user)):
    """
    Create a new specLong contact.
    """
    
    # speLong = get_by_code(db_session=db_session,code=speLong_in.code)
    
    
    # if speLong:
    #     raise HTTPException(status_code=400, detail="The specLong with this code already exists.")
    
    speLong_in.created_by = current_user.email
    speLong_in.updated_by = current_user.email
    try:
        speLong = create(db_session=db_session, spelong_in=speLong_in)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return speLong


@router.get("/{speLong_id}", response_model=SpeLongRead)
def get_speLong(*, db_session: Session = Depends(get_db), speLong_id: int):
    """
    Get a specLong contact.
    """
    speLong = get(db_session=db_session, id=speLong_id)
    if not speLong:
        raise HTTPException(status_code=400, detail="The specLong with this id does not exist.")
    return speLong


@router.put("/{speLong_id}", response_model=SpeLongRead)
def update_speLong(
    *,
    db_session: Session = Depends(get_db),
    speLong_id: int,
    speLong_in: SpeLongUpdate, current_user: DispatchUser = Depends(get_current_user)
):
    """
    Update a specLong contact.
    """
    speLong = get(db_session=db_session, id=speLong_id)
    if not speLong:
        raise HTTPException(status_code=400, detail="The specLong with this id does not exist.")

    speLong = update(
        db_session=db_session,
        spelong=speLong,
        spelong_in=speLong_in,
    )
    return speLong

@router.post("/update/", response_model=SpeLongRead)
def update_spelong_new(
    *, 
    db_session: Session = Depends(get_db), 
    spelong_in: SpeLongUpdateNew, 
    current_user: DispatchUser = Depends(get_current_user)
):
    speLong_id = spelong_in.id
    speLong = get(db_session=db_session, id=speLong_id)
    if not speLong:
        raise HTTPException(status_code=400, detail="The specLong with this id does not exist.")
    spelong_in.data["updated_at"] = datetime.now(timezone.utc)
    spelong_in.data["updated_by"] = current_user.email
    speLong = update_new(
        db_session=db_session,
        speLong=speLong,
        speLong_in=spelong_in.data,
    )
    return speLong


@router.put("/speLong_code/{specLong_code}", response_model=SpeLongRead)
def update_speLong_by_code(
    *,
    db_session: Session = Depends(get_db),
    speLong_code: str,
    speLong_in: SpeLongUpdate, current_user: DispatchUser = Depends(get_current_user)
):
    """
    Update a specLong contact.
    """
    speLong = get_by_code(db_session=db_session, code=speLong_code)
    if not speLong:
        raise HTTPException(status_code=400, detail="The specLong with this id does not exist.")

    speLong_in.updated_by = current_user.email
    specLong = update(
        db_session=db_session,
        speLong=speLong,
        specLong_in=speLong_in,
    )

    return specLong


@router.delete("/{speLong_id}", response_model=SpeLongRead)
def delete_speLong(*, db_session: Session = Depends(get_db), speLong_id: int):
    """
    Delete a specLong contact.
    """
    specLong = get(db_session=db_session, id=speLong_id)
    if not specLong:
        raise HTTPException(status_code=400, detail="The specLong with this id does not exist.")

    return delete(db_session=db_session, spelong_id=speLong_id)


@router.post("/copy_to")
def create_by_copy_to(*, db_session: Session = Depends(get_db), copy_dict: SpeLongCopyToCode, current_user: DispatchUser = Depends(get_current_user)):
    spimpact = create_by_copy_spec_code(db_session=db_session, copy_dict=copy_dict, current_user=current_user)
    return spimpact