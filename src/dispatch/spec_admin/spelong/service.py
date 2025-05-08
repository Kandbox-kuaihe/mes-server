
from typing import List, Optional
from fastapi import HTTPException
from dispatch.mill.models import Mill
from dispatch.spec_admin.spec.models import Spec
from .models import Spelong as SpeLong
from .models import SpeLongCreate, SpeLongUpdate, SpeLongCreate, SpeLongBySpecCode, SpeLongCopyToCode
from sqlalchemy_filters import apply_pagination
from sqlalchemy.exc import IntegrityError

def get(*, db_session, id: int) -> Optional[SpeLong]:
    """Returns an spelong given an spelong id."""
    return db_session.query(SpeLong).filter(SpeLong.id == id).one_or_none()


def get_by_spec_id(*, db_session, spec_id:int)-> List[SpeLong]:
    return db_session.query(SpeLong).filter(SpeLong.spec_id==spec_id).all()

def get_one_spec_id(*, db_session, spec_id:int)-> Optional[SpeLong]:
    return db_session.query(SpeLong).filter(SpeLong.spec_id==spec_id).first()

def get_by_code(*, db_session, code: str) -> Optional[SpeLong]:
    """Returns an spelong given an spelong code address."""
    return db_session.query(SpeLong).filter(SpeLong.code == code).one_or_none()


def get_default_spelong(*, db_session ) -> Optional[SpeLong]:
    """Returns an spelong given an spelong code address."""
    return db_session.query(SpeLong).first()


def get_all(*, db_session) -> List[SpeLong]:
    """Returns all spelongs."""
    return db_session.query(SpeLong)

def get_spelong_by_spec_id_and_flange_thickness(*, db_session, spec_id: int, flange_thickness: float) -> Optional[SpeLong]:
    if not spec_id or not flange_thickness:
        return None
    return db_session.query(SpeLong).filter(
        SpeLong.spec_id == spec_id,
        SpeLong.thick_from <= flange_thickness, SpeLong.thick_to >= flange_thickness).first()


def create(*, db_session, spelong_in: SpeLongCreate) -> SpeLong:
    """Creates an spelong."""
    
    spec = None
    mill = None
    if spelong_in.spec_id:
        spec = db_session.query(Spec).filter(Spec.id == spelong_in.spec_id).one_or_none()
    
    if spelong_in.mill_id:
        mill = db_session.query(Mill).filter(Mill.id == spelong_in.mill_id).one_or_none()
    

    contact = SpeLong(**spelong_in.dict(exclude={"flex_form_data", "spec", "mill"}),
                    mill=mill,
                    spec=spec,
                    flex_form_data=spelong_in.flex_form_data)
    
    db_session.add(contact)
    db_session.commit()
    return contact


def update(
    *,
    db_session,
    spelong: SpeLong,
    spelong_in: SpeLongUpdate,
) -> SpeLong:
    
    if spelong_in.mill_id:
        spelong.mill = db_session.query(Mill).filter(Mill.id == spelong_in.mill_id).one_or_none()


    update_data = spelong_in.dict(
        exclude={"flex_form_data", "location", "spec", "mill"},
    )
    for field, field_value in update_data.items():
        setattr(spelong, field, field_value)

    spelong.flex_form_data = spelong_in.flex_form_data
    db_session.add(spelong)
    db_session.commit()
    return spelong


def update_new(*,db_session,speLong: SpeLong, speLong_in:dict) -> SpeLong:
    for field, field_value in speLong_in.items():
        setattr(speLong, field, field_value)

    db_session.add(speLong)
    db_session.commit()
    return speLong


def delete(*, db_session, spelong_id: int):
    spelong = db_session.query(SpeLong).filter(SpeLong.id == spelong_id).one_or_none()
    
    if spelong:
        spelong.is_deleted = 1
    db_session.add(spelong)
    db_session.commit()

    return spelong


def get_by_spec_code(*, db_session, search_dict:SpeLongBySpecCode):

    spelong = db_session.query(SpeLong).join(Spec).filter(Spec.spec_code==search_dict.spec_code)

    if not spelong:
        raise HTTPException(status_code=400, detail="The spelong with this id does not exist.")

    query, pagination = apply_pagination(spelong, page_number=search_dict.page, page_size=search_dict.itemsPerPage)
    
    return {
        "items": query.all(),
        "itemsPerPage": pagination.page_size,
        "page": pagination.page_number,
        "total": pagination.total_results,

    }


def create_by_copy_spec_code(*, db_session, copy_dict: SpeLongCopyToCode,current_user):
    # 通过复制前的spec_code 查询数据
    copy_before_values = db_session.query(SpeLong).join(Spec).filter(Spec.spec_code==copy_dict.before_code).all()

    if not copy_before_values:
        raise HTTPException(status_code=400, detail="The spelong with this spec_code does not exist.") 

    # 查询copy to 的spec记录
    copy_to_spec = db_session.query(Spec).filter(Spec.spec_code == copy_dict.after_code).order_by(Spec.id.desc()).first()

    if not copy_to_spec:
        raise HTTPException(status_code=400, detail="The spelong with this spec_code does not exist.") 

    after_list = []
    try:
        for cbv in copy_before_values:

            is_cunzai = db_session.query(SpeLong).filter(SpeLong.spec_id == copy_to_spec.id, 
                                                        SpeLong.thick_from == cbv.thick_from,
                                                        SpeLong.thick_to == cbv.thick_to).first()
                
            if is_cunzai:
                continue
            
            cbv_value = SpeLongCreate(**cbv.__dict__)
            cbv_value.created_by = current_user.email
            after_list.append(SpeLong(**cbv_value.dict(exclude={"flex_form_data", "spec", "mill"}), spec=copy_to_spec, mill=cbv.mill))

        if len(after_list) > 0:
            db_session.add_all(after_list)
            db_session.commit()
        else:
            raise HTTPException(status_code=400, detail="There are no replicable objects.") 

    except IntegrityError:
        db_session.rollback()
        raise HTTPException(status_code=400, detail="Insertion failed, the same record already exists.")


    return True


def get_all_data(*, db_session) -> List[Optional[SpeLong]]:
    """Returns all sptensils."""
    return db_session.query(SpeLong).all()


def get_all_data_dict_of_spec_id(*, db_session) -> dict:
    """Returns all sptensils."""

    data = get_all_data(db_session=db_session)

    dic = {}

    for d in data:
        if d.spec_id not in dic:
            dic[d.spec_id] = []
        dic[d.spec_id].append(d)

    return dic
