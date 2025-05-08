
from typing import List, Optional
from fastapi import HTTPException
from sqlalchemy import and_
from sqlalchemy.orm import Session

from dispatch.mill.models import Mill
from dispatch.spec_admin.spec.models import Spec
from .models import Spbend, SpbendCreate, SpbendUpdate, SpbendCreate, SpbendBySpecCode, SpbendCopyToCode
from sqlalchemy_filters import apply_pagination
from sqlalchemy.exc import IntegrityError

def get(*, db_session, id: int) -> Optional[Spbend]:
    """Returns an Spbend given an Spbend id."""
    return db_session.query(Spbend).filter(Spbend.id == id).one_or_none()


def get_by_code(*, db_session, code: str) -> Optional[Spbend]:
    """Returns an Spbend given an Spbend code address."""
    return db_session.query(Spbend).filter(Spbend.code == code).one_or_none()


def get_by_spec_id(*, db_session, spec_id:int) -> List[Spbend]:
    return db_session.query(Spbend).filter(Spbend.spec_id==spec_id).all()



def get_default_spbend(*, db_session ) -> Optional[Spbend]:
    """Returns an spbend given an spbend code address."""
    return db_session.query(Spbend).first()


def get_all(*, db_session) -> List[Spbend]:
    """Returns all spbends."""
    return db_session.query(Spbend)


def create(*, db_session, spbend_in: SpbendCreate) -> Spbend:
    """Creates an spbend."""
    
    spec = None
    mill = None
    if spbend_in.spec_id:
        spec = db_session.query(Spec).filter(Spec.id == spbend_in.spec_id).one_or_none()

    if spbend_in.mill_id:
        mill = db_session.query(Mill).filter(Mill.id == spbend_in.mill_id).one_or_none()

    contact = Spbend(**spbend_in.dict(exclude={"flex_form_data", "spec", "mill"}),
                    mill=mill,
                    spec=spec,
                    flex_form_data=spbend_in.flex_form_data)
    
    db_session.add(contact)
    db_session.commit()
    return contact


def update(
    *,
    db_session,
    spbend: Spbend,
    spbend_in: SpbendUpdate,
) -> Spbend:
    
    if spbend_in.mill_id:
        spbend.mill = db_session.query(Mill).filter(Mill.id == spbend_in.mill_id).one_or_none()


    update_data = spbend_in.dict(
        exclude={"flex_form_data", "spec", "mill"},
    )
    for field, field_value in update_data.items():
        setattr(spbend, field, field_value)

    spbend.flex_form_data = spbend_in.flex_form_data
    db_session.add(spbend)
    db_session.commit()
    return spbend


def update_new(*,db_session,spbend: Spbend, spbend_in:dict) -> Spbend:
    for field, field_value in spbend_in.items():
        setattr(spbend, field, field_value)

    db_session.add(spbend)
    db_session.commit()
    return spbend


def delete(*, db_session, id: int):
    spbend = db_session.query(Spbend).filter(Spbend.id == id).one_or_none()
    
    if spbend:
        spbend.is_deleted = 1
    db_session.add(spbend)
    db_session.commit()

    return spbend


def get_by_spec_code(*, db_session, search_dict:SpbendBySpecCode):

    spbend = db_session.query(Spbend).join(Spec).filter(Spec.spec_code==search_dict.spec_code)

    if not spbend:
        raise HTTPException(status_code=400, detail="The spbend with this id does not exist.")

    query, pagination = apply_pagination(spbend, page_number=search_dict.page, page_size=search_dict.itemsPerPage)
    
    return {
        "items": query.all(),
        "itemsPerPage": pagination.page_size,
        "page": pagination.page_number,
        "total": pagination.total_results,

    }



def create_by_copy_spec_code(*, db_session, copy_dict: SpbendCopyToCode,current_user):
    # 通过复制前的spec_code 查询数据
    copy_before_values = db_session.query(Spbend).join(Spec).filter(Spec.spec_code==copy_dict.before_code).all()

    if not copy_before_values:
        raise HTTPException(status_code=400, detail="The spbend with this spec_code does not exist.") 

    # 查询copy to 的spec记录
    copy_to_spec = db_session.query(Spec).filter(Spec.spec_code == copy_dict.after_code).order_by(Spec.id.desc()).first()

    if not copy_to_spec:
        raise HTTPException(status_code=400, detail="The spbend with this spec_code does not exist.") 

    after_list = []
    try:
        for cbv in copy_before_values:

            is_cunzai = db_session.query(Spbend).filter(Spbend.spec_id == copy_to_spec.id, 
                                                            Spbend.thick_from == cbv.thick_from,
                                                            Spbend.thick_to == cbv.thick_to).first()
                
            if is_cunzai:
                continue
            
            cbv_value = SpbendCreate(**cbv.__dict__)
            cbv_value.created_by = current_user.email
            after_list.append(Spbend(**cbv_value.dict(exclude={"flex_form_data", "spec", "mill"}), spec=copy_to_spec,  mill=cbv.mill))

        if len(after_list) > 0:
            db_session.add_all(after_list)
            db_session.commit()
        else:
            raise HTTPException(status_code=400, detail="There are no replicable objects.") 

    except IntegrityError:
        db_session.rollback()
        raise HTTPException(status_code=400, detail="Insertion failed, the same record already exists.")


    return True


def get_all_data(*, db_session) -> List[Optional[Spbend]]:
    return db_session.query(Spbend).all()


def get_all_data_dict_of_spec_id(*, db_session) -> dict:
    data = get_all_data(db_session=db_session)
    dic = {}
    for d in data:
        if d.spec_id not in dic:
            dic[d.spec_id] = []
        dic[d.spec_id].append(d)
    return dic


def bend_print_card(db_session, spec_id, product_type_flange_thickness, mill_id):
    return db_session.query(Spbend).filter(and_(
        Spbend.spec_id == spec_id,
        Spbend.thick_from <= product_type_flange_thickness,
        product_type_flange_thickness < Spbend.thick_to,
        Spbend.mill_id == mill_id
    )).first()


def get_spbend_by_spec_id_and_flange_thickness(*, db_session, spec_id: int, flange_thickness: float) -> Optional[Spbend]:
    if not spec_id or not flange_thickness:
        return None
    return db_session.query(Spbend).filter(
        Spbend.spec_id == spec_id,
        Spbend.thick_from <= flange_thickness, Spbend.thick_to >= flange_thickness).one_or_none()