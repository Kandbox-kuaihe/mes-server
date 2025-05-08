
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from dispatch.database import get_db
from dispatch.database_util.service import common_parameters, search_filter_sort_paginate
from dispatch.system_admin.auth.models import DispatchUser
from dispatch.system_admin.auth.service import get_current_user

from .models import (
    SemiSizeDetailBase,
    SemiSizeDetailRead,
    SemiSizeDetailPagination,
    SemiSizeDetailUpdate,
)
from .service import  create, get, update, delete, get_length_by_size_id


router = APIRouter()


@router.get("/", response_model=SemiSizeDetailPagination)
def get_all(*, common: dict=Depends(common_parameters)):
    return search_filter_sort_paginate(model="SemiSizeDetail", **common)

@router.post("/",response_model=SemiSizeDetailRead)
def create_semi_size_detail(*, db_session: Session = Depends(get_db), semi_size_detail_in: SemiSizeDetailBase,
                 current_user: DispatchUser = Depends(get_current_user)):
    semi_size_detail_in.created_by=current_user.email
    created = create(db_session=db_session, semi_size_detail_in=semi_size_detail_in)
    return created

@router.put("/{semi_size_detail_id}", response_model=SemiSizeDetailRead)
def update_semi_size_detail(
    *,
    db_session: Session = Depends(get_db),
    semi_size_detail_id: int,
    semi_size_detail_in: SemiSizeDetailUpdate, current_user: DispatchUser = Depends(get_current_user)
):
    semi_size_detail = get(db_session=db_session, id=semi_size_detail_id)
    if not semi_size_detail:
        raise HTTPException(status_code=400, detail="The semi_size_detail with this id does not exist.")
    # code_existed = get_by_code(db_session=db_session, code=semi_size_detail_in.code)
    semi_size_detail_in.updated_by = current_user.email
    updated = update(
        db_session=db_session,
        item=semi_size_detail,
        semi_size_detail_in=semi_size_detail_in,
    )
    return updated

@router.delete("/{semi_size_detail_id}")
def delete_semi_size_detail(*, db_session: Session = Depends(get_db), semi_size_detail_id: int):
    existed = get(db_session=db_session, id=semi_size_detail_id)
    if not existed:
        raise HTTPException(status_code=400, detail="The semi_size_detail with this id does not exist.")

    delete(db_session=db_session, id=semi_size_detail_id)

    return {"deleted": "ok"}


@router.get("/item/length")
def get_codes(db_session: Session = Depends(get_db)):
    # print(id)
    ls = get_length_by_size_id(db_session=db_session)
    return ls