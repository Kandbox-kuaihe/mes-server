from dispatch.database import get_db
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from dispatch.system_admin.auth.models import DispatchUser
from dispatch.system_admin.auth.service import get_current_user

from dispatch.database_util.service import common_parameters, search_filter_sort_paginate
from .models import (
    SpmainelOtherElement,
    SpmainelOtherElementCreate,
    SpmainelOtherElementPagination,
    SpmainelOtherElementRead,
    SpmainelOtherElementUpdate,
)
from .service import create, delete, get, get_by_code, update
from datetime import datetime, timezone

router = APIRouter()


@router.get("/", response_model=SpmainelOtherElementPagination)
def get_spMainEls(*, common: dict = Depends(common_parameters)):

    return search_filter_sort_paginate(model="SpmainelOtherElement", **common)


@router.post("/{spmainel_id}", response_model=SpmainelOtherElementRead)
def create_spMainEl(
    *, 
    db_session: Session = Depends(get_db), 
    spmainel_id: int,
    spMainEl_in: SpmainelOtherElementCreate,
    current_user: DispatchUser = Depends(get_current_user)
):
    """
    Create a new specMainEl contact.
    """

    spMainEl = create(db_session=db_session, spmainel_id=spmainel_id, spmainel_other_element_in=spMainEl_in)
    return spMainEl


@router.get("/{spmainel_id}", response_model=SpmainelOtherElementRead)
def get_spMainEl(*, db_session: Session = Depends(get_db), spMainEl_id: int):
    """
    Get a specMainEl contact.
    """
    spMainEl = get(db_session=db_session, id=spMainEl_id)
    if not spMainEl:
        raise HTTPException(status_code=400, detail="The spMainEl with this id does not exist.")
    return spMainEl


@router.put("/{spmainel_id}", response_model=SpmainelOtherElementRead)
def update_spMainEl(
    *,
    db_session: Session = Depends(get_db),
    spmainel_id: int,
    spMainEl_in: SpmainelOtherElementUpdate, current_user: DispatchUser = Depends(get_current_user)
):
    """
    Update a spMainEl contact.
    """
    spMainEl = get(db_session=db_session, id=spmainel_id)
    if not spMainEl:
        raise HTTPException(status_code=400, detail="The spMainEl with this id does not exist.")
    spMainEl_in.updated_by = current_user.email
    spMainEl_in.updated_at = datetime.now(timezone.utc)
    spMainEl = update(
        db_session=db_session,
        spmainel_other_element=spMainEl,
        spmainel_other_element_in=spMainEl_in,
    )
    return spMainEl


@router.delete("/{spmainel_id}", response_model=SpmainelOtherElementRead)
def delete_spMainEl(*, db_session: Session = Depends(get_db), spmainel_id: int):
    """
    Delete a specMainEl contact.
    """
    spMainEl = get(db_session=db_session, id=spmainel_id)
    if not spMainEl:
        raise HTTPException(status_code=400, detail="The specMainEl with this id does not exist.")

    return delete(db_session=db_session, id=spmainel_id)
