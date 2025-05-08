from dispatch.database import get_db
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from dispatch.system_admin.auth.models import DispatchUser
from dispatch.system_admin.auth.service import get_current_user

from dispatch.database_util.service import common_parameters, search_filter_sort_paginate
from .models import AlternativeSemiSize, AlternativeSemiSizeCreate, AlternativeSemiSizePagination, AlternativeSemiSizeRead, AlternativeSemiSizeUpdate
from .service import create, delete, get, update
from dispatch.order_admin.order_group.models import OrderGroup

router = APIRouter()


@router.get("/", response_model=AlternativeSemiSizePagination)
def get_semis(*, common: dict = Depends(common_parameters)):
    return search_filter_sort_paginate(model="AlternativeSemiSize", **common)


@router.post("/", response_model=AlternativeSemiSizeRead)
def create_semi(
        *,
        db_session: Session = Depends(get_db),
        semi_in: AlternativeSemiSizeCreate,
        current_user: DispatchUser = Depends(get_current_user)
):
    """
    Create a new semi contact.
    """
    semi_in.created_by = current_user.email
    semi_in.updated_by = current_user.email
    semi = create(db_session=db_session, semi_in=semi_in)
    return semi


@router.get("/{semi_id}", response_model=AlternativeSemiSizeRead)
def get_semi(*, db_session: Session = Depends(get_db), semi_id: int):
    """
    Get a semi contact.
    """
    semi = get(db_session=db_session, semi_id=semi_id)
    if not semi:
        raise HTTPException(status_code=400, detail="The semi size with this id does not exist.")
    return semi


@router.put("/{semi_id}", response_model=AlternativeSemiSizeRead)
def update_semi(
        *,
        db_session: Session = Depends(get_db),
        semi_id: int,
        semi_in: AlternativeSemiSizeUpdate,
        current_user: DispatchUser = Depends(get_current_user)
):
    """
    Update a semi contact.
    """
    semi = get(db_session=db_session, semi_id=semi_id)
    if not semi:
        raise HTTPException(status_code=400, detail="The semi size with this id does not exist.")
    semi_in.updated_by = current_user.email
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


@router.get('/semi_size_by_order_group/{order_group_id}', response_model=AlternativeSemiSizePagination)
def get_semi_size_by_order_group(*, db_session: Session = Depends(get_db), order_group_id: int, common: dict = Depends(common_parameters)):
    group = db_session.query(OrderGroup).filter(OrderGroup.id == order_group_id).first()
    if not group:
        raise HTTPException(status_code=400, detail="The order group with this id does not exist.")
    query = db_session.query(AlternativeSemiSize).filter(AlternativeSemiSize.product_type_id == group.product_id).order_by(AlternativeSemiSize.rank_seq)
    common["query"] = query
    return search_filter_sort_paginate(model="AlternativeSemiSize", **common)