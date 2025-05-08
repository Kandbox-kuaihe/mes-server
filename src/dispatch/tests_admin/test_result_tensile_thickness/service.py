from datetime import datetime
from typing import List, Optional

from sqlalchemy.sql.functions import func
from dispatch.mill.models import MillCreate
from dispatch.tests_admin.test_sample import service as test_sample_service
from dispatch.mill import service as mill_service 
from .models import TestResultTensileThickness, TestResultTensileThicknessCreate, TestResultTensileThicknessRead, TestResultTensileThicknessUpdate, TestResultTensileThicknessCreate

def get(*, db_session, testResultTensileThickness_id: int) -> Optional[TestResultTensileThickness]:
    """Returns an testResultTensile given an testResultTensile id."""
    return db_session.query(TestResultTensileThickness).filter(TestResultTensileThickness.id == testResultTensileThickness_id).one_or_none()

def get_by_test_sample_id(*, db_session, test_sample_id: int) ->  List[Optional[TestResultTensileThickness]]:
    return db_session.query(TestResultTensileThickness).filter(
        TestResultTensileThickness.test_sample_id == test_sample_id).all()



def get_default_testResultTensile(*, db_session ) -> Optional[TestResultTensileThickness]:
    """Returns an testResultTensile given an testResultTensile code address."""
    return db_session.query(TestResultTensileThickness).first()


def get_all(*, db_session) -> List[Optional[TestResultTensileThickness]]:
    """Returns all testResultTensiles."""
    return db_session.query(TestResultTensileThickness)

 

def  get_float(data):
    f = None
    try:
        f = float(data)
    except ValueError:
        pass
    return f

def create_form_mq(*, db_session, testResultTensile_in,test_sample_id) -> TestResultTensileThickness:
    """Creates an testResultTensile.""" 
    from dispatch.tests_admin.test_sample.service import get as test_sample_service_get
    test_sample = test_sample_service_get(db_session= db_session, testSample_id = test_sample_id)
    mill = None
    mill_code = "TBM"
    mill = mill_service.get_by_code(db_session=db_session, code=mill_code)
    if not mill:
        mill_in = MillCreate(
            code=mill_code,
            type="TBM",
            desc="TBM",

        )
        mill = mill_service.create(db_session=db_session, mill_in=mill_in)
    contact = TestResultTensileThickness( 
        test_sample = test_sample,
        mill = mill,
        retest_seq= get_float(testResultTensile_in.get('Retest No')),
        tested_diameter_1 = get_float(testResultTensile_in.get("Tested Diameter 1")),
        tested_diameter_2 = get_float(testResultTensile_in.get("Tested Diameter 2")),
        tested_diameter_3 = get_float(testResultTensile_in.get("Tested Diameter 3")),

        value_mpa_1 = get_float(testResultTensile_in.get("Rm 1")),
        value_mpa_2 = get_float(testResultTensile_in.get("Rm 2")),
        value_mpa_3 = get_float(testResultTensile_in.get("Rm 3")),

        yield_rt0_5_1 = get_float(testResultTensile_in.get("Yield Rt0.5 1")),
        yield_rt0_5_2 = get_float(testResultTensile_in.get("Yield Rt0.5 2")),
        yield_rt0_5_3 = get_float(testResultTensile_in.get("Yield Rt0.5 3")),

        reduction_in_area_1 = get_float(testResultTensile_in.get("Reduction in Area 1")),
        reduction_in_area_2 = get_float(testResultTensile_in.get("Reduction in Area 2")),
        reduction_in_area_3 = get_float(testResultTensile_in.get("Reduction in Area 3")),
        ria_average = get_float(testResultTensile_in.get("RIA Average")),
    )
    db_session.add(contact)
    db_session.commit()
    return contact

def create(*, db_session, testResultTensileThickness_in: TestResultTensileThicknessCreate) -> TestResultTensileThickness:
    """Creates an testResultTensile."""

    mill = None
    test_sample = None
    if testResultTensileThickness_in.test_sample_id is not None and testResultTensileThickness_in.test_sample_id != -1:
        test_sample = test_sample_service.get(db_session= db_session, testSample_id = testResultTensileThickness_in.test_sample_id) 
        mill = test_sample.mill
    contact = TestResultTensileThickness(**testResultTensileThickness_in.dict(exclude={"flex_form_data","test_sample","mill"}),
                    flex_form_data=testResultTensileThickness_in.flex_form_data,
                    test_sample=test_sample,
                    mill=mill,
                    )
    db_session.add(contact)
    db_session.commit()
    return contact


def update(
    *,
    db_session,
    testResultTensileThickness: TestResultTensileThickness,
    testResultTensileThickness_in: TestResultTensileThicknessUpdate,
) -> TestResultTensileThickness:

    update_data = testResultTensileThickness_in.dict(
        exclude={"flex_form_data" ,"test_sample","mill"},
    )
    for field, field_value in update_data.items():
        setattr(testResultTensileThickness, field, field_value)
    
    test_sample = None
    mill = None
    if testResultTensileThickness_in.test_sample_id is not None and testResultTensileThickness_in.test_sample_id != -1:
        test_sample = test_sample_service.get(db_session= db_session, testSample_id = testResultTensileThickness_in.test_sample_id) 
        if test_sample:
            mill = test_sample.mill
            test_sample.test_sample_part = testResultTensileThickness_in.test_sample_part
            test_sample.updated_at = datetime.now()
            db_session.add(test_sample)

    testResultTensileThickness.flex_form_data = testResultTensileThickness_in.flex_form_data
    testResultTensileThickness.test_sample = test_sample
    testResultTensileThickness.mill = mill
    db_session.add(testResultTensileThickness)
    db_session.commit()
    return testResultTensileThickness


def delete(*, db_session, testResultTensile_id: int):
    db_session.query(TestResultTensileThickness).filter(TestResultTensileThickness.id == testResultTensile_id).update({"is_deleted": 1})
    db_session.commit()
    return TestResultTensileThicknessRead(id=testResultTensile_id)



def get_all_by_test_id(*, db_session, test_id: int, inspector_code: Optional[List[str]] = None) -> Optional[TestResultTensileThickness]:
    """Returns an testResultImpactBase given an testResultImpactBase id."""
    query = db_session.query(TestResultTensileThickness).filter(TestResultTensileThickness.test_id == test_id)
    if inspector_code:
        query = query.filter(TestResultTensileThickness.insp_code.in_(inspector_code))
    return query.all()

def get_by_test_sample_ids(*, db_session, test_sample_ids: List[int], inspector_code: Optional[List[str]] = None) -> List[Optional[TestResultTensileThickness]]:
    query = db_session.query(TestResultTensileThickness).filter(TestResultTensileThickness.test_sample_id.in_(test_sample_ids))
    if inspector_code:
        query = query.filter(TestResultTensileThickness.insp_code.in_(inspector_code))
    return query.all()


def get_all_data_dict_of_spec_id(*, db_session, test_sample_ids: List[int], inspector_code: Optional[List[str]] = None) -> dict:
    data = get_by_test_sample_ids(db_session=db_session, test_sample_ids=test_sample_ids, inspector_code=inspector_code)

    dic = {}
    for d in data:
        if d.test_sample_id not in dic:
            dic[d.test_sample_id] = []
        dic[d.test_sample_id].append(d)
    return dic


def get_by_test_sample_ids_tbm_inspector_is_none(*, db_session, test_sample_ids: List[int]) -> List[Optional[TestResultTensileThickness]]:
    query = db_session.query(TestResultTensileThickness).filter(
        TestResultTensileThickness.test_sample_id.in_(test_sample_ids))
    return query.all()


def get_all_data_dict_of_spec_id_tbm_inspector_is_none(*, db_session, test_sample_ids: List[int]) -> dict:
    data = get_by_test_sample_ids_tbm_inspector_is_none(db_session=db_session, test_sample_ids=test_sample_ids)

    dic = {}
    for d in data:
        dic.setdefault(d.test.test_sample_id, []).append(d)
    return dic

