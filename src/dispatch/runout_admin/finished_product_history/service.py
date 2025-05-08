from typing import List

from fastapi import HTTPException

from dispatch.runout_admin.finished_product.models import FinishedProduct
from dispatch.runout_admin.runout_list.models import Runout
from .models import FinishedProductHistory


def get_runout_ids_by_code(*, db_session, q: str) -> List[int]:
    return db_session.query(Runout.id).filter(Runout.runout_code.contains(q)).all()


def get_finished_product_ids_by_code(*, db_session, q: str) -> List[int]:
    return (
        db_session.query(FinishedProduct.id)
        .filter(FinishedProduct.code.contains(q))
        .all()
    )


def bulk_create_finished_product_history(
    *, db_session, finished_product_history_in: List[dict]
):
    """
    批量插入数据到 FinishedProductHistory 表。

    Parameters:
    - db_session:
    - finished_product_history_in: 包含多个字典的列表，每个字典表示一条历史记录

    #使用示例
    from dispatch.runout_admin.finished_product_history.server import bulk_create_finished_product_history
    from dispatch.runout_admin.finished_product_history.models import FinishedProductHistoryChangeTypeEnum

    history_list = [
            {
                "finished_product_id": finished_product.id,
                "created_by": current_user.email,
                "change_type": FinishedProductHistoryChangeTypeEnum.MOVE,  # 不同的业务选不同的字段
    
                # ... 上面为必填， 下面根据业务 有什么填什么 看 FinishedProductHistory 表定义
                
                "runout_id": None if finished_product.runout is None else finished_product.runout.id,
                "area_id": None if finished_product.area is None else finished_product.area.id,  # from area_id
            }
    ]
    bulk_create_finished_product_history(db_session=db_session, finished_product_history_in=history_list)
    """
    if not finished_product_history_in:
        return []

    try:
        db_session.bulk_insert_mappings(
            FinishedProductHistory, finished_product_history_in
        )
        db_session.commit()
        return finished_product_history_in
    except Exception as e:
        db_session.rollback()
        raise HTTPException(status_code=400, detail=str(e))
