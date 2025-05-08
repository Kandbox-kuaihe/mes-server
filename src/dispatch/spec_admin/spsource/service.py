
from typing import List, Optional
from fastapi import HTTPException
from dispatch.mill.models import Mill
from dispatch.spec_admin.spec.models import Spec
from .models import Spsource, SpsourceCreate, SpsourceUpdate, SpsourceCreate, SpsourceBySpecCode, SpsourceCopyToCode
from sqlalchemy_filters import apply_pagination
from sqlalchemy.exc import IntegrityError


def get_filter_by_spec_ids(*, db_session,spec_id: List[int]) -> List[Optional[Spsource]]:
    """Returns all spmainels."""
    return db_session.query(Spsource).filter(Spsource.spec_id.in_(spec_id)).all()



def get(*, db_session, id: int) -> Optional[Spsource]:
    """Returns an spsource given an spsource id."""
    return db_session.query(Spsource).filter(Spsource.id == id).one_or_none()


def get_by_code(*, db_session, code: str) -> Optional[Spsource]:
    """Returns an spsource given an spsource code address."""
    return db_session.query(Spsource).filter(Spsource.code == code).one_or_none()


def get_default_spsource(*, db_session ) -> Optional[Spsource]:
    """Returns an spsource given an spsource code address."""
    return db_session.query(Spsource).first()


def get_all(*, db_session) -> List[Optional[Spsource]]:
    """Returns all spsources."""
    return db_session.query(Spsource)


def create(*, db_session, spsource_in: SpsourceCreate) -> Spsource:
    """Creates an spsource."""
    
    spec = None
    mill = None
    if spsource_in.spec_id:
        spec = db_session.query(Spec).filter(Spec.id == spsource_in.spec_id).one_or_none()

    if spsource_in.mill_id:
        mill = db_session.query(Mill).filter(Mill.id == spsource_in.mill_id).one_or_none()

    contact = Spsource(**spsource_in.dict(exclude={"flex_form_data", "spec", "mill"}),
                    mill=mill,
                    spec=spec,
                    flex_form_data=spsource_in.flex_form_data)
    
    db_session.add(contact)
    db_session.commit()
    return contact


def update(
    *,
    db_session,
    spsource: Spsource,
    spsource_in: SpsourceUpdate,
) -> Spsource:
    
    if spsource_in.mill_id:
        spsource.mill = db_session.query(Mill).filter(Mill.id == spsource_in.mill_id).one_or_none()

    update_data = spsource_in.dict(
        exclude={"flex_form_data", "spec", "mill"},
    )
    for field, field_value in update_data.items():
        setattr(spsource, field, field_value)

    spsource.flex_form_data = spsource_in.flex_form_data
    db_session.add(spsource)
    db_session.commit()
    return spsource

def update_new(*,db_session,spsource: Spsource, spsource_in:dict) -> Spsource:
    for field, field_value in spsource_in.items():
        setattr(spsource, field, field_value)

    db_session.add(spsource)
    db_session.commit()
    return spsource

def delete(*, db_session, id: int):
    spsource = db_session.query(Spsource).filter(Spsource.id == id).one_or_none()
    
    if spsource:
        spsource.is_deleted = 1
    db_session.add(spsource)
    db_session.commit()

    return spsource

def get_by_spec_code(*, db_session, search_dict:SpsourceBySpecCode):

    spsource = db_session.query(Spsource).join(Spec).filter(Spec.spec_code==search_dict.spec_code)

    if not spsource:
        raise HTTPException(status_code=400, detail="The spsource with this id does not exist.")

    query, pagination = apply_pagination(spsource, page_number=search_dict.page, page_size=search_dict.itemsPerPage)
    
    return {
        "items": query.all(),
        "itemsPerPage": pagination.page_size,
        "page": pagination.page_number,
        "total": pagination.total_results,

    }



def create_by_copy_spec_code(*, db_session, copy_dict: SpsourceCopyToCode,current_user):
    # 通过复制前的spec_code 查询数据
    copy_before_values = db_session.query(Spsource).join(Spec).filter(Spec.spec_code==copy_dict.before_code).all()

    if not copy_before_values:
        raise HTTPException(status_code=400, detail="The spsource with this spec_code does not exist.") 

    # 查询copy to 的spec记录
    copy_to_spec = db_session.query(Spec).filter(Spec.spec_code == copy_dict.after_code).order_by(Spec.id.desc()).first()

    if not copy_to_spec:
        raise HTTPException(status_code=400, detail="The spsource with this spec_code does not exist.") 

    after_list = []
    try:
        for cbv in copy_before_values:

            is_cunzai = db_session.query(Spsource).filter(Spsource.spec_id == copy_to_spec.id, 
                                                            Spsource.thick_from == cbv.thick_from,
                                                            Spsource.thick_to == cbv.thick_to).first()
                
            if is_cunzai:
                continue
            
            cbv_value = SpsourceCreate(**cbv.__dict__)
            cbv_value.created_by = current_user.email
            after_list.append(Spsource(**cbv_value.dict(exclude={"flex_form_data", "spec", "mill"}), spec=copy_to_spec, mill=cbv.mill))

        if len(after_list) > 0:
            db_session.add_all(after_list)
            db_session.commit()
        else:
            raise HTTPException(status_code=400, detail="There are no replicable objects.") 

    except IntegrityError:
        db_session.rollback()
        raise HTTPException(status_code=400, detail="Insertion failed, the same record already exists.")


    return True
    