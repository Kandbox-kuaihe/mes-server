from dispatch.database import get_db
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from dispatch.system_admin.auth.models import DispatchUser
from dispatch.system_admin.auth.service import get_current_user

from dispatch.database_util.service import common_parameters, search_filter_sort_paginate
from .models import (
    Spmillref,
    SpmillrefCreate,
    SpmillrefPagination,
    SpmillrefRead,
    SpmillrefUpdate,
    SpmillrefUpdateNew,
    SpmillrefBySpecCode,
    SpmillrefCopyToCode
)
from .service import create, delete, get, get_by_code, update, update_new, get_by_spec_code, create_by_copy_spec_code
from datetime import datetime, timezone

router = APIRouter()


@router.get("/", response_model=SpmillrefPagination)
def get_filters(*, common: dict = Depends(common_parameters)):

    return search_filter_sort_paginate(model="Spmillref", **common)


@router.post("/search_data/", response_model=SpmillrefPagination)
def getBySpecCode(*, db_session: Session = Depends(get_db), search_dict: SpmillrefBySpecCode):
    spmillref = get_by_spec_code(db_session=db_session,search_dict=search_dict)
    return spmillref


@router.post("/", response_model=SpmillrefRead)
def create_obj(*, db_session: Session = Depends(get_db), request_in: SpmillrefCreate,
                 current_user: DispatchUser = Depends(get_current_user)):
    """
    Create a new spmillref contact.
    """
    
    # spmillref = get_by_code(db_session=db_session,code=request_in.code)
    
    
    # if spmillref:
    #     raise HTTPException(status_code=400, detail="The spmillref with this code already exists.")
    
    request_in.created_by = current_user.email
    request_in.updated_by = current_user.email
    try:
        spmillref = create(db_session=db_session, spmillref_in=request_in)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return spmillref


@router.get("/{spmillref_id}", response_model=SpmillrefRead)
def get_spmillref(*, db_session: Session = Depends(get_db), spmillref_id: int):
    """
    Get a spmillref contact.
    """
    spmillref = get(db_session=db_session, id=spmillref_id)
    if not spmillref:
        raise HTTPException(status_code=400, detail="The spmillref with this id does not exist.")
    return spmillref


@router.put("/{spmillref_id}", response_model=SpmillrefRead)
def update_spmillref(
    *,
    db_session: Session = Depends(get_db),
    spmillref_id: int,
    spmillref_in: SpmillrefUpdate, current_user: DispatchUser = Depends(get_current_user)
):
    """
    Update a spmillref contact.
    """
    spmillref = get(db_session=db_session, id=spmillref_id)
    if not spmillref:
        raise HTTPException(status_code=400, detail="The spmillref with this id does not exist.")

    spmillref = update(
        db_session=db_session,
        spmillref=spmillref,
        spmillref_in=spmillref_in,
    )
    return spmillref


@router.post("/update/", response_model=SpmillrefRead)
def update_spmillref_new(
    *, 
    db_session: Session = Depends(get_db), 
    spmillref_in: SpmillrefUpdateNew, 
    current_user: DispatchUser = Depends(get_current_user)
):
    spmillref_id = spmillref_in.id
    spmillref = get(db_session=db_session, id=spmillref_id)
    if not spmillref:
        raise HTTPException(status_code=400, detail="The spmillref with this id does not exist.")
    spmillref_in.data["updated_at"] = datetime.now(timezone.utc)
    spmillref_in.data["updated_by"] = current_user.email
    spmillref = update_new(
        db_session=db_session,
        spmillref=spmillref,
        spmillref_in=spmillref_in.data,
    )
    return spmillref


@router.put("/spmillref_code/{spmillref_code}", response_model=SpmillrefRead)
def update_spmillref_by_code(
    *,
    db_session: Session = Depends(get_db),
    spmillref_code: str,
    spmillref_in: SpmillrefUpdate, current_user: DispatchUser = Depends(get_current_user)
):
    """
    Update a spmillref contact.
    """
    spmillref = get_by_code(db_session=db_session, code=spmillref_code)
    if not spmillref:
        raise HTTPException(status_code=400, detail="The spmillref with this id does not exist.")

    spmillref_in.updated_by = current_user.email
    spmillref = update(
        db_session=db_session,
        spmillref=spmillref,
        spmillref_in=spmillref_in,
    )

    return spmillref


@router.delete("/{spmillref_id}", response_model=SpmillrefRead)
def delete_spmillref(*, db_session: Session = Depends(get_db), spmillref_id: int):
    """
    Delete a spmillref contact.
    """
    spmillref = get(db_session=db_session, id=spmillref_id)
    if not spmillref:
        raise HTTPException(status_code=400, detail="The spmillref with this id does not exist.")

    return delete(db_session=db_session, id=spmillref_id)



@router.post("/copy_to")
def create_by_copy_to(*, db_session: Session = Depends(get_db), copy_dict: SpmillrefCopyToCode, current_user: DispatchUser = Depends(get_current_user)):
    spimpact = create_by_copy_spec_code(db_session=db_session, copy_dict=copy_dict, current_user=current_user)
    return spimpact