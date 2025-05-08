from sqlalchemy import desc
from dispatch.database import get_db, get_class_by_tablename
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from dispatch.system_admin.auth.models import DispatchUser
from dispatch.system_admin.auth.service import get_current_user

from dispatch.database_util.service import common_parameters, search_filter_sort_paginate
from .models import (
    SpecDeoxidation,
    SpecDeoxidationCreate,
    SpecDeoxidationUpdate,
    SpecDeoxidationRead,
    SpecDeoxidationPagination,
    SpecDeoxidationBase
)
from .service import create, delete, get, update
from datetime import datetime, timezone
from dispatch.spec_admin.inspector import service as inspector_service

router = APIRouter()


@router.get("/", response_model=SpecDeoxidationPagination)
def get_deoxidation(*, common: dict = Depends(common_parameters)):

    return search_filter_sort_paginate(model="SpecDeoxidation", **common)


@router.get("/{deoxidation_id}", response_model=SpecDeoxidationRead)
def get_deoxidation(*, db_session: Session = Depends(get_db), deoxidation_id: int):
    """
    Get a deoxidation contact.
    """
    deoxidation = get(db_session=db_session, id=deoxidation_id)
    if not deoxidation:
        raise HTTPException(status_code=400, detail="The deoxidation with this id does not exist.")
    return deoxidation

@router.post("/", response_model=SpecDeoxidationRead)
def create_deoxidation(
    *,
    db_session: Session = Depends(get_db),
    deoxidation_in: SpecDeoxidationCreate,
    current_user: DispatchUser = Depends(get_current_user)
):
    """
    Create a new deoxidation contact.
    """

    deoxidation_in.created_by = current_user.email
    deoxidation_in.updated_by = current_user.email
    deoxidation = create(db_session=db_session, deoxidation_in=deoxidation_in)

    db_session.add(deoxidation)
    db_session.commit()
    return deoxidation



@router.put("/{deoxidation_id}", response_model=SpecDeoxidationRead)
def update_deoxidation(
    *,
    db_session: Session = Depends(get_db),
    deoxidation_id: int,
    deoxidation_in: SpecDeoxidationUpdate,
    current_user: DispatchUser = Depends(get_current_user)
):
    """
    Update a deoxidation contact.
    """
    deoxidation = get(db_session=db_session, id=deoxidation_id)
    if not deoxidation:
        raise HTTPException(status_code=400, detail="The deoxidation with this id does not exist.")

    deoxidation_in.updated_by = current_user.email
    deoxidation_in.updated_at = datetime.now(timezone.utc)
    deoxidation = update(
        db_session=db_session,
        deoxidation=deoxidation,
        deoxidation_in=deoxidation_in,
    )
    return deoxidation


@router.delete("/{deoxidation_id}", response_model=SpecDeoxidationRead)
def delete_deoxidation(*, db_session: Session = Depends(get_db), deoxidation_id: int):
    """
    Delete a deoxidation test card contact.
    """
    deoxidation = get(db_session=db_session, id=deoxidation_id)
    if not deoxidation:
        raise HTTPException(status_code=400, detail="The spec with this id does not exist.")

    return delete(db_session=db_session, id=deoxidation_id)

