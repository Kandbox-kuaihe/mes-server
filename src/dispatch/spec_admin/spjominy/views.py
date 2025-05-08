from dispatch.database import get_db
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from dispatch.system_admin.auth.models import DispatchUser
from dispatch.system_admin.auth.service import get_current_user

from dispatch.database_util.service import common_parameters, search_filter_sort_paginate
from .models import Spjominy as SpecJominy
from .models import (
    SpecJominyCreate,
    SpecJominyPagination,
    SpecJominyRead,
    SpecJominyUpdate,
    SpecJominyBySpecCode,
    SpecJominyCopyToCode
)
from .service import create, delete, get, get_by_code, update, get_by_spec_code, create_by_copy_spec_code

router = APIRouter()


@router.get("/", response_model=SpecJominyPagination)
def get_specJominys(*, common: dict = Depends(common_parameters)):

    return search_filter_sort_paginate(model="Spjominy", **common)

@router.post("/search_data/", response_model=SpecJominyPagination)
def getBySpecCode(*, db_session: Session = Depends(get_db), search_dict: SpecJominyBySpecCode):
    specjominy = get_by_spec_code(db_session=db_session,search_dict=search_dict)
    return specjominy


@router.post("/", response_model=SpecJominyRead)
def create_specJominy(*, db_session: Session = Depends(get_db), specJominy_in: SpecJominyCreate,
                 current_user: DispatchUser = Depends(get_current_user)):
    """
    Create a new specJominy contact.
    """
    
    # specJominy = get_by_code(db_session=db_session,code=specJominy_in.code)
    
    
    # if specJominy:
    #     raise HTTPException(status_code=400, detail="The specJominy with this code already exists.")
    specJominy_in.created_by = current_user.email
    specJominy_in.updated_by = current_user.email
    try:
        specJominy = create(db_session=db_session, spjominy_in=specJominy_in)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return specJominy


@router.get("/{specJominy_id}", response_model=SpecJominyRead)
def get_specJominy(*, db_session: Session = Depends(get_db), specJominy_id: int):
    """
    Get a specJominy contact.
    """
    specJominy = get(db_session=db_session, id=specJominy_id)
    if not specJominy:
        raise HTTPException(status_code=400, detail="The specJominy with this id does not exist.")
    return specJominy


@router.put("/{specJominy_id}", response_model=SpecJominyRead)
def update_specJominy(
    *,
    db_session: Session = Depends(get_db),
    specJominy_id: int,
    specJominy_in: SpecJominyUpdate, current_user: DispatchUser = Depends(get_current_user)
):
    """
    Update a specJominy contact.
    """
    specJominy = get(db_session=db_session, id=specJominy_id)
    if not specJominy:
        raise HTTPException(status_code=400, detail="The specJominy with this id does not exist.")

    specJominy = update(
        db_session=db_session,
        spjominy=specJominy,
        spjominy_in=specJominy_in,
    )
    return specJominy


@router.put("/specJominy_code/{specJominy_code}", response_model=SpecJominyRead)
def update_specJominy_by_code(
    *,
    db_session: Session = Depends(get_db),
    specJominy_code: str,
    specJominy_in: SpecJominyUpdate, current_user: DispatchUser = Depends(get_current_user)
):
    """
    Update a specJominy contact.
    """
    specJominy = get_by_code(db_session=db_session, code=specJominy_code)
    if not specJominy:
        raise HTTPException(status_code=400, detail="The specJominy with this id does not exist.")
    specJominy_in.updated_by = current_user.email
    specJominy = update(
        db_session=db_session,
        specJominy=specJominy,
        spjominy_in=specJominy_in,
    )

    return specJominy


@router.delete("/{specJominy_id}", response_model=SpecJominyRead)
def delete_specJominy(*, db_session: Session = Depends(get_db), specJominy_id: int):
    """
    Delete a specJominy contact.
    """
    specJominy = get(db_session=db_session, id=specJominy_id)
    if not specJominy:
        raise HTTPException(status_code=400, detail="The specJominy with this id does not exist.")

    return delete(db_session=db_session, id=specJominy_id)



@router.post("/copy_to")
def create_by_copy_to(*, db_session: Session = Depends(get_db), copy_dict: SpecJominyCopyToCode, current_user: DispatchUser = Depends(get_current_user)):
    spimpact = create_by_copy_spec_code(db_session=db_session, copy_dict=copy_dict, current_user=current_user)
    return spimpact