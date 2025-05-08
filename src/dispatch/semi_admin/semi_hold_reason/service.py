from typing import Optional
from .models import SemiHoldReason, SemiHoldReasonCreate, SemiHoldReasonUpdate
from dispatch.mill.models import Mill, MillRead


def get(*, db_session, id: int) -> Optional[SemiHoldReason]:
    return db_session.query(SemiHoldReason).filter(SemiHoldReason.id == id).one_or_none()

def get_by_code(*, db_session, code: str) -> Optional[SemiHoldReason]:
    return db_session.query(SemiHoldReason).filter(SemiHoldReason.code == code).one_or_none()

def create(*, db_session, holdreason_in: SemiHoldReasonCreate) -> SemiHoldReason:

    mill = db_session.query(Mill).filter(Mill.id == holdreason_in.mill_id).one_or_none()
    holdreason = SemiHoldReason(**holdreason_in.dict(
        exclude={"flex_form_data", "mill"}
    ),mill=mill)
    db_session.add(holdreason)
    db_session.commit()
    return holdreason

def update(
    db_session,
    item: SemiHoldReason,
    item_in: SemiHoldReasonUpdate,
) -> SemiHoldReason:
    update_data = item_in.dict(
        exclude={"flex_form_data", "mill"},
    )
    for field, field_value in update_data.items():
        setattr(item, field, field_value)
    
    db_session.add(item)
    db_session.commit()
    return item

def delete(*, db_session, id: int):
    item = db_session.query(SemiHoldReason).filter(SemiHoldReason.id == id).update({"is_deleted": 1})
    db_session.commit()
    return item


def get_codes(*, db_session):
    codes = []
    result = db_session.query(SemiHoldReason.code, SemiHoldReason.name).all()
    if not result:
        return codes
    for i in result:
        SemiHoldReasonCode = f"{i[0]}-{i[1]}"
        codes.append(SemiHoldReasonCode)
    return codes