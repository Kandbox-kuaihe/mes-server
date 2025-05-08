
from datetime import datetime
from typing import Optional

from .models import TestConductivity

from dispatch.mill import service as mill_service
from dispatch.tests_admin.test_list import service as test_service


def get(*, db_session, TestConductivity_id: int) -> Optional[TestConductivity]:
    """Returns an TestHardness given an TestHardness id."""
    return db_session.query(TestConductivity).filter(TestConductivity.id == TestConductivity_id).one_or_none()


def get_by_test_id(*, db_session, test_id: int) -> TestConductivity:
    return db_session.query(TestConductivity).filter(TestConductivity.test_id == test_id).one_or_none()
