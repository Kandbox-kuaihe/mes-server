
from datetime import datetime
from typing import List, Optional


from sqlalchemy import or_
from dispatch.area import service as area_service
from dispatch.cast import service as cast_service
from dispatch.cast.models import CastCreate
from dispatch.mill import service as mill_service
from dispatch.mill.models import MillCreate
from dispatch.runout_admin.finished_product.models import FinishedProduct
from dispatch.runout_admin.runout_list import service as runout_service
from dispatch.runout_admin.runout_list.models import RunoutCreate
from dispatch.spec_admin.spec import service as spec_service
from dispatch.spec_admin.spec.models import SpecCreate
from dispatch.tests_admin.test_list.models import Test
from dispatch.tests_admin.test_result_chemical.models import TestResultChemical
from dispatch.tests_admin.test_result_impact.models import TestResultImpact
from dispatch.tests_admin.test_result_tensile.models import TestResultTensile
from dispatch.tests_admin.test_result_tensile_thickness.models import TestResultTensileThickness
from dispatch.tests_admin.test_piece.models import TestPiece
# from dispatch.runout_admin.finished_product import service as finished_product_service

from .models import TestSample, TestSampleCreate, TestSampleRead, TestSampleUpdate
from dispatch.log import getLog
from ...config import MILLEnum

log = getLog(__name__)

def get(*, db_session, testSample_id: int) -> Optional[TestSample]:
    """Returns an testSample given an testSample id."""
    return db_session.query(TestSample).filter(TestSample.id == testSample_id).one_or_none()


def get_by_runout_id(*, db_session, runout_id: int) -> list[TestSample]:
    """Returns an testSample given an testSample id."""
    return db_session.query(TestSample).filter(TestSample.runout_id == runout_id).all()

def get_by_test_ref_by_finished(*, db_session, finished_code: str, finished_date: str) -> list[TestPiece]:
    return db_session.query(TestPiece.test_number,TestPiece.occurrence, TestPiece.cast_id).filter(TestPiece.bundle_date == finished_date, TestPiece.bun_identity == finished_code).filter(TestPiece.is_deleted==0).all()

def get_test_list_by_testref(*, db_session, test_ref_list: list[TestPiece], cast_id: int) -> list[Test]:
    test_codes = [t.test_number for t in test_ref_list]
    if not test_codes:
        return []
    return list(db_session.query(Test).filter(Test.ref_code.in_(test_codes)).filter(or_(Test.is_deleted == 0, Test.is_deleted == None)).filter(Test.cast_id == cast_id).all())

def get_test_list_by_ids(*, db_session, test_ids: list[int]) -> list[Test]:
    return list(db_session.query(Test).filter(Test.id.in_(test_ids)).filter(or_(Test.is_deleted == 0, Test.is_deleted == None)).all())

def get_by_runout_id_and_spec_id(*, db_session, runout_id: int,spec_id:int) -> Optional[TestSample]:
    """Returns an testSample given an testSample id."""
    return db_session.query(TestSample).filter(TestSample.runout_id == runout_id).filter(TestSample.spec_id == spec_id).all()

def get_by_concast_code(*, db_session, concast_code) -> Optional[TestSample]:
    """Returns an testSample given a concast code."""
    return db_session.query(TestSample).filter(TestSample.concast_code == concast_code).first()


def get_by_code(*, db_session, code: str) -> Optional[TestSample]:
    """Returns an testSample given an testSample code address."""
    return db_session.query(TestSample).filter(TestSample.code == code).one_or_none()

def get_test_sample_id_by_test_ref(*,db_session, test_ref:str, cast_id:int) -> Optional[int]:
    test = db_session.query(Test).filter(Test.ref_code == test_ref, Test.cast_id == cast_id).order_by(Test.created_at.desc()).first()
    if not test:
        return None
    return test.test_sample_id
 
def get_by_test_sample_code(*, db_session, test_sample_code: str, test_sample_part: str) -> Optional[TestSample]:
    """Returns an testSample given an testSample code address."""
    test_sample = db_session.query(TestSample).filter(TestSample.test_sample_code == test_sample_code,TestSample.test_sample_part == test_sample_part).one_or_none()
    if not test_sample:
        test_sample = db_session.query(TestSample).filter(TestSample.test_sample_code == test_sample_code).first() # lims 140,141 do not need test_sample_part
    return test_sample

def get_default_testSample(*, db_session ) -> Optional[TestSample]:
    """Returns an testSample given an testSample code address."""
    return db_session.query(TestSample).first()

def get_by_test_sample_code_m(*, db_session, test_sample_code: str, mill_id: int) -> Optional[TestSample]:
    """Returns an testSample given an testSample code address."""
    return db_session.query(TestSample).filter(TestSample.test_sample_code == test_sample_code,TestSample.mill_id == mill_id).one_or_none()

def get_by_test_sample_code_mill_id(*, db_session, test_sample_code: str, mill_id: int) -> Optional[TestSample]:
    """Returns an testSample given an testSample code address."""
    return db_session.query(TestSample).filter(TestSample.test_sample_code == test_sample_code,TestSample.mill_id == mill_id).first()


def get_all(*, db_session) -> List[Optional[TestSample]]:
    """Returns all testSamples."""
    return db_session.query(TestSample)



def get_float(data):
    if data is None:
        return None
    try:
        return float(data)
    except (ValueError, TypeError):
        return None


def create_from_mq(*, db_session, testSample_in, message_code=None) -> TestSample:
    """Creates an testSample."""
    runout_code = testSample_in.get("Piece ID",None)
    cast_code = testSample_in.get("Concast No","")
 
    # Validate cast_code
    cast = None
    if cast_code:
        cast = cast_service.get_by_code(db_session=db_session, code=cast_code)
        if not cast:
            cast = cast_service.get_by_code(db_session=db_session, code='999999999')
            # cast = cast_service.create(db_session=db_session, cast_in=new_cast)
            # print(f"Invalid cast_code: '{cast_code}'. No matching cast found. Create New Cast: '{cast_code}'.")
    # Validate runout_id
    runout = None
    if runout_code:
        runout = runout_service.get_by_code(db_session=db_session, code=runout_code)
        if not runout:
            new_runout = RunoutCreate(runout_code=runout_code, mill_id=MILLEnum.MILL410)
            runout = runout_service.create(db_session=db_session, runout_in=new_runout)
            print(f"Invalid runout_id: '{runout_code}'. No matching runout found. Create New Runout: '{runout_code}'.")


    mill = None
    mill_code = "TBM"
    sample_type = testSample_in.get("Sample Type","B")
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

    test_sample_code = testSample_in.get("Piece ID",None)
    #test_sample_part = testSample_in.get("Piece Sub ID",None)

    test_sample = db_session.query(TestSample).filter(TestSample.test_sample_code == test_sample_code
                                                      #,TestSample.test_sample_part == test_sample_part
                                                      ).first() # sample_cut_type = ["T", "W", "D", "I"], sometimes one runout have multi test_samples, like: "W" and "D", but "D" one for one year
    spec_short_name = testSample_in.get("Short Name",None)
    spec = None
    if spec_short_name:
        spec_list = spec_service.get_by_short_name(db_session=db_session, short_name=spec_short_name)
        if spec_list:
            spec = spec_list[0]
        if not spec:
            new_spec = SpecCreate(short_name=spec_short_name)
            spec = spec_service.create(db_session=db_session, spec_in=new_spec)
            print(f"Invalid spec_short_name: '{spec_short_name}'. No matching spec found. Create New Spec: '{spec_short_name}'.")
    elif runout:
        finished_product = db_session.query(FinishedProduct).filter(FinishedProduct.runout_id == runout.id).first()
        if finished_product:
            spec = spec_service.get(db_session=db_session, id=finished_product.spec_id)
    
    if "inspector" in testSample_in:
        inspector = testSample_in.get("Inspector",None) 
    elif "Inspector Code" in testSample_in:
        inspector = testSample_in.get("Inspector Code",None) 
    elif "Inspection Code" in testSample_in:
        inspector = testSample_in.get("Inspection Code",None) 
    else:
        inspector = ''
    test_sample_dict = {
        'runout_id': runout.id if runout else None ,
        'runout': runout,
        "rolling_id": runout.rolling_id if runout else None,
        'mill_id': mill.id if mill else None,
        'mill': mill,
        'cast_id': cast.id if cast else None,
        'cast': cast,
        'spec_id': spec.id if spec else None,
        'spec': spec,
        'test_sample_code': test_sample_code,
        #test_sample_part: test_sample_part,
        'product_name': testSample_in.get("Product String",None),
        'concast_code': testSample_in.get("Concast No",None),
        'sample_thickness': get_float(testSample_in.get("Sample Thickness")),
        'sample_info': testSample_in.get("Sample_Info",None),
        'spec_name': testSample_in.get("Short Name",None),
        #'inspector': inspector,
        'retest': testSample_in.get("Retest Number",None),
        'orientation': testSample_in.get("Orientation",None),
        'standard': testSample_in.get("Standard",None),
    }
    if message_code == '121':
        test_sample_dict.update({'status': 'R'})
    elif message_code == '127':
        test_sample_dict.update({'status': 'T'})

    test_sample_dict = {k: v for k, v in test_sample_dict.items() if v is not None}
    if test_sample is None:
        test_sample_dict.update({'source': 'TEST-RESULT'})
        testSample_in_data = TestSampleCreate(**test_sample_dict)
        test_sample = create(db_session=db_session, testSample_in=testSample_in_data)
    else:
        for key, value in test_sample_dict.items():
            setattr(test_sample, key, value)
        db_session.commit()
    return test_sample

def create(*, db_session, testSample_in: TestSampleCreate) -> TestSample:
    """Creates an testSample."""


    spec = None
    if testSample_in.spec_id is not None and testSample_in.spec_id != -1:
        spec = spec_service.get(db_session= db_session, id = testSample_in.spec_id) 

    cast = None
    if testSample_in.cast_id is not None and testSample_in.cast_id != -1:
        cast = cast_service.get(db_session= db_session, id = testSample_in.cast_id) 
    runout = None
    if testSample_in.runout_id is not None and testSample_in.runout_id != -1:
        runout = runout_service.get(db_session= db_session, runout_id = testSample_in.runout_id) 

    mill = None
    if testSample_in.mill_id is not None and testSample_in.mill_id != -1:
        mill = mill_service.get(db_session= db_session, mill_id = testSample_in.mill_id) 

    area = None
    if testSample_in.area_id:
        area = area_service.get(db_session= db_session, area_id = testSample_in.area_id)

    contact = TestSample(
        **testSample_in.dict(exclude={"id", "flex_form_data", "spec", "cast", "runout", "mill", "area", "finished_product"}),
        flex_form_data=testSample_in.flex_form_data,
        spec=spec,
        cast=cast,
        runout=runout,
        mill=mill,
        area=area
    )
    db_session.add(contact)
    db_session.commit()
    return contact


def update(
    *,
    db_session,
    testSample: TestSample,
    testSample_in: TestSampleUpdate,
) -> TestSample:

    update_data = testSample_in.dict(
        exclude={"flex_form_data","spec","cast","mill","runout","area","finished_product"},
    )
    for field, field_value in update_data.items():
        setattr(testSample, field, field_value)


    spec = None
    if testSample_in.spec_id is not None and testSample_in.spec_id != -1:
        spec = spec_service.get(db_session= db_session, id = testSample_in.spec_id) 
    cast = None
    if testSample_in.cast_id is not None and testSample_in.cast_id != -1:
        cast = cast_service.get(db_session= db_session, id = testSample_in.cast_id) 
    runout = None
    if testSample_in.runout_id is not None and testSample_in.runout_id != -1:
        runout = runout_service.get(db_session= db_session, runout_id = testSample_in.runout_id) 

    mill = None
    if testSample_in.mill_id is not None and testSample_in.mill_id != -1:
        mill = mill_service.get(db_session= db_session, mill_id = testSample_in.mill_id) 

    area = None
    if testSample_in.area_id:
        area = area_service.get(db_session= db_session, area_id = testSample_in.area_id)

    testSample.flex_form_data = testSample_in.flex_form_data
    testSample.mill = mill
    testSample.runout = runout
    testSample.cast = cast
    testSample.spec = spec
    testSample.area = area
    testSample.updated_at = datetime.utcnow()
    db_session.add(testSample)
    db_session.commit()
    return testSample


def delete(*, db_session, testSample_id: int):
    
    db_session.query(TestSample).filter(TestSample.id == testSample_id).update({"is_deleted": 1})

    db_session.query(TestResultChemical).filter(TestResultChemical.test_sample_id == testSample_id).update({"is_deleted": 1}) 
    db_session.query(TestResultImpact).filter(TestResultImpact.test_sample_id == testSample_id).update({"is_deleted": 1}) 
    db_session.query(TestResultTensile).filter(TestResultTensile.test_sample_id == testSample_id).update({"is_deleted": 1}) 
    db_session.query(TestResultTensileThickness).filter(TestResultTensileThickness.test_sample_id == testSample_id).update({"is_deleted": 1}) 
    db_session.commit()
    return TestSampleRead(id=testSample_id)  