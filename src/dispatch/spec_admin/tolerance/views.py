
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from dispatch.database import get_db
from dispatch.database_util.service import common_parameters, search_filter_sort_paginate
from dispatch.system_admin.auth.models import DispatchUser
from dispatch.system_admin.auth.service import get_current_user

from .models import (
    ToleranceBase,
    ToleranceRead,
    TolerancePagination,
    ToleranceUpdate,
)
from .service import get_by_code, create, get, update, delete, get_tolerance_codes


router = APIRouter()


@router.get("/", response_model=TolerancePagination)
def get_all(*, common: dict=Depends(common_parameters)):
    return search_filter_sort_paginate(model="Tolerance", **common)

@router.get("/{tolerance_id}", response_model=ToleranceRead)
def get_advice(
    *,
    db_session: Session = Depends(get_db),
    tolerance_id: int
):
    tolerance = get(db_session=db_session, id=tolerance_id)
    return tolerance

@router.get("/tolerance_code/{tolerance_code}", response_model=ToleranceRead)
def get_code(
    *,
    db_session: Session = Depends(get_db),
    tolerance_code: str
):
    tolerance = get_by_code(db_session=db_session, code=tolerance_code)
    return tolerance
@router.post("/",response_model=ToleranceRead)
def create_tolerance(*, db_session: Session = Depends(get_db), tolerance_in: ToleranceBase,
                 current_user: DispatchUser = Depends(get_current_user)):
    existed = get_by_code(db_session=db_session, code=tolerance_in.code)
    if existed:
        raise HTTPException(status_code=400, detail="The tolerance with this code already exists.")
    created = create(db_session=db_session, tolerance_in=tolerance_in)
    return created

@router.put("/{tolerance_id}", response_model=ToleranceRead)
def update_tolerance(
    *,
    db_session: Session = Depends(get_db),
    tolerance_id: int,
    tolerance_in: ToleranceUpdate, current_user: DispatchUser = Depends(get_current_user)
):
    tolerance = get(db_session=db_session, id=tolerance_id)
    if not tolerance:
        raise HTTPException(status_code=400, detail="The tolerance with this id does not exist.")
    code_existed = get_by_code(db_session=db_session, code=tolerance_in.code)

    updated = update(
        db_session=db_session,
        item=tolerance,
        item_in=tolerance_in,
    )
    return updated

@router.delete("/{tolerance_id}")
def delete_tolerance(*, db_session: Session = Depends(get_db), tolerance_id: int):
    existed = get(db_session=db_session, id=tolerance_id)
    if not existed:
        raise HTTPException(status_code=400, detail="The tolerance with this id does not exist.")

    delete(db_session=db_session, id=tolerance_id)

    return {"deleted": "ok"}


@router.get("/item/codes")
def get_codes(db_session: Session = Depends(get_db)):
    # print(id)
    ls = get_tolerance_codes(db_session=db_session)
    return ls