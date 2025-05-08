from datetime import datetime
from typing import Optional

from fastapi import HTTPException

from dispatch.mill.models import MillCreate

from .models import TestJob, TestJobCreate, TestJobUpdate, TestJobRead

from dispatch.cast import service as cast_service
from dispatch.runout_admin.runout_list import service as runout_service
from dispatch.mill import service as mill_service
from dispatch.tests_admin.test_list import service as test_service
from dispatch.cast.models import CastCreate
from dispatch.runout_admin.runout_list.models import RunoutCreate


def get(*, db_session, test_job_id: int) -> Optional[TestJob]:
    """Returns an TestJob given an TestJob id."""
    return db_session.query(TestJob).filter(TestJob.id == test_job_id).one_or_none()


def create(*, db_session, test_job_in: TestJobCreate, is_flush: bool = False) -> TestJob:
    """Creates an TestJob."""
    try:
        with db_session.begin():
            created = TestJob(**test_job_in.model_dump())
            db_session.add(created)
            if is_flush:
                db_session.flush()
            created.code = created.id
    except Exception as e:
        db_session.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Error: {str(e)}"
        )
    return created


def update(
        *,
        db_session,
        test_job: TestJob,
        test_job_in: TestJobUpdate,
) -> TestJob:
    update_data = test_job_in.model_dump()
    for field, field_value in update_data.items():
        setattr(test_job, field, field_value)
    db_session.add(test_job)
    db_session.commit()
    return test_job


def delete(*, db_session, test_job_id: int):
    db_session.query(TestJob).filter(TestJob.id == test_job_id).update({"is_deleted": 1})
    db_session.commit()
    return TestJobRead(id=test_job_id)

