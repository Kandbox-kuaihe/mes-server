from dispatch.database import get_db
from typing import List
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from dispatch.system_admin.auth.models import DispatchUser
from dispatch.system_admin.auth.service import get_current_user

from dispatch.database_util.service import common_parameters, search_filter_sort_paginate
from .models import (
    Runout,
    RunoutCreate,
    RunoutPagination,
    RunoutRead,
    RunoutUpdate,
)
from .service import create, delete, get, get_by_code, update
from dispatch.rolling.rolling_list import service as rolling_service
from dispatch.semi_admin.semi import service as semi_service
from dispatch.cast import service as cast_service
from dispatch.rolling.rolling_list.models import Rolling
from dispatch.cast.models import Cast
from dispatch.semi_admin.semi.models import Semi
from dispatch.product_type.models import ProductType
from dispatch.tests_admin.test_sample.models import TestSample


router = APIRouter()


@router.get("/", response_model=RunoutPagination)
def get_runouts(*,db_session: Session = Depends(get_db), common: dict = Depends(common_parameters), pick_runout_id:int= Query(None)):
    query = db_session.query(Runout
                        ).outerjoin(Rolling, Runout.rolling_id == Rolling.id
                        ).outerjoin(Cast, Runout.cast_id == Cast.id
                        ).outerjoin(Semi,Runout.semi_id == Semi.id
                        ).outerjoin(ProductType, Runout.product_type_id == ProductType.id)
    if pick_runout_id:
        query = query.join(TestSample, Runout.id == TestSample.runout_id)
        r = get(db_session=db_session, runout_id=pick_runout_id)
        query = query.filter(Runout.rolling_id == r.rolling_id, Runout.cast_id == r.cast_id, Runout.cast_id.isnot(None), Runout.rolling_id.isnot(None))
        flange_thickness = (r.product_type.flange_thickness or float('inf')) if r.product_type else float('inf')
        query = query.filter(ProductType.flange_thickness >= flange_thickness)
    common['query'] = query
    return search_filter_sort_paginate(model="Runout", **common)


@router.post("/", response_model=RunoutRead)
def create_runout(*, db_session: Session = Depends(get_db), runout_in: RunoutCreate,
                 current_user: DispatchUser = Depends(get_current_user)):
    """
    Create a new runout contact.
    """
    
    runout = get_by_code(db_session=db_session,code=runout_in.runout_code)
    if runout:
        raise HTTPException(status_code=400, detail="The runout with this code already exists.")
    
    runout_in.created_by = current_user.email
    runout_in.updated_by = current_user.email
    runout_in.created_at = datetime.now()
    runout_in.updated_at = datetime.now()
    runout_in.mill_id = current_user.current_mill_id
    runout = create(db_session=db_session, runout_in=runout_in)
    return runout


@router.get("/code/{runout_code}", response_model=RunoutRead)
def get_runout_by_code(*, db_session: Session = Depends(get_db), runout_code: str):
    runout = get_by_code(db_session=db_session, code=runout_code)
    if not runout:
        raise HTTPException(status_code=400, detail="The runout with this code does not exist.")
    return runout


@router.get("/{runout_id}", response_model=RunoutRead)
def get_runout(*, db_session: Session = Depends(get_db), runout_id: int):
    """
    Get a runout contact.
    """
    runout = get(db_session=db_session, runout_id=runout_id)
    if not runout:
        raise HTTPException(status_code=400, detail="The runout with this id does not exist.")
    return runout


@router.put("/{runout_id}", response_model=RunoutRead)
def update_runout(
    *,
    db_session: Session = Depends(get_db),
    runout_id: int,
    runout_in: RunoutUpdate, current_user: DispatchUser = Depends(get_current_user)
):
    """
    Update a runout contact.
    """
    runout = get(db_session=db_session, runout_id=runout_id)
    if not runout:
        raise HTTPException(status_code=400, detail="The runout with this id does not exist.")
    
    runout_in.updated_by = current_user.email
    runout_in.updated_at = datetime.now()
    runout_in.mill_id = current_user.current_mill_id
    runout = update(
        db_session=db_session,
        runout=runout,
        runout_in=runout_in,
    )
    return runout


@router.put("/runout_code/{runout_code}", response_model=RunoutRead)
def update_runout_by_code(
    *,
    db_session: Session = Depends(get_db),
    runout_code: str,
    runout_in: RunoutUpdate, current_user: DispatchUser = Depends(get_current_user)
):
    """
    Update a runout contact.
    """
    runout = get_by_code(db_session=db_session, code=runout_code)
    if not runout:
        raise HTTPException(status_code=400, detail="The runout with this id does not exist.")

    runout_in.updated_by = current_user.email
    runout = update(
        db_session=db_session,
        runout=runout,
        runout_in=runout_in,
    )

    return runout


@router.delete("/{runout_id}")
def delete_runout(*, db_session: Session = Depends(get_db), runout_id: int):
    """
    Delete a runout contact.
    """
    runout = get(db_session=db_session, runout_id=runout_id)
    if not runout:
        raise HTTPException(status_code=400, detail="The runout with this id does not exist.")

    delete(db_session=db_session, runout_id=runout_id)
    
    return {"deleted": "ok"}
