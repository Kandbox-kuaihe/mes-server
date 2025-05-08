from datetime import datetime
import logging
from typing import Optional, List

from dispatch.cast import service as cast_service
from dispatch.cast.models import CastCreate
from dispatch.mill import service as mill_service
from dispatch.mill.models import MillCreate
from dispatch.runout_admin.runout_list import service as runout_service
from dispatch.runout_admin.runout_list.models import RunoutCreate
from dispatch.tests_admin.test_list import service as test_service
from dispatch.tests_admin.test_list.models import Test

from .models import TestImpact, TestImpactCreate, TestImpactRead, TestImpactUpdate
from sqlalchemy import or_, and_

from dispatch.log import getLogger
log = getLogger(__name__)

def get(*, db_session, TestImpact_id: int) -> Optional[TestImpact]:
    """Returns an TestImpact given an TestImpact id."""
    return db_session.query(TestImpact).filter(TestImpact.id == TestImpact_id).one_or_none()


def  get_float(data):
    f = None
    try:
        f = float(data)
    except ValueError:
        pass
    return f


def get_by_code(*, db_session, code: str) -> Optional[TestImpact]:
    """Returns an TestImpact given an TestImpact code address."""
    return db_session.query(TestImpact).filter(TestImpact.test_code == code).one_or_none()


def get_by_testing_machine(*, db_session, testing_machine: str) -> Optional[TestImpact]:
    """Returns an TestImpact given an TestImpact testing_machine address."""
    return db_session.query(TestImpact).filter(TestImpact.testing_machine == testing_machine).one_or_none()


def get_by_test_id(*, db_session, test_id: str) -> Optional[TestImpact]:
    """Returns an TestImpact given an TestImpact test_id address."""
    if not test_id: return
    return db_session.query(TestImpact).filter(TestImpact.test_id == test_id).one_or_none()

def create_or_update_impact_from_mq(*, db_session, testResultImpactBase_in,test_sample, test) -> TestImpact:
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

    retest_seq = get_float(testResultImpactBase_in.get('Retest No', 0))
    prefix = ""
    if retest_seq == 1:
        prefix = "r1_"
    elif retest_seq == 2:
        prefix = "r2_"

    new_test_result_impact_dict = {
        "test_sample": test_sample,
        'test_id': test.id,
        "mill": mill,
        "size_code": testResultImpactBase_in.get('Size Code', ""),
        "retest_seq": retest_seq,
        "orientation": testResultImpactBase_in.get("Orientation",None),
        "standard": testResultImpactBase_in.get('Standard'),
        "insp_code": testResultImpactBase_in.get('Inspection Code'),
        f"{prefix}temp_c": get_float(testResultImpactBase_in.get('Charpy Temp (C)')),
        f"{prefix}temp_f": get_float(testResultImpactBase_in.get('Charpy Temp (F)')),
        f"{prefix}energy_1_j": get_float(testResultImpactBase_in.get('Charpy Energy 1 (J)')),
        f"{prefix}energy_2_j": get_float(testResultImpactBase_in.get('Charpy Energy 2 (J)')),
        f"{prefix}energy_3_j": get_float(testResultImpactBase_in.get('Charpy Energy 3 (J)')),
        f"{prefix}energy_average_j": get_float(testResultImpactBase_in.get('Charpy Energy Average (J)')),
        f"{prefix}energy_1_f": get_float(testResultImpactBase_in.get('Charpy Energy 1 (F)')),
        f"{prefix}energy_2_f": get_float(testResultImpactBase_in.get('Charpy Energy 2 (F)')),
        f"{prefix}energy_3_f": get_float(testResultImpactBase_in.get('Charpy Energy 3 (F)')),
        f"{prefix}energy_average_f": get_float(testResultImpactBase_in.get('Charpy Energy Average (F)')),
        f"{prefix}shear_1": get_float(testResultImpactBase_in.get('Charpy Shear 1')),
        f"{prefix}shear_2": get_float(testResultImpactBase_in.get('Charpy Shear 2')),
        f"{prefix}shear_3": get_float(testResultImpactBase_in.get('Charpy Shear 3')),
        f"{prefix}shear_average": get_float(testResultImpactBase_in.get('Charpy Shear Average')),
        f"{prefix}temp_units": testResultImpactBase_in.get('Charpy Temp Units'),
        f"{prefix}impact_units": testResultImpactBase_in.get('Charpy Impact Units'),
    }

    # Remove None values to avoid setting fields that weren't provided
    new_test_result_impact_dict = {k: v for k, v in new_test_result_impact_dict.items() if v is not None}

    old_test_tensile = None
    if test:
        old_test_tensile = get_by_test_id(db_session=db_session, test_id=test.id)
    if not old_test_tensile:
        log.error(f"Test tensile with TEST ID {test.id} not found, test tensile in: {old_test_tensile}")
        old_test_tensile = TestImpact(**new_test_result_impact_dict)
        db_session.add(old_test_tensile)
    else:
        for key, value in new_test_result_impact_dict.items():
            setattr(old_test_tensile, key, value)
        old_test_tensile.updated_at = datetime.now()
    db_session.commit()
    return old_test_tensile

# def get_by_test_sample_code(*, db_session, test_sample_code: str, test_sample_part: str) -> Optional[TestImpact]:
    """Returns an TestImapct given an TestImpact code address."""
    return db_session.query(TestImpact).filter(TestImpact.test_sample_code == test_sample_code,TestImpact.test_sample_part == test_sample_part).one_or_none()


# def get_default_TestImapct(*, db_session ) -> Optional[TestImpact]:
#     """Returns an TestImpact given an TestImpact code address."""
#     return db_session.query(TestImpact).first()


# def get_all(*, db_session) -> List[Optional[TestImpact]]:
#     """Returns all TestImpact."""
#     return db_session.query(TestImpact)

# def get_float(data):
    if data is None:
        return None
    try:
        return float(data)
    except (ValueError, TypeError):
        return None


# def create_form_mq(*, db_session, TestImpact_in) -> TestImpact:
    """Creates an TestImpact."""
    runout_code = TestImpact_in.get("Piece ID",None)
    cast_code = TestImpact_in.get("Concast No","")
    # Validate cast_code
    cast = None
    if cast_code:
        cast = cast_service.get_by_code(db_session=db_session, code=cast_code)
        if not cast:
            new_cast = CastCreate(cast_code=cast_code)
            cast_service.create(db_session=db_session, cast_in=new_cast)
            print(f"Invalid cast_code: '{cast_code}'. No matching cast found. Create New Cast: '{cast_code}'.")
    # Validate runout_id
    runout = None
    if runout_code:
        runout = runout_service.get_by_code(db_session=db_session, code=runout_code)
        if not runout:
            new_runout = RunoutCreate(runout_code=runout_code)
            runout_service.create(db_session=db_session, runout_in=new_runout)
            print(f"Invalid runout_id: '{runout_code}'. No matching runout found. Create New Runout: '{cast_code}'.")


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
        
    contact = TestImpact(
        runout = runout,
        mill  = mill,
        cast = cast,
        test_sample_code = TestImpact_in.get("Piece ID",""),
        test_sample_part = TestImpact_in.get("Piece Sub ID",""),
        product_name = TestImpact_in.get("Product String",""),
        concast_code = TestImpact_in.get("Concast No",""),
        sample_thickness = get_float(TestImpact_in.get("Sample Thickness")),
        sample_info = TestImpact_in.get("Sample_Info",""),
        spec_name = TestImpact_in.get("Short Name",""),
        inspector = TestImpact_in.get("Inspector",""),
        retest = TestImpact_in.get("Retest Number",""),
        test_code = TestImpact_in.get("test_code"),
        section = TestImpact_in.get("section",""),
        sextion_size_code = TestImpact_in.get("sextion_size_code",""),
        charpy_temp_c= get_float(TestImpact_in.get('charpy_temp_c')),
        charpy_temp_f= get_float(TestImpact_in.get('charpy_temp_f')),
        charpy_energy_1_j= get_float(TestImpact_in.get('charpy_energy_1_j')),
        charpy_energy_2_j= get_float(TestImpact_in.get('charpy_energy_2_j')),
        charpy_energy_3_j= get_float(TestImpact_in.get('charpy_energy_3_j')),
        charpy_energy_average_j= get_float(TestImpact_in.get('charpy_energy_average_j')),
        charpy_energy_1_f= get_float(TestImpact_in.get('charpy_energy_2_f')),
        charpy_energy_2_f= get_float(TestImpact_in.get('charpy_energy_2_f')),
        charpy_energy_3_f= get_float(TestImpact_in.get('charpy_energy_3_f')),
        charpy_energy_average_f= get_float(TestImpact_in.get('charpy_energy_average_f')),
        charpy_shear_1= get_float(TestImpact_in.get('charpy_shear_1')),
        charpy_shear_2= get_float(TestImpact_in.get('charpy_shear_2')),
        charpy_shear_3= get_float(TestImpact_in.get('charpy_shear_3')),
        charpy_shear_average= get_float(TestImpact_in.get('charpy_shear_average')),
        charpy_temp_units= TestImpact_in.get('charpy_temp_units'),
        charpy_impact_units= TestImpact_in.get('charpy_impact_units'),
        teststandard= TestImpact_in.get('teststandard'),
        # status= '2345',
                )
    db_session.add(contact)
    db_session.commit()
    return contact

def create(*, db_session, TestImpact_in: TestImpactCreate) -> TestImpact:
    """Creates an TestImpact."""

    mill = None
    if TestImpact_in.mill_id is not None and TestImpact_in.mill_id != -1:
        mill = mill_service.get(db_session= db_session, mill_id = TestImpact_in.mill_id)

    contact = TestImpact(**TestImpact_in.dict(exclude={"flex_form_data", "mill", "test"}),
                    flex_form_data=TestImpact_in.flex_form_data,
                    mill=mill
                    )
    db_session.add(contact)
    db_session.commit()
    return contact

def update(
    *,
    db_session,
    TestImpact: TestImpact,
    TestImpact_in: TestImpactUpdate,
) -> TestImpact:

    update_data = TestImpact_in.dict(
        exclude={"flex_form_data", "mill", "test"},
    )
    for field, field_value in update_data.items():
        setattr(TestImpact, field, field_value)

    mill = None
    if TestImpact_in.mill_id is not None and TestImpact_in.mill_id != -1:
        mill = mill_service.get(db_session= db_session, mill_id = TestImpact_in.mill_id) 

    TestImpact.flex_form_data = TestImpact_in.flex_form_data
    TestImpact.mill = mill
    TestImpact.updated_at = datetime.utcnow()
    db_session.add(TestImpact)
    db_session.commit()
    return TestImpact


def delete(*, db_session, TestImpact_id: int):
    
    db_session.query(TestImpact).filter(TestImpact.id == TestImpact_id).update({"is_deleted": 1})
    db_session.commit()
    return TestImpactRead(id=TestImpact_id)  



def get_by_test_sample_ids(*, db_session, test_sample_ids: list[int], runout_id:int=None) ->  list[TestImpact]:
    query = db_session.query(TestImpact).join(Test, Test.id==TestImpact.test_id).filter(
        Test.test_sample_id.in_(test_sample_ids))
    if runout_id:
        query = query.filter(Test.runout_id == runout_id)
    return query.all()


def get_all_data_dict_of_spec_id(*, db_session, test_sample_ids: list[int], runout_id:int=None) -> dict[int, list[TestImpact]]:
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
        dic.setdefault(d.test_sample_id, []).append(d)
    return dic

def get_by_test_ids(*, db_session, test_ids: list[int]) -> list[TestImpact]:
    return db_session.query(TestImpact).filter(TestImpact.test_id.in_(test_ids)).all()

def get_all_data_dict_by_test_ids(*, db_session, test_ids: list[int]) -> dict[int,list[TestImpact]]:
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


def get_all_by_test_id(*, db_session, test_id: int, inspector_code: Optional[List[str]] = None) -> Optional[TestImpact]:
    """Returns an testResultImpactBase given an testResultImpactBase id."""
    query = db_session.query(TestImpact).filter(TestImpact.test_id == test_id)
    if inspector_code:
        query = query.filter(TestImpact.insp_code.in_(inspector_code))
    return query.all()


def get_by_test_sample_ids_tbm(*, db_session, test_sample_ids: List[int], inspector_code: Optional[List[str]] = None) -> List[Optional[TestImpact]]:
    query = db_session.query(TestImpact).join(Test, Test.id==TestImpact.test_id).filter(
        Test.test_sample_id.in_(test_sample_ids))
    if inspector_code:
        query = query.filter(TestImpact.insp_code.in_(inspector_code))
    return query.all()
    # if inspector_code:
    #         query = query.filter(
    #             or_(
    #                 Test.inspector_id_1.in_(inspector_code),
    #                 Test.inspector_id_2.in_(inspector_code),
    #                 Test.inspector_id_3.in_(inspector_code),
    #                 Test.inspector_id_4.in_(inspector_code)
    #             )
    #         )
    # return query.all()


def get_all_data_dict_of_spec_id_tbm(*, db_session, test_sample_ids: List[int], inspector_code: Optional[List[str]] = None) -> dict:
    data = get_by_test_sample_ids_tbm(db_session=db_session, test_sample_ids=test_sample_ids, inspector_code=inspector_code)

    dic = {}
    for d in data:
        dic.setdefault(d.test.test_sample_id, []).append(d)
    return dic


def get_by_test_sample_ids_tbm_inspector_is_none(*, db_session, test_sample_ids: List[int]) -> List[Optional[TestImpact]]:
    query = db_session.query(TestImpact).join(Test, Test.id == TestImpact.test_id).filter(
        Test.test_sample_id.in_(test_sample_ids))
    # .filter(
    #     # 增加条件，同时筛选 insp_code 为 None 或者空字符串的记录
    #     (TestImpact.insp_code.is_(None)) | (TestImpact.insp_code == "")
    # )
    return query.all()
    # query = (
    #     db_session.query(TestImpact)
    #     .join(Test, Test.id == TestImpact.test_id)
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


def get_all_data_dict_of_spec_id_tbm_by_test(
    *, 
    db_session, 
    test_id: int, 
    inspector_code: Optional[List[str]] = None
) -> dict:
    if not inspector_code:
        data_null = db_session.query(TestImpact).filter(
            TestImpact.test_id == test_id,
            TestImpact.insp_code.is_(None)
        ).all()
        data = data_null if data_null else db_session.query(TestImpact).filter(
            TestImpact.test_id == test_id
        ).all()
    else:
        data = db_session.query(TestImpact).filter(
            TestImpact.test_id == test_id,
            TestImpact.insp_code.in_(inspector_code)
        ).all()
    
    return data


