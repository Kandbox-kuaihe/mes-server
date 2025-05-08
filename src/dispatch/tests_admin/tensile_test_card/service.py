from datetime import datetime
from typing import Optional, List
from sqlalchemy import or_, and_

from dispatch.mill.models import MillCreate
from .models import TestTensile, TestTensileCreate, TestTensileUpdate, TestTensileRead
from dispatch.tests_admin.test_list.models import Test
from dispatch.mill import service as mill_service
from dispatch.tests_admin.test_list import service as test_service

from dispatch.log import getLogger
log = getLogger(__name__)

def  get_float(data):
    f = None
    try:
        f = float(data)
    except ValueError:
        pass
    return f

def get(*, db_session, TestTensile_id: int) -> Optional[TestTensile]:
    """Returns an TestTensile given an TestTensile id."""
    return db_session.query(TestTensile).filter(TestTensile.id == TestTensile_id).one_or_none()

def get_tensile_by_test_id(*, db_session, test_id) -> Optional[TestTensile]:
    if not test_id: return
    return db_session.query(TestTensile).filter(TestTensile.test_id == test_id).one_or_none()


# def get_by_code(*, db_session, code: str) -> Optional[TestTensile]:
#     """Returns an TestTensile given an TestTensile code address."""
#     return db_session.query(TestTensile).filter(TestTensile.test_code == code).one_or_none()

def create_or_update_tensile_from_mq(*, db_session, test_result_tensile_in,test_sample, test) -> Optional[TestTensile]:
  
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

    retest_seq = get_float(test_result_tensile_in.get("Retest Number", 0))
    prefix = ""
    if retest_seq == 1:
        prefix = "r1_"
    elif retest_seq == 2:
        prefix = "r2_"

    new_test_result_tensile_dict = {
        "test_sample": test_sample,
        'test_id': test.id,
        "mill": mill,
        "retest_seq": retest_seq,
        "sample_shape": test_result_tensile_in.get("Sample Shape", ""),
        "orientation": test_result_tensile_in.get("Orientation",None),
        "standard": test_result_tensile_in.get('Standard'),
        "insp_code": test_result_tensile_in.get('Inspection Code'),
        "tested_thickness": get_float(test_result_tensile_in.get("Tested Thickness", None)),
        "tested_width": get_float(test_result_tensile_in.get("Tested Width", None)),
        "tested_diameter": get_float(test_result_tensile_in.get("Tested Diameter", None)),
        "value_mpa": get_float(test_result_tensile_in.get("Rm (Tensile)", None)),

        f"{prefix}yield_tt0_5": get_float(test_result_tensile_in.get("Yield Rt0.5", None)),
        f"{prefix}yield_high": get_float(test_result_tensile_in.get("Yield High", None)),
        f"{prefix}yield_rp0_2": get_float(test_result_tensile_in.get("Yield Rp0.2", None)),
        f"{prefix}yield_low": get_float(test_result_tensile_in.get("Yield Low", None)),
        f"{prefix}elongation_code": test_result_tensile_in.get("Elongation Code", None),
        f"{prefix}elongation_a565": get_float(test_result_tensile_in.get("Elongation A565", None)),
        f"{prefix}elongation_a200": get_float(test_result_tensile_in.get("Elongation A200", None)),
        f"{prefix}elongation_a50": get_float(test_result_tensile_in.get("Elongation A50", None)),
        f"{prefix}elongation_8": get_float(test_result_tensile_in.get("Elongation 8in", None)),
        f"{prefix}elongation_2": get_float(test_result_tensile_in.get("Elongation 2in", None)),
        f"{prefix}elongation_a80": get_float(test_result_tensile_in.get("Elongation A80", None)),
    }

    # Remove None values to avoid setting fields that weren't provided
    new_test_result_tensile_dict = {k: v for k, v in new_test_result_tensile_dict.items() if v is not None}

    old_test_result_tensile = None
    if test:
        old_test_result_tensile = get_tensile_by_test_id(db_session=db_session, test_id=test.id)
    if not old_test_result_tensile:
        log.error(f"Test tensile with TEST ID {test.id} not found, test tensile in: {test_result_tensile_in}")
        old_test_result_tensile = TestTensile(**new_test_result_tensile_dict)
        db_session.add(old_test_result_tensile)
    else:
        for key, value in new_test_result_tensile_dict.items():
            setattr(old_test_result_tensile, key, value)
        old_test_result_tensile.updated_at = datetime.now()
    db_session.commit()
    return old_test_result_tensile

def create(*, db_session, TestTensile_in: TestTensileCreate) -> TestTensile:
    """Creates an TestTensile."""

    mill = None
    if TestTensile_in.mill_id is not None and TestTensile_in.mill_id != -1:
        mill = mill_service.get(db_session= db_session, mill_id = TestTensile_in.mill_id)

    test = None 
    if TestTensile_in.test_id is not None and TestTensile_in.test_id != -1:
        test = test_service.get(db_session= db_session, id = TestTensile_in.test_id)

    contact = TestTensile(**TestTensile_in.dict(exclude={"flex_form_data", "mill", "test"}),
                    flex_form_data=TestTensile_in.flex_form_data,
                    mill = mill,
                    )
    db_session.add(contact)
    db_session.commit()
    return contact


def update(
    *,
    db_session,
    TestTensile: TestTensile,
    TestTensile_in: TestTensileUpdate,
) -> TestTensile:

    update_data = TestTensile_in.dict(
        exclude={"flex_form_data", "mill", "test"},
    )
    for field, field_value in update_data.items():
        setattr(TestTensile, field, field_value)

    mill = None
    if TestTensile_in.mill_id is not None and TestTensile_in.mill_id != -1:
        mill = mill_service.get(db_session= db_session, mill_id = TestTensile_in.mill_id) 

    test = None
    if TestTensile_in.test_id is not None and TestTensile_in.test_id != -1:
        test = test_service.get(db_session= db_session, id = TestTensile_in.test_id)

    TestTensile.flex_form_data = TestTensile_in.flex_form_data
    TestTensile.mill = mill
    TestTensile.test = test
    TestTensile.updated_at = datetime.utcnow()
    db_session.add(TestTensile)
    db_session.commit()
    return TestTensile


def delete(*, db_session, TestTensile_id: int):
    
    db_session.query(TestTensile).filter(TestTensile.id == TestTensile_id).update({"is_deleted": 1})
    db_session.commit()
    return TestTensileRead(id=TestTensile_id)  


def get_by_test_id(*, db_session, test_id: int) -> TestTensile:
    return db_session.query(TestTensile).filter(TestTensile.test_id == test_id).one_or_none()


def get_by_test_sample_ids(*, db_session, test_sample_ids: list[int], runout_id:Optional[int]=None) -> list[TestTensile]:
    query = db_session.query(TestTensile).join(Test, Test.id==TestTensile.test_id).filter(
        Test.test_sample_id.in_(test_sample_ids))
    if runout_id:
        query = query.filter(Test.runout_id == runout_id)
    return query.all()


def get_all_data_dict_of_spec_id(*, db_session, test_sample_ids: list[int], runout_id:Optional[int]=None) -> dict[int,list[TestTensile]]:
    data = get_by_test_sample_ids(db_session=db_session, test_sample_ids=test_sample_ids, runout_id=runout_id)
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

def get_by_test_ids(*, db_session, test_ids: list[int]) -> list[TestTensile]:
    return db_session.query(TestTensile).filter(TestTensile.test_id.in_(test_ids)).all()

def get_all_data_dict_by_test_ids(*, db_session, test_ids: list[int]) -> dict[int,list[TestTensile]]:
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


def get_all_by_test_id(*, db_session, test_id: int, inspector_code: Optional[List[str]] = None) -> Optional[TestTensile]:
    """Returns an testResultImpactBase given an testResultImpactBase id."""
    query = db_session.query(TestTensile).filter(TestTensile.test_id == test_id)
    if inspector_code:
        query = query.filter(TestTensile.insp_code.in_(inspector_code))
    return query.all()


def get_by_test_sample_ids_tbm(*, db_session, test_sample_ids: List[int], inspector_code: Optional[List[str]] = None) -> List[Optional[TestTensile]]:
    query = db_session.query(TestTensile).join(Test, Test.id==TestTensile.test_id).filter(
        Test.test_sample_id.in_(test_sample_ids))
    if inspector_code:
        query = query.filter(TestTensile.insp_code.in_(inspector_code))
    return query.all()
    # if inspector_code:
    #     query = query.filter(
    #         or_(
    #             Test.inspector_id_1.in_(inspector_code),
    #             Test.inspector_id_2.in_(inspector_code),
    #             Test.inspector_id_3.in_(inspector_code),
    #             Test.inspector_id_4.in_(inspector_code)
    #         )
    #     )
    # return query.all()


def get_all_data_dict_of_spec_id_tbm(*, db_session, test_sample_ids: List[int], inspector_code: Optional[List[str]] = None) -> dict:
    data = get_by_test_sample_ids_tbm(db_session=db_session, test_sample_ids=test_sample_ids, inspector_code=inspector_code)

    dic = {}
    for d in data:
        dic.setdefault(d.test.test_sample_id, []).append(d)
    return dic


def get_all_data_dict_of_spec_id_tbm_by_test(
    *, 
    db_session, 
    test_id: int, 
    inspector_code: Optional[List[str]] = None
) -> dict:
    if not inspector_code:
        data_null = db_session.query(TestTensile).filter(
            TestTensile.test_id == test_id,
            TestTensile.insp_code.is_(None)
        ).all()
        data = data_null if data_null else db_session.query(TestTensile).filter(
            TestTensile.test_id == test_id
        ).all()
    else:
        data = db_session.query(TestTensile).filter(
            TestTensile.test_id == test_id,
            TestTensile.insp_code.in_(inspector_code)
        ).all()
    
    dic = {}
    for d in data:
        dic.setdefault(d.test.test_sample_id, []).append(d)
    return dic


def get_by_test_sample_ids_tbm_inspector_is_none(*, db_session, test_sample_ids: List[int]) -> List[Optional[TestTensile]]:
    query = db_session.query(TestTensile).join(Test, Test.id == TestTensile.test_id).filter(
        Test.test_sample_id.in_(test_sample_ids))
    # .filter(
    #     # 增加条件，同时筛选 insp_code 为 None 或者空字符串的记录
    #     (TestTensile.insp_code.is_(None)) | (TestTensile.insp_code == "")
    # )
    return query.all()
    # query = (
    #     db_session.query(TestTensile)
    #     .join(Test, Test.id == TestTensile.test_id)
    #     .filter(Test.test_sample_id.in_(test_sample_ids))
    #     .filter(
    #         and_(
    #             or_(Test.inspector_id_1.is_(None), Test.inspector_id_1 == ""),
    #             or_(Test.inspector_id_2.is_(None), Test.inspector_id_2 == ""),
    #             or_(Test.inspector_id_3.is_(None), Test.inspector_id_3 == ""),
    #             or_(Test.inspector_id_4.is_(None), Test.inspector_id_4 == "")
    #         )
    #     )
    # )
    # return query.all()


def get_all_data_dict_of_spec_id_tbm_inspector_is_none(*, db_session, test_sample_ids: List[int]) -> dict:
    data = get_by_test_sample_ids_tbm_inspector_is_none(db_session=db_session, test_sample_ids=test_sample_ids)

    dic = {}
    for d in data:
        dic.setdefault(d.test.test_sample_id, []).append(d)
    return dic

