from dispatch.database import get_db
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from dispatch.system_admin.auth.models import DispatchUser
from dispatch.system_admin.auth.service import get_current_user

from dispatch.database_util.service import common_parameters, search_filter_sort_paginate
from .models import (
    Sptcert,
    SptcertCreate,
    SptcertPagination,
    SptcertRead,
    SptcertUpdate,
    SptcertUpdateNew,
    SptcertBySpecCode,
    SptcertCopyToCode,
    SptcertCopyToCode
)
from .service import create, delete, get, get_by_code, update, update_new, get_by_spec_code, create_by_copy_spec_code
from datetime import datetime, timezone

router = APIRouter()


@router.get("/", response_model=SptcertPagination)
def get_filters(*, common: dict = Depends(common_parameters)):

    return search_filter_sort_paginate(model="Sptcert", **common)


@router.post("/search_data/", response_model=SptcertPagination)
def getBySpecCode(*, db_session: Session = Depends(get_db), search_dict: SptcertBySpecCode):
    sptcert = get_by_spec_code(db_session=db_session,search_dict=search_dict)
    return sptcert


@router.post("/", response_model=SptcertRead)
def create_obj(*, db_session: Session = Depends(get_db), request_in: SptcertCreate,
                 current_user: DispatchUser = Depends(get_current_user)):
    """
    Create a new sptcert contact.
    """
    
    # sptcert = get_by_code(db_session=db_session,code=request_in.code)
    
    
    # if sptcert:
    #     raise HTTPException(status_code=400, detail="The sptcert with this code already exists.")
    
    request_in.created_by = current_user.email
    request_in.updated_by = current_user.email
    try:
        sptcert = create(db_session=db_session, sptcert_in=request_in)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return sptcert


@router.get("/{sptcert_id}", response_model=SptcertRead)
def get_sptcert(*, db_session: Session = Depends(get_db), sptcert_id: int):
    """
    Get a sptcert contact.
    """
    sptcert = get(db_session=db_session, id=sptcert_id)
    if not sptcert:
        raise HTTPException(status_code=400, detail="The sptcert with this id does not exist.")
    return sptcert


@router.put("/{sptcert_id}", response_model=SptcertRead)
def update_sptcert(
    *,
    db_session: Session = Depends(get_db),
    sptcert_id: int,
    sptcert_in: SptcertUpdate, current_user: DispatchUser = Depends(get_current_user)
):
    """
    Update a sptcert contact.
    """
    sptcert = get(db_session=db_session, id=sptcert_id)
    if not sptcert:
        raise HTTPException(status_code=400, detail="The sptcert with this id does not exist.")

    sptcert = update(
        db_session=db_session,
        sptcert=sptcert,
        sptcert_in=sptcert_in,
    )
    return sptcert


@router.post("/update/", response_model=SptcertRead)
def update_sptcert_new(
    *, 
    db_session: Session = Depends(get_db), 
    sptcert_in: SptcertUpdateNew, 
    current_user: DispatchUser = Depends(get_current_user)
):
    sptcert_id = sptcert_in.id
    sptcert = get(db_session=db_session, id=sptcert_id)
    if not sptcert:
        raise HTTPException(status_code=400, detail="The sptcert with this id does not exist.")
    sptcert_in.data["updated_at"] = datetime.now(timezone.utc)
    sptcert_in.data["updated_by"] = current_user.email
    sptcert = update_new(
        db_session=db_session,
        sptcert=sptcert,
        sptcert_in=sptcert_in.data,
    )
    return sptcert


@router.put("/sptcert_code/{sptcert_code}", response_model=SptcertRead)
def update_sptcert_by_code(
    *,
    db_session: Session = Depends(get_db),
    sptcert_code: str,
    sptcert_in: SptcertUpdate, current_user: DispatchUser = Depends(get_current_user)
):
    """
    Update a sptcert contact.
    """
    sptcert = get_by_code(db_session=db_session, code=sptcert_code)
    if not sptcert:
        raise HTTPException(status_code=400, detail="The sptcert with this id does not exist.")

    sptcert_in.updated_by = current_user.email
    sptcert = update(
        db_session=db_session,
        sptcert=sptcert,
        sptcert_in=sptcert_in,
    )

    return sptcert


@router.delete("/{sptcert_id}", response_model=SptcertRead)
def delete_sptcert(*, db_session: Session = Depends(get_db), sptcert_id: int):
    """
    Delete a sptcert contact.
    """
    sptcert = get(db_session=db_session, id=sptcert_id)
    if not sptcert:
        raise HTTPException(status_code=400, detail="The sptcert with this id does not exist.")

    return delete(db_session=db_session, id=sptcert_id)



@router.post("/copy_to")
def create_by_copy_to(*, db_session: Session = Depends(get_db), copy_dict: SptcertCopyToCode, current_user: DispatchUser = Depends(get_current_user)):
    spimpact = create_by_copy_spec_code(db_session=db_session, copy_dict=copy_dict, current_user=current_user)
    return spimpact