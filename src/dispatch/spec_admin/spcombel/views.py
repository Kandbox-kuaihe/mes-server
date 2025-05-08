from dispatch.database import get_db
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from dispatch.system_admin.auth.models import DispatchUser
from dispatch.system_admin.auth.service import get_current_user

from dispatch.database_util.service import common_parameters, search_filter_sort_paginate
from .models import Spcombel as SpComBel
from .models import (
    SpComBelCreate,
    SpComBelPagination,
    SpComBelRead,
    SpComBelUpdate,
    SpComBelUpdateNew,
    SpComBelBySpecCode,
    SpComBelCopyToCode
)
from .service import create, delete, get, get_by_code, update, update_new, get_by_spec_code, create_by_copy_spec_code
from datetime import datetime, timezone

router = APIRouter()


@router.get("/", response_model=SpComBelPagination)
def get_spComBels(*, common: dict = Depends(common_parameters)):

    return search_filter_sort_paginate(model="Spcombel", **common)

@router.post("/search_data/", response_model=SpComBelPagination)
def getBySpecCode(*, db_session: Session = Depends(get_db), search_dict: SpComBelBySpecCode):
    spcombel = get_by_spec_code(db_session=db_session,search_dict=search_dict)
    return spcombel


@router.post("/", response_model=SpComBelRead)
def create_spComBel(*, db_session: Session = Depends(get_db), spComBel_in: SpComBelCreate,
                 current_user: DispatchUser = Depends(get_current_user)):
    """
    Create a new spComBel contact.
    """
    
    # spComBel = get_by_code(db_session=db_session,code=spComBel_in.code)
    
    
    # if spComBel:
    #     raise HTTPException(status_code=400, detail="The spComBel with this code already exists.")
    
    spComBel_in.created_by = current_user.email
    spComBel_in.updated_by = current_user.email
    try:
        spComBel = create(db_session=db_session, spComBel_in=spComBel_in)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return spComBel


@router.get("/{spComBel_id}", response_model=SpComBelRead)
def get_spComBel(*, db_session: Session = Depends(get_db), spComBel_id: int):
    """
    Get a spComBel contact.
    """
    spComBel = get(db_session=db_session, id=spComBel_id)
    if not spComBel:
        raise HTTPException(status_code=400, detail="The spComBel with this id does not exist.")
    return spComBel


@router.put("/{spComBel_id}", response_model=SpComBelRead)
def update_spComBel(
    *,
    db_session: Session = Depends(get_db),
    spComBel_id: int,
    spComBel_in: SpComBelUpdate, current_user: DispatchUser = Depends(get_current_user)
):
    """
    Update a spComBel contact.
    """
    spComBel = get(db_session=db_session, id=spComBel_id)
    if not spComBel:
        raise HTTPException(status_code=400, detail="The spComBel with this id does not exist.")

    spComBel = update(
        db_session=db_session,
        spComBel=spComBel,
        spComBel_in=spComBel_in,
    )
    return spComBel

@router.post("/update/", response_model=SpComBelRead)
def update_spcombel_new(
    *, 
    db_session: Session = Depends(get_db), 
    spcombel_in: SpComBelUpdateNew, 
    current_user: DispatchUser = Depends(get_current_user)
):
    spcombel_id = spcombel_in.id
    spComBel = get(db_session=db_session, id=spcombel_id)
    if not spComBel:
        raise HTTPException(status_code=400, detail="The spComBel with this id does not exist.")
    spcombel_in.data["updated_at"] = datetime.now(timezone.utc)
    spcombel_in.data["updated_by"] = current_user.email
    spComBel = update_new(
        db_session=db_session,
        spComBel=spComBel,
        spComBel_in=spcombel_in.data,
    )
    return spComBel


@router.put("/spComBel_code/{spComBel_code}", response_model=SpComBelRead)
def update_spComBel_by_code(
    *,
    db_session: Session = Depends(get_db),
    spComBel_code: str,
    spComBel_in: SpComBelUpdate, current_user: DispatchUser = Depends(get_current_user)
):
    """
    Update a spComBel contact.
    """
    spComBel = get_by_code(db_session=db_session, code=spComBel_code)
    if not spComBel:
        raise HTTPException(status_code=400, detail="The spComBel with this id does not exist.")

    spComBel_in.updated_by = current_user.email
    spComBel = update(
        db_session=db_session,
        spComBel=spComBel,
        spComBel_in=spComBel_in,
    )

    return spComBel


@router.delete("/{spComBel_id}", response_model=SpComBelRead)
def delete_spComBel(*, db_session: Session = Depends(get_db), spComBel_id: int):
    """
    Delete a spComBel contact.
    """
    spComBel = get(db_session=db_session, id=spComBel_id)
    if not spComBel:
        raise HTTPException(status_code=400, detail="The spComBel with this id does not exist.")

    return delete(db_session=db_session, spComBel_id=spComBel_id)



@router.post("/copy_to")
def create_by_copy_to(*, db_session: Session = Depends(get_db), copy_dict: SpComBelCopyToCode, current_user: DispatchUser = Depends(get_current_user)):
    print("-=-=-=--")
    spimpact = create_by_copy_spec_code(db_session=db_session, copy_dict=copy_dict, current_user=current_user)
    return spimpact