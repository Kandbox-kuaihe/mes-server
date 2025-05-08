from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from dispatch.database import get_db
from dispatch.rail_despatch_detail.models import RailDispatchDetailCreate, RailDispatchDetailRead
from dispatch.rail_despatch_detail.service import create_detail, get_detail, delete_detail

router = APIRouter()

@router.post("/detail/", response_model=RailDispatchDetailRead)
def create_rail_dispatch_detail(*, db_session: Session = Depends(get_db), rail_dispatch_detail_in: RailDispatchDetailCreate):
    """
    Create a new rail dispatch detail record.
    """
    rail_dispatch_detail = create_detail(db_session=db_session, request_in=rail_dispatch_detail_in)
    return rail_dispatch_detail

@router.get("/detail/{rail_dispatch_detail_id}", response_model=RailDispatchDetailRead)
def get_rail_dispatch_detail(*, db_session: Session = Depends(get_db), rail_dispatch_detail_id: int):
    """
    Get a specific rail dispatch detail by ID.
    """
    rail_dispatch_detail = get_detail(db_session=db_session, rail_dispatch_detail_id=rail_dispatch_detail_id)
    if not rail_dispatch_detail:
        raise HTTPException(status_code=400, detail="Rail dispatch detail not found.")
    return rail_dispatch_detail

@router.delete("/detail/{rail_dispatch_detail_id}", response_model=RailDispatchDetailRead)
def delete_rail_dispatch_detail(*, db_session: Session = Depends(get_db), rail_dispatch_detail_id: int):
    """
    Delete a rail dispatch detail record by ID.
    """
    rail_dispatch_detail = delete_detail(db_session=db_session, rail_dispatch_detail_id=rail_dispatch_detail_id)
    if not rail_dispatch_detail:
        raise HTTPException(status_code=400, detail="Rail dispatch detail not found.")
    return rail_dispatch_detail
