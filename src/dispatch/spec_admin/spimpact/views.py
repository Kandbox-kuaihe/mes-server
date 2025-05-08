from dispatch.database import get_db
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from dispatch.spec_admin.spec.service import get as get_spec
from dispatch.system_admin.auth.models import DispatchUser
from dispatch.system_admin.auth.service import get_current_user

from dispatch.database_util.service import common_parameters, search_filter_sort_paginate
from .models import Spimpact as SpImpact
from .models import (
    SpImpactCreate,
    SpImpactPagination,
    SpImpactRead,
    SpImpactUpdate,
    SpImapctBySpecCode,
    SpImpactUpdateNew,
    SpImpactCopyToCode
)
from .service import create, delete, get, get_by_code, update, update_new, get_by_spec_code, create_by_copy_spec_code
from datetime import datetime, timezone
from dispatch.tests_admin.test_sample.service import get as get_test_sample

router = APIRouter()


@router.get("/", response_model=SpImpactPagination)
def get_spImpacts(*, common: dict = Depends(common_parameters)):

    return search_filter_sort_paginate(model="Spimpact", **common)

@router.post("/search_data/", response_model=SpImpactPagination)
def getBySpecCode(*, db_session: Session = Depends(get_db), search_dict: SpImapctBySpecCode):
    spimpact = get_by_spec_code(db_session=db_session,search_dict=search_dict)
    return spimpact

@router.post("/", response_model=SpImpactRead)
def create_spImpact(*, db_session: Session = Depends(get_db), spImpact_in: SpImpactCreate,
                 current_user: DispatchUser = Depends(get_current_user)):
    """
    Create a new spImpact contact.
    """
    # spImpact = get_by_code(db_session=db_session,code=spImpact_in.code)
    
    
    # if spImpact:
    #     raise HTTPException(status_code=400, detail="The spImpact with this code already exists.")
    
    spImpact_in.created_by = current_user.email
    spImpact_in.updated_by = current_user.email
    try:
        spImpact = create(db_session=db_session, spImpact_in=spImpact_in)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return spImpact


@router.get("/{spImpact_id}", response_model=SpImpactRead)
def get_spImpact(*, db_session: Session = Depends(get_db), spImpact_id: int):
    """
    Get a spImpact contact.
    """
    spImpact = get(db_session=db_session, id=spImpact_id)
    if not spImpact:
        raise HTTPException(status_code=400, detail="The spImpact with this id does not exist.")
    return spImpact


@router.put("/{spImpact_id}", response_model=SpImpactRead)
def update_spImpact(
    *,
    db_session: Session = Depends(get_db),
    spImpact_id: int,
    spImpact_in: SpImpactUpdate, current_user: DispatchUser = Depends(get_current_user)
):
    """
    Update a spImpact contact.
    """
    spImpact = get(db_session=db_session, id=spImpact_id)
    if not spImpact:
        raise HTTPException(status_code=400, detail="The spImpact with this id does not exist.")
    spImpact_in.updated_at = datetime.now(timezone.utc)
    spImpact_in.updated_by = current_user.email
    spImpact = update(
        db_session=db_session,
        spImpact=spImpact,
        spImpact_in=spImpact_in,
    )
    return spImpact

@router.post("/update/", response_model=SpImpactRead)
def update_spimpact_new(
    *, 
    db_session: Session = Depends(get_db), 
    spImpact_in: SpImpactUpdateNew, 
    current_user: DispatchUser = Depends(get_current_user)
):
    spImpact_id = spImpact_in.id
    spImpact = get(db_session=db_session, id=spImpact_id)
    if not spImpact:
        raise HTTPException(status_code=400, detail="The spImpact with this id does not exist.")
    spImpact_in.data["updated_at"] = datetime.now(timezone.utc)
    spImpact_in.data["updated_by"] = current_user.email
    spImpact = update_new(
        db_session=db_session,
        spImpact=spImpact,
        spImpact_in=spImpact_in.data,
    )
    return spImpact



@router.put("/spImpact_code/{spImpact_code}", response_model=SpImpactRead)
def update_spImpact_by_code(
    *,
    db_session: Session = Depends(get_db),
    spImpact_code: str,
    spImpact_in: SpImpactUpdate, current_user: DispatchUser = Depends(get_current_user)
):
    """
    Update a spImpact contact.
    """
    spImpact = get_by_code(db_session=db_session, code=spImpact_code)
    if not spImpact:
        raise HTTPException(status_code=400, detail="The spImpact with this id does not exist.")

    spImpact_in.updated_by = current_user.email
    spImpact = update(
        db_session=db_session,
        spImpact=spImpact,
        spImpact_in=spImpact_in,
    )

    return spImpact


@router.delete("/{spImpact_id}", response_model=SpImpactRead)
def delete_spImpact(*, db_session: Session = Depends(get_db), spImpact_id: int):
    """
    Delete a spImpact contact.
    """
    spImpact = get(db_session=db_session, id=spImpact_id)
    if not spImpact:
        raise HTTPException(status_code=400, detail="The spImpact with this id does not exist.")

    return delete(db_session=db_session, spImpact_id=spImpact_id)


@router.post("/copy_to")
def create_by_copy_to(*, db_session: Session = Depends(get_db), copy_dict: SpImpactCopyToCode, current_user: DispatchUser = Depends(get_current_user)):
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
    query = db_session.query(SpImpact).filter(SpImpact.spec_id == spec_id).filter( SpImpact.thick_from <= thickness).filter(thickness <= SpImpact.thick_to)
    spimpact = list(query)
    if not spimpact:
        raise HTTPException(status_code=400, detail="The spec not found sptensile")
    if len(spimpact) != 1:
        raise HTTPException(status_code=400, detail="The sptensile  record not only one")
    
    spimpact = spimpact[0]
    return {
        "thickness_min": spimpact.thick_from,
        "thickness_max": spimpact.thick_to,
        "temp_c": spimpact.temp_value_1,
        "notch": spimpact.notch[0] if spimpact.notch else None,
        "ave_value_1": spimpact.ave_value_1,
        "ave_value_2": spimpact.ave_value_2,
        "ave_value_3": spimpact.ave_value_3,
        "min_value_1": spimpact.min_value_1,
        "min_value_2": spimpact.min_value_2,
        "min_value_3": spimpact.min_value_3
    }