from dispatch.database import get_db
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from dispatch.system_admin.auth.models import DispatchUser
from dispatch.system_admin.auth.service import get_current_user

from dispatch.database_util.service import common_parameters, search_filter_sort_paginate
from .models import (
    Spscond,
    SpscondCreate,
    SpscondPagination,
    SpscondRead,
    SpscondUpdate,
    SpscondUpdateNew,
    SpscondBySpecCode,
    SpscondCopyToCode
)
from .service import create, delete, get, get_by_code, update, update_new, get_by_spec_code, create_by_copy_spec_code
from datetime import datetime, timezone

router = APIRouter()


@router.get("/", response_model=SpscondPagination)
def get_filters(*, common: dict = Depends(common_parameters)):

    return search_filter_sort_paginate(model="Spscond", **common)


@router.post("/search_data/", response_model=SpscondPagination)
def getBySpecCode(*, db_session: Session = Depends(get_db), search_dict: SpscondBySpecCode):
    spscond = get_by_spec_code(db_session=db_session,search_dict=search_dict)
    return spscond


@router.post("/", response_model=SpscondRead)
def create_obj(*, db_session: Session = Depends(get_db), request_in: SpscondCreate,
                 current_user: DispatchUser = Depends(get_current_user)):
    """
    Create a new spscond contact.
    """
    
    # spscond = get_by_code(db_session=db_session,code=request_in.code)
    
    
    # if spscond:
    #     raise HTTPException(status_code=400, detail="The spscond with this code already exists.")
    
    request_in.created_by = current_user.email
    request_in.updated_by = current_user.email
    try:
        spscond = create(db_session=db_session, spscond_in=request_in)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return spscond


@router.get("/{spscond_id}", response_model=SpscondRead)
def get_spscond(*, db_session: Session = Depends(get_db), spscond_id: int):
    """
    Get a spscond contact.
    """
    spscond = get(db_session=db_session, id=spscond_id)
    if not spscond:
        raise HTTPException(status_code=400, detail="The spscond with this id does not exist.")
    return spscond


@router.put("/{spscond_id}", response_model=SpscondRead)
def update_spscond(
    *,
    db_session: Session = Depends(get_db),
    spscond_id: int,
    spscond_in: SpscondUpdate, current_user: DispatchUser = Depends(get_current_user)
):
    """
    Update a spscond contact.
    """
    spscond = get(db_session=db_session, id=spscond_id)
    if not spscond:
        raise HTTPException(status_code=400, detail="The spscond with this id does not exist.")

    spscond = update(
        db_session=db_session,
        spscond=spscond,
        spscond_in=spscond_in,
    )
    return spscond


@router.post("/update/", response_model=SpscondRead)
def update_spscond_new(
    *, 
    db_session: Session = Depends(get_db), 
    spscond_in: SpscondUpdateNew, 
    current_user: DispatchUser = Depends(get_current_user)
):
    spscond_id = spscond_in.id
    spscond = get(db_session=db_session, id=spscond_id)
    if not spscond:
        raise HTTPException(status_code=400, detail="The spscond with this id does not exist.")
    spscond_in.data["updated_at"] = datetime.now(timezone.utc)
    spscond_in.data["updated_by"] = current_user.email
    spscond = update_new(
        db_session=db_session,
        spscond=spscond,
        spscond_in=spscond_in.data,
    )
    return spscond


@router.put("/spscond_code/{spscond_code}", response_model=SpscondRead)
def update_spscond_by_code(
    *,
    db_session: Session = Depends(get_db),
    spscond_code: str,
    spscond_in: SpscondUpdate, current_user: DispatchUser = Depends(get_current_user)
):
    """
    Update a spscond contact.
    """
    spscond = get_by_code(db_session=db_session, code=spscond_code)
    if not spscond:
        raise HTTPException(status_code=400, detail="The spscond with this id does not exist.")

    spscond_in.updated_by = current_user.email
    spscond = update(
        db_session=db_session,
        spscond=spscond,
        spscond_in=spscond_in,
    )

    return spscond


@router.delete("/{spscond_id}", response_model=SpscondRead)
def delete_spscond(*, db_session: Session = Depends(get_db), spscond_id: int):
    """
    Delete a spscond contact.
    """
    spscond = get(db_session=db_session, id=spscond_id)
    if not spscond:
        raise HTTPException(status_code=400, detail="The spscond with this id does not exist.")

    return delete(db_session=db_session, id=spscond_id)



@router.post("/copy_to")
def create_by_copy_to(*, db_session: Session = Depends(get_db), copy_dict: SpscondCopyToCode, current_user: DispatchUser = Depends(get_current_user)):
    spimpact = create_by_copy_spec_code(db_session=db_session, copy_dict=copy_dict, current_user=current_user)
    return spimpact