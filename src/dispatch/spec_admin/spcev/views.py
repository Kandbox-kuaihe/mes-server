from dispatch.database import get_db
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from dispatch.system_admin.auth.models import DispatchUser
from dispatch.system_admin.auth.service import get_current_user

from dispatch.database_util.service import common_parameters, search_filter_sort_paginate
from .models import (
    Spcev,
    SpcevCreate,
    SpcevPagination,
    SpcevRead,
    SpcevUpdate,
    SpcevUpdateNew,
    SpcevBySpecCode,
    SpcevCopyToCode
)
from .service import create, delete, get, get_by_code, update, update_new, get_by_spec_code, create_by_copy_spec_code
from datetime import datetime, timezone

router = APIRouter()


@router.get("/", response_model=SpcevPagination)
def get_filters(*, common: dict = Depends(common_parameters)):

    return search_filter_sort_paginate(model="Spcev", **common)


@router.post("/search_data/", response_model=SpcevPagination)
def getBySpecCode(*, db_session: Session = Depends(get_db), search_dict: SpcevBySpecCode):
    spcev = get_by_spec_code(db_session=db_session,search_dict=search_dict)
    return spcev


@router.post("/", response_model=SpcevRead)
def create_obj(*, db_session: Session = Depends(get_db), request_in: SpcevCreate,
                 current_user: DispatchUser = Depends(get_current_user)):
    """
    Create a new spcev contact.
    """
    
    # spcev = get_by_code(db_session=db_session,code=request_in.code)
    
    
    # if spcev:
    #     raise HTTPException(status_code=400, detail="The spcev with this code already exists.")
    
    request_in.created_by = current_user.email
    request_in.updated_by = current_user.email
    try:
        spcev = create(db_session=db_session, spcev_in=request_in)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return spcev


@router.get("/{spcev_id}", response_model=SpcevRead)
def get_spcev(*, db_session: Session = Depends(get_db), spcev_id: int):
    """
    Get a spcev contact.
    """
    spcev = get(db_session=db_session, id=spcev_id)
    if not spcev:
        raise HTTPException(status_code=400, detail="The spcev with this id does not exist.")
    return spcev


@router.put("/{spcev_id}", response_model=SpcevRead)
def update_spcev(
    *,
    db_session: Session = Depends(get_db),
    spcev_id: int,
    spcev_in: SpcevUpdate, current_user: DispatchUser = Depends(get_current_user)
):
    """
    Update a spcev contact.
    """
    spcev = get(db_session=db_session, id=spcev_id)
    if not spcev:
        raise HTTPException(status_code=400, detail="The spcev with this id does not exist.")

    spcev = update(
        db_session=db_session,
        spcev=spcev,
        spcev_in=spcev_in,
    )
    return spcev


@router.post("/update/", response_model=SpcevRead)
def update_spcev_new(
    *, 
    db_session: Session = Depends(get_db), 
    spcev_in: SpcevUpdateNew, 
    current_user: DispatchUser = Depends(get_current_user)
):
    spcev_id = spcev_in.id
    spcev = get(db_session=db_session, id=spcev_id)
    if not spcev:
        raise HTTPException(status_code=400, detail="The spcev with this id does not exist.")
    spcev_in.data["updated_at"] = datetime.now(timezone.utc)
    spcev_in.data["updated_by"] = current_user.email
    sptcert = update_new(
        db_session=db_session,
        spcev=spcev,
        spcev_in=spcev_in.data,
    )
    return spcev


@router.put("/spcev_code/{spcev_code}", response_model=SpcevRead)
def update_spcev_by_code(
    *,
    db_session: Session = Depends(get_db),
    spcev_code: str,
    spcev_in: SpcevUpdate, current_user: DispatchUser = Depends(get_current_user)
):
    """
    Update a spcev contact.
    """
    spcev = get_by_code(db_session=db_session, code=spcev_code)
    if not spcev:
        raise HTTPException(status_code=400, detail="The spcev with this id does not exist.")

    spcev_in.updated_by = current_user.email
    spcev = update(
        db_session=db_session,
        spcev=spcev,
        spcev_in=spcev_in,
    )

    return spcev


@router.delete("/{spcev_id}", response_model=SpcevRead)
def delete_spcev(*, db_session: Session = Depends(get_db), spcev_id: int):
    """
    Delete a spcev contact.
    """
    spcev = get(db_session=db_session, id=spcev_id)
    if not spcev:
        raise HTTPException(status_code=400, detail="The spcev with this id does not exist.")

    return delete(db_session=db_session, id=spcev_id)



@router.post("/copy_to")
def create_by_copy_to(*, db_session: Session = Depends(get_db), copy_dict: SpcevCopyToCode, current_user: DispatchUser = Depends(get_current_user)):
    spimpact = create_by_copy_spec_code(db_session=db_session, copy_dict=copy_dict, current_user=current_user)
    return spimpact