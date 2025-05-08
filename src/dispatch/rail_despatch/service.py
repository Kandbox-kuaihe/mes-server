from typing import List, Optional
from sqlalchemy.orm import Session
from dispatch.rail.rail_despatch.models import RailDispatch, RailDispatchCreate, RailDispatchUpdate

def get(*, db_session: Session, rail_dispatch_id: int) -> Optional[RailDispatch]:
    """Returns a rail dispatch record by its ID."""
    return db_session.query(RailDispatch).filter(RailDispatch.id == rail_dispatch_id).one_or_none()

def get_all(*, db_session: Session) -> List[RailDispatch]:
    """Returns all rail dispatch records."""
    return db_session.query(RailDispatch).all()

def create(*, db_session: Session, request_in: RailDispatchCreate) -> RailDispatch:
    """Creates a new rail dispatch record."""
    rail_dispatch = RailDispatch(**request_in.dict())
    db_session.add(rail_dispatch)
    db_session.commit()
    db_session.refresh(rail_dispatch)
    return rail_dispatch

def update(*, db_session: Session, rail_dispatch: RailDispatch, rail_dispatch_in: RailDispatchUpdate) -> RailDispatch:
    """Updates an existing rail dispatch record."""
    update_data = rail_dispatch_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(rail_dispatch, field, value)
    
    db_session.add(rail_dispatch)
    db_session.commit()
    return rail_dispatch

def delete(*, db_session: Session, rail_dispatch_id: int) -> Optional[RailDispatch]:
    """Deletes a rail dispatch record by its ID."""
    rail_dispatch = db_session.query(RailDispatch).filter(RailDispatch.id == rail_dispatch_id).one_or_none()
    if rail_dispatch:
        db_session.delete(rail_dispatch)
        db_session.commit()
    return rail_dispatch
