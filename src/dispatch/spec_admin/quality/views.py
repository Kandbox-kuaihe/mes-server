from dispatch.database import get_db
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from dispatch.system_admin.auth.models import DispatchUser
from dispatch.system_admin.auth.service import get_current_user
from .service import  get
from dispatch.database_util.service import common_parameters, search_filter_sort_paginate
from .models import (
    Quality,
    QualityResponse,
    QualityPagination,
    QualityRead,
    QualityUpdate,
)
from .service import create, update, delete
from datetime import datetime, timezone
from sqlalchemy import func
from .models import QualityCreate
router = APIRouter()


@router.get("/", response_model=QualityPagination)
def get_Quality(*, common: dict = Depends(common_parameters), db_session: Session = Depends(get_db)):
    # print(db_session.query(Quality).count())
    quality = search_filter_sort_paginate(model="Quality", **common)
    # print("==========",quality)
    return quality


@router.get("/{quality_id}", response_model=QualityRead)
def get_advice(
    *,
    db_session: Session = Depends(get_db),
    quality_id: int
):
    quality = get(db_session=db_session, id=quality_id)
    return quality



@router.post("/", response_model=QualityRead)
def create_quality(*, db_session: Session = Depends(get_db), quality_in: QualityCreate,
                 current_user: DispatchUser = Depends(get_current_user)):
    """
    Create a new quality contact.
    """
    
    quality_in.created_by = current_user.email
    quality_in.updated_by = current_user.email
    qualityEl = create(db_session=db_session, quality_in=quality_in)
    return qualityEl


@router.put("/{quality_id}", response_model=QualityRead)
def update_qualityEl(
    *,
    db_session: Session = Depends(get_db),
    quality_id: int,
    quality_in: QualityUpdate, current_user: DispatchUser = Depends(get_current_user)
):
    """
    Update a qualityEl contact.
    """
    qualityEl = get(db_session=db_session, id=quality_id)
    if not qualityEl:
        raise HTTPException(status_code=400, detail="The qualityEl with this id does not exist.")

    qualityEl = update(
        db_session=db_session,
        spmainel=qualityEl,
        spmainel_in=quality_in,
    )
    return qualityEl




@router.delete("/{qualityEl_id}", response_model=QualityRead)
def delete_qualityEl(*, db_session: Session = Depends(get_db), qualityEl_id: int):
    """
    Delete a qualityEl contact.
    """
    qualityEl = get(db_session=db_session, id=qualityEl_id)
    if not qualityEl:
        raise HTTPException(status_code=400, detail="The qualityEl with this id does not exist.")

    return delete(db_session=db_session, id=qualityEl_id)


