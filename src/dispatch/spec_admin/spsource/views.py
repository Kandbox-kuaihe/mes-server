from dispatch.database import get_db
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from dispatch.system_admin.auth.models import DispatchUser
from dispatch.system_admin.auth.service import get_current_user

from dispatch.database_util.service import common_parameters, search_filter_sort_paginate
from .models import (
    Spsource,
    SpsourceCreate,
    SpsourcePagination,
    SpsourceRead,
    SpsourceUpdate,
    SpsourceUpdateNew,
    SpsourceBySpecCode,
    SpsourceCopyToCode
)
from .service import create, delete, get, get_by_code, update, update_new, get_by_spec_code, create_by_copy_spec_code
from datetime import datetime, timezone

router = APIRouter()


@router.get("/", response_model=SpsourcePagination)
def get_filters(*, common: dict = Depends(common_parameters)):
    result = search_filter_sort_paginate(model="Spsource", **common)
    result["items"] = [item for item in result["items"] if getattr(item, "is_deleted", 0) != 1]

    return result

@router.post("/search_data/", response_model=SpsourcePagination)
def getBySpecCode(*, db_session: Session = Depends(get_db), search_dict: SpsourceBySpecCode):
    spsource = get_by_spec_code(db_session=db_session,search_dict=search_dict)
    return spsource


@router.post("/", response_model=SpsourceRead)
def create_obj(*, db_session: Session = Depends(get_db), request_in: SpsourceCreate,
                 current_user: DispatchUser = Depends(get_current_user)):
    """
    Create a new spsource contact.
    """
    
    # spsource = get_by_code(db_session=db_session,code=request_in.code)
    
    
    # if spsource:
    #     raise HTTPException(status_code=400, detail="The spsource with this code already exists.")
    
    request_in.created_by = current_user.email
    request_in.updated_by = current_user.email
    try:
        spsource = create(db_session=db_session, spsource_in=request_in)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return spsource


@router.get("/{spsource_id}", response_model=SpsourceRead)
def get_spsource(*, db_session: Session = Depends(get_db), spsource_id: int):
    """
    Get a spsource contact.
    """
    spsource = get(db_session=db_session, id=spsource_id)
    if not spsource:
        raise HTTPException(status_code=400, detail="The spsource with this id does not exist.")
    return spsource


@router.put("/{spsource_id}", response_model=SpsourceRead)
def update_spsource(
    *,
    db_session: Session = Depends(get_db),
    spsource_id: int,
    spsource_in: SpsourceUpdate, current_user: DispatchUser = Depends(get_current_user)
):
    """
    Update a spsource contact.
    """
    spsource = get(db_session=db_session, id=spsource_id)
    if not spsource:
        raise HTTPException(status_code=400, detail="The spsource with this id does not exist.")

    spsource = update(
        db_session=db_session,
        spsource=spsource,
        spsource_in=spsource_in,
    )
    return spsource


@router.post("/update/", response_model=SpsourceRead)
def update_spsource_new(
    *, 
    db_session: Session = Depends(get_db), 
    spsource_in: SpsourceUpdateNew, 
    current_user: DispatchUser = Depends(get_current_user)
):
    spsource_id = spsource_in.id
    spsource = get(db_session=db_session, id=spsource_id)
    if not spsource:
        raise HTTPException(status_code=400, detail="The spsource with this id does not exist.")
    spsource_in.data["updated_at"] = datetime.now(timezone.utc)
    spsource_in.data["updated_by"] = current_user.email
    spsource = update_new(
        db_session=db_session,
        spsource=spsource,
        spsource_in=spsource_in.data,
    )
    return spsource


@router.put("/spsource_code/{spsource_code}", response_model=SpsourceRead)
def update_spsource_by_code(
    *,
    db_session: Session = Depends(get_db),
    spsource_code: str,
    spsource_in: SpsourceUpdate, current_user: DispatchUser = Depends(get_current_user)
):
    """
    Update a spsource contact.
    """
    spsource = get_by_code(db_session=db_session, code=spsource_code)
    if not spsource:
        raise HTTPException(status_code=400, detail="The spsource with this id does not exist.")

    spsource_in.updated_by = current_user.email
    spsource = update(
        db_session=db_session,
        spsource=spsource,
        spsource_in=spsource_in,
    )

    return spsource


@router.delete("/{spsource_id}", response_model=SpsourceRead)
def delete_spsource(*, db_session: Session = Depends(get_db), spsource_id: int):
    """
    Delete a spsource contact.
    """
    spsource = get(db_session=db_session, id=spsource_id)
    if not spsource:
        raise HTTPException(status_code=400, detail="The spsource with this id does not exist.")

    return delete(db_session=db_session, id=spsource_id)



@router.post("/copy_to")
def create_by_copy_to(*, db_session: Session = Depends(get_db), copy_dict: SpsourceCopyToCode, current_user: DispatchUser = Depends(get_current_user)):
    spimpact = create_by_copy_spec_code(db_session=db_session, copy_dict=copy_dict, current_user=current_user)
    return spimpact