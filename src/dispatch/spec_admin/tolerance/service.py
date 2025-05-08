from typing import List, Optional
from sqlalchemy.sql.functions import func
from .models import Tolerance, ToleranceCreate, ToleranceUpdate


def get(*, db_session, id: int) -> Optional[Tolerance]:
    return db_session.query(Tolerance).filter(Tolerance.id == id).one_or_none()

def get_by_code(*, db_session, code: str) -> Optional[Tolerance]:
    return db_session.query(Tolerance).filter(Tolerance.code == code).one_or_none()

def create(*, db_session, tolerance_in: ToleranceCreate) -> Tolerance:
    # exclude={"flex_form_data", "location"}
    tolerance = Tolerance(**tolerance_in.dict())
    db_session.add(tolerance)
    db_session.commit()
    return tolerance

def update(
    db_session,
    item: Tolerance,
    item_in: ToleranceUpdate,
) -> Tolerance:

    update_data = item_in.dict(
        exclude={"flex_form_data"},
    )
    for field, field_value in update_data.items():
        setattr(item, field, field_value)

    db_session.add(item)
    db_session.commit()
    return item

def delete(*, db_session, id: int):
    # db_session.query(Tolerance).filter(Tolerance.id == id).delete()
    db_session.query(Tolerance).filter(Tolerance.id == id).update({"is_deleted": 1})
    db_session.commit()


def get_tolerance_codes(*, db_session):
    codes = []
    result = db_session.query(Tolerance.code).all()
    if not result:
        return codes
    for i in result:
        codes.append(i[0])
    print(codes)
    return codes