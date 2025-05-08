
from typing import List, Optional
from fastapi import HTTPException
from dispatch.mill.models import Mill
from dispatch.spec_admin.spec.models import Spec
from .models import Spjominy as SpecJominy
from .models import SpecJominyCreate, SpecJominyUpdate, SpecJominyCreate, SpecJominyBySpecCode, SpecJominyCopyToCode
from sqlalchemy_filters import apply_pagination
from sqlalchemy.exc import IntegrityError

def get(*, db_session, id: int) -> Optional[SpecJominy]:
    """Returns an spjominy given an spjominy id."""
    return db_session.query(SpecJominy).filter(SpecJominy.id == id).one_or_none()


def get_by_code(*, db_session, code: str) -> Optional[SpecJominy]:
    """Returns an spjominy given an spjominy code address."""
    return db_session.query(SpecJominy).filter(SpecJominy.code == code).one_or_none()


def get_default_spjominy(*, db_session ) -> Optional[SpecJominy]:
    """Returns an spjominy given an spjominy code address."""
    return db_session.query(SpecJominy).first()


def get_all(*, db_session) -> List[Optional[SpecJominy]]:
    """Returns all spjominys."""
    return db_session.query(SpecJominy)






def create(*, db_session, spjominy_in: SpecJominyCreate) -> SpecJominy:
    """Creates an spjominy."""
    
    spec = None
    mill = None
    if spjominy_in.spec_id:
        spec = db_session.query(Spec).filter(Spec.id == spjominy_in.spec_id).one_or_none()

    if spjominy_in.mill_id:
        mill = db_session.query(Mill).filter(Mill.id == spjominy_in.mill_id).one_or_none()

    contact = SpecJominy(**spjominy_in.dict(exclude={"flex_form_data", "spec", "mill"}),
                        mill=mill,
                        spec=spec,
                        flex_form_data=spjominy_in.flex_form_data)
    
    db_session.add(contact)
    db_session.commit()
    return contact


def update(
    *,
    db_session,
    spjominy: SpecJominy,
    spjominy_in: SpecJominyUpdate,
) -> SpecJominy:
    
    if spjominy_in.mill_id:
        spjominy.mill = db_session.query(Mill).filter(Mill.id == spjominy_in.mill_id).one_or_none()

    update_data = spjominy_in.dict(
        exclude={"flex_form_data", "location", "spec", "mill"},
    )
    for field, field_value in update_data.items():
        setattr(spjominy, field, field_value)

    spjominy.flex_form_data = spjominy_in.flex_form_data
    db_session.add(spjominy)
    db_session.commit()
    return spjominy


def delete(*, db_session, id: int):
    spjominy = db_session.query(SpecJominy).filter(SpecJominy.id == id).one_or_none()
    
    if spjominy:
        spjominy.is_deleted = 1
    db_session.add(spjominy)
    db_session.commit()

    return spjominy


def get_by_spec_code(*, db_session, search_dict:SpecJominyBySpecCode):

    specjominy = db_session.query(SpecJominy).join(Spec).filter(Spec.spec_code==search_dict.spec_code)

    if not specjominy:
        raise HTTPException(status_code=400, detail="The specjominy with this id does not exist.")

    query, pagination = apply_pagination(specjominy, page_number=search_dict.page, page_size=search_dict.itemsPerPage)
    
    return {
        "items": query.all(),
        "itemsPerPage": pagination.page_size,
        "page": pagination.page_number,
        "total": pagination.total_results,

    }



def create_by_copy_spec_code(*, db_session, copy_dict: SpecJominyCopyToCode,current_user):
    # 通过复制前的spec_code 查询数据
    copy_before_values = db_session.query(SpecJominy).join(Spec).filter(Spec.spec_code==copy_dict.before_code).all()

    if not copy_before_values:
        raise HTTPException(status_code=400, detail="The specjominy with this spec_code does not exist.") 

    # 查询copy to 的spec记录
    copy_to_spec = db_session.query(Spec).filter(Spec.spec_code == copy_dict.after_code).order_by(Spec.id.desc()).first()

    if not copy_to_spec:
        raise HTTPException(status_code=400, detail="The specjominy with this spec_code does not exist.") 

    after_list = []
    try:
        for cbv in copy_before_values:

            is_cunzai = db_session.query(SpecJominy).filter(SpecJominy.spec_id == copy_to_spec.id, 
                                                            SpecJominy.thick_from == cbv.thick_from,
                                                            SpecJominy.thick_to == cbv.thick_to).first()
                
            if is_cunzai:
                continue
            
            cbv_value = SpecJominyCreate(**cbv.__dict__)
            cbv_value.created_by = current_user.email
            after_list.append(SpecJominy(**cbv_value.dict(exclude={"flex_form_data", "spec", "mill"}), spec=copy_to_spec, mill=cbv.mill))

        if len(after_list) > 0:
            db_session.add_all(after_list)
            db_session.commit()
        else:
            raise HTTPException(status_code=400, detail="There are no replicable objects.") 

    except IntegrityError:
        db_session.rollback()
        raise HTTPException(status_code=400, detail="Insertion failed, the same record already exists.")

    return True
    