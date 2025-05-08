
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.sql import and_
from sqlalchemy.sql.functions import func

from .models import TestCoverage, TestCoverageCreate, TestCoverageUpdate, TestCoverageRead, TestCoveragePagination
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from dispatch.tests_admin.test_list import service as test_service
from dispatch.tests_admin.test_list.models import Test



def get(*, db_session, id: int) -> Optional[TestCoverage]:
    return db_session.get(TestCoverage, id)


def get_by_test_id(*, db_session, test_id: int) -> Optional[TestCoverage]:
    return db_session.query(TestCoverage).filter(TestCoverage.test_id == test_id).all()


def get_by_test_id_and_bundle_id(*, db_session, test_id: int, bundle_id) -> Optional[TestCoverage]:
    return db_session.query(TestCoverage).filter(and_(TestCoverage.test_id == test_id, TestCoverage.finished_product_id == bundle_id)).first()


def create(*, db_session, test_coverage_in: TestCoverageCreate) -> TestCoverage:

    created = TestCoverage(**test_coverage_in.model_dump())
    db_session.add(created)
    db_session.commit()
    return created


def update(
    *,
    db_session,
    test_coverage: TestCoverage,
    test_coverage_in: TestCoverageUpdate,
) -> TestCoverage:

    update_data = test_coverage_in.model_dump()
    for field, field_value in update_data.items():
        setattr(test_coverage, field, field_value)

    db_session.add(test_coverage)
    db_session.commit()
    return test_coverage


def delete(*, db_session, test_coverage_id: int):
    db_session.query(TestCoverage).filter(TestCoverage.id == test_coverage_id).delete()
    db_session.commit()


def create_dict(*, db_session, test_coverage_in) -> TestCoverage:

    created = TestCoverageCreate(**test_coverage_in)
    created = create(db_session=db_session, test_coverage_in=created)
    return created


def delete_by_finished_product_id(*, db_session: Session, finished_product_id: int) -> Optional[list[TestCoverage]]:
    try:
        result = db_session.query(TestCoverage).filter(TestCoverage.finished_product_id==finished_product_id).delete(synchronize_session=False)
        db_session.commit()
        return result
    except SQLAlchemyError as e:
        db_session.rollback()
        print(f"Batch deletion failed: {e}")
        return None


def delete_by_test_ids_finished_product_id(*, db_session: Session, test_ids: List[int], finished_product_id: int) -> Optional[List['TestCoverage']]:
    try:
        # 使用 in_ 方法来匹配 test_ids 列表中的所有 test_id
        result = db_session.query(TestCoverage).filter(TestCoverage.test_id.in_(test_ids),
                                                       TestCoverage.finished_product_id==finished_product_id
                                                       ).delete(synchronize_session=False)
        db_session.commit()
        return result
    except SQLAlchemyError as e:
        db_session.rollback()
        print(f"Batch deletion failed: {e}")
        return None


def delete_by_finished_product_id_type(*, db_session: Session, finished_product_id: int, type: str):
    try:
        subquery = db_session.query(TestCoverage.id).join(
            Test, TestCoverage.test_id == Test.id
        ).filter(
            TestCoverage.finished_product_id == finished_product_id,
            Test.type == type
        ).subquery()

        # 删除符合条件的 TestCoverage 记录
        test_coverage_delete_count = db_session.query(TestCoverage).filter(
            TestCoverage.id.in_(select(subquery))
        ).delete(synchronize_session=False)

        # # 删除关联的 Test 记录
        # for test_id in test_ids:
        #     test = test_service.get(db_session= db_session, id=test_id)
        #     if test:
        #         test_service.delete(db_session=db_session, test=test, test_id=test_id)

        db_session.commit()
        return test_coverage_delete_count
    except SQLAlchemyError as e:
        db_session.rollback()
        print(f"Batch deletion failed: {e}")
        return None


def get_by_finished_product_id(*, db_session: Session, finished_product_id: int) -> Optional[TestCoverage]:
    return db_session.query(TestCoverage).filter(TestCoverage.finished_product_id==finished_product_id).first()

