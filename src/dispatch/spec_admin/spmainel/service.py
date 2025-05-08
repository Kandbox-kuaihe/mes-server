
from typing import List, Optional
from fastapi import HTTPException
from dispatch.mill.models import Mill
from dispatch.spec_admin.spec.models import Spec
from dispatch.spec_admin.spmainel_other_element.models import SpmainelOtherElement
from dispatch.spec_admin.spmainel_other_element.service import get_by_spmainel_id
from .models import Spmainel as SpMainEl
from .models import SpMainElCreate, SpMainElUpdate, SpMainElCreate, SpMainElBySpecCode, SpMainElCopyToCode
from sqlalchemy_filters import apply_pagination
from sqlalchemy.exc import IntegrityError

def get(*, db_session, id: int) -> Optional[SpMainEl]:
    """Returns an spmainel given an spmainel id."""
    return db_session.query(SpMainEl).filter(SpMainEl.id == id).first()


def get_by_code(*, db_session, code: str) -> Optional[SpMainEl]:
    """Returns an spmainel given an spmainel code address."""
    return db_session.query(SpMainEl).filter(SpMainEl.code == code).one_or_none()


def get_default_spmainel(*, db_session ) -> Optional[SpMainEl]:
    """Returns an spmainel given an spmainel code address."""
    return db_session.query(SpMainEl).first()


def get_all(*, db_session) -> List[SpMainEl]:
    """Returns all spmainels."""
    return db_session.query(SpMainEl)



def get_filter_by_spec_ids(*, db_session,spec_id: List[int]) -> List[Optional[SpMainEl]]:
    """Returns all spmainels."""
    return db_session.query(SpMainEl).filter(SpMainEl.spec_id.in_(spec_id))

def get_spmainel_by_spec_id_and_flange_thickness(*, db_session, spec_id: int, flange_thickness: float, mill_id:int=None) -> Optional[SpMainEl]:
    if not spec_id or not flange_thickness:
        return None
    query = db_session.query(SpMainEl).filter(
        SpMainEl.spec_id == spec_id,
        SpMainEl.thick_from <= flange_thickness, SpMainEl.thick_to >= flange_thickness)
    if mill_id:
        query = query.filter(SpMainEl.mill_id == mill_id)
    return query.first()


def get_filter_by_spec_ids_and_type(db_session,spec_id: List[int],specmainel_type: str ) -> List[Optional[SpMainEl]]:
    """Returns all spmainels."""
    return get_filter_by_spec_ids(db_session=db_session,spec_id=spec_id).filter(SpMainEl.type==specmainel_type).all()

def get_sphydrogen_by_spec_id_and_flange_thickness(*, db_session, spec_id: int, flange_thickness: float, mill_id:int) -> Optional[SpMainEl]:
    if not spec_id or not flange_thickness:
        return None
    return db_session.query(SpMainEl).filter(
        SpMainEl.spec_id == spec_id,
        SpMainEl.mill_id == mill_id,
        SpMainEl.thick_from <= flange_thickness, SpMainEl.thick_to >= flange_thickness).one_or_none()

# def create(*, db_session, spmainel_in: SpMainElCreate) -> SpMainEl:
#     """Creates an spmainel."""
#     spec = None
#     mill = None
#     if spmainel_in.spec_id:
#         spec = db_session.query(Spec).filter(Spec.id == spmainel_in.spec_id).one_or_none()

#     if spmainel_in.mill_id:
#         mill = db_session.query(Mill).filter(Mill.id == spmainel_in.mill_id).one_or_none()

#     contact = SpMainEl(**spmainel_in.dict(exclude={"flex_form_data", "spec", "mill"}),
#                     mill=mill,
#                     spec=spec,
#                     flex_form_data=spmainel_in.flex_form_data)
    
#     db_session.add(contact)
#     db_session.commit()
#     return contact

def create(*, db_session, spmainel_in: SpMainElCreate) -> SpMainEl:
    """Creates an SpMainEl with multiple child records."""

    spec = None
    mill = None
    if spmainel_in.spec_id:
        spec = db_session.query(Spec).filter(Spec.id == spmainel_in.spec_id).one_or_none()

    if spmainel_in.mill_id:
        mill = db_session.query(Mill).filter(Mill.id == spmainel_in.mill_id).one_or_none()

    main_record = SpMainEl(
        **spmainel_in.dict(exclude={"other_element", "spec", "mill", "flex_form_data"}), 
        mill=mill,
        spec=spec,
        flex_form_data=spmainel_in.flex_form_data,
    )
    db_session.add(main_record)
    db_session.flush()
    if spmainel_in.other_element:
        child_records = [
            SpmainelOtherElement(
                **detail.dict(exclude={"spmainel_id"}),
                spmainel=main_record 
            )
            for detail in spmainel_in.other_element
        ]
        db_session.add_all(child_records)

    db_session.commit()
    db_session.refresh(main_record)

    return main_record


def update(
    *,
    db_session,
    spmainel: SpMainEl,
    spmainel_in: SpMainElUpdate,
) -> SpMainEl:
    
    if spmainel_in.mill_id:
        spmainel.mill = db_session.query(Mill).filter(Mill.id == spmainel_in.mill_id).one_or_none()


    update_data = spmainel_in.dict(
        exclude={"flex_form_data", "spec", "mill"},
    )
    for field, field_value in update_data.items():
        setattr(spmainel, field, field_value)

    spmainel.flex_form_data = spmainel_in.flex_form_data
    db_session.add(spmainel)
    db_session.commit()
    return spmainel


def update_new(*,db_session,spMainel: SpMainEl, spMainel_in:dict) -> SpMainEl:
    for field, field_value in spMainel_in.items():
        setattr(spMainel, field, field_value)

    db_session.add(spMainel)
    db_session.commit()
    return spMainel


def delete(*, db_session, id: int):
    spmainel = db_session.query(SpMainEl).filter(SpMainEl.id == id).one_or_none()
    
    if spmainel:
        spmainel.is_deleted = 1
    db_session.add(spmainel)
    db_session.commit()

    return spmainel



def get_by_spec_code(*, db_session, search_dict:SpMainElBySpecCode):

    spmainel = db_session.query(SpMainEl).join(Spec).filter(Spec.spec_code==search_dict.spec_code)

    if not spmainel:
        raise HTTPException(status_code=400, detail="The spmainel with this id does not exist.")

    query, pagination = apply_pagination(spmainel, page_number=search_dict.page, page_size=search_dict.itemsPerPage)
    
    return {
        "items": query.all(),
        "itemsPerPage": pagination.page_size,
        "page": pagination.page_number,
        "total": pagination.total_results,

    }


def create_by_copy_spec_code(*, db_session, copy_dict: SpMainElCopyToCode,current_user):
    # 通过复制前的spec_code 查询数据
    copy_before_values = db_session.query(SpMainEl).join(Spec).filter(Spec.spec_code==copy_dict.before_code).all()

    if not copy_before_values:
        raise HTTPException(status_code=400, detail="The spmainel with this spec_code does not exist.") 

    # 查询copy to 的spec记录
    copy_to_spec = db_session.query(Spec).filter(Spec.spec_code == copy_dict.after_code).order_by(Spec.id.desc()).first()

    if not copy_to_spec:
        raise HTTPException(status_code=400, detail="The spmainel with this spec_code does not exist.") 

    after_list = []
    other_element_list = []
    try:
        for cbv in copy_before_values:

            is_cunzai = db_session.query(SpMainEl).filter(SpMainEl.spec_id == copy_to_spec.id, 
                                                            SpMainEl.thick_from == cbv.thick_from,
                                                            SpMainEl.thick_to == cbv.thick_to).first()
                
            if is_cunzai:
                continue

            
            cbv_value = SpMainElCreate(**cbv.__dict__)
            cbv_value.created_by = current_user.email
            cbv_value_object = SpMainEl(**cbv_value.dict(exclude={"flex_form_data", "spec", "mill","other_element"}), spec=copy_to_spec, mill=cbv.mill)

            # 处理copy  other_element
            other_elements = get_by_spmainel_id(db_session=db_session, id=cbv.id)
            if len(other_elements) > 0:
                for other_element in other_elements:
                    other_value = {
                        "code": other_element.code,
                        "min_value": other_element.min_value,
                        "max_value": other_element.max_value,
                        "precision": other_element.precision,
                        "element_abbr": other_element.element_abbr,
                        "uom": other_element.uom,
                        "created_by":current_user.email,
                        "spmainel":cbv_value_object
                    }
                    other_element_list.append(SpmainelOtherElement(**other_value))

            after_list.append(cbv_value_object)


        if len(after_list) > 0:
            db_session.add_all(after_list)
            db_session.flush()

            if len(other_element_list)>0:
                db_session.add_all(other_element_list)
            db_session.commit()
        else:
            raise HTTPException(status_code=400, detail="There are no replicable objects.") 

    except IntegrityError:
        db_session.rollback()
        raise HTTPException(status_code=400, detail="Insertion failed, the same record already exists.")

    return True



def spmain_union_other(db_session,spmainel:SpMainEl)->SpMainEl:
    other_quality = db_session.query(SpmainelOtherElement).filter(
            SpmainelOtherElement.spmainel_id == spmainel.id).all()
    
    # 拼接otherElement 供cast 页对比使用
    for oth in other_quality:
        abbr = oth.element_abbr or oth.code.lower()
        setattr(spmainel, f"precision_{abbr}", oth.precision)
        setattr(spmainel, f"main_el_min_value_{abbr}", oth.min_value)
        setattr(spmainel, f"main_el_max_value_{abbr}", oth.max_value)
    return spmainel


def get_by_spec_id(*, db_session, spec_id: int, type:Optional[str] = None) -> List[SpMainEl]:
    query =  db_session.query(SpMainEl).filter(
        SpMainEl.spec_id == spec_id)
    if type:
        query = query.filter(SpMainEl.type == type)
    return list(query.all())
