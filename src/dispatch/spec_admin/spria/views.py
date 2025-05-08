import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from dispatch.database import get_db
from dispatch.database_util.service import common_parameters, search_filter_sort_paginate
from dispatch.system_admin.auth.models import DispatchUser
from dispatch.system_admin.auth.service import get_current_user
from .models import SpriaCreate, SpriaPagination, SpriaRead, SpriaUpdate, SpriaCopyToCode
from .service import create, delete, get, get_by_code, update, create_by_copy_spec_code

router = APIRouter()


@router.get("/", response_model=SpriaPagination)
def get_sprias(*, common: dict = Depends(common_parameters)):

    return search_filter_sort_paginate(model="Spria", **common)


@router.post("/", response_model=SpriaRead)
def create_spria(
    *,
    db_session: Session = Depends(get_db),
    spria_in: SpriaCreate,
    current_user: DispatchUser = Depends(get_current_user)
):
    """
    Create a new spria contact.
    """
    spria_in.created_by = current_user.email
    spria_in.updated_by = current_user.email
    try:
        spria = create(db_session=db_session, spria_in=spria_in)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return spria


@router.get("/{spria_id}", response_model=SpriaRead)
def get_spria(*, db_session: Session = Depends(get_db), spria_id: int):
    """
    Get a spria contact.
    """
    spria = get(db_session=db_session, id=spria_id)
    if not spria:
        raise HTTPException(status_code=400, detail="The spria with this id does not exist.")
    return spria


@router.put("/{spria_id}", response_model=SpriaRead)
def update_spria(
    *,
    db_session: Session = Depends(get_db),
    spria_id: int,
    spria_in: SpriaUpdate,
    current_user: DispatchUser = Depends(get_current_user)
):
    """
    Update a spria contact.
    """
    spria = get(db_session=db_session, id=spria_id)
    if not spria:
        raise HTTPException(status_code=400, detail="The spria with this id does not exist.")
    spria.updated_by = current_user.email
    spria.updated_at = datetime.datetime.now(datetime.UTC)
    spria = update(
        db_session=db_session,
        spria=spria,
        spria_in=spria_in,
    )
    return spria


@router.put("/spria_code/{spria_code}", response_model=SpriaRead)
def update_spria_by_code(
    *,
    db_session: Session = Depends(get_db),
    spria_code: str,
    spria_in: SpriaUpdate,
    current_user: DispatchUser = Depends(get_current_user)
):
    """
    Update a spria contact.
    """
    spria = get_by_code(db_session=db_session, code=spria_code)
    if not spria:
        raise HTTPException(status_code=400, detail="The spria with this id does not exist.")

    spria_in.updated_by = current_user.email
    spria = update(
        db_session=db_session,
        spria=spria,
        spria_in=spria_in,
    )

    return spria


@router.delete("/{spria_id}", response_model=SpriaRead)
def delete_spria(*, db_session: Session = Depends(get_db), spria_id: int):
    """
    Delete a spria contact.
    """
    spria = get(db_session=db_session, id=spria_id)
    if not spria:
        raise HTTPException(status_code=400, detail="The spria with this id does not exist.")

    return delete(db_session=db_session, id=spria_id)


@router.post("/copy_to")
def create_by_copy_to(
    *,
    db_session: Session = Depends(get_db),
    copy_dict: SpriaCopyToCode,
    current_user: DispatchUser = Depends(get_current_user)
):
    spimpact = create_by_copy_spec_code(db_session=db_session, copy_dict=copy_dict, current_user=current_user)
    return spimpact
