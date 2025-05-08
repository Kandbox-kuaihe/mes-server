from datetime import datetime
from typing import List, Optional
from dispatch.tests_admin.bend_test_card.models import TestBend
from dispatch.tests_admin.test_list.models import Test
from dispatch.tests_admin.test_sample import service as test_sample_service

from dispatch.system_admin.auth.models import DispatchUser
from .models import TestResultBend, TestResultBendCreate, TestResultBendRead, TestResultBendUpdate
import logging
from dispatch.log import getLogger
log = getLogger(__name__)


 

def get(*, db_session, id: int) -> Optional[TestResultBend]:
    return db_session.query(TestResultBend).filter(
        TestResultBend.id == id).one_or_none()
 
 
def get_by_test_sample_id(*, db_session, test_sample_id: int) ->List[Optional[TestResultBend]]:
    return db_session.query(TestResultBend).filter(
        TestResultBend.test_sample_id == test_sample_id).all()
    
    
def get_all_data(*, db_session) -> List[Optional[TestResultBend]]:
    """Returns all sptensils."""
    return db_session.query(TestResultBend).all()


#  def get_by_test_sample_dict(*, db_session, test_sample_ids: List[int]) ->dict:
     
     
#     data = get_by_test_sample_ids(db_session=db_session, test_sample_ids=test_sample_ids)
    
#     dic = {}
#     for d in data:
#         if d.test_sample_id not in dic:
#             dic[d.test_sample_id] = []
#         dic[d.test_sample_id].append(d)
    
    
 
 
 
def get_or_create_by_code(*, db_session, test_result_tensile_in) -> TestResultBend:
    if test_result_tensile_in.id:   
        q = db_session.query(TestResultBend).filter(
            TestResultBend.id == test_result_tensile_in.id)
    else:
        # return None
        raise Exception("The TestResultBend.id can not be None.")

    instance = q.first()

    if instance:
        return instance

    return create(db_session=db_session, test_result_tensile_in=test_result_tensile_in)


def get_all(*, db_session) -> List[Optional[TestResultBend]]:
    return db_session.query(TestResultBend)


def  get_float(data):
    f = None
    try:
        f = float(data)
    except ValueError:
        pass
    return f

def create_form_mq(*, db_session, test_result_tensile_in,test_sample_id) -> TestResultBend:

    from dispatch.tests_admin.test_sample.service import get as test_sample_service_get
    test_sample = test_sample_service_get(db_session= db_session, testSample_id = test_sample_id)
    test_result_tensile = TestResultBend( 
        test_sample = test_sample,
        sample_shape = test_result_tensile_in.get("Sample Shape",""),
        tested_thickness = get_float(test_result_tensile_in.get("Tested Thickness",None)),
        tested_width = get_float(test_result_tensile_in.get("Tested Width",None)),
        tested_diameter = get_float(test_result_tensile_in.get("Tested Diameter",None)),
        value_mpa = get_float(test_result_tensile_in.get("Rm (Tensile)",None)),

        yield_tt0_5 = get_float(test_result_tensile_in.get("Yield Rt0.5",None)),
        yield_high = get_float(test_result_tensile_in.get("Yield High",None)),
        yield_rp0_2 = get_float(test_result_tensile_in.get("Yield Rp0.2",None)),
        yield_low = get_float(test_result_tensile_in.get("Yield Low",None)),

        elongation_code = get_float(test_result_tensile_in.get("Elongation Code",None)),
        elongation_a565 = get_float(test_result_tensile_in.get("Elongation A565",None)),
        elongation_a200 = get_float(test_result_tensile_in.get("Elongation A200",None)),
        elongation_a50 = get_float(test_result_tensile_in.get("Elongation A50",None)),
        elongation_8 = get_float(test_result_tensile_in.get("Elongation 8in",None)),
        elongation_2 = get_float(test_result_tensile_in.get("Elongation 2in",None)),
        elongation_a80 = get_float(test_result_tensile_in.get("Elongation A80",None)),

    ) 
    db_session.add(test_result_tensile)
    db_session.commit()
    return test_result_tensile

def create(*, db_session, test_result_tensile_in: TestResultBendCreate) -> TestResultBend:
    test_sample = None
    if test_result_tensile_in.test_sample_id is not None and test_result_tensile_in.test_sample_id != -1:
        test_sample = test_sample_service.get(db_session= db_session, testSample_id = test_result_tensile_in.test_sample_id) 

    test_result_tensile = TestResultBend(**test_result_tensile_in.dict(exclude={"flex_form_data" ,"test_sample"}),
                                             flex_form_data=test_result_tensile_in.flex_form_data,
                                             test_sample = test_sample
                                             ) 
    db_session.add(test_result_tensile)
    db_session.commit()
    return test_result_tensile


def create_all(*, db_session,
               test_result_tensile_in: List[TestResultBendCreate]) -> List[TestResultBend]:
    
    test_result_tensile = [TestResultBend(id=d.id) for d in test_result_tensile_in]
    db_session.bulk_save_insert(test_result_tensile)
    db_session.commit()
    db_session.refresh()
    return test_result_tensile


def update(*, db_session, test_result_tensile: TestResultBend,
           test_result_tensile_in: TestResultBendUpdate) -> TestResultBend:
 
    update_data = test_result_tensile_in.dict(
        exclude={"flex_form_data","test_sample"},
    )
    for field, field_value in update_data.items():
        setattr(test_result_tensile, field, field_value)

    test_sample = None
    if test_result_tensile_in.test_sample_id is not None and test_result_tensile_in.test_sample_id != -1:
        test_sample = test_sample_service.get(db_session= db_session, testSample_id = test_result_tensile_in.test_sample_id) 

    test_result_tensile.test_sample = test_sample
    test_result_tensile.flex_form_data = test_result_tensile_in.flex_form_data
    test_result_tensile.updated_at = datetime.utcnow()
    db_session.add(test_result_tensile)
    db_session.commit()
    return test_result_tensile

def delete(*, db_session, id: int):
    test_result_tensile = db_session.query(TestResultBend).filter(
        TestResultBend.id == id).first()

    db_session.delete(test_result_tensile)
    db_session.commit()

    return TestResultBendRead(id=id)

def get_by_test_sample_ids(*, db_session, test_sample_ids: List[int]) -> List[TestResultBend]:
    return db_session.query(TestResultBend).join(Test, Test.id==TestResultBend.test_id).filter(
        TestResultBend.test_sample_id.in_(test_sample_ids)).all()


def get_all_data_dict_of_spec_id(*, db_session, test_sample_ids: List[int]) -> dict[int,list[TestResultBend]]:
    data = get_by_test_sample_ids(db_session=db_session, test_sample_ids=test_sample_ids)
    dic = {}
    for d in data:
        if d.test_sample_id not in dic:
            dic[d.test_sample_id] = []
        inspector_id_1,inspector_id_2,inspector_id_3 = None, None, None
        if d.test:
            d.test_sample_id = d.test.test_sample_id
            inspector_id_1 = d.test.inspector_id_1
            inspector_id_2 = d.test.inspector_id_2
            inspector_id_3 = d.test.inspector_id_3
        d.inspector_id_1 = inspector_id_1
        d.inspector_id_2 = inspector_id_2
        d.inspector_id_3 = inspector_id_3
        dic[d.test_sample_id].append(d)
    return dic

def get_by_test_ids(*, db_session, test_ids: list[int]) -> list[TestBend]:
    return db_session.query(TestBend).filter(TestBend.test_id.in_(test_ids)).all()

def get_all_data_dict_by_test_ids(*, db_session, test_ids: list[int]) -> dict[int,list[TestBend]]:
    data = get_by_test_ids(db_session=db_session, test_ids=test_ids)
    dic = {}
    for d in data:
        inspector_id_1,inspector_id_2,inspector_id_3 = None, None, None
        if d.test:
            d.test_sample_id = d.test.test_sample_id
            inspector_id_1 = d.test.inspector_id_1
            inspector_id_2 = d.test.inspector_id_2
            inspector_id_3 = d.test.inspector_id_3
        d.inspector_id_1 = inspector_id_1
        d.inspector_id_2 = inspector_id_2
        d.inspector_id_3 = inspector_id_3
        dic.setdefault(d.test.test_sample_id, []).append(d)
    return dic