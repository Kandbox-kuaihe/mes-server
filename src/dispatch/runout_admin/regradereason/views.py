from fastapi import APIRouter, Depends, HTTPException
from .models import RegradeReason, RegradereasonCreate, RegradereasonRead, RegradereasonUpdate, RegradereasonPagination, RegradereasonBase
from dispatch.database_util.service import common_parameters, search_filter_sort_paginate
from sqlalchemy.orm import Session
from dispatch.database import get_db
from dispatch.system_admin.auth.models import DispatchUser
from dispatch.system_admin.auth.service import get_current_user
from .service import create, delete, get, update, get_by_code, get_codes

router = APIRouter()


@router.get("/", response_model=RegradereasonPagination)
def get_all(*, common: dict=Depends(common_parameters)):
    return search_filter_sort_paginate(model="RegradeReason", **common)

@router.post("/", response_model=RegradereasonRead)
def create_regradereason(*, db_session: Session = Depends(get_db), regradereason_in: RegradereasonBase,
                      current_user: DispatchUser = Depends(get_current_user)):
    existed = get_by_code(db_session=db_session, code=regradereason_in.code)

    if existed and existed.is_deleted == 1:
        db_session.query(RegradeReason).filter(RegradeReason.id == existed.id).update({"is_deleted": 0})
        update(db_session=db_session, item=existed, item_in=regradereason_in)
        db_session.commit()
        return existed
    elif existed and existed.is_deleted == 0:
        raise HTTPException(status_code=400, detail="The RegradeReason with this code already exists.")
    else:
        created = create(db_session=db_session, regradereason_in=regradereason_in)
        return created

@router.put("/{regradereason_id}", response_model=RegradereasonRead)
def update_regradereason(
    *,
    db_session: Session = Depends(get_db),
    current_user: DispatchUser = Depends(get_current_user),
    regradereason_id: int,
    regradereason_in: RegradereasonUpdate
):
    regradereason = get(db_session=db_session, id=regradereason_id)
    if not regradereason:
        raise HTTPException(status_code=400, detail="The RegradeReason with this id does not exist.")
    updated = update(db_session=db_session, item=regradereason, item_in=regradereason_in)
    return updated

@router.delete("/{regradereason_id}")
def delete_regradereason(
    *,
    db_session: Session = Depends(get_db),
    current_user: DispatchUser = Depends(get_current_user),
    regradereason_id: int
):
    regradereason = get(db_session=db_session, id=regradereason_id)
    if not regradereason:
        raise HTTPException(status_code=400, detail="The RegradeReason with this id does not exist.")
    deleted = delete(db_session=db_session, id=regradereason_id)
    return deleted


@router.get("/item/codes")
def get_code(db_session: Session = Depends(get_db)):
    # print(id)
    ls = get_codes(db_session=db_session)
    return ls