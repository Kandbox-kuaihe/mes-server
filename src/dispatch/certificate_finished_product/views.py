from dispatch.database import get_db

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from dispatch.system_admin.auth.models import DispatchUser
from dispatch.system_admin.auth.service import get_current_user




from dispatch.database_util.service import common_parameters, search_filter_sort_paginate
from .models import (
    CertificateFinishedProduct,
    CertificateFinishedProductCreate,
    CertificateFinishedProductPagination,
    CertificateFinishedProductRead,
    CertificateFinishedProductUpdate,
)
from .service import create, delete, get, get_by_code, update

router = APIRouter()


@router.get("/", response_model=CertificateFinishedProductPagination)
def get_filters(*, common: dict = Depends(common_parameters)):

    return search_filter_sort_paginate(model="CertificateFinishedProduct", **common)
