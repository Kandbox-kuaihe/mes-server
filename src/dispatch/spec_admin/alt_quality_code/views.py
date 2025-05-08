from dispatch.database import get_db
from typing import List
from dispatch.database_util.service import common_parameters, search_filter_sort_paginate
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from dispatch.system_admin.auth.models import DispatchUser
from dispatch.spec_admin.quality.models import Quality

from dispatch.system_admin.auth.service import get_current_user
from .models import AltQualityCode as AltQualityCode
from .models import (
    AltQualityCodeCreate,
    AltQualityCodeRead,
    AltQualityCodePagination,
    AltQualityCodeUpdate
)
from .service import create, delete, get, update, get_all, get_id
from datetime import datetime, timezone

router = APIRouter()


@router.get("/", response_model=AltQualityCodePagination)
def get_alt_quality_codes(*, common: dict = Depends(common_parameters)):
    
    common["query_str"] = ''

    return search_filter_sort_paginate(model="AltQualityCode", **common)

@router.get("/{id}", response_model=AltQualityCodeRead)
def get_alt_quality_cod_by_id(*, db_session: Session = Depends(get_db), id: int):
    alt_quality_code = get_id(db_session=db_session, id=id)
    return alt_quality_code

@router.post("/search", response_model=AltQualityCodePagination)
def search_alt_quality_codes(
    *,
    db_session: Session = Depends(get_db),
    quality_code: str = Query(..., description="Quality Code to search for"),
    page: int = Query(1, description="Page number"),
    items_per_page: int = Query(10, description="Number of items per page")
):
    quality = db_session.query(Quality).filter_by(code=quality_code).first()
    if not quality:
        raise HTTPException(status_code=404, detail="Quality not found.")
    """Search AltQualityCodes by quality_code."""
    return get(db_session=db_session, quality_id=quality.id, page=page, items_per_page=items_per_page)


@router.post("/", response_model=AltQualityCodeRead)
def create_alt_quality_code(
    *,
    db_session: Session = Depends(get_db),
    alt_quality_code_in: AltQualityCodeCreate,
    current_user: DispatchUser = Depends(get_current_user)
):
    quality = db_session.query(Quality).get(alt_quality_code_in.quality_id)
    if not quality:
        raise HTTPException(
            status_code=400,
            detail="Provided quality code does not exist."
        )
    
    alt_quality_code_in.quality_id = quality.id
    alt_quality_code_in.quality_code = quality.code
    """Create a new AltQualityCode."""
    # Check if the combination of quality_code and alt_quality_code already exists
    existing_record = db_session.query(AltQualityCode).filter_by(
        quality_id=quality.id,
        alt_quality_code=alt_quality_code_in.alt_quality_code
    ).first()

    if existing_record:
        raise HTTPException(
            status_code=400,
            detail="The same quality code cannot have the same alternate quality code."
        )


   # Check if the rank is already taken for the same quality_code
    rank_exists = db_session.query(AltQualityCode).filter_by(
        quality_id=quality.id,
        rank=alt_quality_code_in.rank
    ).first()

    if rank_exists:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Rank {alt_quality_code_in.rank} is already taken for Quality Code: "
                f"{rank_exists.quality.code}, Alternate Quality Code: {rank_exists.alt_quality_code}."
            )
        )
    alt_quality_code_in.created_by = current_user.email
    alt_quality_code_in.updated_by = current_user.email
    alt_quality_code = create(db_session=db_session, alt_quality_code_in=alt_quality_code_in)
    return alt_quality_code


@router.delete("/{id}")
def delete_alt_quality_code(
    *,
    db_session: Session = Depends(get_db),
    id: int,
):
    """Delete an AltQualityCode by ID."""
    alt_quality_code = delete(db_session=db_session, id=id)
    if not alt_quality_code:
        raise HTTPException(status_code=404, detail="AltQualityCode not found.")
    
    return delete(db_session=db_session, id=id)


@router.put("/{id}", response_model=AltQualityCodeRead)
def update_alt_quality_code(
    *,
    db_session: Session = Depends(get_db),
    id: int,
    alt_quality_code_in: AltQualityCodeUpdate,
    current_user: DispatchUser = Depends(get_current_user)
):
    alt_quality_code = get_id(db_session=db_session, id=id)
    if not alt_quality_code:
        raise HTTPException(status_code=400, detail="The Quality Code with this ID does not exist.")

    quality = db_session.query(Quality).filter_by(code=alt_quality_code_in.quality_code).first()
    if not quality:
        raise HTTPException(
            status_code=400,
            detail="Provided quality code does not exist."
        )
    # Set the foreign key on the update payload.
    alt_quality_code_in.quality_id = quality.id

    # Check if the updated combination of quality_code and alt_quality_code already exists
    existing_record = db_session.query(AltQualityCode).filter_by(
        quality_id=quality.id,
        alt_quality_code=alt_quality_code_in.alt_quality_code
    ).first()

    if existing_record and existing_record.id != id:
        raise HTTPException(
            status_code=400,
            detail="The same quality code cannot have the same alternate quality code."
        )

    # Check if the rank is already taken for the same quality_code
    rank_exists = db_session.query(AltQualityCode).filter_by(
        quality_id=quality.id,
        rank=alt_quality_code_in.rank
    ).first()

    if rank_exists and rank_exists.id != id:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Rank {alt_quality_code_in.rank} is already taken for Quality Code: "
                f"{rank_exists.quality.code}, Alternate Quality Code: {rank_exists.alt_quality_code}."
            )
        )

    update_data = alt_quality_code_in.dict(
        exclude_unset=True,                    # skip any field not provided
        exclude={ "id", "created_by", "created_at", "flex_form_data" }
    )
    for field, value in update_data.items():
        setattr(alt_quality_code, field, value)


    alt_quality_code_in.updated_at = datetime.now(timezone.utc)
    alt_quality_code_in.updated_by = current_user.email

    alt_quality_code = update(
        db_session=db_session,
        alt_quality_code=alt_quality_code,
        alt_quality_code_in=alt_quality_code_in,
    )
    return alt_quality_code
