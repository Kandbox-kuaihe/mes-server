
from typing import List, Optional

from dispatch.mill.models import Mill
from .models import Sptensil, SptensilCreate, SptensilUpdate, SptensilCreate, SptensilBySpecCode, SptensilCopyToCode
from dispatch.spec_admin.spec.models import Spec
from fastapi import HTTPException
from sqlalchemy_filters import apply_pagination
from sqlalchemy.exc import IntegrityError

def get(*, db_session, id: int) -> Optional[Sptensil]:
    """Returns an sptensil given an sptensil id."""
    return db_session.query(Sptensil).filter(Sptensil.id == id).one_or_none()


def get_by_spec_id(*, db_session, spec_id: int) ->List[Sptensil]:
    return db_session.query(Sptensil).filter(
        Sptensil.spec_id == spec_id).all()

def get_sptensil_by_spec_id_and_flange_thickness(*, db_session, spec_id: int, flange_thickness: float) -> Optional[Sptensil]:
    if not spec_id or not flange_thickness:
        return None
    return db_session.query(Sptensil).filter(
        Sptensil.spec_id == spec_id,
        Sptensil.thick_from <= flange_thickness, Sptensil.thick_to >= flange_thickness).first()

def get_by_code(*, db_session, code: str) -> Optional[Sptensil]:
    """Returns an sptensil given an sptensil code address."""
    return db_session.query(Sptensil).filter(Sptensil.code == code).one_or_none()

def get_one_spec_id(*, db_session, spec_id: str) -> Optional[Sptensil]:
    """Returns an sptensil given a spec id."""
    return db_session.query(Sptensil).filter(Sptensil.spec_id == spec_id).first()


def get_default_sptensil(*, db_session ) -> Optional[Sptensil]:
    """Returns an sptensil given an sptensil code address."""
    return db_session.query(Sptensil).first()


def get_all(*, db_session) -> List[Sptensil]:
    """Returns all sptensils."""
    return db_session.query(Sptensil)


def create(*, db_session, sptensil_in: SptensilCreate) -> Sptensil:
    """Creates an sptensil."""
    
    spec = None
    mill = None
    if sptensil_in.spec_id:
        spec = db_session.query(Spec).filter(Spec.id == sptensil_in.spec_id).one_or_none()

    if sptensil_in.mill_id:
        mill = db_session.query(Mill).filter(Mill.id == sptensil_in.mill_id).one_or_none()
    

    contact = Sptensil(**sptensil_in.dict(exclude={"flex_form_data", "spec", "mill"}),
                    mill=mill,
                    spec=spec,
                    flex_form_data=sptensil_in.flex_form_data)
    
    db_session.add(contact)
    db_session.commit()
    return contact


def update(
    *,
    db_session,
    sptensil: Sptensil,
    sptensil_in: SptensilUpdate,
) -> Sptensil:
    
    if sptensil_in.mill_id:
        sptensil.mill = db_session.query(Mill).filter(Mill.id == sptensil_in.mill_id).one_or_none()


    update_data = sptensil_in.dict(
        exclude={"flex_form_data", "spec", "mill"},
    )
    for field, field_value in update_data.items():
        setattr(sptensil, field, field_value)

    sptensil.flex_form_data = sptensil_in.flex_form_data
    db_session.add(sptensil)
    db_session.commit()
    return sptensil


def update_new(*,db_session,spTensil: Sptensil, spTensil_in:dict) -> Sptensil:
    for field, field_value in spTensil_in.items():
        setattr(spTensil, field, field_value)

    db_session.add(spTensil)
    db_session.commit()
    return spTensil


def delete(*, db_session, id: int):
    sptensil = db_session.query(Sptensil).filter(Sptensil.id == id).one_or_none()
    
    if sptensil:
        sptensil.is_deleted = 1
    db_session.add(sptensil)
    db_session.commit()

    return sptensil


def get_by_spec_code(*, db_session, search_dict:SptensilBySpecCode):

    sptensil = db_session.query(Sptensil).join(Spec).filter(Spec.spec_code==search_dict.spec_code)

    if not sptensil:
        raise HTTPException(status_code=400, detail="The sptensil with this id does not exist.")

    query, pagination = apply_pagination(sptensil, page_number=search_dict.page, page_size=search_dict.itemsPerPage)
    
    return {
        "items": query.all(),
        "itemsPerPage": pagination.page_size,
        "page": pagination.page_number,
        "total": pagination.total_results,

    }


def create_by_copy_spec_code(*, db_session, copy_dict: SptensilCopyToCode, current_user):
    # 通过复制前的spec_code 查询数据
    copy_before_values = db_session.query(Sptensil).join(Spec).filter(Spec.spec_code==copy_dict.before_code).all()

    if not copy_before_values:
        raise HTTPException(status_code=400, detail="The spensil with this spec_code does not exist.") 

    # 查询copy to 的spec记录
    copy_to_spec = db_session.query(Spec).filter(Spec.spec_code == copy_dict.after_code).order_by(Spec.id.desc()).first()

    if not copy_to_spec:
        raise HTTPException(status_code=400, detail="The spensil with this spec_code does not exist.") 

    after_list = []
    try:
        for cbv in copy_before_values:

            is_cunzai = db_session.query(Sptensil).filter(Sptensil.spec_id == copy_to_spec.id, 
                                                          Sptensil.thick_from == cbv.thick_from,
                                                          Sptensil.thick_to == cbv.thick_to).first()
            
            if is_cunzai:
                continue

            cbv_value = SptensilCreate(**cbv.__dict__)
            cbv_value.created_by = current_user.email
            after_list.append(Sptensil(**cbv_value.dict(exclude={"flex_form_data", "spec", "mill"}), spec=copy_to_spec, mill=cbv.mill))

        if len(after_list) > 0:
            db_session.add_all(after_list)
            db_session.commit()
        else:
            raise HTTPException(status_code=400, detail="There are no replicable objects.") 

    except IntegrityError:
        db_session.rollback()
        raise HTTPException(status_code=400, detail="Insertion failed, the same record already exists.")

    return True


def get_all_data(*, db_session) -> List[Optional[Sptensil]]:
    """Returns all sptensils."""
    return db_session.query(Sptensil).all()


def get_all_data_dict_of_spec_id(*, db_session) -> dict:
    """Returns all sptensils."""

    data = get_all_data(db_session=db_session)

    dic = {}

    for d in data:
        if d.spec_id not in dic:
            dic[d.spec_id] = []
        dic[d.spec_id].append(d)

    return dic
