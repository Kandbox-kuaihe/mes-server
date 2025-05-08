from typing import List

from fastapi import HTTPException

from dispatch.runout_admin.transport.models import Transport
from dispatch.runout_admin.runout_list.models import Runout
from .models import TransportHistory


# def get_runout_ids_by_code(*, db_session, q: str) -> List[int]:
#     return db_session.query(Runout.id).filter(Runout.runout_code.contains(q)).all()
#
#
# def get_transport_ids_by_code(*, db_session, q: str) -> List[int]:
#     return (
#         db_session.query(Transport.id)
#         .filter(Transport.code.contains(q))
#         .all()
#     )


def bulk_create_transport_history(
    *, db_session, transport_history_in: List[dict]
):
    """
    批量插入数据到 TransportHistory 表。

    Parameters:
    - db_session:
    - transport_history_in: 包含多个字典的列表，每个字典表示一条历史记录

    #使用示例
    from dispatch.runout_admin.transport_history.service import bulk_create_transport_history
    from dispatch.runout_admin.transport_history.models import TransportHistoryActionEnum

    history_list = [
            {
                "transport_id": transport.id,
                "created_by": current_user.email,
                "action": TransportHistoryChangeTypeEnum.MOVE,  # 不同的业务选不同的字段
                ...
            }
    ]
    bulk_create_transport_history(db_session=db_session, transport_history_in=history_list)
    """
    if not transport_history_in:
        return []

    try:
        db_session.bulk_insert_mappings(
            TransportHistory, transport_history_in
        )
        db_session.commit()
        return transport_history_in
    except Exception as e:
        db_session.rollback()
        raise HTTPException(status_code=400, detail=str(e))
