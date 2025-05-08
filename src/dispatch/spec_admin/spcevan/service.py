
from typing import List, Optional
from fastapi import HTTPException
from dispatch.mill.models import Mill
from dispatch.spec_admin.spec.models import Spec
from .models import Spcevan, SpcevanCreate, SpcevanUpdate, SpcevanCreate, SpcevanBySpecCode, SpcevanCopyToCode
from sqlalchemy_filters import apply_pagination
from sqlalchemy.exc import IntegrityError


def get_filter_by_spec_ids(*, db_session,spec_id: List[int]) -> List[Optional[Spcevan]]:
    """Returns all spmainels."""
    return db_session.query(Spcevan).filter(Spcevan.spec_id.in_(spec_id)).all()

def get(*, db_session, id: int) -> Optional[Spcevan]:
    """Returns an spcevan given an spcevan id."""
    return db_session.query(Spcevan).filter(Spcevan.id == id).one_or_none()


def get_by_code(*, db_session, code: str) -> Optional[Spcevan]:
    """Returns an spcevan given an spcevan code address."""
    return db_session.query(Spcevan).filter(Spcevan.code == code).one_or_none()


def get_default_spcevan(*, db_session ) -> Optional[Spcevan]:
    """Returns an spcevan given an spcevan code address."""
    return db_session.query(Spcevan).first()


def get_all(*, db_session) -> List[Optional[Spcevan]]:
    """Returns all spcevans."""
    return db_session.query(Spcevan)






def create(*, db_session, spcevan_in: SpcevanCreate) -> Spcevan:
    """Creates an spcevan."""
    
    spec = None
    mill = None
    if spcevan_in.spec_id:
        spec = db_session.query(Spec).filter(Spec.id == spcevan_in.spec_id).one_or_none()

    if spcevan_in.mill_id:
        mill = db_session.query(Mill).filter(Mill.id == spcevan_in.mill_id).one_or_none()

    contact = Spcevan(**spcevan_in.dict(exclude={"flex_form_data", "spec", "mill"}),
                    mill=mill,
                    spec=spec,
                    flex_form_data=spcevan_in.flex_form_data)
    
    db_session.add(contact)
    db_session.commit()
    return contact


def update(
    *,
    db_session,
    spcevan: Spcevan,
    spcevan_in: SpcevanUpdate,
) -> Spcevan:
    
    if spcevan_in.mill_id:
        spcevan.mill = db_session.query(Mill).filter(Mill.id == spcevan_in.mill_id).one_or_none()


    update_data = spcevan_in.dict(
        exclude={"flex_form_data", "location", "spec", "mill"},
    )
    for field, field_value in update_data.items():
        setattr(spcevan, field, field_value)

    spcevan.flex_form_data = spcevan_in.flex_form_data
    db_session.add(spcevan)
    db_session.commit()
    return spcevan

def update_new(*,db_session,spcevan: Spcevan, spcevan_in:dict) -> Spcevan:
    for field, field_value in spcevan_in.items():
        setattr(spcevan, field, field_value)

    db_session.add(spcevan)
    db_session.commit()
    return spcevan


def delete(*, db_session, spcevan_id: int):
    spcevan = db_session.query(Spcevan).filter(Spcevan.id == spcevan_id).one_or_none()
    
    if spcevan:
        spcevan.is_deleted = 1
    db_session.add(spcevan)
    db_session.commit()

    return spcevan


def get_by_spec_code(*, db_session, search_dict:SpcevanBySpecCode):

    spcevan = db_session.query(Spcevan).join(Spec).filter(Spec.spec_code==search_dict.spec_code)

    if not spcevan:
        raise HTTPException(status_code=400, detail="The spcevan with this id does not exist.")

    query, pagination = apply_pagination(spcevan, page_number=search_dict.page, page_size=search_dict.itemsPerPage)
    
    return {
        "items": query.all(),
        "itemsPerPage": pagination.page_size,
        "page": pagination.page_number,
        "total": pagination.total_results,

    }


def create_by_copy_spec_code(*, db_session, copy_dict: SpcevanCopyToCode,current_user):
    # 通过复制前的spec_code 查询数据
    copy_before_values = db_session.query(Spcevan).join(Spec).filter(Spec.spec_code==copy_dict.before_code).all()

    if not copy_before_values:
        raise HTTPException(status_code=400, detail="The spcevan with this spec_code does not exist.") 

    # 查询copy to 的spec记录
    copy_to_spec = db_session.query(Spec).filter(Spec.spec_code == copy_dict.after_code).order_by(Spec.id.desc()).first()

    if not copy_to_spec:
        raise HTTPException(status_code=400, detail="The spcevan with this spec_code does not exist.") 

    after_list = []
    try:
        for cbv in copy_before_values:

            is_cunzai = db_session.query(Spcevan).filter(Spcevan.spec_id == copy_to_spec.id, 
                                                            Spcevan.thick_from == cbv.thick_from,
                                                            Spcevan.thick_to == cbv.thick_to).first()
                
            if is_cunzai:
                continue
            
            cbv_value = SpcevanCreate(**cbv.__dict__)
            cbv_value.created_by = current_user.email
            after_list.append(Spcevan(**cbv_value.dict(exclude={"flex_form_data", "spec", "mill"}), spec=copy_to_spec, mill=cbv.mill))

        if len(after_list) > 0:
            db_session.add_all(after_list)
            db_session.commit()
        else:
            raise HTTPException(status_code=400, detail="There are no replicable objects.") 

    except IntegrityError:
        db_session.rollback()
        raise HTTPException(status_code=400, detail="Insertion failed, the same record already exists.")


    return True
    