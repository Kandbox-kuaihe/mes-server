from typing import List, Optional
from fastapi.encoders import jsonable_encoder

from dispatch.system_admin.auth.models import DispatchUser
from .models import OperationLog, OperationLogCreate, OperationLogUpdate
import logging
from dispatch.log import getLogger
log = getLogger(__name__)


 

def get(*, db_session, id: int) -> Optional[OperationLog]:
    return db_session.query(OperationLog).filter(
        OperationLog.id == id).one_or_none()
 
 
 
def get_or_create_by_code(*, db_session, operation_log_in) -> OperationLog:
    if operation_log_in.id:   
        q = db_session.query(OperationLog).filter(
            OperationLog.id == operation_log_in.id)
    else:
        # return None
        raise Exception("The OperationLog.id can not be None.")

    instance = q.first()

    if instance:
        return instance

    return create(db_session=db_session, operation_log_in=operation_log_in)


def get_all(*, db_session) -> List[Optional[OperationLog]]:
    return db_session.query(OperationLog)


def create(*, db_session, operation_log_in: OperationLogCreate) -> OperationLog:

    operation_log = OperationLog(**operation_log_in.dict(exclude={ })) 
    db_session.add(operation_log)
    db_session.commit()
    return operation_log


def create_all(*, db_session,
               operation_log_in: List[OperationLogCreate]) -> List[OperationLog]:
    operation_log = [OperationLog(id=d.id) for d in operation_log_in]
    db_session.bulk_save_insert(operation_log)
    db_session.commit()
    db_session.refresh()
    return operation_log


def update(*, db_session, operation_log: OperationLog,
           operation_log_in: OperationLogUpdate) -> OperationLog:
 
    operation_log_data = jsonable_encoder(operation_log)

    update_data = operation_log_in.dict(skip_defaults=True)

    for field in operation_log_data:
        if field in update_data:
            setattr(operation_log, field, update_data[field])

    db_session.add(operation_log)
    db_session.commit()
    return operation_log

def delete(*, db_session, id: int):
    operation_log = db_session.query(OperationLog).filter(
        OperationLog.id == id).first()

    db_session.delete(operation_log)
    db_session.commit()

 