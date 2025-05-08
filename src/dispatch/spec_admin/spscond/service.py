
from typing import List, Optional
from fastapi import HTTPException
from dispatch.mill.models import Mill
from dispatch.spec_admin.spec.models import Spec
from .models import Spscond, SpscondCreate, SpscondUpdate, SpscondCreate, SpscondBySpecCode, SpscondCopyToCode
from sqlalchemy_filters import apply_pagination
from sqlalchemy.exc import IntegrityError

def get(*, db_session, id: int) -> Optional[Spscond]:
    """Returns an spscond given an spscond id."""
    return db_session.query(Spscond).filter(Spscond.id == id).one_or_none()


def get_by_code(*, db_session, code: str) -> Optional[Spscond]:
    """Returns an spscond given an spscond code address."""
    return db_session.query(Spscond).filter(Spscond.code == code).one_or_none()


def get_default_spscond(*, db_session ) -> Optional[Spscond]:
    """Returns an spscond given an spscond code address."""
    return db_session.query(Spscond).first()


def get_all(*, db_session) -> List[Optional[Spscond]]:
    """Returns all spsconds."""
    return db_session.query(Spscond)


def create(*, db_session, spscond_in: SpscondCreate) -> Spscond:
    """Creates an spscond."""
    
    spec = None
    mill = None
    if spscond_in.spec_id:
        spec = db_session.query(Spec).filter(Spec.id == spscond_in.spec_id).one_or_none()

    if spscond_in.mill_id:
        mill = db_session.query(Mill).filter(Mill.id == spscond_in.mill_id).one_or_none()

    contact = Spscond(**spscond_in.dict(exclude={"flex_form_data", "spec", "mill"}),
                    mill=mill,
                    spec=spec,
                    flex_form_data=spscond_in.flex_form_data)
    
    db_session.add(contact)
    db_session.commit()
    return contact


def update(
    *,
    db_session,
    spscond: Spscond,
    spscond_in: SpscondUpdate,
) -> Spscond:
    
    if spscond_in.mill_id:
        spscond.mill = db_session.query(Mill).filter(Mill.id == spscond_in.mill_id).one_or_none()


    update_data = spscond_in.dict(
        exclude={"flex_form_data", "spec", "mill"},
    )
    for field, field_value in update_data.items():
        setattr(spscond, field, field_value)

    spscond.flex_form_data = spscond_in.flex_form_data
    db_session.add(spscond)
    db_session.commit()
    return spscond


def update_new(*,db_session,spscond: Spscond, spscond_in:dict) -> Spscond:
    for field, field_value in spscond_in.items():
        setattr(spscond, field, field_value)

    db_session.add(spscond)
    db_session.commit()
    return spscond


def delete(*, db_session, id: int):
    spscond = db_session.query(Spscond).filter(Spscond.id == id).one_or_none()
    
    if spscond:
        spscond.is_deleted = 1
    db_session.add(spscond)
    db_session.commit()

    return spscond


def get_by_spec_code(*, db_session, search_dict:SpscondBySpecCode):

    spscond = db_session.query(Spscond).join(Spec).filter(Spec.spec_code==search_dict.spec_code)

    if not spscond:
        raise HTTPException(status_code=400, detail="The spscond with this id does not exist.")

    query, pagination = apply_pagination(spscond, page_number=search_dict.page, page_size=search_dict.itemsPerPage)
    
    return {
        "items": query.all(),
        "itemsPerPage": pagination.page_size,
        "page": pagination.page_number,
        "total": pagination.total_results,

    }



def create_by_copy_spec_code(*, db_session, copy_dict: SpscondCopyToCode,current_user):
    # 通过复制前的spec_code 查询数据
    copy_before_values = db_session.query(Spscond).join(Spec).filter(Spec.spec_code==copy_dict.before_code).all()

    if not copy_before_values:
        raise HTTPException(status_code=400, detail="The spscond with this spec_code does not exist.") 

    # 查询copy to 的spec记录
    copy_to_spec = db_session.query(Spec).filter(Spec.spec_code == copy_dict.after_code).order_by(Spec.id.desc()).first()

    if not copy_to_spec:
        raise HTTPException(status_code=400, detail="The spscond with this spec_code does not exist.") 

    after_list = []
    try:
        for cbv in copy_before_values:

            is_cunzai = db_session.query(Spscond).filter(Spscond.spec_id == copy_to_spec.id, 
                                                            Spscond.thick_from == cbv.thick_from,
                                                            Spscond.thick_to == cbv.thick_to).first()
                
            if is_cunzai:
                continue
            
            cbv_value = SpscondCreate(**cbv.__dict__)
            cbv_value.created_by = current_user.email
            after_list.append(Spscond(**cbv_value.dict(exclude={"flex_form_data", "spec", "mill"}), spec=copy_to_spec, mill=cbv.mill))

        if len(after_list) > 0:
            db_session.add_all(after_list)
            db_session.commit()
        else:
            raise HTTPException(status_code=400, detail="There are no replicable objects.") 

    except IntegrityError:
        db_session.rollback()
        raise HTTPException(status_code=400, detail="Insertion failed, the same record already exists.")


    return True
    