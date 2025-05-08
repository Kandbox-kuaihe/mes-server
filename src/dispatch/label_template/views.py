from dispatch.database import get_db
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from dispatch.system_admin.auth.models import DispatchUser
from dispatch.system_admin.auth.service import get_current_user

from dispatch.database_util.service import common_parameters, search_filter_sort_paginate
from .models import LabelTemplateCreate, LabelTemplatePagination, LabelTemplateRead, LabelTemplateUpdate
from .service import create, delete, get, update

router = APIRouter()


@router.get("/", response_model=LabelTemplatePagination)
def get_semis(*, common: dict = Depends(common_parameters)):
    return search_filter_sort_paginate(model="LabelTemplate", **common)


@router.post("/", response_model=LabelTemplateRead)
def create_semi(
        *,
        db_session: Session = Depends(get_db),
        semi_in: LabelTemplateCreate,
        current_user: DispatchUser = Depends(get_current_user)
):
    """
    Create a new semi contact.
    """
    semi_in.created_by = current_user.email
    semi_in.updated_by = current_user.email
    semi = create(db_session=db_session, semi_in=semi_in)
    return semi


@router.get("/{semi_id}", response_model=LabelTemplateRead)
def get_semi(*, db_session: Session = Depends(get_db), semi_id: int):
    """
    Get a semi contact.
    """
    semi = get(db_session=db_session, semi_id=semi_id)
    if not semi:
        raise HTTPException(status_code=400, detail="The semi size with this id does not exist.")
    return semi


@router.put("/{semi_id}", response_model=LabelTemplateRead)
def update_semi(
        *,
        db_session: Session = Depends(get_db),
        semi_id: int,
        semi_in: LabelTemplateUpdate,
        current_user: DispatchUser = Depends(get_current_user)
):
    """
    Update a semi contact.
    """
    semi = get(db_session=db_session, semi_id=semi_id)
    if not semi:
        raise HTTPException(status_code=400, detail="The semi size with this id does not exist.")

    semi = update(
        db_session=db_session,
        semi=semi,
        semi_in=semi_in,
    )
    return semi


@router.delete("/{semi_id}")
def delete_semi(*, db_session: Session = Depends(get_db), semi_id: int):
    """
    Delete a semi contact.
    """
    semi = get(db_session=db_session, semi_id=semi_id)

    if not semi:
        raise HTTPException(status_code=400, detail="The semi size with this id does not exist.")

    return delete(db_session=db_session, semi_id=semi_id)


