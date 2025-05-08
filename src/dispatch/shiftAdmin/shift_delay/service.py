
import json
from typing import List, Optional

from sqlalchemy.sql.functions import func

from dispatch.mill.models import Mill
from dispatch.shiftAdmin.shift.models import Shift

from .models import ShiftDelay, ShiftDelayCreate, ShiftDelayUpdate


def get(*, db_session, id: int) -> Optional[ShiftDelay]:
    """Returns an depot given an depot id."""
    return db_session.query(ShiftDelay).filter(ShiftDelay.id == id).one_or_none()

def get_by_code(*, db_session, code: str) -> Optional[ShiftDelay]:
    """Returns an depot given an depot code address."""
    return db_session.query(ShiftDelay).filter(ShiftDelay.delay_code == code).one_or_none()



def get_or_create(*, db_session, code: str, **kwargs) -> ShiftDelay:
    """Gets or creates an depot."""
    contact = get_by_code(db_session=db_session, code=code)
    if not contact: 
        ShiftDelay_in = ShiftDelayCreate(**kwargs)
        contact = create(db_session=db_session, ShiftDelay_in=ShiftDelay_in)

    return contact


def create(*, db_session, ShiftDelay_in: ShiftDelayCreate) -> ShiftDelay:
    """Creates an depot."""

    shift = None
    mill = None
    if ShiftDelay_in.shift_id:
        shift = db_session.query(Shift).filter(Shift.id == ShiftDelay_in.shift_id).one_or_none()

    if ShiftDelay_in.mill_id:
        mill = db_session.query(Mill).filter(Mill.id == ShiftDelay_in.mill_id).one_or_none()
    

    contact = ShiftDelay(**ShiftDelay_in.dict(exclude={"flex_form_data", "shift","mill"}),mill=mill,shift=shift   )
    db_session.add(contact)
    db_session.commit()
    return contact

 

def update(
    db_session,
    item: ShiftDelay,
    item_in: ShiftDelayUpdate,
) -> ShiftDelay:

    shift = None
    mill = None
    if item_in.shift_id:
        shift = db_session.query(Shift).filter(Shift.id == item_in.shift_id).one_or_none()

    if item_in.mill_id:
        mill = db_session.query(Mill).filter(Mill.id == item_in.mill_id).one_or_none()
    
    update_data = item_in.dict(
        exclude={"flex_form_data","shift","mill"},
    )
    for field, field_value in update_data.items():
        setattr(item, field, field_value)

    item.shift = shift
    item.mill = mill
    # item.flex_form_data = item_in.flex_form_data  
    db_session.add(item)
    db_session.commit()
    return item

def delete(*, db_session, id: int):
    db_session.query(ShiftDelay).filter(ShiftDelay.id == id).delete()
    db_session.commit()
