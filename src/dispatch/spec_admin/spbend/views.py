from dispatch.database import get_db
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from dispatch.system_admin.auth.models import DispatchUser
from dispatch.system_admin.auth.service import get_current_user

from dispatch.database_util.service import common_parameters, search_filter_sort_paginate
from .models import (
    Spbend,
    SpbendCreate,
    SpbendPagination,
    SpbendRead,
    SpbendUpdate,
    SpbendUpdateNew,
    SpbendBySpecCode,
    SpbendCopyToCode,
    SpbendPrintCardReturnValue
)
from .service import create, delete, get, get_by_code, update, update_new, get_by_spec_code, create_by_copy_spec_code, bend_print_card
from datetime import datetime, timezone

from ...product_type.models import ProductType

router = APIRouter()


@router.get("/", response_model=SpbendPagination)
def get_filters(*, common: dict = Depends(common_parameters)):

    return search_filter_sort_paginate(model="Spbend", **common)


@router.post("/search_data/", response_model=SpbendPagination)
def getBySpecCode(*, db_session: Session = Depends(get_db), search_dict: SpbendBySpecCode):
    spbend = get_by_spec_code(db_session=db_session,search_dict=search_dict)
    return spbend


@router.post("/", response_model=SpbendRead)
def create_obj(*, db_session: Session = Depends(get_db), request_in: SpbendCreate,
                 current_user: DispatchUser = Depends(get_current_user)):
    """
    Create a new spbend contact.
    """

    # spbend = db_session.query(Spbend).filter(Spbend.spec_id==request_in.spec_id,
    #                                          Spbend.mill_id==request_in.mill_id,
    #                                          Spbend.thick_from==request_in.thick_from,
    #                                          Spbend.thick_to==request_in.thick_to).first()
    # if spbend:
    #     raise HTTPException(status_code=400, detail="The spbend with this code already exists.")
    

    request_in.created_by = current_user.email
    request_in.updated_by = current_user.email
    try:
        spbend = create(db_session=db_session, spbend_in=request_in)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return spbend


@router.get("/{spbend_id}", response_model=SpbendRead)
def get_spbend(*, db_session: Session = Depends(get_db), spbend_id: int):
    """
    Get a spbend contact.
    """
    spbend = get(db_session=db_session, id=spbend_id)
    if not spbend:
        raise HTTPException(status_code=400, detail="The spbend with this id does not exist.")
    return spbend


@router.put("/{spbend_id}", response_model=SpbendRead)
def update_spbend(
    *,
    db_session: Session = Depends(get_db),
    spbend_id: int,
    spbend_in: SpbendUpdate, current_user: DispatchUser = Depends(get_current_user)
):
    """
    Update a spbend contact.
    """
    spbend = get(db_session=db_session, id=spbend_id)
    if not spbend:
        raise HTTPException(status_code=400, detail="The spbend with this id does not exist.")

    spbend = update(
        db_session=db_session,
        spbend=spbend,
        spbend_in=spbend_in,
    )
    return spbend


@router.post("/update/", response_model=SpbendRead)
def update_spbend_new(
    *, 
    db_session: Session = Depends(get_db), 
    spbend_in: SpbendUpdateNew, 
    current_user: DispatchUser = Depends(get_current_user)
):
    spbend_id = spbend_in.id
    spbend = get(db_session=db_session, id=spbend_id)
    if not spbend:
        raise HTTPException(status_code=400, detail="The spbend with this id does not exist.")
    spbend_in.data["updated_at"] = datetime.now(timezone.utc)
    spbend_in.data["updated_by"] = current_user.email
    spbend = update_new(
        db_session=db_session,
        spbend=spbend,
        spbend_in=spbend_in.data,
    )
    return spbend


@router.put("/spbend_code/{spbend_code}", response_model=SpbendRead)
def update_spbend_by_code(
    *,
    db_session: Session = Depends(get_db),
    spbend_code: str,
    spbend_in: SpbendUpdate, current_user: DispatchUser = Depends(get_current_user)
):
    """
    Update a spbend contact.
    """
    spbend = get_by_code(db_session=db_session, code=spbend_code)
    if not spbend:
        raise HTTPException(status_code=400, detail="The spbend with this id does not exist.")

    spbend_in.updated_by = current_user.email
    spbend = update(
        db_session=db_session,
        spbend=spbend,
        spbend_in=spbend_in,
    )

    return spbend


@router.delete("/{spbend_id}", response_model=SpbendRead)
def delete_spbend(*, db_session: Session = Depends(get_db), spbend_id: int):
    """
    Delete a spbend contact.
    """
    spbend = get(db_session=db_session, id=spbend_id)
    if not spbend:
        raise HTTPException(status_code=400, detail="The spbend with this id does not exist.")

    return delete(db_session=db_session, id=spbend_id)



@router.post("/copy_to")
def create_by_copy_to(*, db_session: Session = Depends(get_db), copy_dict: SpbendCopyToCode, current_user: DispatchUser = Depends(get_current_user)):
    spimpact = create_by_copy_spec_code(db_session=db_session, copy_dict=copy_dict, current_user=current_user)
    return spimpact

@router.post("/get_code_by_flange_spec")
def get_code_by_flange_spec(data: SpbendPrintCardReturnValue, db_session: Session = Depends(get_db), current_user: DispatchUser = Depends(get_current_user)):
    mill_id = current_user.current_mill_id
    if data.spec_id is None or data.product_type_id is None:
        raise HTTPException(status_code=400, detail="Spec id and product type id must be specified.")
    product_type = db_session.query(ProductType).filter(ProductType.id == data.product_type_id).first()
    if not product_type:
        raise HTTPException(status_code=400, detail="Product type must be specified.")
    Spbend = bend_print_card(db_session=db_session, mill_id=mill_id, spec_id=data.spec_id, product_type_flange_thickness=product_type.flange_thickness)
    return {
        "diameter_mm": Spbend.diameter_mm,
    } if Spbend else {
        "diameter_mm": None,
    }