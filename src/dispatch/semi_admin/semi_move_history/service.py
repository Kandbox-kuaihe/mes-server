from datetime import datetime
from typing import List, Optional

from dispatch.semi_admin.semi_move_history.models import SemiMoveHistory, SemiMoveHistoryCreate, SemiMoveHistoryRead, \
    SemiMoveHistoryUpdate
from dispatch.area import service as area_service
from dispatch.semi_admin.semi import service as semi_service
from dispatch.semi_admin.semi.models import Semi
from dispatch.area.models import Area
from dispatch.semi_admin.semi.models import Semi
from sqlalchemy import select
from sqlalchemy import desc

def get(*, db_session, history_id: int) -> Optional[SemiMoveHistory]:
    """Returns a SemiMoveHistory record by its id."""
    return db_session.query(SemiMoveHistory).filter(SemiMoveHistory.id == history_id).one_or_none()

def search_semi_code(db_session, semi_code: str):
    ls = []
    history_ids = []
    ids = db_session.query(Semi).filter(Semi.semi_code.ilike(f"%{semi_code}%")).all()
    for i in ids:
        ls.append(i.id)
    all_result = get_all(db_session=db_session)
    print(f"ls: {ls}")
    if not all_result:
        raise
    for i in all_result:
        history_ids.append(i.semi_id)
    print(f"history_ids: {history_ids}")
    common_ids = [id for id in ls if id in history_ids]
    print(f"common_ids: {common_ids}")
    return common_ids


def get_all(*, db_session) -> List[Optional[SemiMoveHistory]]:
    """Returns all SemiMoveHistory records."""
    return db_session.query(SemiMoveHistory).all()


def search_semi_code(db_session, semi_code: str):
    ids = [i.id for i in db_session.query(Semi).filter(Semi.semi_code.ilike(f"%{semi_code}%")).all()]
    all_result = [record.semi_id for record in get_all(db_session=db_session)]
    common_ids = [id for id in ids if id in all_result]
    print(common_ids)
    return common_ids


def create(*, db_session, semi_move_history_in: SemiMoveHistoryCreate) -> SemiMoveHistory:
    """Creates a new SemiMoveHistory record."""

    # Get related data from semi and area if available
    semi = None
    from_area = None
    to_area = None

    if semi_move_history_in.semi_id:
        semi = semi_service.get(db_session=db_session, semi_id=semi_move_history_in.semi_id)

    if semi_move_history_in.from_area_id:
        from_area = area_service.get(db_session=db_session, area_id=semi_move_history_in.from_area_id)

    if semi_move_history_in.to_area_id:
        to_area = area_service.get(db_session=db_session, area_id=semi_move_history_in.to_area_id)

    # Create new SemiMoveHistory object
    semi_move_history = SemiMoveHistory(
        semi_id=semi.id if semi else None,
        from_area_id=from_area.id if from_area else None,
        from_location=semi_move_history_in.from_location,
        to_area_id=to_area.id if to_area else None,
        to_location=semi_move_history_in.to_location,
        move_date=semi_move_history_in.move_date,
        move_by=semi_move_history_in.move_by,
    )

    db_session.add(semi_move_history)
    db_session.commit()
    return semi_move_history


def update(*, db_session, semi_move_history: SemiMoveHistory,
           semi_move_history_in: SemiMoveHistoryUpdate) -> SemiMoveHistory:
    """Updates a SemiMoveHistory record."""

    # Update related data if needed
    if semi_move_history_in.semi_id and semi_move_history_in.semi_id != semi_move_history.semi_id:
        semi = semi_service.get(db_session=db_session, semi_id=semi_move_history_in.semi_id)
        semi_move_history.semi_id = semi.id

    if semi_move_history_in.from_area_id and semi_move_history_in.from_area_id != semi_move_history.from_area_id:
        from_area = area_service.get(db_session=db_session, area_id=semi_move_history_in.from_area_id)
        semi_move_history.from_area_id = from_area.id

    if semi_move_history_in.to_area_id and semi_move_history_in.to_area_id != semi_move_history.to_area_id:
        to_area = area_service.get(db_session=db_session, area_id=semi_move_history_in.to_area_id)
        semi_move_history.to_area_id = to_area.id

    # Update the other fields directly
    update_data = semi_move_history_in.dict(exclude_defaults=True)
    for field, value in update_data.items():
        setattr(semi_move_history, field, value)

    semi_move_history.updated_at = datetime.utcnow()
    semi_move_history.updated_by = semi_move_history_in.updated_by

    db_session.commit()
    return semi_move_history


def delete(*, db_session, history_id: int) -> SemiMoveHistoryRead:
    """Deletes a SemiMoveHistory record."""

    history = db_session.query(SemiMoveHistory).filter(SemiMoveHistory.id == history_id).first()
    if history:
        db_session.delete(history)
        db_session.commit()
        return SemiMoveHistoryRead(id=history_id)
    else:
        raise ValueError(f"SemiMoveHistory with id {history_id} not found.")


def bulk_get_history(*, db_session, history_ids: List[int]) -> List[Optional[SemiMoveHistory]]:
    """Gets multiple SemiMoveHistory records by their ids."""
    return db_session.query(SemiMoveHistory).filter(SemiMoveHistory.id.in_(history_ids)).all()


def get_area_location(*, db_session, history_ids: List[int]) -> List[Optional[SemiMoveHistory]]:
    """Fetches area and location information for multiple records."""
    return db_session.query(SemiMoveHistory).filter(SemiMoveHistory.id.in_(history_ids)).all()


def bulk_create_move_history(*, db_session, semi_move_histories_in: List[dict]):
    """
    批量插入数据到 SemiMoveHistory 表。

    Parameters:
    - db_session: 数据库会话
    - semi_move_histories_in: 包含多个字典的列表，每个字典表示一条历史记录
    """
    if not semi_move_histories_in:
        return []

    try:
        db_session.bulk_insert_mappings(SemiMoveHistory, semi_move_histories_in)
        db_session.commit()
        return semi_move_histories_in  # 返回已插入的记录
    except Exception as e:
        db_session.rollback()
        raise e


def bulk_get_area_code(db_session, ids):
    area_ids = {entry['from_area_id'] for entry in ids} | {entry['to_area_id'] for entry in ids}

    # 查询对应的 code
    areas = db_session.query(Area).filter(Area.id.in_(area_ids)).all()

    # 构建字典以便快速查找
    code_lookup = {area.id: area.code for area in areas}

    # 按原查询顺序构建结果
    result = [
        {
            'from_area_code': code_lookup[entry['from_area_id']],
            'to_area_code': code_lookup[entry['to_area_id']]
        }
        for entry in ids  # 修正这里，遍历 ids 而不是 area_ids
    ]

    return result


def block_time_max(db_session):
    # 获取semi block 状态的最大值
    return (
        db_session.query(SemiMoveHistory)
        .filter(SemiMoveHistory.change_type == "block")  # 筛选 change_type 为 block
        .order_by(desc(SemiMoveHistory.created_at))  # 按 created_at 降序排列
        .limit(1)  # 获取最新的一条记录
        .first()  # 提取单个结果
    )