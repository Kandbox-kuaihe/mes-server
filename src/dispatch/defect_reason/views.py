from dispatch.database import get_db
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from dispatch.system_admin.auth.models import DispatchUser
from dispatch.system_admin.auth.service import get_current_user

from dispatch.database_util.service import common_parameters, search_filter_sort_paginate
from .models import (
    DefectReasonBase,
    DefectReasonRead,
    DefectReasonPagination,
    DefectReasonUpdate,
    DefectReasonCreate
    # DepotPagination,
)
# from .service import create, delete, get, get_by_code, get_by_code_org_id, update


from .service import get_by_code,create,get,update,delete
router = APIRouter()


from .models import DefectReason

@router.get("/", response_model=DefectReasonPagination)
def get_DefectReasons(*, common: dict = Depends(common_parameters)):

    return search_filter_sort_paginate(model="DefectReason", **common)




@router.post("/",response_model=DefectReasonCreate)
def create_depot(*, db_session: Session = Depends(get_db), DefectReason_in: DefectReasonBase,
                 current_user: DispatchUser = Depends(get_current_user)):
    """
    Create a new depot contact.
    # """
    DefectReason_in.created_by = current_user.email
    DefectReason_in.updated_by = current_user.email
    DefectReason = get_by_code(db_session=db_session,code=DefectReason_in.code)
    if DefectReason:
        raise HTTPException(status_code=400, detail="The DefectReason with this code already exists.")
    DefectReason_obj = create(db_session=db_session, DefectReason_in=DefectReason_in)
    return DefectReason_obj



@router.get("/{id}", response_model=DefectReasonRead)
def get_DefectReason(*, db_session: Session = Depends(get_db), id: int):
    """
    Get a depot contact.
    """
    depot = get(db_session=db_session, id=id)
    if not depot:
        raise HTTPException(status_code=400, detail="The depot with this id does not exist.")
    return depot


@router.put("/{id}", response_model=DefectReasonUpdate)
def update_obj(
    *,
    db_session: Session = Depends(get_db),
    id: int,
    DefectReason_in: DefectReasonUpdate, current_user: DispatchUser = Depends(get_current_user)
):
    """
    Update a DefectReason .
    """
    DefectReason = get(db_session=db_session, id=id)
    if not DefectReason:
        raise HTTPException(status_code=400, detail="The DefectReason with this id does not exist.")
    
    DefectReason_in.updated_by = current_user.email
    DefectReasonObj = update(
        db_session=db_session,
        item=DefectReason,
        item_in=DefectReason_in,
    )
    return DefectReasonObj



@router.delete("/{id}")
def delete_depot(*, db_session: Session = Depends(get_db), id: int):
    """
    Delete a depot contact.
    """
    depot = get(db_session=db_session, id=id)
    if not depot:
        raise HTTPException(status_code=400, detail="The depot with this id does not exist.")

    delete(db_session=db_session, id=id)
