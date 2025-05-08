
from typing import List, Optional
from fastapi import HTTPException
from dispatch.mill.models import Mill
from dispatch.spec_admin.spec.models import Spec
from .models import Sptcert, SptcertCreate, SptcertUpdate, SptcertCreate, SptcertBySpecCode, SptcertCopyToCode
from sqlalchemy_filters import apply_pagination
from sqlalchemy.exc import IntegrityError


def get_filter_by_spec_ids(*, db_session,spec_id: List[int]) -> List[Optional[Sptcert]]:
    """Returns all spmainels."""
    return db_session.query(Sptcert).filter(Sptcert.spec_id.in_(spec_id)).all()


def get(*, db_session, id: int) -> Optional[Sptcert]:
    """Returns an sptert given an sptert id."""
    return db_session.query(Sptcert).filter(Sptcert.id == id).one_or_none()


def get_by_code(*, db_session, code: str) -> Optional[Sptcert]:
    """Returns an sptert given an sptert code address."""
    return db_session.query(Sptcert).filter(Sptcert.code == code).one_or_none()


def get_default_sptert(*, db_session ) -> Optional[Sptcert]:
    """Returns an sptert given an sptert code address."""
    return db_session.query(Sptcert).first()


def get_all(*, db_session) -> List[Optional[Sptcert]]:
    """Returns all spterts."""
    return db_session.query(Sptcert)


def create(*, db_session, sptcert_in: SptcertCreate) -> Sptcert:
    """Creates an sptert."""
    
    spec = None
    mill = None
    if sptcert_in.spec_id:
        spec = db_session.query(Spec).filter(Spec.id == sptcert_in.spec_id).one_or_none()

    if sptcert_in.mill_id:
        mill = db_session.query(Mill).filter(Mill.id == sptcert_in.mill_id).one_or_none()
    

    contact = Sptcert(**sptcert_in.dict(exclude={"flex_form_data", "spec", "mill"}),
                    mill=mill,
                    spec=spec,
                    flex_form_data=sptcert_in.flex_form_data)
    
    db_session.add(contact)
    db_session.commit()
    return contact


def update(
    *,
    db_session,
    sptcert: Sptcert,
    sptcert_in: SptcertUpdate,
) -> Sptcert:
    
    if sptcert_in.mill_id:
        sptcert.mill = db_session.query(Mill).filter(Mill.id == sptcert_in.mill_id).one_or_none()

    update_data = sptcert_in.dict(
        exclude={"flex_form_data","spec", "mill"},
    )
    for field, field_value in update_data.items():
        setattr(sptcert, field, field_value)

    sptcert.flex_form_data = sptcert_in.flex_form_data
    db_session.add(sptcert)
    db_session.commit()
    return sptcert


def update_new(*,db_session,sptcert: Sptcert, sptcert_in:dict) -> Sptcert:
    for field, field_value in sptcert_in.items():
        setattr(sptcert, field, field_value)

    db_session.add(sptcert)
    db_session.commit()
    return sptcert

def delete(*, db_session, id: int):
    sptert = db_session.query(Sptcert).filter(Sptcert.id == id).one_or_none()
    
    if sptert:
        sptert.is_deleted = 1
    db_session.add(sptert)
    db_session.commit()

    return sptert


def get_by_spec_code(*, db_session, search_dict:SptcertBySpecCode):

    sptcert = db_session.query(Sptcert).join(Spec).filter(Spec.spec_code==search_dict.spec_code)

    if not sptcert:
        raise HTTPException(status_code=400, detail="The sptcert with this id does not exist.")

    query, pagination = apply_pagination(sptcert, page_number=search_dict.page, page_size=search_dict.itemsPerPage)
    
    return {
        "items": query.all(),
        "itemsPerPage": pagination.page_size,
        "page": pagination.page_number,
        "total": pagination.total_results,

    }



def create_by_copy_spec_code(*, db_session, copy_dict: SptcertCopyToCode,current_user):
    # 通过复制前的spec_code 查询数据
    copy_before_values = db_session.query(Sptcert).join(Spec).filter(Spec.spec_code==copy_dict.before_code).all()

    if not copy_before_values:
        raise HTTPException(status_code=400, detail="The sptcert with this spec_code does not exist.") 

    # 查询copy to 的spec记录
    copy_to_spec = db_session.query(Spec).filter(Spec.spec_code == copy_dict.after_code).order_by(Spec.id.desc()).first()

    if not copy_to_spec:
        raise HTTPException(status_code=400, detail="The sptcert with this spec_code does not exist.") 

    after_list = []
    try:
        for cbv in copy_before_values:

            is_cunzai = db_session.query(Sptcert).filter(Sptcert.spec_id == copy_to_spec.id, 
                                                            Sptcert.thick_from == cbv.thick_from,
                                                            Sptcert.thick_to == cbv.thick_to).first()
                
            if is_cunzai:
                continue
            
            cbv_value = SptcertCreate(**cbv.__dict__)
            cbv_value.created_by = current_user.email
            after_list.append(Sptcert(**cbv_value.dict(exclude={"flex_form_data", "spec", "mill"}), spec=copy_to_spec, mill=cbv.mill))

        if len(after_list) > 0:
            db_session.add_all(after_list)
            db_session.commit()
        else:
            raise HTTPException(status_code=400, detail="There are no replicable objects.") 

    except IntegrityError:
        db_session.rollback()
        raise HTTPException(status_code=400, detail="Insertion failed, the same record already exists.")


    return True
    