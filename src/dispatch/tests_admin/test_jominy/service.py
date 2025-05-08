
from datetime import datetime
from typing import Optional

from dispatch.mill.models import MillCreate

from .models import TestJominy, TestJominyCreate, TestJominyUpdate, TestJominyRead

from dispatch.cast import service as cast_service
from dispatch.runout_admin.runout_list import service as runout_service
from dispatch.mill import service as mill_service
from dispatch.tests_admin.test_list import service as test_service
from dispatch.cast.models import CastCreate
from dispatch.runout_admin.runout_list.models import RunoutCreate

def get(*, db_session, test_jominy_id: int) -> Optional[TestJominy]:
    """Returns an TestJominy given an TestJominy id."""
    return db_session.query(TestJominy).filter(TestJominy.id == test_jominy_id).one_or_none()

def create(*, db_session, test_jominy_in: TestJominyCreate, is_flush: bool = False) -> TestJominy:
    """Creates an TestJominy."""

    created = TestJominy(**test_jominy_in.model_dump())
    db_session.add(created)
    if is_flush:
        db_session.flush()
    return created


def update(
    *,
    db_session,
    test_jominy: TestJominy,
    test_jominy_in: TestJominyUpdate,
) -> TestJominy:

    update_data = test_jominy_in.model_dump()
    for field, field_value in update_data.items():
        setattr(test_jominy, field, field_value)
    db_session.add(test_jominy)
    db_session.commit()
    return test_jominy


def delete(*, db_session, test_jominy_id: int):
    
    db_session.query(TestJominy).filter(TestJominy.id == test_jominy_id).update({"is_deleted": 1})
    db_session.commit()
    return TestJominyRead(id=test_jominy_id)

