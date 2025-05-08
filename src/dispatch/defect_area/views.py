from dispatch.database import get_db
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from dispatch.system_admin.auth.models import DispatchUser
from dispatch.system_admin.auth.service import get_current_user

from dispatch.database_util.service import common_parameters, search_filter_sort_paginate
from .models import (
    DefectAreaBase,
    DefectAreaRead,
    DefectAreaPagination,
    DefectAreaUpdate
    # DepotPagination,
)

from .service import get_by_code, create, get, update, delete

router = APIRouter()

from .models import DefectArea


@router.get("/", response_model=DefectAreaPagination)
def get_DefectAreas(*, common: dict = Depends(common_parameters)):
    return search_filter_sort_paginate(model="DefectArea", **common)


@router.post("/", response_model=DefectAreaRead)
def create_depot(*, db_session: Session = Depends(get_db), DefectArea_in: DefectAreaBase,
                 current_user: DispatchUser = Depends(get_current_user)):
    """
    Create a new depot contact.
    # """
    DefectArea = get_by_code(db_session=db_session, code=DefectArea_in.code)
    if DefectArea:
        raise HTTPException(status_code=400, detail="The DefectArea with this code already exists.")
    DefectArea_obj = create(db_session=db_session, DefectArea_in=DefectArea_in)
    return DefectArea_obj


@router.get("/{id}", response_model=DefectAreaRead)
def get_DefectArea(*, db_session: Session = Depends(get_db), id: int):
    """
    Get a depot contact.
    """
    depot = get(db_session=db_session, id=id)
    if not depot:
        raise HTTPException(status_code=400, detail="The depot with this id does not exist.")
    return depot


@router.put("/{id}", response_model=DefectAreaRead)
def update_obj(
        *,
        db_session: Session = Depends(get_db),
        id: int,
        DefectArea_in: DefectAreaUpdate, current_user: DispatchUser = Depends(get_current_user)
):
    """
    Update a DefectArea .
    """
    DefectArea = get(db_session=db_session, id=id)
    if not DefectArea:
        raise HTTPException(status_code=400, detail="The DefectArea with this id does not exist.")

    DefectAreaObj = update(
        db_session=db_session,
        item=DefectArea,
        item_in=DefectArea_in,
    )
    return DefectAreaObj


@router.delete("/{id}")
def delete_depot(*, db_session: Session = Depends(get_db), id: int):
    """
    Delete a depot contact.
    """
    depot = get(db_session=db_session, id=id)
    if not depot:
        raise HTTPException(status_code=400, detail="The depot with this id does not exist.")

    delete(db_session=db_session, id=id)
