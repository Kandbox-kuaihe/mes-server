from dispatch.database import get_db

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from dispatch.system_admin.auth.models import DispatchUser
from dispatch.system_admin.auth.service import get_current_user




from dispatch.database_util.service import common_parameters, search_filter_sort_paginate
from .models import (
    Certificate,
    CertificateCreate,
    CertificatePagination,
    CertificateRead,
    CertificateUpdate,
)
from .service import create, delete, get, get_by_code, update

router = APIRouter()


@router.get("/", response_model=CertificatePagination)
def get_filters(*, common: dict = Depends(common_parameters)):

    return search_filter_sort_paginate(model="Certificate", **common)


@router.post("/", response_model=CertificateRead)
def create_obj(*, db_session: Session = Depends(get_db), request_in: CertificateCreate,
                 current_user: DispatchUser = Depends(get_current_user)):
    """
    Create a new certificate contact.
    """
    
    certificate = get_by_code(db_session=db_session,code=request_in.certificate_code)
    
    
    if certificate:
        raise HTTPException(status_code=400, detail="The certificate with this code already exists.")
    
    request_in.created_by = current_user.email
    request_in.updated_by = current_user.email
    certificate = create(db_session=db_session, certificate_in=request_in)
    return certificate


@router.get("/{certificate_id}", response_model=CertificateRead)
def get_certificate(*, db_session: Session = Depends(get_db), certificate_id: int):
    """
    Get a certificate contact.
    """
    certificate = get(db_session=db_session, id=certificate_id)
    if not certificate:
        raise HTTPException(status_code=404, detail="The certificate with this id does not exist.")
    return certificate


@router.put("/{certificate_id}", response_model=CertificateRead)
def update_certificate(
    *,
    db_session: Session = Depends(get_db),
    certificate_id: int,
    certificate_in: CertificateUpdate, current_user: DispatchUser = Depends(get_current_user)
):
    """
    Update a certificate contact.
    """
    certificate = get(db_session=db_session, id=certificate_id)
    if not certificate:
        raise HTTPException(status_code=404, detail="The certificate with this id does not exist.")

    certificate = update(
        db_session=db_session,
        certificate=certificate,
        certificate_in=certificate_in,
    )
    return certificate



@router.delete("/{certificate_id}", response_model=CertificateRead)
def delete_certificate(*, db_session: Session = Depends(get_db), certificate_id: int):
    """
    Delete a certificate contact.
    """
    certificate = get(db_session=db_session, id=certificate_id)
    if not certificate:
        raise HTTPException(status_code=404, detail="The certificate with this id does not exist.")

    return delete(db_session=db_session, id=certificate_id)
