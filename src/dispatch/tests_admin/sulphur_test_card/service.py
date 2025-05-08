
from datetime import datetime
from typing import Optional

from dispatch.mill.models import MillCreate

from .models import TestSulphur, TestSulphurCreate, TestSulphurUpdate, TestSulphurRead

from dispatch.cast import service as cast_service
from dispatch.runout_admin.runout_list import service as runout_service
from dispatch.mill import service as mill_service
from dispatch.tests_admin.test_list import service as test_service
from dispatch.cast.models import CastCreate
from dispatch.runout_admin.runout_list.models import RunoutCreate

def get(*, db_session, TestSulphur_id: int) -> Optional[TestSulphur]:
    """Returns an TestSulphur given an TestSulphur id."""
    return db_session.query(TestSulphur).filter(TestSulphur.id == TestSulphur_id).one_or_none()


# def get_by_runout_id(*, db_session, runout_id: int) -> Optional[TestSulphur]:
#     """Returns an TestSulphur given an TestSulphur id."""
#     return db_session.query(TestSulphur).filter(TestSulphur.runout_id == runout_id).all()

# def get_by_runout_id_and_spec_id(*, db_session, runout_id: int,spec_id:int) -> Optional[TestSulphur]:
#     """Returns an TestSulphur given an TestSulphur id."""
#     return db_session.query(TestSulphur).filter(TestSulphur.runout_id == runout_id).filter(TestSulphur.spec_id == spec_id).all()






def get_by_code(*, db_session, code: str) -> Optional[TestSulphur]:
    """Returns an TestSulphur given an TestSulphur code address."""
    return db_session.query(TestSulphur).filter(TestSulphur.test_code == code).one_or_none()

 
# def get_by_test_sample_code(*, db_session, test_sample_code: str, test_sample_part: str) -> Optional[TestSulphur]:
    """Returns an TestSulphur given an TestSulphur code address."""
    return db_session.query(TestSulphur).filter(TestSulphur.test_sample_code == test_sample_code,TestSulphur.test_sample_part == test_sample_part).one_or_none()

# def get_default_TestSulphur(*, db_session ) -> Optional[TestSulphur]:
#     """Returns an TestSulphur given an TestSulphur code address."""
#     return db_session.query(TestSulphur).first()


# def get_all(*, db_session) -> List[Optional[TestSulphur]]:
#     """Returns all TestSulphurs."""
#     return db_session.query(TestSulphur)



# def get_float(data):
    if data is None:
        return None
    try:
        return float(data)
    except (ValueError, TypeError):
        return None


# def create_form_mq(*, db_session, TestSulphur_in) -> TestSulphur:
    """Creates an TestSulphur."""
    runout_code = TestSulphur_in.get("Piece ID",None)
    cast_code = TestSulphur_in.get("Concast No","")

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
        
    contact = TestSulphur(
        runout = runout,
        mill  = mill,
        cast = cast,
        test_sample_code = TestSulphur_in.get("Piece ID",""),
        test_sample_part = TestSulphur_in.get("Piece Sub ID",""),
        product_name = TestSulphur_in.get("Product String",""),
        concast_code = TestSulphur_in.get("Concast No",""),
        sample_thickness = get_float(TestSulphur_in.get("Sample Thickness")),
        sample_info = TestSulphur_in.get("Sample_Info",""),
        spec_name = TestSulphur_in.get("Short Name",""),
        inspector = TestSulphur_in.get("Inspector",""),
        retest = TestSulphur_in.get("Retest Number",""),
        orientation = TestSulphur_in.get("Orientation",""),
        standard = TestSulphur_in.get("Standard",""),
    )
    db_session.add(contact)
    db_session.commit()
    return contact

def create(*, db_session, TestSulphur_in: TestSulphurCreate) -> TestSulphur:
    """Creates an TestSulphur."""

    mill = None
    if TestSulphur_in.mill_id is not None and TestSulphur_in.mill_id != -1:
        mill = mill_service.get(db_session= db_session, mill_id = TestSulphur_in.mill_id) 
    
    test = None
    if TestSulphur_in.test_id is not None and TestSulphur_in.test_id != -1:
        test = test_service.get(db_session= db_session, id = TestSulphur_in.test_id)

    contact = TestSulphur(**TestSulphur_in.dict(exclude={"flex_form_data", "mill"}),
                    flex_form_data=TestSulphur_in.flex_form_data,
                    mill = mill,
                          )
    db_session.add(contact)
    db_session.commit()
    return contact


def update(
    *,
    db_session,
    TestSulphur: TestSulphur,
    TestSulphur_in: TestSulphurUpdate,
) -> TestSulphur:

    update_data = TestSulphur_in.model_dump(
        exclude={"flex_form_data", "mill"},
    )
    for field, field_value in update_data.items():
        setattr(TestSulphur, field, field_value)

    mill = None
    if TestSulphur_in.mill_id is not None and TestSulphur_in.mill_id != -1:
        mill = mill_service.get(db_session= db_session, mill_id = TestSulphur_in.mill_id) 
    
    test = None
    if TestSulphur_in.test_id is not None and TestSulphur_in.test_id != -1:
        test = test_service.get(db_session= db_session, id = TestSulphur_in.test_id)

    TestSulphur.flex_form_data = TestSulphur_in.flex_form_data
    TestSulphur.mill = mill
    TestSulphur.test = test
    TestSulphur.updated_at = datetime.utcnow()
    db_session.add(TestSulphur)
    db_session.commit()
    return TestSulphur


def delete(*, db_session, TestSulphur_id: int):
    
    db_session.query(TestSulphur).filter(TestSulphur.id == TestSulphur_id).update({"is_deleted": 1})
    db_session.commit()
    return TestSulphurRead(id=TestSulphur_id)  


def get_by_test_id(*, db_session, test_id: int) -> TestSulphur:
    return db_session.query(TestSulphur).filter(TestSulphur.test_id == test_id).one_or_none()
