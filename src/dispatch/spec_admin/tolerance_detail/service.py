from typing import List, Optional
from sqlalchemy.sql.functions import func
from .models import ToleranceDetail, ToleranceDetailCreate, ToleranceDetailUpdate
from dispatch.mill import service as mill_service
from dispatch.spec_admin.tolerance import service as tolerance_service
 

def get(*, db_session, id: int) -> Optional[ToleranceDetail]:
    return db_session.query(ToleranceDetail).filter(ToleranceDetail.id == id).one_or_none()

def get_by_code(*, db_session, code: str) -> Optional[ToleranceDetail]:
    return db_session.query(ToleranceDetail).filter(ToleranceDetail.bar_loc_code == code).one_or_none()

def create(*, db_session, tolerance_detail_in: ToleranceDetailCreate) -> ToleranceDetail:
    # exclude={"flex_form_data", "location"}
    mill = None
    if tolerance_detail_in.mill_id:
        mill = mill_service.get(db_session=db_session, mill_id=tolerance_detail_in.mill_id)
    tolerance = None
    if tolerance_detail_in.tolerance_id:
        tolerance = tolerance_service.get(db_session=db_session, id=tolerance_detail_in.tolerance_id)
    tolerance_detail = ToleranceDetail(**tolerance_detail_in.dict(exclude={"flex_form_data", "mill", "tolerance"}), mill=mill, tolerance=tolerance)
    db_session.add(tolerance_detail)
    db_session.commit()
    return tolerance_detail

def update(
    db_session,
    item: ToleranceDetail,
    tolerance_detail_in: ToleranceDetailUpdate,
) -> ToleranceDetail:
    
    mill = None
    if tolerance_detail_in.mill_id:
        mill = mill_service.get(db_session=db_session, mill_id=tolerance_detail_in.mill_id)
    tolerance = None
    if tolerance_detail_in.tolerance_id:
        tolerance = tolerance_service.get(db_session=db_session, id=tolerance_detail_in.tolerance_id)

    update_data = tolerance_detail_in.dict(
        exclude={"flex_form_data", "mill", "tolerance"},
    )
    for field, field_value in update_data.items():
        setattr(item, field, field_value)
    
    item.mill = mill
    item.tolerance = tolerance

    db_session.add(item)
    db_session.commit()
    return item

def delete(*, db_session, id: int):
    # db_session.query(ToleranceDetail).filter(ToleranceDetail.id == id).delete()
    db_session.query(ToleranceDetail).filter(ToleranceDetail.id == id).update({"is_deleted": 1})
    db_session.commit()


def get_tolerance_detail_codes(*, db_session):
    codes = []
    result = db_session.query(ToleranceDetail.code).all()
    if not result:
        return codes
    for i in result:
        codes.append(i[0])
    print(codes)
    return codes

def get_tolerance_detail_by_tolerance_id_and_bar_loc_code_and_flange_thickness(*, db_session, tolerance_id: int, bar_loc_code: str, flange_thickness: float) -> Optional[ToleranceDetail]:
    if not tolerance_id or not flange_thickness:
        return None
    return db_session.query(ToleranceDetail).filter(
        ToleranceDetail.tolerance_id == tolerance_id,
        ToleranceDetail.bar_loc_code == bar_loc_code,
        ToleranceDetail.value_min <= flange_thickness, ToleranceDetail.value_max >= flange_thickness).one_or_none()

def get_by_bar_loc_code(*, db_session, id, bar_loc_code) -> ToleranceDetail:
    return db_session.query(ToleranceDetail).filter(ToleranceDetail.tolerance_id == id, ToleranceDetail.bar_loc_code == bar_loc_code).all()

def get_by_required_value(tolerances: List[ToleranceDetail], value):
    print(f"DEBUG: Received value: {value} (type: {type(value)})")
    
    if value is None:
        return None  # Handle None case properly

    for tolerance in tolerances:
        if tolerance.value_min < float(value) < tolerance.value_max:
            return tolerance
