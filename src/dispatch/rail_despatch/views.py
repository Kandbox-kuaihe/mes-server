from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from dispatch.database import get_db
from dispatch.rail_despatch.models import RailDispatchCreate, RailDispatchRead, RailDispatchUpdate
from dispatch.rail_despatch.service import create, get, get_all, update, delete
from typing import List
router = APIRouter()

@router.get("/", response_model=List[RailDispatchRead])
def get_rail_dispatches(*, db_session: Session = Depends(get_db)):
    """
    Get a list of all rail dispatch records.
    """
    return get_all(db_session=db_session)

@router.post("/", response_model=RailDispatchRead)
def create_rail_dispatch(*, db_session: Session = Depends(get_db), rail_dispatch_in: RailDispatchCreate):
    """
    Create a new rail dispatch record.
    """
    rail_dispatch = create(db_session=db_session, request_in=rail_dispatch_in)
    return rail_dispatch

@router.get("/{rail_dispatch_id}", response_model=RailDispatchRead)
def get_rail_dispatch(*, db_session: Session = Depends(get_db), rail_dispatch_id: int):
    """
    Get a specific rail dispatch record by ID.
    """
    rail_dispatch = get(db_session=db_session, rail_dispatch_id=rail_dispatch_id)
    if not rail_dispatch:
        raise HTTPException(status_code=400, detail="Rail dispatch not found.")
    return rail_dispatch

@router.put("/{rail_dispatch_id}", response_model=RailDispatchRead)
def update_rail_dispatch(*, db_session: Session = Depends(get_db), rail_dispatch_id: int, rail_dispatch_in: RailDispatchUpdate):
    """
    Update an existing rail dispatch record.
    """
    rail_dispatch = get(db_session=db_session, rail_dispatch_id=rail_dispatch_id)
    if not rail_dispatch:
        raise HTTPException(status_code=400, detail="Rail dispatch not found.")
    
    rail_dispatch = update(db_session=db_session, rail_dispatch=rail_dispatch, rail_dispatch_in=rail_dispatch_in)
    return rail_dispatch

@router.delete("/{rail_dispatch_id}", response_model=RailDispatchRead)
def delete_rail_dispatch(*, db_session: Session = Depends(get_db), rail_dispatch_id: int):
    """
    Delete a specific rail dispatch record by ID.
    """
    rail_dispatch = delete(db_session=db_session, rail_dispatch_id=rail_dispatch_id)
    if not rail_dispatch:
        raise HTTPException(status_code=400, detail="Rail dispatch not found.")
    return rail_dispatch
