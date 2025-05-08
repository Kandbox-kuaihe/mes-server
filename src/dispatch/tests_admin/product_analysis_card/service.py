from datetime import datetime
from typing import Optional, List

from .models import (
    TestProdan,
    TestProductAnalysisCreate,
    TestProductAnalysisUpdate,
    TestProductAnalysisRead,
)
from dispatch.mill import service as mill_service
from dispatch.tests_admin.test_list import service as test_service
from dispatch.tests_admin.test_list.models import Test


def get(*, db_session, test_prodan_id: int) -> Optional[TestProdan]:
    """Returns a TestProdan given its ID."""
    return db_session.query(TestProdan).filter(TestProdan.id == test_prodan_id).one_or_none()


def create(*, db_session, test_prodan_in: TestProductAnalysisCreate) -> TestProdan:
    """Creates a new TestProdan."""
    mill = None
    if test_prodan_in.mill_id is not None and test_prodan_in.mill_id != -1:
        mill = mill_service.get(db_session=db_session, mill_id=test_prodan_in.mill_id)

    test = None
    if test_prodan_in.test_id is not None and test_prodan_in.test_id != -1:
        test = test_service.get(db_session=db_session, id=test_prodan_in.test_id)

    test_product_analysis = TestProdan(
        **test_prodan_in.dict(exclude={"mill", "test"}),
    )
    db_session.add(test_product_analysis)
    db_session.commit()
    return test_product_analysis


def update(
        *,
        db_session,
        test_prodan: TestProdan,
        test_prodan_in: TestProductAnalysisUpdate,
) -> TestProdan:
    """Updates an existing TestProdan."""
    update_data = test_prodan_in.dict(exclude={"mill", "test"})
    for field, value in update_data.items():
        setattr(test_prodan, field, value)

    mill = None
    if test_prodan_in.mill_id is not None and test_prodan_in.mill_id != -1:
        mill = mill_service.get(db_session=db_session, mill_id=test_prodan_in.mill_id)

    test = None
    if test_prodan_in.test_id is not None and test_prodan_in.test_id != -1:
        test = test_service.get(db_session=db_session, id=test_prodan_in.test_id)

    test_prodan.mill = mill
    test_prodan.updated_at = datetime.utcnow()
    db_session.add(test_prodan)
    db_session.commit()
    return test_prodan


def delete(*, db_session, test_prodan_id: int):
    """Marks a TestProdan as deleted."""
    db_session.query(TestProdan).filter(TestProdan.id == test_prodan_id).update({"is_deleted": 1})
    db_session.commit()
    return TestProductAnalysisRead(id=test_prodan_id)


def get_all_by_test_id(*, db_session, test_id: int) -> Optional[TestProdan]:
    """Returns an testResultImpactBase given an testResultImpactBase id."""
    query = db_session.query(TestProdan).filter(TestProdan.test_id == test_id)
    return query.all()


def get_by_test_sample_ids_tbm(*, db_session, test_sample_ids: List[int], inspector_code: Optional[List[str]] = None) -> List[Optional[TestProdan]]:
    query = db_session.query(TestProdan).join(Test, Test.id==TestProdan.test_id).filter(
        Test.test_sample_id.in_(test_sample_ids))
    if inspector_code:
        query = query.filter(TestProdan.insp_code.in_(inspector_code))
    return query.all()


def get_all_data_dict_of_spec_id_tbm(*, db_session, test_sample_ids: List[int], inspector_code: Optional[List[str]] = None) -> dict:
    data = get_by_test_sample_ids_tbm(db_session=db_session, test_sample_ids=test_sample_ids, inspector_code=inspector_code)

    dic = {}
    for d in data:
        dic.setdefault(d.test.test_sample_id, []).append(d)
    return dic


