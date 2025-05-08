from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from dispatch.database import get_db
from dispatch.system_admin.auth.models import DispatchUser
from dispatch.system_admin.auth.service import get_current_user
from dispatch.database_util.service import common_parameters, search_filter_sort_paginate

from .models import (
    TestProdan,
    TestProductAnalysisCreate,
    TestProductAnalysisPagination,
    TestProductAnalysisRead,
    TestProductAnalysisUpdate,
)
from .service import create, delete, get, update

router = APIRouter()


@router.get("/", response_model=TestProductAnalysisPagination)
def get_TestProductAnalyses(*, common: dict = Depends(common_parameters)):
    """
    Retrieve a list of TestProdan records with search, filter, sort, and pagination.
    """
    return search_filter_sort_paginate(model="TestProdan", **common)


@router.post("/", response_model=TestProductAnalysisRead)
def create_TestProductAnalysis(
    *,
    db_session: Session = Depends(get_db),
    TestProductAnalysis_in: TestProductAnalysisCreate,
    current_user: DispatchUser = Depends(get_current_user),
):
    """
    Create a new TestProdan record.
    """
    TestProductAnalysis_in.created_by = current_user.email
    TestProductAnalysis_in.updated_by = current_user.email
    TestProdan = create(db_session=db_session, TestProductAnalysis_in=TestProductAnalysis_in)
    return TestProdan


@router.get("/{TestProductAnalysis_id}", response_model=TestProductAnalysisRead)
def get_TestProductAnalysis(
    *,
    db_session: Session = Depends(get_db),
    TestProductAnalysis_id: int,
):
    """
    Get a specific TestProdan record by ID.
    """
    TestProdan = get(db_session=db_session, TestProductAnalysis_id=TestProductAnalysis_id)
    if not TestProdan:
        raise HTTPException(status_code=404, detail="The TestProdan with this ID does not exist.")
    return TestProdan


@router.put("/{TestProductAnalysis_id}", response_model=TestProductAnalysisRead)
def update_TestProductAnalysis(
    *,
    db_session: Session = Depends(get_db),
    TestProductAnalysis_id: int,
    TestProductAnalysis_in: TestProductAnalysisUpdate,
    current_user: DispatchUser = Depends(get_current_user),
):
    """
    Update a specific TestProdan record by ID.
    """
    TestProdan = get(db_session=db_session, TestProductAnalysis_id=TestProductAnalysis_id)
    if not TestProdan:
        raise HTTPException(status_code=404, detail="The TestProdan with this ID does not exist.")

    TestProductAnalysis_in.updated_by = current_user.email
    TestProdan = update(
        db_session=db_session,
        TestProdan=TestProdan,
        TestProductAnalysis_in=TestProductAnalysis_in,
    )
    return TestProdan


@router.delete("/{TestProductAnalysis_id}", response_model=TestProductAnalysisRead)
def delete_TestProductAnalysis(
    *,
    db_session: Session = Depends(get_db),
    TestProductAnalysis_id: int,
):
    """
    Delete a specific TestProdan record by ID.
    """
    TestProdan = get(db_session=db_session, TestProductAnalysis_id=TestProductAnalysis_id)
    if not TestProdan:
        raise HTTPException(status_code=404, detail="The TestProdan with this ID does not exist.")

    return delete(db_session=db_session, TestProductAnalysis_id=TestProductAnalysis_id)
