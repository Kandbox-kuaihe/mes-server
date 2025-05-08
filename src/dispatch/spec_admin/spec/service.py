
from typing import List, Optional

from dispatch.cast_spec.models import CastSpec
from dispatch.mill.models import Mill
from dispatch.spec_admin.sp_other_test.models import SpOtherTest
from dispatch.spec_admin.sp_various.models import SpVarious
from dispatch.spec_admin.spmainel.models import Spmainel
from dispatch.spec_admin.spmainel_other_element.models import SpmainelOtherElement
from dispatch.spec_admin.tolerance.models import Tolerance
from .models import Spec, SpecCreate, SpecUpdate, SpecCreate, SpecByCode
from sqlalchemy import or_, not_, func
from datetime import datetime, timezone
from fastapi import HTTPException
from sqlalchemy_filters import apply_pagination
from dispatch.spec_admin.inspector import service as inspector_service
from dispatch.spec_admin.inspector.models import Inspector
from sqlalchemy.exc import IntegrityError

from dispatch.log import getLogger
logger = getLogger(__name__)


def get(*, db_session, id: int) -> Optional[Spec]:
    """Returns an spec given an spec id."""
    if not id: return
    return db_session.query(Spec).filter(Spec.id == id).one_or_none()

def get_by_list_code(*, db_session, list_code: list[str]) -> List[Optional[Spec]]:
    """Returns an spec given an spec id."""
    return db_session.query(Spec).filter(Spec.spec_code.in_(list_code)).all()


def get_by_short_name(*, db_session, short_name: list[str]) -> List[Optional[Spec]]:
    """Returns an spec given an spec id."""
    return db_session.query(Spec).filter(Spec.short_name==short_name).all()

def get_by_code(*, db_session, code: str, mill:int, version_status:str) -> Optional[Spec]:
    """Returns an spec given an spec code address."""
    return db_session.query(Spec).filter(Spec.spec_code == code, Spec.mill_id == mill, Spec.version_status == version_status).first()

def get_by_spec_codes(*, db_session, spec_codes: List[int]) -> List[Optional[Spec]]:
    """Returns an semi given an semi id."""
    return db_session.query(Spec).filter(Spec.spec_code.in_(spec_codes)).all()

def get_by_code_m(*, db_session, code: str, mill_id: int) -> Optional[Spec]:
    """Returns an spec given an spec code address."""
    return db_session.query(Spec).filter(Spec.spec_code == code, Spec.mill_id == mill_id, Spec.version_status == 'R').one_or_none()


def get_by_ids(*, db_session, ids: list) ->  List[Optional[Spec]]:
    """Returns an spec given an spec id."""
    return db_session.query(Spec).filter(Spec.id.in_(ids)).all()


def get_default_spec(*, db_session ) -> Optional[Spec]:
    """Returns an spec given an spec code address."""
    return db_session.query(Spec).first()


def get_all(*, db_session) -> List[Optional[Spec]]:
    """Returns all specs."""
    return db_session.query(Spec)


def get_all_data(*, db_session) -> List[Optional[Spec]]:
    """Returns all specs."""
    return db_session.query(Spec).filter(Spec.spec_code.like('S%')).all()

def get_by_first_code(*, db_session, code: str) -> Optional[Spec]:
    """Returns an spec given an spec code address."""
    return db_session.query(Spec).filter(Spec.spec_code == code).first()





def create(*, db_session, spec_in: SpecCreate) -> Spec:
    """Creates an spec."""
    mill = None
    tolerance = None
    if spec_in.mill_id:
        mill = db_session.query(Mill).filter(Mill.id == spec_in.mill_id).one_or_none()

    if spec_in.tolerance_id:
        tolerance = db_session.query(Tolerance).filter(Tolerance.id == spec_in.tolerance_id).one_or_none()

    contact = Spec(**spec_in.dict(exclude={"flex_form_data","inspector","mill", "redio_type","children_specs","tolerance"}),
                   mill=mill,
                   tolerance=tolerance,
                    flex_form_data=spec_in.flex_form_data)
    try:
        db_session.add(contact)
        db_session.commit()
    except Exception as err:
        db_session.rollback()
        # 输出异常信息
        logger.error(f"Failed: {str(err)}")

    return contact


def update(
    *,
    db_session,
    spec: Spec,
    spec_in: SpecUpdate,
    inspectors:List[Inspector] = [],
    children_specs:List[Spec] = []
) -> Spec:
    
    if spec_in.mill_id:
        spec.mill = db_session.query(Mill).filter(Mill.id == spec_in.mill_id).one_or_none()

    if spec_in.tolerance_id:
        spec.tolerance = db_session.query(Tolerance).filter(Tolerance.id == spec_in.tolerance_id).one_or_none()

    update_data = spec_in.dict(
        exclude={"flex_form_data", "location","inspector","mill","children_specs","tolerance"},
    )
    for field, field_value in update_data.items():
        setattr(spec, field, field_value)

    spec.inspector = inspectors
    spec.children_specs = children_specs
    spec.flex_form_data = spec_in.flex_form_data
    db_session.add(spec)
    db_session.commit()
    return spec

def update_new(*,db_session,spec: Spec, spec_in:dict) -> Spec:
    for field, field_value in spec_in.items():
        setattr(spec, field, field_value)

    db_session.add(spec)
    db_session.commit()
    return spec



def delete(*, db_session, spec_id: int):
    spec = db_session.query(Spec).filter(Spec.id == spec_id).one_or_none()
    
    if spec:
        spec.is_deleted = 1
    db_session.add(spec)
    db_session.commit()

    return spec


def get_by_code_short_full(*, db_session, search_dict: SpecByCode):
    spec = db_session.query(Spec).filter(
        or_(
            Spec.spec_code.like(f'%{search_dict.code}%'),
            Spec.short_name.like(f'%{search_dict.code}%'),
            Spec.full_name.like(f'%{search_dict.code}%')
        )
    )

    query, pagination = apply_pagination(spec, page_number=search_dict.page, page_size=search_dict.itemsPerPage)
    
    return {
        "items": query.all(),
        "itemsPerPage": pagination.page_size,
        "page": pagination.page_number,
        "total": pagination.total_results,

    }

def spec_version_update(*, db_session, spec:Spec):

    try:
        r_spec = db_session.query(Spec).filter(Spec.id != spec.id, 
                                                Spec.spec_code ==spec.spec_code, 
                                                Spec.version_status == 'R').first()
        if r_spec:

            # 将目前为R的spec数据拷贝
            temp_r_spec = SpecUpdate(**r_spec.__dict__).model_dump(
                        exclude={"id", "spec_code","version_status","archive_date"},
                    )
            temp_r_spec_version = r_spec.version
            
            temp_r_spec['version_status'] = "A"
            temp_r_spec['archive_date'] = datetime.now(timezone.utc)

            # 拷贝当前为D的spec数据
            temp_d_spec = SpecUpdate(**spec.__dict__).model_dump(
                        exclude={"id", "spec_code","version_status","release_date","archive_date"},
                    )
            temp_d_spec_version = spec.version
            temp_d_spec['release_date'] = datetime.now(timezone.utc)

            # 将当前为D的version置空，防止报唯一约束错误
            spec.version = None
            db_session.commit()


            for d_field, d_field_value in temp_d_spec.items():
                setattr(r_spec, d_field, d_field_value)

            for r_field, r_field_value in temp_r_spec.items():
                setattr(spec, r_field, r_field_value)
            spec.version = temp_r_spec_version

            db_session.commit()

        else:
            spec.version_status = "R"
            spec.release_date = datetime.now(timezone.utc)
            db_session.commit()
            return spec
    except Exception as e:
        db_session.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    return r_spec


def get_all_data_start_with_s(*, db_session,spec_id) -> List[Optional[Spec]]:
    # 查spec_code S开头的数据 并且 test_type_flag test_sub_type 不为空 或不为 "" 或不为 None
    query =  db_session.query(Spec).filter(func.like(Spec.spec_code, 'S%')).filter(not_(Spec.test_type_flag.is_(None))).filter(not_(Spec.test_sub_type.is_(None))).filter(not_(Spec.test_type_flag == "")).filter(not_(Spec.test_sub_type== ""))

    if not spec_id:
        result = query.all()
    else:
        result = query.filter(Spec.id== spec_id).all()
    return result


def get_all_data_start_with_s_dict(*, db_session, spec_id):
    result = get_all_data_start_with_s(db_session=db_session, spec_id=spec_id)
    result_dict = {spec.id: spec for spec in result}
    return result_dict


def archive_spec_version_update(*, db_session, spec:Spec):
    try:
        spec.version_status = "A"
        spec.archive_date = datetime.now(timezone.utc)

        cast_spec = db_session.query(CastSpec).filter(CastSpec.spec_id == spec.id).delete()

        db_session.commit()
    except Exception as e:
        db_session.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    return spec

def get_xspe_spec_data(*, db_session, spec_code):
        query = (
            db_session.query(Spec, SpOtherTest, SpVarious, Spmainel, SpmainelOtherElement)
            .join(SpOtherTest, Spec.id == SpOtherTest.spec_id, isouter=True)
            .join(SpVarious, Spec.id == SpVarious.spec_id, isouter=True).join(Spmainel, Spec.id == Spmainel.spec_id, isouter=True).join(SpmainelOtherElement, Spmainel.id == SpmainelOtherElement.spmainel_id, isouter=True)
            .filter(Spec.spec_code == spec_code)
        )
        results = query.all()
        if not results:
            raise ValueError(f"No data found for spec_code: {spec_code}")

        sp_other_tests = [row[1] for row in results if row[1] is not None]
        sp_various = [row[2] for row in results if row[2] is not None]
        spmainel = [row[3] for row in results if row[3] is not None]
        spmainel_oe = [row[4] for row in results if row[4] is not None]

        return sp_other_tests, sp_various, spmainel, spmainel_oe