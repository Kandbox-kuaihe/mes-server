
from typing import List, Optional
from fastapi import HTTPException
from dispatch.mill.models import Mill
from dispatch.spec_admin.spec.models import Spec
from .models import Spcombel as SpComBel
from .models import SpComBelCreate, SpComBelUpdate, SpComBelCreate, SpComBelBySpecCode, SpComBelCopyToCode
from sqlalchemy_filters import apply_pagination
from sqlalchemy.exc import IntegrityError

def get(*, db_session, id: int) -> Optional[SpComBel]:
    """Returns an spComBel given an spComBel id."""
    return db_session.query(SpComBel).filter(SpComBel.id == id).one_or_none()


def get_by_code(*, db_session, code: str) -> Optional[SpComBel]:
    """Returns an spComBel given an spComBel code address."""
    return db_session.query(SpComBel).filter(SpComBel.code == code).one_or_none()


def get_default_spComBel(*, db_session ) -> Optional[SpComBel]:
    """Returns an spComBel given an spComBel code address."""
    return db_session.query(SpComBel).first()


def get_all(*, db_session) -> List[Optional[SpComBel]]:
    """Returns all spComBels."""
    return db_session.query(SpComBel).all()

def get_filter_by_spec_ids(*, db_session,spec_id: List[int]) -> List[Optional[SpComBel]]:
    """Returns all spmainels."""
    return db_session.query(SpComBel).filter(SpComBel.spec_id.in_(spec_id)).all()






def create(*, db_session, spComBel_in: SpComBelCreate) -> SpComBel:
    """Creates an spComBel."""
    
    spec = None
    mill = None
    if spComBel_in.spec_id:
        spec = db_session.query(Spec).filter(Spec.id == spComBel_in.spec_id).one_or_none()

    if spComBel_in.mill_id:
        mill = db_session.query(Mill).filter(Mill.id == spComBel_in.mill_id).one_or_none()

    contact = SpComBel(**spComBel_in.dict(exclude={"flex_form_data", "spec", "mill"}),
                    mill=mill,
                    spec=spec,
                    flex_form_data=spComBel_in.flex_form_data)
    
    db_session.add(contact)
    db_session.commit()
    return contact


def update(
    *,
    db_session,
    spComBel: SpComBel,
    spComBel_in: SpComBelUpdate,
) -> SpComBel:
    
    if spComBel_in.mill_id:
        spComBel.mill = db_session.query(Mill).filter(Mill.id == spComBel_in.mill_id).one_or_none()


    update_data = spComBel_in.dict(
        exclude={"flex_form_data", "location", "spec", "mill"},
    )
    for field, field_value in update_data.items():
        setattr(spComBel, field, field_value)

    spComBel.flex_form_data = spComBel_in.flex_form_data
    db_session.add(spComBel)
    db_session.commit()
    return spComBel


def update_new(*,db_session,spComBel: SpComBel, spComBel_in:dict) -> SpComBel:
    for field, field_value in spComBel_in.items():
        setattr(spComBel, field, field_value)

    db_session.add(spComBel)
    db_session.commit()
    return spComBel


def delete(*, db_session, spComBel_id: int):
    spComBel = db_session.query(SpComBel).filter(SpComBel.id == spComBel_id).one_or_none()
    
    if spComBel:
        spComBel.is_deleted = 1
    db_session.add(spComBel)
    db_session.commit()

    return spComBel


def get_by_spec_code(*, db_session, search_dict:SpComBelBySpecCode):

    spcombel = db_session.query(SpComBel).join(Spec).filter(Spec.spec_code==search_dict.spec_code)

    if not spcombel:
        raise HTTPException(status_code=400, detail="The spcombel with this id does not exist.")

    query, pagination = apply_pagination(spcombel, page_number=search_dict.page, page_size=search_dict.itemsPerPage)
    
    return {
        "items": query.all(),
        "itemsPerPage": pagination.page_size,
        "page": pagination.page_number,
        "total": pagination.total_results,

    }


def create_by_copy_spec_code(*, db_session, copy_dict: SpComBelCopyToCode,current_user):
    # 通过复制前的spec_code 查询数据
    copy_before_values = db_session.query(SpComBel).join(Spec).filter(Spec.spec_code==copy_dict.before_code).all()

    if not copy_before_values:
        raise HTTPException(status_code=400, detail="The spcombel with this spec_code does not exist.") 

    # 查询copy to 的spec记录
    copy_to_spec = db_session.query(Spec).filter(Spec.spec_code == copy_dict.after_code).order_by(Spec.id.desc()).first()

    if not copy_to_spec:
        raise HTTPException(status_code=400, detail="The spcombel with this spec_code does not exist.") 

    after_list = []
    try:
        for cbv in copy_before_values:

            is_cunzai = db_session.query(SpComBel).filter(SpComBel.spec_id == copy_to_spec.id,
                                                          SpComBel.thick_from == cbv.thick_from,
                                                          SpComBel.thick_to == cbv.thick_to).first()
                
            if is_cunzai:
                continue
            
            cbv_value = SpComBelCreate(**cbv.__dict__)
            cbv_value.created_by = current_user.email
            after_list.append(SpComBel(**cbv_value.dict(exclude={"flex_form_data", "spec", "mill"}), spec=copy_to_spec, mill=cbv.mill))

        if len(after_list) > 0:
            db_session.add_all(after_list)
            db_session.commit()
        else:
            raise HTTPException(status_code=400, detail="There are no replicable objects.") 

    except IntegrityError:
        db_session.rollback()
        raise HTTPException(status_code=400, detail="Insertion failed, the same record already exists.")

    return True