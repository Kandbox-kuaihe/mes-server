
from datetime import datetime
from typing import Optional

from .models import TestMicrostructure

from dispatch.mill import service as mill_service
from dispatch.tests_admin.test_list import service as test_service


def get(*, db_session, TestMicrostructure_id: int) -> Optional[TestMicrostructure]:
    """Returns an TestHardness given an TestHardness id."""
    return db_session.query(TestMicrostructure).filter(TestMicrostructure.id == TestMicrostructure_id).one_or_none()


def get_by_test_id(*, db_session, test_id: int) -> TestMicrostructure:
    return db_session.query(TestMicrostructure).filter(TestMicrostructure.test_id == test_id).one_or_none()
