from dispatch.database import get_db
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from dispatch.spec_admin.quality_other_element.service import get_by_element_id
from dispatch.system_admin.auth.models import DispatchUser
from dispatch.system_admin.auth.service import get_current_user

from dispatch.database_util.service import common_parameters, search_filter_sort_paginate
from .models import (
    QualityElement,
    QualityElementCreate,
    QualityElementPagination,
    QualityElementRead,
    QualityElementUpdate,
)
from .service import get,delete,create,update
from datetime import datetime, timezone

router = APIRouter()


@router.get("/", response_model=QualityElementPagination)
def get_quality_element(*, db_session: Session = Depends(get_db), common: dict = Depends(common_parameters)):

    quality_element = search_filter_sort_paginate(model="QualityElement", **common)
    return quality_element

@router.get("/{id}", response_model=QualityElementRead)
def get_quality_element_by_id(*, db_session: Session = Depends(get_db), id: int):
    quality_element = get(db_session=db_session, id=id)
    if not quality_element:
        raise HTTPException(
            status_code=404,
            detail="The quality element with this id does not exist.",
        )
    
    other = get_by_element_id(db_session=db_session, quality_element_id=quality_element.id)
    quality_element.quality_other_element = other
    return quality_element

@router.post("/", response_model=QualityElementRead)
def create_quality_element(*, db_session: Session = Depends(get_db), quality_element_in: QualityElementCreate,
                 current_user: DispatchUser = Depends(get_current_user)):
    """
    Create a new quality_element contact.
    """
    
    # spMainEl = get_by_code(db_session=db_session,code=spMainEl_in.code)
    
    
    # if spMainEl:
    #     raise HTTPException(status_code=400, detail="The specMainEl with this code already exists.")
    
    # 确保 is_active 有值
    if quality_element_in.is_active is None:
        quality_element_in.is_active = True        
        
    quality_element_in.created_by = current_user.email
    quality_element_in.updated_by = current_user.email
    quality_element = create(db_session=db_session, quality_element_in=quality_element_in)
    return quality_element




@router.put("/{quality_element_id}", response_model=QualityElementRead)
def update_quality_element(
    *,
    db_session: Session = Depends(get_db),
    quality_element_id: int,
    quality_element_in: QualityElementUpdate, current_user: DispatchUser = Depends(get_current_user)
):
    """
    Update a quality_element contact.
    """
    quality_element = get(db_session=db_session, id=quality_element_id)
    if not quality_element:
        raise HTTPException(status_code=400, detail="The quality_element with this id does not exist.")

    quality_element = update(
        db_session=db_session,
        quality_element=quality_element,
        quality_element_in=quality_element_in,
    )
    return quality_element


@router.delete("/{quality_element_id}", response_model=QualityElementRead)
def delete_quality_element(*, db_session: Session = Depends(get_db), quality_element_id: int):
    """
    Delete a quality_element_id contact.
    """
    quality_element = get(db_session=db_session, id=quality_element_id)
    if not quality_element:
        raise HTTPException(status_code=400, detail="The quality_element with this id does not exist.")

    return delete(db_session=db_session, id=quality_element_id)
