from fastapi import APIRouter, Depends, HTTPException
from .models import SemiHoldReason, SemiHoldReasonCreate, SemiHoldReasonRead, SemiHoldReasonUpdate, SemiHoldReasonPagination, SemiHoldReasonBase
from dispatch.database_util.service import common_parameters, search_filter_sort_paginate
from sqlalchemy.orm import Session
from dispatch.database import get_db
from dispatch.system_admin.auth.models import DispatchUser
from dispatch.system_admin.auth.service import get_current_user
from .service import create, delete, get, update, get_by_code, get_codes

router = APIRouter()


@router.get("/", response_model=SemiHoldReasonPagination)
def get_all(*, common: dict=Depends(common_parameters)):
    return search_filter_sort_paginate(model="SemiHoldReason", **common)

@router.post("/", response_model=SemiHoldReasonRead)
def create_holdreason(*, db_session: Session = Depends(get_db), holdreason_in: SemiHoldReasonBase,
                      current_user: DispatchUser = Depends(get_current_user)):
    existed = get_by_code(db_session=db_session, code=holdreason_in.code)

    if existed:
        raise HTTPException(status_code=400, detail="The HoldReason with this code already exists.")
    created = create(db_session=db_session, holdreason_in=holdreason_in)
    return created

@router.put("/{holdreason_id}", response_model=SemiHoldReasonRead)
def update_holdreason(
    *,
    db_session: Session = Depends(get_db),
    current_user: DispatchUser = Depends(get_current_user),
    holdreason_id: int,
    holdreason_in: SemiHoldReasonUpdate
):
    holdreason = get(db_session=db_session, id=holdreason_id)
    if not holdreason:
        raise HTTPException(status_code=400, detail="The HoldReason with this id does not exist.")
    updated = update(db_session=db_session, item=holdreason, item_in=holdreason_in)
    return updated

@router.delete("/{holdreason_id}")
def delete_holdreason(
    *,
    db_session: Session = Depends(get_db),
    current_user: DispatchUser = Depends(get_current_user),
    holdreason_id: int
):
    holdreason = get(db_session=db_session, id=holdreason_id)
    if not holdreason:
        raise HTTPException(status_code=400, detail="The HoldReason with this id does not exist.")
    deleted = delete(db_session=db_session, id=holdreason_id)
    return deleted


@router.get("/item/codes")
def get_code(db_session: Session = Depends(get_db)):
    # print(id)
    ls = get_codes(db_session=db_session)
    return ls