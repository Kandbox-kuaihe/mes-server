
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from dispatch.database import get_db
from dispatch.database_util.service import common_parameters, search_filter_sort_paginate
from dispatch.system_admin.auth.models import DispatchUser
from dispatch.system_admin.auth.service import get_current_user

from .models import (
    SemiSizeBase,
    SemiSizeRead,
    SemiSizePagination,
    SemiSizeUpdate,
)
from .service import get_by_code, create, get, update, delete, get_width_thick


router = APIRouter()


@router.get("/", response_model=SemiSizePagination)
def get_all(*, common: dict=Depends(common_parameters)):
    return search_filter_sort_paginate(model="SemiSize", **common)

@router.get("/{semi_size_id}", response_model=SemiSizeRead)
def get_semi_size(
    *,
    db_session: Session = Depends(get_db),
    semi_size_id: int
):
    semi_size = get(db_session=db_session, id=semi_size_id)
    return semi_size
@router.post("/",response_model=SemiSizeRead)
def create_semi_size(*, db_session: Session = Depends(get_db), semi_size_in: SemiSizeBase,
                 current_user: DispatchUser = Depends(get_current_user)):
    existed = get_by_code(db_session=db_session, code=semi_size_in.code)
    if existed:
        if existed.is_deleted==1:
            existed.is_deleted = 0
            db_session.commit()
            db_session.refresh(existed)
            return existed
        else:
            raise HTTPException(status_code=400, detail="The semi_size with this code already exists.")
    created = create(db_session=db_session, semi_size_in=semi_size_in)
    return created

@router.put("/{semi_size_id}", response_model=SemiSizeRead)
def update_semi_size(
    *,
    db_session: Session = Depends(get_db),
    semi_size_id: int,
    semi_size_in: SemiSizeUpdate, current_user: DispatchUser = Depends(get_current_user)
):
    semi_size = get(db_session=db_session, id=semi_size_id)
    if not semi_size:
        raise HTTPException(status_code=400, detail="The semi_size with this id does not exist.")
    code_existed = get_by_code(db_session=db_session, code=semi_size_in.code)

    updated = update(
        db_session=db_session,
        item=semi_size,
        item_in=semi_size_in,
    )
    return updated

@router.delete("/{semi_size_id}")
def delete_semi_size(*, db_session: Session = Depends(get_db), semi_size_id: int):
    existed = get(db_session=db_session, id=semi_size_id)
    if not existed:
        raise HTTPException(status_code=400, detail="The semi_size with this id does not exist.")

    delete(db_session=db_session, id=semi_size_id)

    return {"deleted": "ok"}


@router.get("/item/width_thick")
def get_codes(db_session: Session = Depends(get_db)):
    # print(id)
    ls = get_width_thick(db_session=db_session)
    return ls