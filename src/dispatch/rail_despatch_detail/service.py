from typing import Optional
from sqlalchemy.orm import Session
from dispatch.rail.rail_despatch_detail.models import RailDispatchDetail, RailDispatchDetailCreate

def create_detail(*, db_session: Session, request_in: RailDispatchDetailCreate) -> RailDispatchDetail:
    """Creates a new rail dispatch detail record."""
    rail_dispatch_detail = RailDispatchDetail(**request_in.dict())
    db_session.add(rail_dispatch_detail)
    db_session.commit()
    db_session.refresh(rail_dispatch_detail)
    return rail_dispatch_detail

def get_detail(*, db_session: Session, rail_dispatch_detail_id: int) -> Optional[RailDispatchDetail]:
    """Returns a rail dispatch detail record by its ID."""
    return db_session.query(RailDispatchDetail).filter(RailDispatchDetail.id == rail_dispatch_detail_id).one_or_none()

def delete_detail(*, db_session: Session, rail_dispatch_detail_id: int) -> Optional[RailDispatchDetail]:
    """Deletes a rail dispatch detail record by its ID."""
    rail_dispatch_detail = db_session.query(RailDispatchDetail).filter(RailDispatchDetail.id == rail_dispatch_detail_id).one_or_none()
    if rail_dispatch_detail:
        db_session.delete(rail_dispatch_detail)
        db_session.commit()
    return rail_dispatch_detail
