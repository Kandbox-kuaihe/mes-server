from dispatch.database import get_db
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from dispatch.system_admin.auth.models import DispatchUser
from dispatch.system_admin.auth.service import get_current_user
from dispatch.mill.models import Mill

from dispatch.database_util.service import common_parameters, search_filter_sort_paginate
from .models import (
    Shift,
    ShiftBase,
    ShiftRead,
    ShiftPagination,
    ShiftUpdate
    # DepotPagination,
)
# from .service import create, delete, get, get_by_code, get_by_code_org_id, update


from .service import get_by_code,create,get,update,delete
router = APIRouter()



@router.get("/", response_model=ShiftPagination)
def get_Shifts(*, db_session: Session = Depends(get_db), common: dict = Depends(common_parameters)):
    query = db_session.query(Shift).outerjoin(Mill, Shift.mill_id == Mill.id)

    if common["query_str"]:
        common['query'] = query.filter(Shift.code.like(f'%{common["query_str"]}%'))
        common["query_str"] = ''

    return search_filter_sort_paginate(model="Shift", **common)




@router.post("/",response_model=ShiftRead)
def create_depot(*, db_session: Session = Depends(get_db), Shift_in: ShiftBase,
                 current_user: DispatchUser = Depends(get_current_user)):
    """
    Create a new depot contact.
    # """
    Shift = get_by_code(db_session=db_session,code=Shift_in.code)
    if Shift:
        raise HTTPException(status_code=400, detail="The Shift with this code already exists.")
    Shift_obj = create(db_session=db_session, Shift_in=Shift_in)
    return Shift_obj



@router.get("/{id}", response_model=ShiftRead)
def get_Shift(*, db_session: Session = Depends(get_db), id: int):
    """
    Get a depot contact.
    """
    depot = get(db_session=db_session, id=id)
    if not depot:
        raise HTTPException(status_code=400, detail="The depot with this id does not exist.")
    return depot


@router.put("/{id}", response_model=ShiftRead)
def update_obj(
    *,
    db_session: Session = Depends(get_db),
    id: int,
    Shift_in: ShiftUpdate, current_user: DispatchUser = Depends(get_current_user)
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
def delete_depot(*, db_session: Session = Depends(get_db), Shift_id: int):
    """
    Delete a depot contact.
    """
    depot = get(db_session=db_session, id=Shift_id)
    if not depot:
        raise HTTPException(status_code=400, detail="The depot with this id does not exist.")

    delete(db_session=db_session, id=Shift_id)
