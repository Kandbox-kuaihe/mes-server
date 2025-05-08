from typing import List, Optional
from sqlalchemy import select, tuple_, and_, exists, desc
from datetime import datetime, timedelta
from sqlalchemy.sql.functions import func
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from .models import CoverEndUse, CoverEndUseCreate, CoverEndUseUpdate
from dispatch.runout_admin.finished_product_history.models import FinishedProductHistoryChangeTypeEnum
from sqlalchemy.schema import Sequence
from dispatch.runout_admin.finished_product.models import FinishedProduct
from dispatch.runout_admin.runout_list.models import Runout
from dispatch.runout_admin.finished_product_history.service import bulk_create_finished_product_history
from dispatch.tests_admin.test_sample.models import TestSample
from dispatch.tests_admin.tensile_test_card.models import TestTensile
from dispatch.tests_admin.impact_test_card.models import TestImpact
from dispatch.tests_admin.test_list.models import Test


def get(*, db_session, id: int) -> Optional[CoverEndUse]:
    return db_session.get(CoverEndUse, id)


def get_by(*, db_session, runout_id: int, spec_id: int) -> Optional[CoverEndUse]:
    end_use = db_session.query(CoverEndUse).filter_by(runout_id=runout_id, spec_id=spec_id).first()
    return end_use


def get_max_runout_id(*, db_session) -> Optional[int]:
    max_runout_id = db_session.query(func.max(CoverEndUse.runout_id)).filter(
        CoverEndUse.tensile_score.in_([8, 9]),
        CoverEndUse.impact_score.in_([8, 9])
    ).scalar()
    return max_runout_id


def delete_cover_end_use_above_runout_id(*, db_session, runout_id: int):
    try:
        # 构建删除查询
        delete_query = db_session.query(CoverEndUse).filter(CoverEndUse.runout_id > runout_id)
        # 执行删除操作
        delete_count = delete_query.delete(synchronize_session=False)
        # 提交事务
        db_session.commit()
        print(f"Successfully deleted {delete_count} records.")
    except Exception as e:
        # 回滚事务
        db_session.rollback()
        print(f"An error occurred while deleting records: {e}")


def clear_cover_end_use_table(db_session: Session):
    try:
        # 删除所有记录
        db_session.query(CoverEndUse).delete()
        db_session.commit()
    except SQLAlchemyError as e:
        db_session.rollback()
        print(f"Error clearing 'cover_end_use' table: {e}")


def reset_sequence_to_max_id(db_session: Session):
    try:
        # 获取最大 id
        max_id = db_session.query(func.max(CoverEndUse.id)).scalar()

        # 如果表为空，max_id 会是 None，设置为 0 或 1（根据你的需求）
        max_id = max_id if max_id is not None else 0
        
        # 获取序列对象
        seq = Sequence('cover_end_use_id_seq', start=max_id + 1)

        # 使用 Sequence 对象来重置序列的值
        db_session.execute(seq)  # 会根据 max_id 自动调整序列
        
        db_session.commit()
    except SQLAlchemyError as e:
        db_session.rollback()
        print(f"Error resetting sequence: {e}")


def create(*, db_session, cover_end_use_in: CoverEndUseCreate) -> CoverEndUse:
    created = CoverEndUse(**cover_end_use_in.model_dump())
    db_session.add(created)
    db_session.commit()
    return created


def create_dict(db_session, cover_end_use_in: dict) -> CoverEndUse:
    created = CoverEndUseCreate(**cover_end_use_in)
    created = create(db_session=db_session, cover_end_use_in=created)
    return created


def batch_insert_cover_end_uses(*, db_session: Session, cover_end_use_ins: List[dict]) -> Optional[int]:
    try:
        db_session.bulk_insert_mappings(CoverEndUse, cover_end_use_ins)
        db_session.commit()
    except SQLAlchemyError as e:
        db_session.rollback()
        print(f"Batch insertion failed: {e}")


def update(
        *,
        db_session,
        cover_end_use: CoverEndUse,
        cover_end_use_in: CoverEndUseUpdate,
) -> CoverEndUse:
    update_data = cover_end_use_in.model_dump()
    for field, field_value in update_data.items():
        setattr(cover_end_use, field, field_value)

    db_session.add(cover_end_use)
    db_session.commit()
    return cover_end_use


def delete(*, db_session, cover_end_use: CoverEndUse, cover_end_use_id: int):
    cover_end_use.is_deleted = 1

    db_session.commit()


def delete_real(*, db_session, cover_end_use: CoverEndUse, cover_end_use_id: int):
    db_session.delete(cover_end_use)
    db_session.commit()


def delete_by_runout_id(*, db_session, runout_id: int):
    db_session.query(CoverEndUse).filter(CoverEndUse.runout_id == runout_id).delete()
    db_session.commit()


def batch_update(db_session, body):
    try:
        db_session.bulk_update_mappings(FinishedProduct, body)
        db_session.commit()
        history_in = []
        for item in body:

            fin = db_session.query(FinishedProduct).filter(FinishedProduct.id == item["id"]).first()

            history_in.append({
                "created_by": fin.updated_by,
                "change_type": FinishedProductHistoryChangeTypeEnum.UNCOVER,
                'spec_code': fin.spec.spec_code if fin.spec else None,

                'mill_id': fin.mill_id,
                'code': fin.code,
                'rolling_code': fin.rolling.rolling_code if fin.rolling else None,
                'runout_code': fin.runout.runout_code if fin.runout else None,
                'area_code': fin.area.code if fin.area else None,
                'cast_no': fin.cast.cast_code if fin.cast else None,
                'order_num': fin.order.order_code if fin.order else None,
                'order_item_num': fin.order_item.line_item_code if fin.order_item else None,
                'product_type': fin.product_type.code if fin.product_type else None,
            })
        bulk_create_finished_product_history(db_session=db_session, finished_product_history_in=history_in)
        return True
    except Exception as e:
        db_session.rollback()  # 如果更新失败，回滚事务
        raise e



def get_finished_product(db_session: Session, mill_id: int):
    subquery = (
        db_session.query(FinishedProduct.id)
        .filter(
            and_(
                # FinishedProduct.cover_status == 'W',
                FinishedProduct.mill_id == mill_id,
                exists().where(
                    and_(
                        TestSample.runout_id == FinishedProduct.runout_id,
                        Test.test_sample_id == TestSample.id,
                        TestImpact.test_id == Test.id,
                        (TestImpact.energy_average_j != None) | (TestImpact.energy_average_f != None)
                    )
                ),
                exists().where(
                    and_(
                        TestSample.runout_id == FinishedProduct.runout_id,
                        Test.test_sample_id == TestSample.id,
                        TestTensile.test_id == Test.id,
                        TestTensile.value_mpa != None
                    )
                )
            )
        )
        .distinct()
        .subquery('subquery')
    )

    # 通过子查询获取完整的 FinishedProduct 对象
    finished_product_query = (
        db_session.query(FinishedProduct)
        .join(subquery, FinishedProduct.id == subquery.c.id)
        .all()
    )
    return finished_product_query


def get_finished_product_rolling_cast(db_session: Session, finished_product_list: list, mill_id: int):
    if not finished_product_list:
        return []
    
    input_runout_ids = list({fp.runout_id for fp in finished_product_list})

    cast_rolling_combinations = db_session.query(
        Runout.cast_id,
        Runout.rolling_id
    ).filter(
        Runout.id.in_(input_runout_ids),
        Runout.mill_id == mill_id
    ).distinct().all()

    if not cast_rolling_combinations:
        return []
    
    subquery = db_session.query(
        Runout.id
    ).filter(
        tuple_(Runout.cast_id, Runout.rolling_id).in_(cast_rolling_combinations),
        Runout.mill_id == mill_id
    ).distinct().subquery("related_runouts")

    result = db_session.query(FinishedProduct).filter(
        FinishedProduct.runout_id.in_(db_session.query(subquery.c.id)),
        FinishedProduct.cover_status == 'W',
        FinishedProduct.mill_id == mill_id
    ).order_by(desc(FinishedProduct.code)).all()

    return result


def get_runout(db_session: Session, mill_id: int):
    base_subquery = (
        db_session.query(Runout.id)
        .filter(
            and_(
                Runout.mill_id == mill_id,
            exists().where(
                and_(
                    TestSample.runout_id == Runout.id,
                    Test.test_sample_id == TestSample.id,
                    TestImpact.test_id == Test.id,
                    (TestImpact.energy_average_j != None) | (TestImpact.energy_average_f != None)
                )
            ),
            exists().where(
                and_(
                    TestSample.runout_id == Runout.id,
                    Test.test_sample_id == TestSample.id,
                    TestTensile.test_id == Test.id,
                    TestTensile.value_mpa != None
                )
            )
        )
        )
        .distinct()
        .subquery('base_subquery')
    )

    # 获取基础 Runout 对象
    base_runouts = (
        db_session.query(Runout).filter(Runout.mill_id == mill_id)
        .join(base_subquery, Runout.id == base_subquery.c.id)
        .all()
    )

    # === 第二部分：获取关联 Runout ===
    if not base_runouts:
        return []

    # 提取有效组合（过滤空值）
    valid_combinations = [
        (r.cast_id, r.rolling_id)
        for r in base_runouts
        if r.cast_id is not None and r.rolling_id is not None
    ]
    if not valid_combinations:
        return base_runouts  # 无有效组合时返回基础结果

    # 子查询2：获取相同 cast/rolling 的 Runout.id
    related_subquery = (
        db_session.query(Runout.id)
        .filter(
            tuple_(Runout.cast_id, Runout.rolling_id).in_(valid_combinations),
            Runout.mill_id == mill_id
        )
        .distinct()
        .subquery('related_subquery')
    )

    # 获取关联 Runout 对象
    related_runouts = (
        db_session.query(Runout).filter(Runout.mill_id == mill_id)
        .join(related_subquery, Runout.id == related_subquery.c.id)
        .all()
    )

    # === 合并去重 ===
    merged = {r.id: r for r in [*base_runouts, *related_runouts]}
    return list(merged.values())
