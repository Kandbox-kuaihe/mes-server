
from datetime import datetime
from typing import List, Optional
from sqlalchemy.sql.functions import func
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

from .models import (TestChemial, TestChemialBase, TestChemialCreate,
                     TestChemialRead, TestChemialUpdate)


def get(*, db_session, id: int) -> Optional[TestChemial]:
    """Returns an TestChemialBase given an TestChemialBase id."""
    return db_session.query(TestChemial).filter(TestChemial.id == id).one_or_none()


def get_all(*, db_session) -> List[Optional[TestChemial]]:
    """Returns all TestChemial."""
    return db_session.query(TestChemial)

def create(*, db_session, test_chemial_in: TestChemialCreate) -> TestChemial:
    test_chemial = TestChemial(**test_chemial_in.dict(exclude={}))
    db_session.add(test_chemial)
    db_session.commit()
    return test_chemial

def update(
    *,
    db_session,
    test_chemial: TestChemial,
    test_chemial_in: TestChemialUpdate,
) -> TestChemial:

    update_data = test_chemial_in.dict(
        exclude={"flex_form_data", "mill"},
    )
    for field, field_value in update_data.items():
        setattr(test_chemial, field, field_value)

    test_chemial.flex_form_data = test_chemial_in.flex_form_data
    db_session.add(test_chemial)
    db_session.commit()
    return test_chemial


def delete(*, db_session, id: int):
    test_chemial = db_session.query(TestChemial).filter(TestChemial.id == id).one_or_none()

    if test_chemial:
        test_chemial.is_deleted = 1
    db_session.add(test_chemial)
    db_session.commit()

    return test_chemial