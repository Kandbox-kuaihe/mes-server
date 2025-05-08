from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.orm import Session
from dispatch.system_admin.auth.models import DispatchUser 
from dispatch.system_admin.auth.service import get_current_user
from dispatch.database import get_db
from .models import OperationLogCreate, OperationLogPagination, OperationLogRead, OperationLogUpdate

from dispatch.database_util.service import common_parameters, search_filter_sort_paginate

 
from .service import create, delete, get, update 

router = APIRouter()


@router.get("/", response_model=OperationLogPagination)
def get_operation_log(*, common: dict = Depends(common_parameters)):
    q = common["query_str"]
    if q:
        common["filter_type"] = "or"
        common["fields"] = ["request_modular", "request_path", "request_method", "request_body", "request_ip", "response_code", "response_status"]
        common["ops"] = ["like"] * len(common["fields"])
        common["values"] = [f'%{q}%'] * len(common["fields"])
        common['query_str'] = ''
    operation_log = search_filter_sort_paginate(
        model="OperationLog", **common
    )
    return operation_log


@router.get("/{id}", response_model=OperationLogRead)
def get_operation_log_by_id(*, db_session: Session = Depends(get_db), id: int):
    """
    Update a operation_log.
    """
    operation_log = get(db_session=db_session, id=id)
    if not operation_log:
        raise HTTPException(status_code=404, detail="The operation log with this id does not exist.")
    return operation_log


@router.post("/", response_model=OperationLogRead)
def create_loperation_log(*, db_session: Session = Depends(get_db), operation_log_in: OperationLogCreate,
                    current_user: DispatchUser = Depends(get_current_user),):
    """
    Create a new operation_log.
    """ 
    operation_log_in.updated_by = current_user.email
    operation_log = create(db_session=db_session, operation_log_in=operation_log_in)
    return operation_log


@router.put("/{id}", response_model=OperationLogRead)
def update_operation_log(
    *, db_session: Session = Depends(get_db), id: int, operation_log_in: OperationLogUpdate,
    current_user: DispatchUser = Depends(get_current_user),
):
    """
    Update a operation_log.
    """
    operation_log = get(db_session=db_session, id=id)
    if not operation_log:
        raise HTTPException(status_code=404, detail="The operation_log with this id does not exist.")

    operation_log_in.updated_by = current_user.email
    operation_log = update(db_session=db_session, operation_log=operation_log, operation_log_in=operation_log_in)
    return operation_log


@router.delete("/{id}", response_model=OperationLogRead)
def delete_operation_log(*, db_session: Session = Depends(get_db), id: int):
    """
    Delete a operation_log.
    """
        
    operation_log = get(db_session=db_session, id=id)
    if not operation_log:
        raise HTTPException(status_code=404, detail="The operation_log with this id does not exist.")
    delete(db_session=db_session, id=id)

    return OperationLogRead(id=id)

 
 