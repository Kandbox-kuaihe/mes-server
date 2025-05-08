from dispatch.database import get_db
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from dispatch.system_admin.auth.models import DispatchUser
from dispatch.system_admin.auth.service import get_current_user

from dispatch.database_util.service import common_parameters, search_filter_sort_paginate
from .models import (
    Spyield,
    SpyieldCreate,
    SpyieldPagination,
    SpyieldRead,
    SpyieldUpdate,
    SpyieldUpdateNew,
    SpyieldBySpecCode,
    SpyieldCopyToCode
)
from .service import create, delete, get, get_by_code, update, update_new, get_by_spec_code, create_by_copy_spec_code
from datetime import datetime, timezone

router = APIRouter()


@router.get("/", response_model=SpyieldPagination)
def get_filters(*, common: dict = Depends(common_parameters)):

    return search_filter_sort_paginate(model="Spyield", **common)


@router.post("/search_data/", response_model=SpyieldPagination)
def getBySpecCode(*, db_session: Session = Depends(get_db), search_dict: SpyieldBySpecCode):
    spyield = get_by_spec_code(db_session=db_session,search_dict=search_dict)
    return spyield


@router.post("/", response_model=SpyieldRead)
def create_obj(*, db_session: Session = Depends(get_db), request_in: SpyieldCreate,
                 current_user: DispatchUser = Depends(get_current_user)):
    """
    Create a new spyield contact.
    """
    
    # spyield = get_by_code(db_session=db_session,code=request_in.code)
    
    
    # if spyield:
    #     raise HTTPException(status_code=400, detail="The spyield with this code already exists.")
    
    request_in.created_by = current_user.email
    request_in.updated_by = current_user.email
    try:
        spyield = create(db_session=db_session, spyield_in=request_in)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return spyield


@router.get("/{spyield_id}", response_model=SpyieldRead)
def get_spyield(*, db_session: Session = Depends(get_db), spyield_id: int):
    """
    Get a spyield contact.
    """
    spyield = get(db_session=db_session, id=spyield_id)
    if not spyield:
        raise HTTPException(status_code=400, detail="The spyield with this id does not exist.")
    return spyield


@router.put("/{spyield_id}", response_model=SpyieldRead)
def update_spyield(
    *,
    db_session: Session = Depends(get_db),
    spyield_id: int,
    spyield_in: SpyieldUpdate, current_user: DispatchUser = Depends(get_current_user)
):
    """
    Update a spyield contact.
    """
    spyield = get(db_session=db_session, id=spyield_id)
    if not spyield:
        raise HTTPException(status_code=400, detail="The spyield with this id does not exist.")

    spyield = update(
        db_session=db_session,
        spyield=spyield,
        spyield_in=spyield_in,
    )
    return spyield

@router.post("/update/", response_model=SpyieldRead)
def update_spyield_new(
    *, 
    db_session: Session = Depends(get_db), 
    spyield_in: SpyieldUpdateNew, 
    current_user: DispatchUser = Depends(get_current_user)
):
    spyield_id = spyield_in.id
    spyield = get(db_session=db_session, id=spyield_id)
    if not spyield:
        raise HTTPException(status_code=400, detail="The spyield with this id does not exist.")
    spyield_in.data["updated_at"] = datetime.now(timezone.utc)
    spyield_in.data["updated_by"] = current_user.email
    spYield = update_new(
        db_session=db_session,
        spYield=spyield,
        spYield_in=spyield_in.data,
    )
    return spYield


@router.put("/spyield_code/{spyield_code}", response_model=SpyieldRead)
def update_spyield_by_code(
    *,
    db_session: Session = Depends(get_db),
    spyield_code: str,
    spyield_in: SpyieldUpdate, current_user: DispatchUser = Depends(get_current_user)
):
    """
    Update a spyield contact.
    """
    spyield = get_by_code(db_session=db_session, code=spyield_code)
    if not spyield:
        raise HTTPException(status_code=400, detail="The spyield with this id does not exist.")

    spyield_in.updated_by = current_user.email
    spyield = update(
        db_session=db_session,
        spyield=spyield,
        spyield_in=spyield_in,
    )

    return spyield


@router.delete("/{spyield_id}", response_model=SpyieldRead)
def delete_spyield(*, db_session: Session = Depends(get_db), spyield_id: int):
    """
    Delete a spyield contact.
    """
    spyield = get(db_session=db_session, id=spyield_id)
    if not spyield:
        raise HTTPException(status_code=400, detail="The spyield with this id does not exist.")

    return delete(db_session=db_session, id=spyield_id)


@router.post("/copy_to")
def create_by_copy_to(*, db_session: Session = Depends(get_db), copy_dict: SpyieldCopyToCode, current_user: DispatchUser = Depends(get_current_user)):
    spimpact = create_by_copy_spec_code(db_session=db_session, copy_dict=copy_dict, current_user=current_user)
    return spimpact