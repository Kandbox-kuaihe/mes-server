from fastapi import APIRouter, Depends, HTTPException
from .models import RemoveReason, RemoveReasonBase, RemoveReasonCreate, RemoveReasonUpdate, RemoveReasonPagination, RemoveReasonRead
from dispatch.database_util.service import common_parameters, search_filter_sort_paginate
from sqlalchemy.orm import Session
from dispatch.database import get_db
from dispatch.system_admin.auth.models import DispatchUser
from dispatch.system_admin.auth.service import get_current_user
from .service import create, delete, get, update, get_by_code, get_codes

router = APIRouter()


@router.get("/", response_model=RemoveReasonPagination)
def get_all(*, common: dict=Depends(common_parameters)):
    return search_filter_sort_paginate(model="RemoveReason", **common)

@router.post("/", response_model=RemoveReasonRead)
def create_holdreason(*, db_session: Session = Depends(get_db), removereason_in: RemoveReasonBase,
                      current_user: DispatchUser = Depends(get_current_user)):
    existed = get_by_code(db_session=db_session, code=removereason_in.code)

    if existed:
        raise HTTPException(status_code=400, detail="The RemoveReason with this code already exists.")
    created = create(db_session=db_session, holdreason_in=removereason_in)
    return created

@router.put("/{removereason_id}", response_model=RemoveReasonRead)
def update_removereason(
    *,
    db_session: Session = Depends(get_db),
    current_user: DispatchUser = Depends(get_current_user),
    removereason_id: int,
    removereason_in: RemoveReasonUpdate
):
    removereason = get(db_session=db_session, id=removereason_id)
    if not removereason:
        raise HTTPException(status_code=400, detail="The RemoveReason with this id does not exist.")
    updated = update(db_session=db_session, item=removereason, item_in=removereason_in)
    return updated

@router.delete("/{removereason_id}")
def delete_removereason(
    *,
    db_session: Session = Depends(get_db),
    current_user: DispatchUser = Depends(get_current_user),
    removereason_id: int
):
    holdreason = get(db_session=db_session, id=removereason_id)
    if not holdreason:
        raise HTTPException(status_code=400, detail="The removeReason with this id does not exist.")
    deleted = delete(db_session=db_session, id=removereason_id)
    return deleted


@router.get("/item/codes")
def get_code(db_session: Session = Depends(get_db)):
    # print(id)
    ls = get_codes(db_session=db_session)
    return ls