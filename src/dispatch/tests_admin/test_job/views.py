from datetime import datetime

from dispatch.database import get_db
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from dispatch.system_admin.auth.models import DispatchUser
from dispatch.system_admin.auth.service import get_current_user

from dispatch.database_util.service import common_parameters, search_filter_sort_paginate
from .models import (
    TestJob,
    TestJobCreate,
    TestJobPagination,
    TestJobRead,
    TestJobUpdate,
)
from .service import create, delete, get, update

router = APIRouter()


@router.get("/", response_model=TestJobPagination)
def get_test_jobs(*, common: dict = Depends(common_parameters)):

    return search_filter_sort_paginate(model="TestJob", **common)


@router.post("/", response_model=TestJobRead)
def create_test_job(*, db_session: Session = Depends(get_db), test_job_in: TestJobCreate,
                 current_user: DispatchUser = Depends(get_current_user)):
    """
    Create a new TestJob contact.
    """

    test_job_in.created_by = current_user.email
    test_job_in.updated_by = current_user.email
    test_job_in.mill_id = current_user.current_mill_id
    test_job = create(db_session=db_session, test_job_in=test_job_in, is_flush=True)
    db_session.commit()
    return test_job


@router.get("/{test_job_id}", response_model=TestJobRead)
def get_test_job(*, db_session: Session = Depends(get_db), test_job_id: int):
    """
    Get a TestJob contact.
    """
    test_job = get(db_session=db_session, test_job_id=test_job_id)
    if not test_job:
        raise HTTPException(status_code=400, detail="The TestJob with this id does not exist.")
    return test_job


@router.put("/{test_job_id}", response_model=TestJobRead)
def update_TestJob(
    *,
    db_session: Session = Depends(get_db),
    test_job_id: int,
    test_job_in: TestJobUpdate,
    current_user: DispatchUser = Depends(get_current_user)
):
    """
    Update a TestJob contact.
    """
    test_job = get(db_session=db_session, test_job_id=test_job_id)
    if not test_job:
        raise HTTPException(status_code=400, detail="The TestJob with this id does not exist.")
    test_job_in.updated_at = datetime.now()
    test_job_in.updated_by = current_user.email
    test_job_in.mill_id = current_user.current_mill_id
    test_job = update(
        db_session=db_session,
        test_job=test_job,
        test_job_in=test_job_in,
    )
    return test_job


@router.delete("/{test_job_id}", response_model=TestJobRead)
def delete_TestJob(*, db_session: Session = Depends(get_db), test_job_id: int):
    """
    Delete a TestJob contact.
    """
    test_job = get(db_session=db_session, test_job_id=test_job_id)
    if not test_job:
        raise HTTPException(status_code=400, detail="The TestJob with this id does not exist.")

    return delete(db_session=db_session, test_job_id=test_job_id)
