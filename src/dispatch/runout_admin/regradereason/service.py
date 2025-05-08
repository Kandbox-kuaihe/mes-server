from typing import Optional
from .models import RegradeReason, RegradereasonCreate, RegradereasonUpdate
from dispatch.mill.models import Mill, MillRead


def get(*, db_session, id: int) -> Optional[RegradeReason]:
    return db_session.query(RegradeReason).filter(RegradeReason.id == id).one_or_none()

def get_by_code(*, db_session, code: str) -> Optional[RegradeReason]:
    return db_session.query(RegradeReason).filter(RegradeReason.code == code).one_or_none()

def create(*, db_session, regradereason_in: RegradereasonCreate) -> RegradeReason:

    mill = db_session.query(Mill).filter(Mill.id == regradereason_in.mill_id).one_or_none()
    regradereason = RegradeReason(**regradereason_in.dict(
        exclude={"flex_form_data", "mill"}
    ),mill=mill)
    db_session.add(regradereason)
    db_session.commit()
    return regradereason

def update(
    db_session,
    item: RegradeReason,
    item_in: RegradereasonUpdate,
) -> RegradeReason:
    update_data = item_in.dict(
        exclude={"flex_form_data", "mill"},
    )
    for field, field_value in update_data.items():
        setattr(item, field, field_value)
    
    db_session.add(item)
    db_session.commit()
    return item

def delete(*, db_session, id: int):
    item = db_session.query(RegradeReason).filter(RegradeReason.id == id).update({"is_deleted": 1})
    db_session.commit()
    return item


def get_codes(*, db_session):
    codes = []
    result = db_session.query(RegradeReason.code, RegradeReason.name).all()
    if not result:
        return codes
    for i in result:
        RegradeReasonCode = f"{i[0]}-{i[1]}"
        codes.append(RegradeReasonCode)
    return codes