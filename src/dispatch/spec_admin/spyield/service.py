
from typing import List, Optional
from fastapi import HTTPException
from dispatch.mill.models import Mill
from dispatch.spec_admin.spec.models import Spec
from .models import Spyield, SpyieldCreate, SpyieldUpdate, SpyieldCreate, SpyieldBySpecCode, SpyieldCopyToCode
from sqlalchemy_filters import apply_pagination
from sqlalchemy.exc import IntegrityError

def get(*, db_session, id: int) -> Optional[Spyield]:
    """Returns an spyield given an spyield id."""
    return db_session.query(Spyield).filter(Spyield.id == id).one_or_none()

def get_by_spec_id(*, db_session, spec_id:int)-> List[Spyield]:
    return db_session.query(Spyield).filter(Spyield.spec_id==spec_id).all()

def get_one_spec_id(*, db_session, spec_id:int)-> Optional[Spyield]:
    return db_session.query(Spyield).filter(Spyield.spec_id==spec_id).first()

def get_by_code(*, db_session, code: str) -> Optional[Spyield]:
    """Returns an spyield given an spyield code address."""
    return db_session.query(Spyield).filter(Spyield.code == code).one_or_none()


def get_default_spyield(*, db_session ) -> Optional[Spyield]:
    """Returns an spyield given an spyield code address."""
    return db_session.query(Spyield).first()

def get_spyield_by_spec_id_and_flange_thickness(*, db_session, spec_id: int, flange_thickness: float) -> Optional[Spyield]:
    if not spec_id or not flange_thickness:
        return None
    return db_session.query(Spyield).filter(
        Spyield.spec_id == spec_id,
        Spyield.thick_from <= flange_thickness, Spyield.thick_to >= flange_thickness).first()


def get_all(*, db_session) -> List[Spyield]:
    """Returns all spyields."""
    return db_session.query(Spyield)


def create(*, db_session, spyield_in: SpyieldCreate) -> Spyield:
    """Creates an spyield."""
    
    spec = None
    mill = None
    if spyield_in.spec_id:
        spec = db_session.query(Spec).filter(Spec.id == spyield_in.spec_id).one_or_none()

    if spyield_in.mill_id:
        mill = db_session.query(Mill).filter(Mill.id == spyield_in.mill_id).one_or_none()
    

    contact = Spyield(**spyield_in.dict(exclude={"flex_form_data", "spec", "mill"}),
                    mill=mill,
                    spec=spec,
                    flex_form_data=spyield_in.flex_form_data)
    
    db_session.add(contact)
    db_session.commit()
    return contact


def update(
    *,
    db_session,
    spyield: Spyield,
    spyield_in: SpyieldUpdate,
) -> Spyield:
    
    if spyield_in.mill_id:
        spyield.mill = db_session.query(Mill).filter(Mill.id == spyield_in.mill_id).one_or_none()


    update_data = spyield_in.dict(
        exclude={"flex_form_data", "spec", "mill"},
    )
    for field, field_value in update_data.items():
        setattr(spyield, field, field_value)

    spyield.flex_form_data = spyield_in.flex_form_data
    db_session.add(spyield)
    db_session.commit()
    return spyield

def update_new(*,db_session,spYield: Spyield, spYield_in:dict) -> Spyield:
    for field, field_value in spYield_in.items():
        setattr(spYield, field, field_value)

    db_session.add(spYield)
    db_session.commit()
    return spYield

def delete(*, db_session, id: int):
    spyield = db_session.query(Spyield).filter(Spyield.id == id).one_or_none()
    
    if spyield:
        spyield.is_deleted = 1
    db_session.add(spyield)
    db_session.commit()

    return spyield


def get_by_spec_code(*, db_session, search_dict:SpyieldBySpecCode):

    spyield = db_session.query(Spyield).join(Spec).filter(Spec.spec_code==search_dict.spec_code)

    if not spyield:
        raise HTTPException(status_code=400, detail="The spyield with this id does not exist.")

    query, pagination = apply_pagination(spyield, page_number=search_dict.page, page_size=search_dict.itemsPerPage)
    
    return {
        "items": query.all(),
        "itemsPerPage": pagination.page_size,
        "page": pagination.page_number,
        "total": pagination.total_results,

    }

def create_by_copy_spec_code(*, db_session, copy_dict: SpyieldCopyToCode, current_user):
    # 通过复制前的spec_code 查询数据
    copy_before_values = db_session.query(Spyield).join(Spec).filter(Spec.spec_code==copy_dict.before_code).all()

    if not copy_before_values:
        raise HTTPException(status_code=400, detail="The spyield with this spec_code does not exist.") 

    # 查询copy to 的spec记录
    copy_to_spec = db_session.query(Spec).filter(Spec.spec_code == copy_dict.after_code).order_by(Spec.id.desc()).first()

    if not copy_to_spec:
        raise HTTPException(status_code=400, detail="The spyield with this spec_code does not exist.") 

    after_list = []
    try:
        for cbv in copy_before_values:

            is_cunzai = db_session.query(Spyield).filter(Spyield.spec_id == copy_to_spec.id, 
                                                          Spyield.thick_from == cbv.thick_from,
                                                          Spyield.thick_to == cbv.thick_to).first()
            
            if is_cunzai:
                continue

            cbv_value = SpyieldCreate(**cbv.__dict__)
            cbv_value.created_by = current_user.email
            after_list.append(Spyield(**cbv_value.dict(exclude={"flex_form_data", "spec", "mill"}), spec=copy_to_spec, mill=cbv.mill))

        if len(after_list) > 0:
            db_session.add_all(after_list)
            db_session.commit()
        else:
            raise HTTPException(status_code=400, detail="There are no replicable objects.") 

    except IntegrityError:
        db_session.rollback()
        raise HTTPException(status_code=400, detail="Insertion failed, the same record already exists.")


    return True


def get_all_data(*, db_session) -> List[Optional[Spyield]]:
    """Returns all sptensils."""
    return db_session.query(Spyield).all()


def get_all_data_dict_of_spec_id(*, db_session) -> dict:
    """Returns all sptensils."""

    data = get_all_data(db_session=db_session)

    dic = {}

    for d in data:
        if d.spec_id not in dic:
            dic[d.spec_id] = []
        dic[d.spec_id].append(d)

    return dic
