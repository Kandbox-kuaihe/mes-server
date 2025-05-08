
from typing import List, Optional
from fastapi import HTTPException, Depends
from dispatch.mill.models import Mill
from dispatch.spec_admin.spec.models import Spec
from .models import Spimpact as SpImpact
from .models import SpImpactCreate, SpImpactUpdate, SpImpactCreate, SpImapctBySpecCode, SpImpactCopyToCode, SpImpactBaseResponse, Spimpact
from sqlalchemy_filters import apply_pagination
from dispatch.system_admin.auth.service import get_current_user
from dispatch.system_admin.auth.models import DispatchUser
from sqlalchemy.exc import IntegrityError
from sqlalchemy import inspect


def get(*, db_session, id: int) -> Optional[SpImpact]:
    """Returns an spImpact given an spImpact id."""
    return db_session.query(SpImpact).filter(SpImpact.id == id).one_or_none()

def get_by_spec_id(*, db_session, spec_id:int)-> List[SpImpact]:
    return db_session.query(SpImpact).filter(SpImpact.spec_id==spec_id).all()

def get_one_spec_id(*, db_session, spec_id:int)-> Optional[SpImpact]:
    return db_session.query(SpImpact).filter(SpImpact.spec_id==spec_id).first()

def get_by_code(*, db_session, code: str) -> Optional[SpImpact]:
    """Returns an spImpact given an spImpact code address."""
    return db_session.query(SpImpact).filter(SpImpact.code == code).one_or_none()


def get_default_spImpact(*, db_session ) -> Optional[SpImpact]:
    """Returns an spImpact given an spImpact code address."""
    return db_session.query(SpImpact).first()

def get_spimpact_by_spec_id_and_flange_thickness(*, db_session, spec_id: int, flange_thickness: float, mill_id:int=None) -> Optional[SpImpact]:
    if not spec_id or not flange_thickness:
        return None
    query = db_session.query(SpImpact).filter(
        SpImpact.spec_id == spec_id,
        SpImpact.thick_from <= flange_thickness, SpImpact.thick_to >= flange_thickness)
    if mill_id:
        query = query.filter(SpImpact.mill_id == mill_id)
    return query.first()


def get_all_spimpact_by_spec_id_and_flange_thickness(*, db_session, spec_id: int, flange_thickness: float, mill_id:int) -> List[Optional[SpImpact]]:
    if not spec_id or not flange_thickness:
        return []
    return db_session.query(SpImpact).filter(
        SpImpact.spec_id == spec_id,
        SpImpact.mill_id == mill_id,
        SpImpact.thick_from <= flange_thickness, SpImpact.thick_to >= flange_thickness).all()


def get_all(*, db_session) -> List[SpImpact]:
    """Returns all spImpacts."""
    return db_session.query(SpImpact)


def validate_field_lengths(data: dict, model):
    """验证字段长度"""
    mapper = inspect(model)
    errors = []
    for column in mapper.columns:
        field_name = column.name
        max_length = getattr(column.type, "length", None)
        if max_length is not None:
            value = data.get(field_name)
            if value and len(value) > max_length:
                errors.append(f"Field '{field_name}' exceeds maximum length of {max_length} characters.")
    if errors:
        raise HTTPException(status_code=400, detail=errors)


def create(*, db_session, spImpact_in: SpImpactCreate) -> SpImpact:
    """Creates an spImpact."""
    
    spec = None
    mill = None
    if spImpact_in.spec_id:
        spec = db_session.query(Spec).filter(Spec.id == spImpact_in.spec_id).one_or_none()

    if spImpact_in.mill_id:
        mill = db_session.query(Mill).filter(Mill.id == spImpact_in.mill_id).one_or_none()
    
    validate_field_lengths(spImpact_in.dict(), SpImpact)

    contact = SpImpact(**spImpact_in.dict(exclude={"flex_form_data", "spec", "mill"}),
                    spec=spec,
                    mill=mill,
                    flex_form_data=spImpact_in.flex_form_data)
    
    db_session.add(contact)
    db_session.commit()
    return contact


def update(
    *,
    db_session,
    spImpact: SpImpact,
    spImpact_in: SpImpactUpdate,
) -> SpImpact:
    
    if spImpact_in.mill_id:
        spImpact.mill = db_session.query(Mill).filter(Mill.id == spImpact_in.mill_id).one_or_none()


    update_data = spImpact_in.dict(
        exclude={"flex_form_data", "location", "spec", "mill"},
    )
    for field, field_value in update_data.items():
        setattr(spImpact, field, field_value)

    spImpact.flex_form_data = spImpact_in.flex_form_data
    db_session.add(spImpact)
    db_session.commit()
    return spImpact

def update_new(*,db_session,spImpact: SpImpact, spImpact_in:dict) -> SpImpact:
    for field, field_value in spImpact_in.items():
        setattr(spImpact, field, field_value)

    db_session.add(spImpact)
    db_session.commit()
    return spImpact



def delete(*, db_session, spImpact_id: int):
    spImpact = db_session.query(SpImpact).filter(SpImpact.id == spImpact_id).one_or_none()
    
    if spImpact:
        spImpact.is_deleted = 1
    db_session.add(spImpact)
    db_session.commit()

    return spImpact



def get_by_spec_code(*, db_session, search_dict:SpImapctBySpecCode):

    spimpact = db_session.query(SpImpact).join(Spec).filter(Spec.spec_code==search_dict.spec_code)

    if not spimpact:
        raise HTTPException(status_code=400, detail="The spimpact with this id does not exist.")

    query, pagination = apply_pagination(spimpact, page_number=search_dict.page, page_size=search_dict.itemsPerPage)
    
    return {
        "items": query.all(),
        "itemsPerPage": pagination.page_size,
        "page": pagination.page_number,
        "total": pagination.total_results,

    }

def create_by_copy_spec_code(*, db_session, copy_dict: SpImpactCopyToCode,current_user):
    # 通过复制前的spec_code 查询数据
    copy_before_values = db_session.query(SpImpact).join(Spec).filter(Spec.spec_code==copy_dict.before_code).all()

    if not copy_before_values:
        raise HTTPException(status_code=400, detail="The spimpact with this spec_code does not exist.") 

    # 查询copy to 的spec记录
    copy_to_spec = db_session.query(Spec).filter(Spec.spec_code == copy_dict.after_code).order_by(Spec.id.desc()).first()

    if not copy_to_spec:
        raise HTTPException(status_code=400, detail="The spimpact with this spec_code does not exist.") 

    after_list = []
    try:
        for cbv in copy_before_values:

            is_cunzai = db_session.query(SpImpact).filter(SpImpact.spec_id == copy_to_spec.id, 
                                                          SpImpact.thick_from == cbv.thick_from,
                                                          SpImpact.thick_to == cbv.thick_to).first()
            
            if is_cunzai:
                continue

            cbv_value = SpImpactCreate(**cbv.__dict__)
            cbv_value.created_by = current_user.email
            after_list.append(SpImpact(**cbv_value.dict(exclude={"flex_form_data", "spec", "mill"}), spec=copy_to_spec,mill=cbv.mill))

    
        if len(after_list) > 0:
            db_session.add_all(after_list)
            db_session.commit()
        else:
            raise HTTPException(status_code=400, detail="There are no replicable objects.") 


    except IntegrityError:
        db_session.rollback()
        raise HTTPException(status_code=400, detail="Insertion failed, the same record already exists.")

    return True


def get_all_data(*, db_session) -> List[Optional[SpImpact]]:
    return db_session.query(SpImpact).all()


def get_all_data_dict_of_spec_id(*, db_session) -> dict:
    data = get_all_data(db_session=db_session)
    dic = {}
    for d in data:
        if d.spec_id not in dic:
            dic[d.spec_id] = []
        dic[d.spec_id].append(d)
    return dic








