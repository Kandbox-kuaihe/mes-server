from dispatch.database import get_db
from typing import List
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from dispatch.system_admin.auth.models import DispatchUser
from dispatch.system_admin.auth.service import get_current_user

from dispatch.database_util.service import common_parameters, search_filter_sort_paginate
from .models import (
    Transport,
    TransportCreate,
    TransportUpdate,
    TransportRead,
    TransportPagination,
)
from .service import create, update, delete, get, update_on_load, update_de_load

router = APIRouter()


@router.get("/", response_model=TransportPagination)
def get_transports(*, common: dict = Depends(common_parameters)):
    return search_filter_sort_paginate(model="Transport", **common)

@router.get("/{id}", response_model=TransportRead)
def get_one(
    *,
    db_session: Session = Depends(get_db),
    id: int
):
    existed = get(db_session=db_session, id=id)
    if not existed:
        raise HTTPException(status_code=400, detail=f"The Transport with this id does not exist.")
    return existed

@router.post("/", response_model=TransportRead)
def create_transport(*, db_session: Session = Depends(get_db), transport_in: TransportCreate,
                 current_user: DispatchUser = Depends(get_current_user)):
    
    # transport = get_by_code(db_session=db_session,code=transport_in.transport_code)
    # if transport:
    #     raise HTTPException(status_code=400, detail="The transport with this code already exists.")
    
    transport_in.created_by = current_user.email
    transport_in.updated_by = current_user.email
    transport_in.created_at = datetime.now()
    transport_in.updated_at = datetime.now()
    transport = create(db_session=db_session, transport_in=transport_in)
    return transport

@router.put("/on_load")
def move_finished_product_load(
    *,
    db_session: Session = Depends(get_db),
    transport_in: TransportUpdate, current_user: DispatchUser = Depends(get_current_user)
):
    transport_in.updated_at = datetime.now()
    transport_in.updated_by = current_user.email
    return update_on_load(db_session=db_session, transport_in=transport_in)

@router.put("/de_load")
def move_finished_product_load(
    *,
    db_session: Session = Depends(get_db),
    transport_in: TransportUpdate, current_user: DispatchUser = Depends(get_current_user)
):
    transport_in.updated_at = datetime.now()
    transport_in.updated_by = current_user.email
    return update_de_load(db_session=db_session, transport_in=transport_in)


@router.put("/{transport_id}", response_model=TransportRead)
def update_transport(
    *,
    db_session: Session = Depends(get_db),
    transport_id: int,
    transport_in: TransportUpdate, current_user: DispatchUser = Depends(get_current_user)
):
    transport = get(db_session=db_session, id=transport_id)
    if not transport:
        raise HTTPException(status_code=400, detail="The transport with this id does not exist.")
    
    transport_in.updated_by = current_user.email
    transport_in.updated_at = datetime.now()

    transport = update(
        db_session=db_session,
        transport=transport,
        transport_in=transport_in,
    )
    return transport


@router.delete("/{transport_id}")
def delete_transport(*, db_session: Session = Depends(get_db), current_user: DispatchUser = Depends(get_current_user), transport_id: int):
    transport = get(db_session=db_session, id=transport_id)
    if not transport:
        raise HTTPException(status_code=400, detail="The transport with this id does not exist.")

    delete(db_session=db_session, transport=transport, transport_id=transport_id, current_user=current_user)
    
    return {"deleted": "ok"}
