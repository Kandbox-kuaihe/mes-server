from dispatch.database import get_db
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from dispatch.system_admin.auth.models import DispatchUser
from dispatch.system_admin.auth.service import get_current_user

from dispatch.database_util.service import common_parameters, search_filter_sort_paginate
from .models import (
    Spprodan,
    SpprodanCreate,
    SpprodanPagination,
    SpprodanRead,
    SpprodanUpdate,
    SpprodanUpdateNew,
    SpprodanBySpecCode,
    SpprodanCopyToCode
)
from .service import create, delete, get, get_by_code, update, update_new, get_by_spec_code, create_by_copy_spec_code
from datetime import datetime, timezone

router = APIRouter()


@router.get("/", response_model=SpprodanPagination)
def get_spprodans(*, common: dict = Depends(common_parameters)):

    spprodan = search_filter_sort_paginate(model="Spprodan", **common)
    ids = []
    for i in spprodan["items"]:
        ids.append(len(i.spprodan_other_element))
    print(ids)
    spprodan["other_element_num"] = ids
    return spprodan

@router.post("/search_data/", response_model=SpprodanPagination)
def getBySpecCode(*, db_session: Session = Depends(get_db), search_dict: SpprodanBySpecCode):
    spprodan = get_by_spec_code(db_session=db_session,search_dict=search_dict)
    return spprodan


@router.post("/", response_model=SpprodanRead)
def create_spprodan(*, db_session: Session = Depends(get_db), spprodan_in: SpprodanCreate,
                 current_user: DispatchUser = Depends(get_current_user)):
    """
    Create a new spprodan contact.
    """
    
    # spprodan = get_by_code(db_session=db_session,code=spprodan_in.code)
    
    
    # if spprodan:
    #     raise HTTPException(status_code=400, detail="The spprodan with this code already exists.")
    
    spprodan_in.created_by = current_user.email
    spprodan_in.updated_by = current_user.email
    try:
        spprodan = create(db_session=db_session, spprodan_in=spprodan_in)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return spprodan


@router.get("/{spprodan_id}", response_model=SpprodanRead)
def get_spprodan(*, db_session: Session = Depends(get_db), spprodan_id: int):
    """
    Get a spprodan contact.
    """
    spprodan = get(db_session=db_session, id=spprodan_id)
    if not spprodan:
        raise HTTPException(status_code=400, detail="The spprodan with this id does not exist.")
    return spprodan


@router.put("/{spprodan_id}", response_model=SpprodanRead)
def update_spprodan(
    *,
    db_session: Session = Depends(get_db),
    spprodan_id: int,
    spprodan_in: SpprodanUpdate, current_user: DispatchUser = Depends(get_current_user)
):
    """
    Update a spprodan contact.
    """
    spprodan = get(db_session=db_session, id=spprodan_id)
    if not spprodan:
        raise HTTPException(status_code=400, detail="The spprodan with this id does not exist.")

    spprodan = update(
        db_session=db_session,
        spprodan=spprodan,
        spprodan_in=spprodan_in,
    )
    return spprodan

@router.post("/update/", response_model=SpprodanRead)
def update_spprodan_new(
    *, 
    db_session: Session = Depends(get_db), 
    spprodan_in: SpprodanUpdateNew, 
    current_user: DispatchUser = Depends(get_current_user)
):
    spprodan_id = spprodan_in.id
    spprodan = get(db_session=db_session, id=spprodan_id)
    if not spprodan:
        raise HTTPException(status_code=400, detail="The spprodan with this id does not exist.")
    spprodan_in.data["updated_at"] = datetime.now(timezone.utc)
    spprodan_in.data["updated_by"] = current_user.email
    spprodan = update_new(
        db_session=db_session,
        spprodan=spprodan,
        spprodan_in=spprodan_in.data,
    )
    return spprodan


@router.put("/spprodan_code/{spprodan_code}", response_model=SpprodanRead)
def update_spprodan_by_code(
    *,
    db_session: Session = Depends(get_db),
    spprodan_code: str,
    spprodan_in: SpprodanUpdate, current_user: DispatchUser = Depends(get_current_user)
):
    """
    Update a spprodan contact.
    """
    spprodan = get_by_code(db_session=db_session, code=spprodan_code)
    if not spprodan:
        raise HTTPException(status_code=400, detail="The spprodan with this id does not exist.")

    spprodan_in.updated_by = current_user.email
    spprodan = update(
        db_session=db_session,
        spprodan=spprodan,
        spprodan_in=spprodan_in,
    )

    return spprodan


@router.delete("/{spprodan_id}", response_model=SpprodanRead)
def delete_spprodan(*, db_session: Session = Depends(get_db), spprodan_id: int):
    """
    Delete a spprodan contact.
    """
    spprodan = get(db_session=db_session, id=spprodan_id)
    if not spprodan:
        raise HTTPException(status_code=400, detail="The spprodan with this id does not exist.")

    return delete(db_session=db_session, id=spprodan_id)



@router.post("/copy_to")
def create_by_copy_to(*, db_session: Session = Depends(get_db), copy_dict: SpprodanCopyToCode, current_user: DispatchUser = Depends(get_current_user)):
    spimpact = create_by_copy_spec_code(db_session=db_session, copy_dict=copy_dict, current_user=current_user)
    return spimpact