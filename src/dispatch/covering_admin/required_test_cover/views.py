from dispatch.database import get_db
from typing import List
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from dispatch.system_admin.auth.models import DispatchUser
from dispatch.system_admin.auth.service import get_current_user

from dispatch.database_util.service import common_parameters, search_filter_sort_paginate
from .models import (
    RequiredTestCover,
    RequiredTestCoverCreate,
    RequiredTestCoverUpdate,
    RequiredTestCoverRead,
    RequiredTestCoverPagination,
)
from .service import create, update, delete, get

router = APIRouter()


@router.get("/", response_model=RequiredTestCoverPagination)
def get_required_test_covers(*, common: dict = Depends(common_parameters)):
    return search_filter_sort_paginate(model="RequiredTestCover", **common)


@router.post("/", response_model=RequiredTestCoverRead)
def create_required_test_cover(*, db_session: Session = Depends(get_db), required_test_cover_in: RequiredTestCoverCreate,
                         current_user: DispatchUser = Depends(get_current_user)):
    required_test_cover_in.created_by = current_user.email
    required_test_cover_in.updated_by = current_user.email
    required_test_cover_in.created_at = datetime.now()
    required_test_cover_in.updated_at = datetime.now()
    required_test_cover = create(db_session=db_session, required_test_cover_in=required_test_cover_in)
    return required_test_cover


@router.put("/{required_test_cover_id}", response_model=RequiredTestCoverRead)
def update_required_test_cover(
        *,
        db_session: Session = Depends(get_db),
        required_test_cover_id: int,
        required_test_cover_in: RequiredTestCoverUpdate, current_user: DispatchUser = Depends(get_current_user)
):
    required_test_cover = get(db_session=db_session, id=required_test_cover_id)
    if not required_test_cover:
        raise HTTPException(status_code=400, detail="The required_test_cover with this id does not exist.")

    required_test_cover_in.updated_by = current_user.email
    required_test_cover_in.updated_at = datetime.now()

    required_test_cover = update(
        db_session=db_session,
        required_test_cover=required_test_cover,
        required_test_cover_in=required_test_cover_in,
    )
    return required_test_cover


@router.delete("/{required_test_cover_id}")
def delete_required_test_cover(*, db_session: Session = Depends(get_db), required_test_cover_id: int):
    required_test_cover = get(db_session=db_session, id=required_test_cover_id)
    if not required_test_cover:
        raise HTTPException(status_code=400, detail="The required_test_cover with this id does not exist.")

    delete(db_session=db_session, required_test_cover=required_test_cover, required_test_cover_id=required_test_cover_id)

    return {"deleted": "ok"}
