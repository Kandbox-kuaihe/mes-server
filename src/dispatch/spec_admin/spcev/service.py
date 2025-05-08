from typing import List, Optional
from fastapi import HTTPException
from dispatch.mill.models import Mill
from dispatch.spec_admin.spec.models import Spec
from .models import Spcev, SpcevCreate, SpcevUpdate, SpcevBySpecCode, SpcevCopyToCode
from sqlalchemy_filters import apply_pagination
from sqlalchemy.exc import IntegrityError



def get_filter_by_spec_ids(*, db_session,spec_id: List[int]) -> List[Optional[Spcev]]:
    """Returns all spmainels."""
    return db_session.query(Spcev).filter(Spcev.spec_id.in_(spec_id)).all()


def get(*, db_session, id: int) -> Optional[Spcev]:
    """Returns an spcev given an spcev id."""
    return db_session.query(Spcev).filter(Spcev.id == id).one_or_none()


def get_by_code(*, db_session, code: str) -> Optional[Spcev]:
    """Returns an spcev given an spcev code address."""
    return db_session.query(Spcev).filter(Spcev.code == code).one_or_none()


def get_default_spcev(*, db_session ) -> Optional[Spcev]:
    """Returns an spcev given an spcev code address."""
    return db_session.query(Spcev).first()


def get_all(*, db_session) -> List[Optional[Spcev]]:
    """Returns all spcevs."""
    return db_session.query(Spcev)


def create(*, db_session, spcev_in: SpcevCreate) -> Spcev:
    """Creates an spcev."""

    spec = None
    mill = None
    if spcev_in.spec_id:
        spec = db_session.query(Spec).filter(Spec.id == spcev_in.spec_id).one_or_none()

    if spcev_in.mill_id:
        mill = db_session.query(Mill).filter(Mill.id == spcev_in.mill_id).one_or_none()

    contact = Spcev(**spcev_in.dict(exclude={"flex_form_data", "spec", "mill"}),
                    mill=mill,
                    spec=spec,
                    flex_form_data=spcev_in.flex_form_data)

    db_session.add(contact)
    db_session.commit()
    return contact


def update(
    *,
    db_session,
    spcev: Spcev,
    spcev_in: SpcevUpdate,
) -> Spcev:
    
    if spcev_in.mill_id:
        spcev.mill = db_session.query(Mill).filter(Mill.id == spcev_in.mill_id).one_or_none()

    update_data = spcev_in.dict(
        exclude={"flex_form_data", "spec", "mill"},
    )
    for field, field_value in update_data.items():
        setattr(spcev, field, field_value)

    spcev.flex_form_data = spcev_in.flex_form_data
    db_session.add(spcev)
    db_session.commit()
    return spcev


def update_new(*,db_session,spcev: Spcev, spcev_in:dict) -> Spcev:
    for field, field_value in spcev_in.items():
        setattr(spcev, field, field_value)

    db_session.add(spcev)
    db_session.commit()
    return spcev

def delete(*, db_session, id: int):
    spcev = db_session.query(Spcev).filter(Spcev.id == id).one_or_none()

    if spcev:
        spcev.is_deleted = 1
    db_session.add(spcev)
    db_session.commit()

    return spcev


def get_by_spec_code(*, db_session, search_dict:SpcevBySpecCode):

    spcev = db_session.query(Spcev).join(Spec).filter(Spec.spec_code==search_dict.spec_code)

    if not spcev:
        raise HTTPException(status_code=400, detail="The spcev with this id does not exist.")

    query, pagination = apply_pagination(spcev, page_number=search_dict.page, page_size=search_dict.itemsPerPage)

    return {
        "items": query.all(),
        "itemsPerPage": pagination.page_size,
        "page": pagination.page_number,
        "total": pagination.total_results,

    }


def create_by_copy_spec_code(*, db_session, copy_dict: SpcevCopyToCode,current_user):
    # 通过复制前的spec_code 查询数据
    copy_before_values = db_session.query(Spcev).join(Spec).filter(Spec.spec_code==copy_dict.before_code).all()

    if not copy_before_values:
        raise HTTPException(status_code=400, detail="The spcev with this spec_code does not exist.") 

    # 查询copy to 的spec记录
    copy_to_spec = db_session.query(Spec).filter(Spec.spec_code == copy_dict.after_code).order_by(Spec.id.desc()).first()

    if not copy_to_spec:
        raise HTTPException(status_code=400, detail="The spcev with this spec_code does not exist.") 

    after_list = []
    try:
        for cbv in copy_before_values:

            is_cunzai = db_session.query(Spcev).filter(Spcev.spec_id == copy_to_spec.id, 
                                                       Spcev.cev_value == cbv.cev_value).first()
                
            if is_cunzai:
                continue
            
            cbv_value = SpcevCreate(**cbv.__dict__)
            cbv_value.created_by = current_user.email
            after_list.append(Spcev(**cbv_value.dict(exclude={"flex_form_data", "spec", "mill"}), spec=copy_to_spec, mill=cbv.mill))

        if len(after_list) > 0:
            db_session.add_all(after_list)
            db_session.commit()
        else:
            raise HTTPException(status_code=400, detail="There are no replicable objects.") 

    except IntegrityError:
        db_session.rollback()
        raise HTTPException(status_code=400, detail="Insertion failed, the same record already exists.")

    return True
    