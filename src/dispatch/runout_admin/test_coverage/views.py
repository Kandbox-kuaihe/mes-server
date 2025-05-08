from dispatch.database import get_db
from typing import List
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from dispatch.system_admin.auth.models import DispatchUser
from dispatch.system_admin.auth.service import get_current_user

from dispatch.database_util.service import common_parameters, search_filter_sort_paginate
from .models import (
    TestCoverage,
    TestCoverageCreate,
    TestCoverageUpdate,
    TestCoverageRead,
    TestCoveragePagination,
)
from .service import create, update, delete, get

router = APIRouter()


@router.get("/", response_model=TestCoveragePagination)
def get_test_coverages(*, common: dict = Depends(common_parameters)):
    return search_filter_sort_paginate(model="TestCoverage", **common)


@router.post("/", response_model=TestCoverageRead)
def create_test_coverage(*, db_session: Session = Depends(get_db), test_coverage_in: TestCoverageCreate,
                 current_user: DispatchUser = Depends(get_current_user)):
    
    # test_coverage = get_by_code(db_session=db_session,code=test_coverage_in.test_coverage_code)
    # if test_coverage:
    #     raise HTTPException(status_code=400, detail="The test_coverage with this code already exists.")
    
    test_coverage_in.created_by = current_user.email
    test_coverage_in.updated_by = current_user.email
    test_coverage_in.created_at = datetime.now()
    test_coverage_in.updated_at = datetime.now()
    test_coverage = create(db_session=db_session, test_coverage_in=test_coverage_in)
    return test_coverage


@router.put("/{test_coverage_id}", response_model=TestCoverageRead)
def update_test_coverage(
    *,
    db_session: Session = Depends(get_db),
    test_coverage_id: int,
    test_coverage_in: TestCoverageUpdate, current_user: DispatchUser = Depends(get_current_user)
):
    test_coverage = get(db_session=db_session, id=test_coverage_id)
    if not test_coverage:
        raise HTTPException(status_code=400, detail="The test_coverage with this id does not exist.")
    
    test_coverage_in.updated_by = current_user.email
    test_coverage_in.updated_at = datetime.now()

    test_coverage = update(
        db_session=db_session,
        test_coverage=test_coverage,
        test_coverage_in=test_coverage_in,
    )
    return test_coverage


@router.delete("/{test_coverage_id}")
def delete_test_coverage(*, db_session: Session = Depends(get_db), test_coverage_id: int):
    test_coverage = get(db_session=db_session, id=test_coverage_id)
    if not test_coverage:
        raise HTTPException(status_code=400, detail="The test_coverage with this id does not exist.")

    delete(db_session=db_session, test_coverage=test_coverage, test_coverage_id=test_coverage_id)
    
    return {"deleted": "ok"}
