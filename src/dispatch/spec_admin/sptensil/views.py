from dispatch.database import get_db
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from dispatch.system_admin.auth.models import DispatchUser
from dispatch.system_admin.auth.service import get_current_user

from dispatch.database_util.service import common_parameters, search_filter_sort_paginate
from .models import (
    Sptensil,
    SptensilCreate,
    SptensilPagination,
    SptensilRead,
    SptensilUpdate,
    SptensilUpdateNew,
    SptensilBySpecCode,
    SptensilCopyToCode
)
from .service import create, delete, get, get_by_code, update, update_new, get_by_spec_code, create_by_copy_spec_code
from datetime import datetime, timezone
from dispatch.tests_admin.test_sample.service import get as get_test_sample
from dispatch.spec_admin.spec.service import get as get_spec

router = APIRouter()


@router.get("/", response_model=SptensilPagination)
def get_filters(*, common: dict = Depends(common_parameters)):

    return search_filter_sort_paginate(model="Sptensil", **common)

@router.post("/search_data/", response_model=SptensilPagination)
def getBySpecCode(*, db_session: Session = Depends(get_db), search_dict: SptensilBySpecCode):
    spimpact = get_by_spec_code(db_session=db_session,search_dict=search_dict)
    return spimpact


@router.post("/", response_model=SptensilRead)
def create_obj(*, db_session: Session = Depends(get_db), request_in: SptensilCreate,
                 current_user: DispatchUser = Depends(get_current_user)):
    """
    Create a new sptensil contact.
    """
    
    # sptensil = get_by_code(db_session=db_session,code=request_in.code)
    
    
    # if sptensil:
    #     raise HTTPException(status_code=400, detail="The sptensil with this code already exists.")
    
    request_in.created_by = current_user.email
    request_in.updated_by = current_user.email
    try:
        sptensil = create(db_session=db_session, sptensil_in=request_in)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return sptensil


@router.get("/{sptensil_id}", response_model=SptensilRead)
def get_sptensil(*, db_session: Session = Depends(get_db), sptensil_id: int):
    """
    Get a sptensil contact.
    """
    sptensil = get(db_session=db_session, id=sptensil_id)
    if not sptensil:
        raise HTTPException(status_code=400, detail="The sptensil with this id does not exist.")
    return sptensil


@router.put("/{sptensil_id}", response_model=SptensilRead)
def update_sptensil(
    *,
    db_session: Session = Depends(get_db),
    sptensil_id: int,
    sptensil_in: SptensilUpdate, current_user: DispatchUser = Depends(get_current_user)
):
    """
    Update a sptensil contact.
    """
    sptensil = get(db_session=db_session, id=sptensil_id)
    if not sptensil:
        raise HTTPException(status_code=400, detail="The sptensil with this id does not exist.")
    
    sptensil_in.updated_at = datetime.now(timezone.utc)
    sptensil_in.updated_by = current_user.email

    sptensil = update(
        db_session=db_session,
        sptensil=sptensil,
        sptensil_in=sptensil_in,
    )
    return sptensil

@router.post("/update/", response_model=SptensilRead)
def update_sptensil_new(
    *, 
    db_session: Session = Depends(get_db), 
    sptensil_in: SptensilUpdateNew, 
    current_user: DispatchUser = Depends(get_current_user)
):
    spTensil_id = sptensil_in.id
    spTensil = get(db_session=db_session, id=spTensil_id)
    if not spTensil:
        raise HTTPException(status_code=400, detail="The sptensil with this id does not exist.")
    sptensil_in.data["updated_at"] = datetime.now(timezone.utc)
    sptensil_in.data["updated_by"] = current_user.email
    spTensil = update_new(
        db_session=db_session,
        spTensil=spTensil,
        spTensil_in=sptensil_in.data,
    )
    return spTensil


@router.put("/sptensil_code/{sptensil_code}", response_model=SptensilRead)
def update_sptensil_by_code(
    *,
    db_session: Session = Depends(get_db),
    sptensil_code: str,
    sptensil_in: SptensilUpdate, current_user: DispatchUser = Depends(get_current_user)
):
    """
    Update a sptensil contact.
    """
    sptensil = get_by_code(db_session=db_session, code=sptensil_code)
    if not sptensil:
        raise HTTPException(status_code=400, detail="The sptensil with this id does not exist.")

    sptensil_in.updated_by = current_user.email
    sptensil = update(
        db_session=db_session,
        sptensil=sptensil,
        sptensil_in=sptensil_in,
    )

    return sptensil


@router.delete("/{sptensil_id}", response_model=SptensilRead)
def delete_sptensil(*, db_session: Session = Depends(get_db), sptensil_id: int):
    """
    Delete a sptensil contact.
    """
    sptensil = get(db_session=db_session, id=sptensil_id)
    if not sptensil:
        raise HTTPException(status_code=400, detail="The sptensil with this id does not exist.")

    return delete(db_session=db_session, id=sptensil_id)


@router.post("/copy_to")
def create_by_copy_to(*, db_session: Session = Depends(get_db), copy_dict: SptensilCopyToCode, current_user: DispatchUser = Depends(get_current_user)):
    spimpact = create_by_copy_spec_code(db_session=db_session, copy_dict=copy_dict, current_user=current_user)
    return spimpact



@router.get("/test/get_test_require")
def get_test_require_byspec(*, db_session: Session = Depends(get_db), spec_id: int, test_sample_id: int):
    spec = get_spec(db_session=db_session, id=spec_id)
    if not spec:
        raise HTTPException(status_code=400, detail="please input Spec Code")
    test_sample = get_test_sample(db_session=db_session, testSample_id=test_sample_id)
    if not test_sample:
        raise HTTPException(status_code=400, detail="please input Test Sample Code")
    thickness = test_sample.sample_thickness
    if not thickness:
        raise HTTPException(status_code=400, detail=f"Test Sample id:{test_sample_id} sample_thickness is not exist")
    query = db_session.query(Sptensil).filter(Sptensil.spec_id == spec_id).filter( Sptensil.thick_from <= thickness).filter(thickness <= Sptensil.thick_to)
    sptensile = list(query)
    if not sptensile:
        raise HTTPException(status_code=400, detail="The spec not found sptensile")
    if len(sptensile) != 1:
        raise HTTPException(status_code=400, detail="The sptensile  record not only one")
    sptensile = sptensile[0]

    uts_min , uts_max = sptensile.tensile_min , sptensile.tensile_max
    if sptensile.spec.spec_units == "I":
        uts_min = int(uts_min * 0.006895) if uts_min else None
        uts_max = int(uts_max * 0.006895) if uts_max else None
    
    return {
        "thickness_min": sptensile.thick_from,
        "thickness_max": sptensile.thick_to,
        "uts_min": uts_min,
        "uts_max": uts_max,
        "yield_min": sptensile.yield_min,
        "yield_max": sptensile.yield_max,
        "elongation_min": sptensile.elong_code_1_min,
        "elongation_code": sptensile.elgge[0] if sptensile.elgge else None,
        "test_standard": int(sptensile.std[0]) if sptensile.std else None,
        "spec_units": sptensile.spec.spec_units,
    }