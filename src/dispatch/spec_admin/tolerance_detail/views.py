
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from dispatch.database import get_db
from dispatch.database_util.service import common_parameters, search_filter_sort_paginate
from dispatch.system_admin.auth.models import DispatchUser
from dispatch.system_admin.auth.service import get_current_user

from .models import (
    ToleranceDetailBase,
    ToleranceDetailRead,
    ToleranceDetailPagination,
    ToleranceDetailUpdate,
)
from .service import get_by_code, create, get, update, delete, get_tolerance_detail_codes


router = APIRouter()


@router.get("/", response_model=ToleranceDetailPagination)
def get_all(*, common: dict=Depends(common_parameters)):
    return search_filter_sort_paginate(model="ToleranceDetail", **common)

@router.get("/{tolerance_id}", response_model=ToleranceDetailRead)
def get_tolerance_detail(
    *,
    db_session: Session = Depends(get_db),
    tolerance_id: int
):
    tolerance_detail = get(db_session=db_session, id=tolerance_id)
    return tolerance_detail

@router.post("/",response_model=ToleranceDetailRead)
def create_tolerance_detail(*, db_session: Session = Depends(get_db), tolerance_detail_in: ToleranceDetailBase,
                 current_user: DispatchUser = Depends(get_current_user)):
    existed = get_by_code(db_session=db_session, code=tolerance_detail_in.bar_loc_code)
    if existed:
        raise HTTPException(status_code=400, detail="The tolerance_detail with this code already exists.")
    created = create(db_session=db_session, tolerance_detail_in=tolerance_detail_in)
    return created

@router.put("/{tolerance_detail_id}", response_model=ToleranceDetailRead)
def update_tolerance_detail(
    *,
    db_session: Session = Depends(get_db),
    tolerance_detail_id: int,
    tolerance_detail_in: ToleranceDetailUpdate, current_user: DispatchUser = Depends(get_current_user)
):
    tolerance_detail = get(db_session=db_session, id=tolerance_detail_id)
    if not tolerance_detail:
        raise HTTPException(status_code=400, detail="The tolerance_detail with this id does not exist.")
    # code_existed = get_by_code(db_session=db_session, code=tolerance_detail_in.code)

    updated = update(
        db_session=db_session,
        item=tolerance_detail,
        tolerance_detail_in=tolerance_detail_in,
    )
    return updated

@router.delete("/{tolerance_detail_id}")
def delete_tolerance_detail(*, db_session: Session = Depends(get_db), tolerance_detail_id: int):
    existed = get(db_session=db_session, id=tolerance_detail_id)
    if not existed:
        raise HTTPException(status_code=400, detail="The tolerance_detail with this id does not exist.")

    delete(db_session=db_session, id=tolerance_detail_id)

    return {"deleted": "ok"}


@router.get("/item/codes")
def get_codes(db_session: Session = Depends(get_db)):
    # print(id)
    ls = get_tolerance_detail_codes(db_session=db_session)
    return ls