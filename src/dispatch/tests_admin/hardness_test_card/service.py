
from datetime import datetime
from typing import Optional

from .models import TestHardness, TestHardnessCreate, TestHardnessUpdate, TestHardnessRead

from dispatch.mill import service as mill_service
from dispatch.tests_admin.test_list import service as test_service


def get(*, db_session, TestHardness_id: int) -> Optional[TestHardness]:
    """Returns an TestHardness given an TestHardness id."""
    return db_session.query(TestHardness).filter(TestHardness.id == TestHardness_id).one_or_none()


# def get_by_code(*, db_session, code: str) -> Optional[TestHardness]:
#     """Returns an TestHardness given an TestHardness code address."""
#     return db_session.query(TestHardness).filter(TestHardness.test_code == code).one_or_none()


def create(*, db_session, TestHardness_in: TestHardnessCreate) -> TestHardness:
    """Creates an TestHardness."""

    mill = None
    if TestHardness_in.mill_id is not None and TestHardness_in.mill_id != -1:
        mill = mill_service.get(db_session= db_session, mill_id = TestHardness_in.mill_id)

    test = None 
    if TestHardness_in.test_id is not None and TestHardness_in.test_id != -1:
        test = test_service.get(db_session= db_session, id = TestHardness_in.test_id)

    contact = TestHardness(**TestHardness_in.dict(exclude={"flex_form_data", "mill", "test"}),
                    flex_form_data=TestHardness_in.flex_form_data,
                    mill = mill,
                           )
    db_session.add(contact)
    db_session.commit()
    return contact


def update(
    *,
    db_session,
    TestHardness: TestHardness,
    TestHardness_in: TestHardnessUpdate,
) -> TestHardness:

    update_data = TestHardness_in.dict(
        exclude={"flex_form_data", "mill", "test"},
    )
    for field, field_value in update_data.items():
        setattr(TestHardness, field, field_value)

    mill = None
    if TestHardness_in.mill_id is not None and TestHardness_in.mill_id != -1:
        mill = mill_service.get(db_session= db_session, mill_id = TestHardness_in.mill_id) 

    test = None
    if TestHardness_in.test_id is not None and TestHardness_in.test_id != -1:
        test = test_service.get(db_session= db_session, id = TestHardness_in.test_id)

    TestHardness.flex_form_data = TestHardness_in.flex_form_data
    TestHardness.mill = mill
    TestHardness.test = test
    TestHardness.updated_at = datetime.utcnow()
    db_session.add(TestHardness)
    db_session.commit()
    return TestHardness


def delete(*, db_session, TestHardness_id: int):
    
    db_session.query(TestHardness).filter(TestHardness.id == TestHardness_id).update({"is_deleted": 1})
    db_session.commit()
    return TestHardnessRead(id=TestHardness_id)  


def get_by_test_id(*, db_session, test_id: int) -> TestHardness:
    return db_session.query(TestHardness).filter(TestHardness.test_id == test_id).one_or_none()
