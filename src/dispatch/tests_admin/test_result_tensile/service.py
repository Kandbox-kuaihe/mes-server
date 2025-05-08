from datetime import datetime
from typing import List, Optional
from fastapi.encoders import jsonable_encoder
from dispatch.mill.models import MillCreate
from dispatch.tests_admin.test_sample import service as test_sample_service

from dispatch.system_admin.auth.models import DispatchUser
from dispatch.mill import service as mill_service 
from .models import TestResultTensile, TestResultTensileCreate, TestResultTensileRead, TestResultTensileUpdate
import logging
from dispatch.log import getLogger
log = getLogger(__name__)


 

def get(*, db_session, id: int) -> Optional[TestResultTensile]:
    return db_session.query(TestResultTensile).filter(
        TestResultTensile.id == id).one_or_none()

def get_tensile_by_test_id(*, db_session, test_id: int) -> Optional[TestResultTensile]:
    return db_session.query(TestResultTensile).filter(
        TestResultTensile.test_id == test_id).one_or_none()
 

def get_all_by_test_id(*, db_session, test_id: int, inspector_code: Optional[List[str]] = None) -> Optional[TestResultTensile]:
    """Returns an testResultImpactBase given an testResultImpactBase id."""
    query = db_session.query(TestResultTensile).filter(TestResultTensile.test_id == test_id)
    if inspector_code:
        query = query.filter(TestResultTensile.insp_code.in_(inspector_code))
    return query.all()


def get_by_test_sample_id(*, db_session, test_sample_id: int) ->List[Optional[TestResultTensile]]:
    return db_session.query(TestResultTensile).filter(
        TestResultTensile.test_sample_id == test_sample_id).all()



def get_by_test_sample_ids(*, db_session, test_sample_ids: List[int], inspector_code: Optional[List[str]] = None) -> List[Optional[TestResultTensile]]:
    query = db_session.query(TestResultTensile).filter(TestResultTensile.test_sample_id.in_(test_sample_ids))
    if inspector_code:
        query = query.filter(TestResultTensile.insp_code.in_(inspector_code))
    return query.all()


def get_all_data_dict_of_spec_id(*, db_session, test_sample_ids: List[int], inspector_code: Optional[List[str]] = None) -> dict:
    data = get_by_test_sample_ids(db_session=db_session, test_sample_ids=test_sample_ids, inspector_code=inspector_code)

    dic = {}
    for d in data:
        if d.test_sample_id not in dic:
            dic[d.test_sample_id] = []
        dic[d.test_sample_id].append(d)
    return dic


def get_or_create_by_code(*, db_session, test_result_tensile_in) -> TestResultTensile:
    if test_result_tensile_in.id:   
        q = db_session.query(TestResultTensile).filter(
            TestResultTensile.id == test_result_tensile_in.id)
    else:
        # return None
        raise Exception("The TestResultTensile.id can not be None.")

    instance = q.first()

    if instance:
        return instance

    return create(db_session=db_session, test_result_tensile_in=test_result_tensile_in)


def get_all(*, db_session) -> List[Optional[TestResultTensile]]:
    return db_session.query(TestResultTensile)


def  get_float(data):
    f = None
    try:
        f = float(data)
    except ValueError:
        pass
    return f

def create_or_update_tensile_from_mq(*, db_session, test_result_tensile_in,test_sample, test) -> TestResultTensile:

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

    new_test_result_tensile_dict = { 
        "test_sample": test_sample,
        'test_id': test.id,
        "mill": mill,
        "sample_shape": test_result_tensile_in.get("Sample Shape",""),
        "orientation": test_result_tensile_in.get("Orientation",None),
        "tested_thickness": get_float(test_result_tensile_in.get("Tested Thickness",None)),
        "tested_width": get_float(test_result_tensile_in.get("Tested Width",None)),
        "tested_diameter": get_float(test_result_tensile_in.get("Tested Diameter",None)),
        "value_mpa": get_float(test_result_tensile_in.get("Rm (Tensile)",None)),
        "retest_seq": get_float(test_result_tensile_in.get("Retest Number",0)),
        "standard": test_result_tensile_in.get('Standard'),
        "insp_code": test_result_tensile_in.get('Inspection Code'),
        "yield_tt0_5": get_float(test_result_tensile_in.get("Yield Rt0.5",None)),
        "yield_high": get_float(test_result_tensile_in.get("Yield High",None)),
        "yield_rp0_2": get_float(test_result_tensile_in.get("Yield Rp0.2",None)),
        "yield_low": get_float(test_result_tensile_in.get("Yield Low",None)),

        "elongation_code": get_float(test_result_tensile_in.get("Elongation Code",None)),
        "elongation_a565": get_float(test_result_tensile_in.get("Elongation A565",None)),
        "elongation_a200": get_float(test_result_tensile_in.get("Elongation A200",None)),
        "elongation_a50": get_float(test_result_tensile_in.get("Elongation A50",None)),
        "elongation_8": get_float(test_result_tensile_in.get("Elongation 8in",None)),
        "elongation_2": get_float(test_result_tensile_in.get("Elongation 2in",None)),
        "elongation_a80": get_float(test_result_tensile_in.get("Elongation A80",None)),
    }
    new_test_result_tensile_dict = {k: v for k, v in new_test_result_tensile_dict.items() if v is not None}
    old_test_result_tensile = None
    
    if test:
        old_test_result_tensile = get_tensile_by_test_id(db_session=db_session, test_id=test.id)
    if not old_test_result_tensile:
        log.error(f"Test result tensile with TEST ID {test.id} not found, test result tensile in: {test_result_tensile_in}")
        old_test_result_tensile = TestResultTensile(**new_test_result_tensile_dict)
        db_session.add(old_test_result_tensile)
    else:
        for key, value in new_test_result_tensile_dict.items():
            setattr(old_test_result_tensile, key, value)
        old_test_result_tensile.updated_at = datetime.now()
    db_session.commit()
    return old_test_result_tensile

def create(*, db_session, test_result_tensile_in: TestResultTensileCreate) -> TestResultTensile:
    test_sample = None
    mill = None
    if test_result_tensile_in.test_sample_id is not None and test_result_tensile_in.test_sample_id != -1:
        test_sample = test_sample_service.get(db_session= db_session, testSample_id = test_result_tensile_in.test_sample_id) 
        mill = test_sample.mill
    test_result_tensile = TestResultTensile(**test_result_tensile_in.dict(exclude={"flex_form_data" ,"test_sample","mill"}),
                                             flex_form_data=test_result_tensile_in.flex_form_data,
                                             test_sample = test_sample,
                                             mill = mill
                                             ) 
    db_session.add(test_result_tensile)
    db_session.commit()
    return test_result_tensile


def create_all(*, db_session,
               test_result_tensile_in: List[TestResultTensileCreate]) -> List[TestResultTensile]:
    
    test_result_tensile = [TestResultTensile(id=d.id) for d in test_result_tensile_in]
    db_session.bulk_save_insert(test_result_tensile)
    db_session.commit()
    db_session.refresh()
    return test_result_tensile


def update(*, db_session, test_result_tensile: TestResultTensile,
           test_result_tensile_in: TestResultTensileUpdate) -> TestResultTensile:
 
    update_data = test_result_tensile_in.dict(
        exclude={"flex_form_data","test_sample","mill"},
    )
    for field, field_value in update_data.items():
        setattr(test_result_tensile, field, field_value)

    test_sample = None
    mill = None
    if test_result_tensile_in.test_sample_id is not None and test_result_tensile_in.test_sample_id != -1:
        test_sample = test_sample_service.get(db_session= db_session, testSample_id = test_result_tensile_in.test_sample_id) 
        mill = test_sample.mill
    test_result_tensile.test_sample = test_sample
    test_result_tensile.mill = mill
    test_result_tensile.flex_form_data = test_result_tensile_in.flex_form_data
    test_result_tensile.updated_at = datetime.utcnow()
    db_session.add(test_result_tensile)
    db_session.commit()
    return test_result_tensile

def delete(*, db_session, id: int):
    db_session.query(TestResultTensile).filter(
        TestResultTensile.id == id).update({"is_deleted": 1})
 
    db_session.commit()

    return TestResultTensileRead(id=id)  
 