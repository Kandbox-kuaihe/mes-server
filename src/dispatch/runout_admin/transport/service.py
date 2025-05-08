
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.sql.functions import func

from .models import Transport, TransportCreate, TransportUpdate, TransportRead, TransportPagination, TransportStatusEnum
from dispatch.runout_admin.transport_history.service import bulk_create_transport_history
from dispatch.runout_admin.transport_history.models import TransportHistoryActionEnum

def get(*, db_session, id: int) -> Optional[Transport]:
    return db_session.get(Transport, id)

def create(*, db_session, transport_in: TransportCreate) -> Transport:
    history_list = []
    created = Transport(**transport_in.model_dump())
    db_session.add(created)
    db_session.commit()
    history_list.append(
        {
            "transport_id": created.id,
            "created_by": transport_in.updated_by,
            "action": TransportHistoryActionEnum.CREATE,  # 不同的业务选不同的字段

            "status": created.status,
            "mill_id": created.mill_id,
        }
    )
    bulk_create_transport_history(db_session=db_session, transport_history_in=history_list)
    return created


def update(
    *,
    db_session,
    transport: Transport,
    transport_in: TransportUpdate,
) -> Transport:
    history_list = []
    update_data = transport_in.model_dump()
    for field, field_value in update_data.items():
        setattr(transport, field, field_value)
    db_session.commit()

    history_list.append(
        {
            "transport_id": transport.id,
            "created_by": transport_in.updated_by,
            "action": TransportHistoryActionEnum.EDIT,  # 不同的业务选不同的字段

            "status": transport.status,
            "mill_id": transport.mill_id,
        }
    )
    bulk_create_transport_history(db_session=db_session, transport_history_in=history_list)

    db_session.add(transport)
    return transport


def delete(*, db_session, transport: Transport, transport_id: int, current_user):
    transport.is_deleted = 1
    history_list = []

    history_list.append(
        {
            "transport_id": transport.id,
            "created_by": current_user.email,
            "action": TransportHistoryActionEnum.DELETE,  # 不同的业务选不同的字段
            "status": transport.status,
            "mill_id": transport.mill_id,
        }
    )
    bulk_create_transport_history(db_session=db_session, transport_history_in=history_list)
    db_session.commit()

def update_on_load(
    *,
    db_session,
    transport_in: TransportUpdate,
):
    history_list = []
    transport_ids = transport_in.ids
    if transport_ids:
        db_session.query(Transport).filter(Transport.id.in_(transport_ids)).update({
            "status": TransportStatusEnum.ONLOAD, "updated_at": transport_in.updated_at, "updated_by": transport_in.updated_by
        }, synchronize_session=False)
        for transport_id in transport_ids:
            transport = db_session.query(Transport).filter(Transport.id == transport_id).first()
            history_list.append(
                {
                    "transport_id": transport.id,
                    "created_by": transport_in.updated_by,
                    "action": TransportHistoryActionEnum.ONLOAD,  # 不同的业务选不同的字段
                    "status": transport.status,
                    "mill_id": transport.mill_id,
                }
            )
        bulk_create_transport_history(db_session=db_session, transport_history_in=history_list)
        db_session.commit()
    return True

def update_de_load(
    *,
    db_session,
    transport_in: TransportUpdate,
):
    history_list = []
    transport_ids = transport_in.ids
    if transport_ids:
        db_session.query(Transport).filter(Transport.id.in_(transport_ids)).update({
            "status": TransportStatusEnum.DELOAD, "updated_at": transport_in.updated_at, "updated_by": transport_in.updated_by
        }, synchronize_session=False)
        for transport_id in transport_ids:
            transport = db_session.query(Transport).filter(Transport.id == transport_id).first()
            history_list.append(
                {
                    "transport_id": transport.id,
                    "created_by": transport_in.updated_by,
                    "action": TransportHistoryActionEnum.DELOAD,  # 不同的业务选不同的字段
                    "status": transport.status,
                    "mill_id": transport.mill_id,
                }
            )
        bulk_create_transport_history(db_session=db_session, transport_history_in=history_list)
        db_session.commit()
    return True

def get_by_code(*, db_session, code: str) -> Optional[Transport]:
    stmt = select(Transport).where(Transport.code == code)
    return db_session.scalars(stmt).one_or_none()