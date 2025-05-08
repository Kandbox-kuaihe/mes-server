from dispatch.database import get_db
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from dispatch.system_admin.auth.models import DispatchUser
from dispatch.system_admin.auth.service import get_current_user

from dispatch.database_util.service import common_parameters, search_filter_sort_paginate
from .models import (
    QualityOtherElement,
    QualityOtherElementCreate,
    QualityOtherElementUpdate,
    QualityOtherElementRead,
    QualityOtherElementPagination,
)
from .service import create, delete, get, get_by_code, update
from datetime import datetime, timezone

router = APIRouter()


@router.get("/", response_model=QualityOtherElementPagination)
def get_quality_other_element(*, common: dict = Depends(common_parameters)):

    return search_filter_sort_paginate(model="QualityElement", **common)


@router.post("/{quality_other_element_id}", response_model=QualityOtherElementRead)
def create_quality_other_element(
    *, 
    db_session: Session = Depends(get_db), 
    quality_other_element_id: int,
    quality_other_element_in: QualityOtherElementCreate,
    current_user: DispatchUser = Depends(get_current_user)
):
    """
    Create a new quality_other_element contact.
    """

    quality_other_element = create(db_session=db_session, 
                      quality_other_element_id=quality_other_element_id,
                      quality_other_element_in=quality_other_element_in)
    return quality_other_element


@router.put("/{quality_other_element_id}", response_model=QualityOtherElementRead)
def update_quality_other_element(
    *,
    db_session: Session = Depends(get_db),
    quality_other_element_id: int,
    quality_other_element_in: QualityOtherElementCreate, current_user: DispatchUser = Depends(get_current_user)
):
    """
    Update a quality_other_element_in contact.
    """
    quality_other_element = get(db_session=db_session, id=quality_other_element_id)
    if not quality_other_element:
        raise HTTPException(status_code=400, detail="The quality_element with this id does not exist.")

    quality_other_element = update(
        db_session=db_session,
        quality_other_element=quality_other_element,
        quality_other_element_in=quality_other_element_in,
    )
    return quality_other_element


@router.delete("/{quality_other_element_id}", response_model=QualityOtherElementRead)
def delete_quality_other_element(*, db_session: Session = Depends(get_db), quality_other_element_id: int):
    """
    Delete a quality_other_element_id contact.
    """
    quality_other_element_id = get(db_session=db_session, id=quality_other_element_id)
    if not quality_other_element_id:
        raise HTTPException(status_code=400, detail="The quality_other_element with this id does not exist.")

    return delete(db_session=db_session, id=quality_other_element_id)
