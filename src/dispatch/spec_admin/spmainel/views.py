from typing import Union

from dispatch.database import get_db

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from dispatch.system_admin.auth.models import DispatchUser
from dispatch.system_admin.auth.service import get_current_user

from dispatch.database_util.service import common_parameters, search_filter_sort_paginate
from .models import Spmainel as SpMainEl
from .models import (
    SpMainElCreate,
    SpMainElPagination,
    SpMainElRead,
    SpMainElUpdate,
    SpMainElUpdateNew,
    SpMainElBySpecCode,
    SpMainElCopyToCode
)
from .service import create, delete, get, get_by_code, update, update_new, get_by_spec_code, create_by_copy_spec_code, spmain_union_other
from datetime import datetime, timezone

from dispatch.spec_admin.spec.models import Spec
from dispatch.mill.models import Mill

router = APIRouter()


@router.get("/",response_model=SpMainElPagination)
def get_spMainEls(*, common: dict = Depends(common_parameters), db_session: Session = Depends(get_db), spec_thickness:int=Query(None)):
    query = db_session.query(SpMainEl).outerjoin(Mill, SpMainEl.mill_id == Mill.id).outerjoin(Spec, SpMainEl.spec_id == Spec.id)
    if spec_thickness:
        query = query.filter(SpMainEl.thick_from < spec_thickness, spec_thickness < SpMainEl.thick_to )
    common["query"] = query
    spmainel = search_filter_sort_paginate(model="Spmainel", **common)
    ids = []
    for i in spmainel["items"]:
        ids.append(len(i.spmainel_other_element))
    spmainel["other_element_num"] = ids
    return spmainel


@router.get("/union_other")
def get_spMainEls(*, common: dict = Depends(common_parameters), db_session: Session = Depends(get_db), spec_thickness:Union[float, int]=Query(None)):
    query = db_session.query(SpMainEl).outerjoin(Mill, SpMainEl.mill_id == Mill.id).outerjoin(Spec, SpMainEl.spec_id == Spec.id)
    if spec_thickness:
        query = query.filter(SpMainEl.thick_from < spec_thickness, spec_thickness < SpMainEl.thick_to )
    common["query"] = query
    spmainel = search_filter_sort_paginate(model="Spmainel", **common)
    for i in spmainel["items"]:
        spmain_union_other(db_session=db_session,spmainel=i)
    return spmainel


@router.post("/search_data/", response_model=SpMainElPagination)
def getBySpecCode(*, db_session: Session = Depends(get_db), search_dict: SpMainElBySpecCode):
    spmainel = get_by_spec_code(db_session=db_session,search_dict=search_dict)
    return spmainel


@router.post("/", response_model=SpMainElRead)
def create_spMainEl(*, db_session: Session = Depends(get_db), spMainEl_in: SpMainElCreate,
                 current_user: DispatchUser = Depends(get_current_user)):
    """
    Create a new specMainEl contact.
    """
    
    # spMainEl = get_by_code(db_session=db_session,code=spMainEl_in.code)
    
    
    # if spMainEl:
    #     raise HTTPException(status_code=400, detail="The specMainEl with this code already exists.")
    
    spMainEl_in.created_by = current_user.email
    spMainEl_in.updated_by = current_user.email
    try:
        spMainEl = create(db_session=db_session, spmainel_in=spMainEl_in)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return spMainEl


@router.get("/{spMainEl_id}", response_model=SpMainElRead)
def get_spMainEl(*, db_session: Session = Depends(get_db), spMainEl_id: int):
    """
    Get a specMainEl contact.
    """
    spMainEl = get(db_session=db_session, id=spMainEl_id)
    if not spMainEl:
        raise HTTPException(status_code=400, detail="The spMainEl with this id does not exist.")
    return spMainEl


@router.put("/{spMainEl_id}", response_model=SpMainElRead)
def update_spMainEl(
    *,
    db_session: Session = Depends(get_db),
    spMainEl_id: int,
    spMainEl_in: SpMainElUpdate, current_user: DispatchUser = Depends(get_current_user)
):
    """
    Update a spMainEl contact.
    """
    spMainEl = get(db_session=db_session, id=spMainEl_id)
    if not spMainEl:
        raise HTTPException(status_code=400, detail="The spMainEl with this id does not exist.")

    spMainEl = update(
        db_session=db_session,
        spmainel=spMainEl,
        spmainel_in=spMainEl_in,
    )
    return spMainEl


@router.post("/update/", response_model=SpMainElRead)
def update_spmainel_new(
    *, 
    db_session: Session = Depends(get_db), 
    spmainel_in: SpMainElUpdateNew, 
    current_user: DispatchUser = Depends(get_current_user)
):
    spmainel_id = spmainel_in.id
    spMainel = get(db_session=db_session, id=spmainel_id)
    if not spMainel:
        raise HTTPException(status_code=400, detail="The spMainEl with this id does not exist.")
    spmainel_in.data["updated_at"] = datetime.now(timezone.utc)
    spmainel_in.data["updated_by"] = current_user.email
    spMainel = update_new(
        db_session=db_session,
        spMainel=spMainel,
        spMainel_in=spmainel_in.data,
    )
    return spMainel


@router.put("/spMainEl_code/{spMainEl_code}", response_model=SpMainElRead)
def update_spMainEl_by_code(
    *,
    db_session: Session = Depends(get_db),
    spMainEl_code: str,
    spMainEl_in: SpMainElUpdate, current_user: DispatchUser = Depends(get_current_user)
):
    """
    Update a specMainEl contact.
    """
    spMainEl = get_by_code(db_session=db_session, code=spMainEl_code)
    if not spMainEl:
        raise HTTPException(status_code=400, detail="The specMainEl with this id does not exist.")

    spMainEl_in.updated_by = current_user.email
    spMainEl = update(
        db_session=db_session,
        spMainEl=spMainEl,
        spMainEl_in=spMainEl_in,
    )

    return spMainEl


@router.delete("/{spMainEl_id}", response_model=SpMainElRead)
def delete_spMainEl(*, db_session: Session = Depends(get_db), spMainEl_id: int):
    """
    Delete a specMainEl contact.
    """
    spMainEl = get(db_session=db_session, id=spMainEl_id)
    if not spMainEl:
        raise HTTPException(status_code=400, detail="The specMainEl with this id does not exist.")

    return delete(db_session=db_session, id=spMainEl_id)



@router.post("/copy_to")
def create_by_copy_to(*, db_session: Session = Depends(get_db), copy_dict: SpMainElCopyToCode, current_user: DispatchUser = Depends(get_current_user)):
    spimpact = create_by_copy_spec_code(db_session=db_session, copy_dict=copy_dict, current_user=current_user)
    return spimpact