from typing import Optional
from .models import RemoveReason, RemoveReasonCreate, RemoveReasonUpdate, RemoveReasonPagination, RemoveReasonRead
from dispatch.mill.models import Mill, MillRead


def get(*, db_session, id: int) -> Optional[RemoveReason]:
    return db_session.query(RemoveReason).filter(RemoveReason.id == id).one_or_none()

def get_by_code(*, db_session, code: str) -> Optional[RemoveReason]:
    return db_session.query(RemoveReason).filter(RemoveReason.code == code).one_or_none()

def create(*, db_session, removereason_in: RemoveReasonCreate) -> RemoveReason:

    mill = db_session.query(Mill).filter(Mill.id == removereason_in.mill_id).one_or_none()
    removereason = RemoveReason(**removereason_in.dict(
        exclude={"flex_form_data", "mill"}
    ),mill=mill)
    db_session.add(removereason)
    db_session.commit()
    return removereason

def update(
    db_session,
    item: RemoveReason,
    item_in: RemoveReasonUpdate,
) -> RemoveReason:
    update_data = item_in.dict(
        exclude={"flex_form_data", "mill"},
    )
    for field, field_value in update_data.items():
        setattr(item, field, field_value)
    
    db_session.add(item)
    db_session.commit()
    return item

def delete(*, db_session, id: int):
    item = db_session.query(RemoveReason).filter(RemoveReason.id == id).update({"is_deleted": 1})
    db_session.commit()
    return item


def get_codes(*, db_session):
    codes = []
    result = db_session.query(RemoveReason.code, RemoveReason.name).all()
    if not result:
        return codes
    for i in result:
        HoldReasonCode = f"{i[0]}-{i[1]}"
        codes.append(HoldReasonCode)
    return codes