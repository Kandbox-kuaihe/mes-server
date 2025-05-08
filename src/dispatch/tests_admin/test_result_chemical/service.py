
from datetime import datetime
from typing import List, Optional
from sqlalchemy.sql.functions import func
from dispatch.mill.models import MillCreate
from dispatch.tests_admin.test_sample import service as test_sample_service
from dispatch.mill import service as mill_service 

from .models import TestResultChemical, TestResultChemicalCreate, TestResultChemicalRead, TestResultChemicalUpdate, TestResultChemicalCreate

def get(*, db_session, testResultChemical_id: int) -> Optional[TestResultChemical]:
    """Returns an testResultChemical given an testResultChemical id."""
    return db_session.query(TestResultChemical).filter(TestResultChemical.id == testResultChemical_id).one_or_none()



def create(*, db_session, testResultChemical_in: TestResultChemicalCreate) -> TestResultChemical:
    """Creates an testResultChemical."""
    test_sample = None
    mill = None
    if testResultChemical_in.test_sample_id is not None and testResultChemical_in.test_sample_id != -1:
        test_sample = test_sample_service.get(db_session= db_session, testSample_id = testResultChemical_in.test_sample_id) 
        mill = test_sample.mill
    contact = TestResultChemical(**testResultChemical_in.dict(exclude={"flex_form_data","test_sample","mill"}),
                    flex_form_data=testResultChemical_in.flex_form_data,
                    test_sample=test_sample,
                    mill=mill,
                    )
    db_session.add(contact)
    db_session.commit()
    return contact

def  get_float(data):
    f = None
    try:
        f = float(data)
    except ValueError:
        pass
    return f

def create_form_mq(*, db_session, testResultChemical_in,test_sample_id) -> TestResultChemical:
    """Creates an testResultChemical."""
    from dispatch.tests_admin.test_sample.service import get as test_sample_service_get
    test_sample = test_sample_service_get(db_session= db_session, testSample_id = test_sample_id)
    mill = None
    mill_code = "TBM"
    sample_type = testResultChemical_in.get("Sample Type","B")
    if sample_type == "B":
        mill_code = "TBM"
    elif sample_type == "S":
        mill_code = "SKG"
    mill = mill_service.get_by_code(db_session=db_session, code=mill_code)
    if not mill:
        mill_in = MillCreate(
            code=mill_code,
            type=mill_code,
            desc=mill_code,

        )
        mill = mill_service.create(db_session=db_session, mill_in=mill_in)

    contact = TestResultChemical(
        test_sample=test_sample ,
        mill=mill ,
        result_c=get_float(testResultChemical_in.get("Result C",None)) ,
        result_si=get_float(testResultChemical_in.get("Result Si",None)) ,
        result_mn=get_float(testResultChemical_in.get("Result Mn",None)) ,
        result_p=get_float(testResultChemical_in.get("Result P",None)) ,
        result_s=get_float(testResultChemical_in.get("Result S",None)) ,
        result_cr=get_float(testResultChemical_in.get("Result Cr",None)) ,
        result_mo=get_float(testResultChemical_in.get("Result Mo",None)) ,
        result_ni=get_float(testResultChemical_in.get("Result Ni",None)) ,
        result_al=get_float(testResultChemical_in.get("Result Al",None)) ,
        result_b=get_float(testResultChemical_in.get("Result B",None)) ,
        result_co=get_float(testResultChemical_in.get("Result Co",None)) ,
        result_cu=get_float(testResultChemical_in.get("Result Cu",None)) ,
        result_nb=get_float(testResultChemical_in.get("Result Nb",None)) ,
        result_sn=get_float(testResultChemical_in.get("Result Sn",None)) ,
        result_ti=get_float(testResultChemical_in.get("Result Ti",None)) ,
        result_v=get_float(testResultChemical_in.get("Result V",None)) ,
        result_ca=get_float(testResultChemical_in.get("Result Ca",None)) ,
        result_n2=get_float(testResultChemical_in.get("Result N2",None)) ,
        result_o=get_float(testResultChemical_in.get("Result O",None)) ,
        result_h=get_float(testResultChemical_in.get("Result H",None)) ,
        result_sal=get_float(testResultChemical_in.get("Result SAl",None)) ,
        result_as=get_float(testResultChemical_in.get("Result As",None)) ,
        result_bi=get_float(testResultChemical_in.get("Result Bi",None)) ,
        result_ce=get_float(testResultChemical_in.get("Result Ce",None)) ,
        result_pb=get_float(testResultChemical_in.get("Result Pb",None)) ,
        result_sb=get_float(testResultChemical_in.get("Result Sb",None)) ,
        result_w=get_float(testResultChemical_in.get("Result W",None)) ,
        result_zn=get_float(testResultChemical_in.get("Result Zn",None)) ,
        result_zr=get_float(testResultChemical_in.get("Result Zr",None)) ,
    )
    db_session.add(contact)
    db_session.commit()
    return contact

def update(
    *,
    db_session,
    testResultChemical: TestResultChemical,
    testResultChemical_in: TestResultChemicalUpdate,
) -> TestResultChemical:

    update_data = testResultChemical_in.dict(
       
        exclude={"flex_form_data","test_sample","mill"},
    )
    for field, field_value in update_data.items():
        setattr(testResultChemical, field, field_value)

    test_sample = None
    mill = None
    if testResultChemical_in.test_sample_id is not None and testResultChemical_in.test_sample_id != -1:
        test_sample = test_sample_service.get(db_session= db_session, testSample_id = testResultChemical_in.test_sample_id) 
        mill = test_sample.mill

    testResultChemical.mill = mill
    testResultChemical.test_sample = test_sample
    testResultChemical.flex_form_data = testResultChemical_in.flex_form_data
    testResultChemical.updated_at = datetime.utcnow()
    db_session.add(testResultChemical)
    db_session.commit()
    return testResultChemical


def delete(*, db_session, testResultChemical_id: int):
    db_session.query(TestResultChemical).filter(TestResultChemical.id == testResultChemical_id).update({"is_deleted": 1})

    db_session.commit()

    return TestResultChemicalRead(id=testResultChemical_id)


def get_by_test_sample_ids(*, db_session, test_sample_ids: List[int]) -> List[Optional[TestResultChemical]]:
    return db_session.query(TestResultChemical).filter(
        TestResultChemical.test_sample_id.in_(test_sample_ids)).all()


def get_all_data_dict_of_spec_id(*, db_session, test_sample_ids: List[int]) -> dict:
    data = get_by_test_sample_ids(db_session=db_session, test_sample_ids=test_sample_ids)

    dic = {}
    for d in data:
        if d.test_sample_id not in dic:
            dic[d.test_sample_id] = []
        dic[d.test_sample_id].append(d)
    return dic
