
from datetime import datetime, timezone
import json
from typing import List, Optional
from sqlalchemy.sql.functions import func
from .models import Shift, ShiftCreate, ShiftUpdate
def get(*, db_session, id: int) -> Optional[Shift]:
    """Returns an depot given an depot id."""
    return db_session.query(Shift).filter(Shift.id == id).one_or_none()

def get_by_code(*, db_session, code: str) -> Optional[Shift]:
    """Returns an depot given an depot code address."""
    return db_session.query(Shift).filter(Shift.code == code).one_or_none()



def get_or_create(*, db_session, code: str, **kwargs) -> Shift:
    """Gets or creates an depot."""
    contact = get_by_code(db_session=db_session, code=code)
    if not contact: 
        Shift_in = ShiftCreate(**kwargs)
        contact = create(db_session=db_session, Shift_in=Shift_in)

    return contact


def create(*, db_session, Shift_in: ShiftCreate) -> Shift:
    """Creates an depot."""
    # exclude={"flex_form_data", "location"}
    if not Shift_in.shift_no:
        raise Exception("shift_no is required")
    Shift_in.created_at=datetime.now(timezone.utc)
    Shift_in.code=f"{Shift_in.created_at.strftime('%Y-%m-%d')}--{Shift_in.shift_no}"
    contact = Shift(**Shift_in.dict())
    db_session.add(contact)
    db_session.commit()
    return contact


# def update(
#     *,
#     db_session,
#     depot: Shift,
#     depot_in: DepotUpdate,
# ) -> Shift:

#     update_data = depot_in.dict(
#        
#         exclude={"flex_form_data", "location"},
#     )
#     if depot_in.location and (not depot.location or depot_in.location.code != depot.location.code):
#         location_obj = location_service.get_or_create_by_code(
#             db_session=db_session, location_in=depot_in.location)
#         depot.location = location_obj

#     for field, field_value in update_data.items():
#         setattr(depot, field, field_value)

#     depot.flex_form_data = depot_in.flex_form_data
#     db_session.add(depot)
#     db_session.commit()
#     return depot


def update(
    db_session,
    item: Shift,
    item_in: ShiftUpdate,
) -> Shift:

    update_data = item_in.dict(
        #
        exclude={"flex_form_data"},
    )
    for field, field_value in update_data.items():
        setattr(item, field, field_value)

    db_session.add(item)
    db_session.commit()
    return item

def delete(*, db_session, id: int):
    db_session.query(Shift).filter(Shift.id == id).delete()
    db_session.commit()
