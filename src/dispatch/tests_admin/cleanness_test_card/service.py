
from datetime import datetime
from typing import Optional

from dispatch.mill.models import MillCreate

from .models import TestCleanness, TestCleannessCreate, TestCleannessUpdate, TestCleannessRead

from dispatch.cast import service as cast_service
from dispatch.runout_admin.runout_list import service as runout_service
from dispatch.mill import service as mill_service
from dispatch.tests_admin.test_list import service as test_service
from dispatch.cast.models import CastCreate
from dispatch.runout_admin.runout_list.models import RunoutCreate

def get(*, db_session, TestCleanness_id: int) -> Optional[TestCleanness]:
    """Returns an TestCleanness given an TestCleanness id."""
    return db_session.query(TestCleanness).filter(TestCleanness.id == TestCleanness_id).one_or_none()


# def get_by_runout_id(*, db_session, runout_id: int) -> Optional[TestCleanness]:
#     """Returns an TestCleanness given an TestCleanness id."""
#     return db_session.query(TestCleanness).filter(TestCleanness.runout_id == runout_id).all()

# def get_by_runout_id_and_spec_id(*, db_session, runout_id: int,spec_id:int) -> Optional[TestCleanness]:
#     """Returns an TestCleanness given an TestCleanness id."""
#     return db_session.query(TestCleanness).filter(TestCleanness.runout_id == runout_id).filter(TestCleanness.spec_id == spec_id).all()






def get_by_code(*, db_session, code: str) -> Optional[TestCleanness]:
    """Returns an TestCleanness given an TestCleanness code address."""
    return db_session.query(TestCleanness).filter(TestCleanness.test_code == code).one_or_none()

 
# def get_by_test_sample_code(*, db_session, test_sample_code: str, test_sample_part: str) -> Optional[TestCleanness]:
    """Returns an TestCleanness given an TestCleanness code address."""
    return db_session.query(TestCleanness).filter(TestCleanness.test_sample_code == test_sample_code,TestCleanness.test_sample_part == test_sample_part).one_or_none()

# def get_default_TestCleanness(*, db_session ) -> Optional[TestCleanness]:
#     """Returns an TestCleanness given an TestCleanness code address."""
#     return db_session.query(TestCleanness).first()


# def get_all(*, db_session) -> List[Optional[TestCleanness]]:
#     """Returns all TestCleannesss."""
#     return db_session.query(TestCleanness)



# def get_float(data):
    if data is None:
        return None
    try:
        return float(data)
    except (ValueError, TypeError):
        return None


# def create_form_mq(*, db_session, TestCleanness_in) -> TestCleanness:
    """Creates an TestCleanness."""
    runout_code = TestCleanness_in.get("Piece ID",None)
    cast_code = TestCleanness_in.get("Concast No","")

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
        
    contact = TestCleanness(
        runout = runout,
        mill  = mill,
        cast = cast,
        test_sample_code = TestCleanness_in.get("Piece ID",""),
        test_sample_part = TestCleanness_in.get("Piece Sub ID",""),
        product_name = TestCleanness_in.get("Product String",""),
        concast_code = TestCleanness_in.get("Concast No",""),
        sample_thickness = get_float(TestCleanness_in.get("Sample Thickness")),
        sample_info = TestCleanness_in.get("Sample_Info",""),
        spec_name = TestCleanness_in.get("Short Name",""),
        inspector = TestCleanness_in.get("Inspector",""),
        retest = TestCleanness_in.get("Retest Number",""),
        orientation = TestCleanness_in.get("Orientation",""),
        standard = TestCleanness_in.get("Standard",""),
    )
    db_session.add(contact)
    db_session.commit()
    return contact

def create(*, db_session, TestCleanness_in: TestCleannessCreate) -> TestCleanness:
    """Creates an TestCleanness."""

    mill = None
    if TestCleanness_in.mill_id is not None and TestCleanness_in.mill_id != -1:
        mill = mill_service.get(db_session= db_session, mill_id = TestCleanness_in.mill_id)

    test = None 
    if TestCleanness_in.test_id is not None and TestCleanness_in.test_id != -1:
        test = test_service.get(db_session= db_session, id = TestCleanness_in.test_id)

    contact = TestCleanness(**TestCleanness_in.dict(exclude={"flex_form_data", "mill"}),
                    flex_form_data=TestCleanness_in.flex_form_data,
                    mill = mill,
                            )
    db_session.add(contact)
    db_session.commit()
    return contact


def update(
    *,
    db_session,
    TestCleanness: TestCleanness,
    TestCleanness_in: TestCleannessUpdate,
) -> TestCleanness:

    update_data = TestCleanness_in.dict(
        exclude={"flex_form_data", "mill", "test"},
    )
    for field, field_value in update_data.items():
        setattr(TestCleanness, field, field_value)

    mill = None
    if TestCleanness_in.mill_id is not None and TestCleanness_in.mill_id != -1:
        mill = mill_service.get(db_session= db_session, mill_id = TestCleanness_in.mill_id) 

    test = None
    if TestCleanness_in.test_id is not None and TestCleanness_in.test_id != -1:
        test = test_service.get(db_session= db_session, id = TestCleanness_in.test_id)

    TestCleanness.flex_form_data = TestCleanness_in.flex_form_data
    TestCleanness.mill = mill
    TestCleanness.test = test
    TestCleanness.updated_at = datetime.utcnow()
    db_session.add(TestCleanness)
    db_session.commit()
    return TestCleanness


def delete(*, db_session, TestCleanness_id: int):
    
    db_session.query(TestCleanness).filter(TestCleanness.id == TestCleanness_id).update({"is_deleted": 1})
    db_session.commit()
    return TestCleannessRead(id=TestCleanness_id)  


def get_by_test_id(*, db_session, test_id: int) -> TestCleanness:
    return db_session.query(TestCleanness).filter(TestCleanness.test_id == test_id).one_or_none()
