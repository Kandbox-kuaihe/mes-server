from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from dispatch.database import get_db
from dispatch.database_util.service import common_parameters, search_filter_sort_paginate
from dispatch.system_admin.auth.models import DispatchUser
from dispatch.system_admin.auth.service import get_current_user
from dispatch.mill.models import Mill
from .models import ShiftDelay, ShiftDelayBase, ShiftDelayPagination, ShiftDelayRead, ShiftDelayUpdate
from .service import create, delete, get, get_by_code, update

# from .service import create, delete, get, get_by_code, get_by_code_org_id, update


router = APIRouter()



@router.get("/", response_model=ShiftDelayPagination)
def get_ShiftDelay(*, 
                   db_session: Session = Depends(get_db),
                   common: dict = Depends(common_parameters),
                   shift_id: int = None,  # 添加 shift_id 参数，默认值为 None
                   area_code: str = None,  # 添加 area_code 参数，默认值为 None
                   delay_code: str = None
                ):  # 添加 delay_code 参数，默认值为 None
    query = db_session.query(ShiftDelay).outerjoin(Mill, ShiftDelay.mill_id == Mill.id)

    if shift_id is not None:
        query = query.filter(ShiftDelay.shift_id == shift_id)
    if area_code is not None:
        query = query.filter(ShiftDelay.area_code == area_code)
    if delay_code is not None:
        query = query.filter(ShiftDelay.delay_code == delay_code)

    if common["query_str"]:
        common['query'] = query.filter(ShiftDelay.code.like(f'%{common["query_str"]}%'))
        common["query_str"] = ''
    else:
        common['query'] = query

    return search_filter_sort_paginate(model="ShiftDelay", **common)




@router.post("/",response_model=ShiftDelayRead)
def createShiftDelay(*, db_session: Session = Depends(get_db), Shift_in: ShiftDelayBase,
                 current_user: DispatchUser = Depends(get_current_user)):
    """
    Create a new depot contact.
    # """
    # id和delay no 作为唯一约束，== 不需要查重
    Shift_obj = create(db_session=db_session, Shift_in=Shift_in)
    return Shift_obj



@router.get("/{id}", response_model=ShiftDelayRead)
def get_ShiftDelay(*, db_session: Session = Depends(get_db), id: int):
    """
    Get a depot contact.
    """
    data = get(db_session=db_session, id=id)
    if not data:
        raise HTTPException(status_code=400, detail="The data with this id does not exist.")
    return data


@router.put("/{id}", response_model=ShiftDelayRead)
def update_shift_delay(
    *,
    db_session: Session = Depends(get_db),
    id: int,
    Shift_in: ShiftDelayUpdate, current_user: DispatchUser = Depends(get_current_user)
):
    """
    Update a Shift .
    """
    Shift = get(db_session=db_session, id=id)
    if not Shift:
        raise HTTPException(status_code=400, detail="The Shift with this id does not exist.")

    ShiftObj = update(
        db_session=db_session,
        item=Shift,
        item_in=Shift_in,
    )
    return ShiftObj



@router.delete("/{Shift_id}")
def deleteShiftDelay(*, db_session: Session = Depends(get_db), Shift_id: int):
    """
    Delete a depot contact.
    """
    data = get(db_session=db_session, id=Shift_id)
    if not data:
        raise HTTPException(status_code=400, detail="The data with this id does not exist.")

    delete(db_session=db_session, id=Shift_id)
