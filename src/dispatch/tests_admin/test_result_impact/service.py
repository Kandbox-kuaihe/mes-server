
from datetime import datetime
import logging
from typing import List, Optional
from sqlalchemy.sql.functions import func
from dispatch.mill.models import MillCreate
from dispatch.tests_admin.test_sample import service as test_sample_service

from dispatch.mill import service as mill_service 
from .models import TestResultImpact, TestResultImpactBase, TestResultImpactBaseCreate, TestResultImpactBaseRead, TestResultImpactBaseUpdate, TestResultImpactBaseCreate

from dispatch.log import getLogger
log = getLogger(__name__)

def get(*, db_session, testResultImpactBase_id: int) -> Optional[TestResultImpact]:
    """Returns an testResultImpactBase given an testResultImpactBase id."""
    return db_session.query(TestResultImpact).filter(TestResultImpact.id == testResultImpactBase_id).one_or_none()

def get_by_test_id(*, db_session, test_id: int) -> Optional[TestResultImpact]:
    """Returns an testResultImpactBase given an testResultImpactBase id."""
    return db_session.query(TestResultImpact).filter(TestResultImpact.test_id == test_id).one_or_none()


def get_all_by_test_id(*, db_session, test_id: int, inspector_code: Optional[List[str]] = None) -> Optional[TestResultImpact]:
    """Returns an testResultImpactBase given an testResultImpactBase id."""
    query = db_session.query(TestResultImpact).filter(TestResultImpact.test_id == test_id)
    if inspector_code:
        query = query.filter(TestResultImpact.insp_code.in_(inspector_code))
    return query.all()


def get_by_test_sample_id(*, db_session, test_sample_id: int) ->  List[Optional[TestResultImpact]]:
    return db_session.query(TestResultImpact).filter(
        TestResultImpact.test_sample_id == test_sample_id).all()


def get_by_test_sample_ids(*, db_session, test_sample_ids: List[int], inspector_code: Optional[List[str]] = None) -> List[Optional[TestResultImpact]]:
    query = db_session.query(TestResultImpact).filter(TestResultImpact.test_sample_id.in_(test_sample_ids))
    if inspector_code:
        query = query.filter(TestResultImpact.insp_code.in_(inspector_code))
    return query.all()


def get_all_data_dict_of_spec_id(*, db_session, test_sample_ids: List[int], inspector_code: Optional[List[str]] = None) -> dict:
    data = get_by_test_sample_ids(db_session=db_session, test_sample_ids=test_sample_ids, inspector_code=inspector_code)

    dic = {}
    for d in data:
        if d.test_sample_id not in dic:
            dic[d.test_sample_id] = []
        dic[d.test_sample_id].append(d)
    return dic




def get_default_testResultImpactBase(*, db_session ) -> Optional[TestResultImpact]:
    """Returns an testResultImpactBase given an testResultImpactBase code address."""
    return db_session.query(TestResultImpact).first()


def get_all(*, db_session) -> List[Optional[TestResultImpact]]:
    """Returns all testResultImpactBases."""
    return db_session.query(TestResultImpact)

 
def  get_float(data):
    f = None
    try:
        f = float(data)
    except ValueError:
        pass
    return f

def create_or_update_impact_from_mq(*, db_session, testResultImpactBase_in, test_sample, test) -> TestResultImpact:
    """Creates an testResultImpactBase."""


    #from dispatch.tests_admin.test_sample.service import get as test_sample_service_get
    #test_sample = test_sample_service_get(db_session= db_session, testSample_id = test_sample_id)
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
    new_test_result_impact_dict = {
        "test_sample": test_sample,
        'test_id': test.id,
        "mill": mill,
        "orientation": testResultImpactBase_in.get("Orientation",None),
        "standard": testResultImpactBase_in.get('Standard'),
        "insp_code": testResultImpactBase_in.get('Inspection Code'),
        "size_code": testResultImpactBase_in.get('Size Code',""),
        "retest_seq": get_float(testResultImpactBase_in.get('Retest No', 0)),
        "charpy_temp_c": get_float(testResultImpactBase_in.get('Charpy Temp (C)')),
        "charpy_temp_f": get_float(testResultImpactBase_in.get('Charpy Temp (F)')),
        "charpy_energy_1_j": get_float(testResultImpactBase_in.get('Charpy Energy 1 (J)')),
        "charpy_energy_2_j": get_float(testResultImpactBase_in.get('Charpy Energy 2 (J)')),
        "charpy_energy_3_j": get_float(testResultImpactBase_in.get('Charpy Energy 3 (J)')),
        "charpy_energy_average_j": get_float(testResultImpactBase_in.get('Charpy Energy Average (J)')),
        "charpy_energy_1_f": get_float(testResultImpactBase_in.get('Charpy Energy 1 (F)')),
        "charpy_energy_2_f": get_float(testResultImpactBase_in.get('Charpy Energy 2 (F)')),
        "charpy_energy_3_f": get_float(testResultImpactBase_in.get('Charpy Energy 3 (F)')),
        "charpy_energy_average_f": get_float(testResultImpactBase_in.get('Charpy Energy Average (F)')),
        "charpy_shear_1": get_float(testResultImpactBase_in.get('Charpy Shear 1')),
        "charpy_shear_2": get_float(testResultImpactBase_in.get('Charpy Shear 2')),
        "charpy_shear_3": get_float(testResultImpactBase_in.get('Charpy Shear 3')),
        "charpy_shear_average": get_float(testResultImpactBase_in.get('Charpy Shear Average')),
        "charpy_temp_units": testResultImpactBase_in.get('Charpy Temp Units'),
        "charpy_i_units": testResultImpactBase_in.get('Charpy Impact Units'),
    }
    new_test_result_impact_dict = {k: v for k, v in new_test_result_impact_dict.items() if v is not None}

    old_test_tensile = None
    if test:
        old_test_tensile = get_by_test_id(db_session=db_session, test_id=test.id)
    if not old_test_tensile:
        log.error(f"Test result impact with TEST ID {test.id} not found, test result impact in: {old_test_tensile}")
        old_test_tensile = TestResultImpact(**new_test_result_impact_dict)
        db_session.add(old_test_tensile)
    else:
        for key, value in new_test_result_impact_dict.items():
            setattr(old_test_tensile, key, value)
        old_test_tensile.updated_at = datetime.now()
    db_session.commit()
    return old_test_tensile

def create(*, db_session, request_in: TestResultImpactBaseCreate) -> TestResultImpact:
    """Creates an testResultImpactBase."""
    mill = None
    test_sample = None
    if request_in.test_sample_id is not None and request_in.test_sample_id != -1:
        test_sample = test_sample_service.get(db_session= db_session, testSample_id = request_in.test_sample_id) 
        mill = test_sample.mill

    contact = TestResultImpact(**request_in.dict(exclude={"flex_form_data","test_sample","mill"}),
                    flex_form_data=request_in.flex_form_data,
                    test_sample=test_sample,
                    mill=mill,
                    )
    db_session.add(contact)
    db_session.commit()
    return contact


def update(
    *,
    db_session,
    testResultImpactBase: TestResultImpact,
    testResultImpactBase_in: TestResultImpactBaseUpdate,
) -> TestResultImpact:

    update_data = testResultImpactBase_in.dict(
        exclude={"flex_form_data","test_sample","mill"},
    )
    for field, field_value in update_data.items():
        setattr(testResultImpactBase, field, field_value)
    mill = None
    test_sample = None
    if testResultImpactBase_in.test_sample_id is not None and testResultImpactBase_in.test_sample_id != -1:
        test_sample = test_sample_service.get(db_session= db_session, testSample_id = testResultImpactBase_in.test_sample_id) 
        mill = test_sample.mill
    testResultImpactBase.test_sample = test_sample
    testResultImpactBase.mill = mill
    testResultImpactBase.flex_form_data = testResultImpactBase_in.flex_form_data
    testResultImpactBase.updated_at = datetime.utcnow()
    db_session.add(testResultImpactBase)
    db_session.commit()
    return testResultImpactBase


def delete(*, db_session, testResultImpactBase_id: int):
    db_session.query(TestResultImpact).filter(TestResultImpact.id == testResultImpactBase_id).update({"is_deleted": 1})
    db_session.commit()
    return TestResultImpactBaseRead(id=testResultImpactBase_id)   