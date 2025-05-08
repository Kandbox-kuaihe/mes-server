
from typing import List, Optional
from fastapi import HTTPException
from dispatch.mill.models import Mill
from dispatch.spec_admin.spec.models import Spec
from dispatch.spec_admin.spprodan_other_element.models import SpprodanOtherElement
from dispatch.spec_admin.spprodan_other_element.service import get_by_spprodan_id
from .models import Spprodan, SpprodanCreate, SpprodanUpdate, SpprodanCreate, SpprodanBySpecCode, SpprodanCopyToCode
from sqlalchemy_filters import apply_pagination
from sqlalchemy.exc import IntegrityError

def get(*, db_session, id: int) -> Optional[Spprodan]:
    """Returns an spprodan given an spprodan id."""
    return db_session.query(Spprodan).filter(Spprodan.id == id).one_or_none()


def get_by_code(*, db_session, code: str) -> Optional[Spprodan]:
    """Returns an spprodan given an spprodan code address."""
    return db_session.query(Spprodan).filter(Spprodan.code == code).one_or_none()


def get_by_spec_id(*, db_session, spec_id:int) -> List[Optional[Spprodan]]:
    return db_session.query(Spprodan).filter(Spprodan.spec_id==spec_id).all()


def get_default_spprodan(*, db_session ) -> Optional[Spprodan]:
    """Returns an spprodan given an spprodan code address."""
    return db_session.query(Spprodan).first()


def get_all(*, db_session) -> List[Optional[Spprodan]]:
    """Returns all spprodans."""
    return db_session.query(Spprodan)


# def create(*, db_session, spprodan_in: SpprodanCreate) -> Spprodan:
#     """Creates an spprodan."""
    
#     spec = None
#     mill = None
#     if spprodan_in.spec_id:
#         spec = db_session.query(Spec).filter(Spec.id == spprodan_in.spec_id).one_or_none()

#     if spprodan_in.mill_id:
#         mill = db_session.query(Mill).filter(Mill.id == spprodan_in.mill_id).one_or_none()

#     contact = Spprodan(**spprodan_in.dict(exclude={"flex_form_data", "spec", "mill"}),
#                     mill=mill,
#                     spec=spec,
#                     flex_form_data=spprodan_in.flex_form_data)
    
#     db_session.add(contact)
#     db_session.commit()
#     return contact

def create(*, db_session, spprodan_in: SpprodanCreate) -> Spprodan:
    """Creates an SpMainEl with multiple child records."""
    spec = None
    mill = None
    if spprodan_in.spec_id:
        spec = db_session.query(Spec).filter(Spec.id == spprodan_in.spec_id).one_or_none()
    if spprodan_in.mill_id:
        mill = db_session.query(Mill).filter(Mill.id == spprodan_in.mill_id).one_or_none()

    main_record = Spprodan(
        **spprodan_in.dict(exclude={"other_element", "spec", "mill", "flex_form_data"}), 
        mill=mill,
        spec=spec,
        flex_form_data=spprodan_in.flex_form_data,
    )
    db_session.add(main_record)
    db_session.flush() 
    if spprodan_in.other_element:
        child_records = [
            SpprodanOtherElement(
                **detail.dict(exclude={"spprodan_id"}),
                spprodan=main_record 
            )
            for detail in spprodan_in.other_element
        ]
        db_session.add_all(child_records)

    db_session.commit()
    db_session.refresh(main_record)

    return main_record


def update(
    *,
    db_session,
    spprodan: Spprodan,
    spprodan_in: SpprodanUpdate,
) -> Spprodan:
    
    if spprodan_in.mill_id:
        spprodan.mill = db_session.query(Mill).filter(Mill.id == spprodan_in.mill_id).one_or_none()

    update_data = spprodan_in.dict(
        exclude={"flex_form_data", "spec", "mill"},
    )
    for field, field_value in update_data.items():
        setattr(spprodan, field, field_value)

    spprodan.flex_form_data = spprodan_in.flex_form_data
    db_session.add(spprodan)
    db_session.commit()
    return spprodan


def update_new(*,db_session,spprodan: Spprodan, spprodan_in:dict) -> Spprodan:
    for field, field_value in spprodan_in.items():
        setattr(spprodan, field, field_value)

    db_session.add(spprodan)
    db_session.commit()
    return spprodan


def delete(*, db_session, id: int):
    spprodan = db_session.query(Spprodan).filter(Spprodan.id == id).one_or_none()
    
    if spprodan:
        spprodan.is_deleted = 1
    db_session.add(spprodan)
    db_session.commit()

    return spprodan


def get_by_spec_code(*, db_session, search_dict:SpprodanBySpecCode):

    spprodan = db_session.query(Spprodan).join(Spec).filter(Spec.spec_code==search_dict.spec_code)

    if not spprodan:
        raise HTTPException(status_code=400, detail="The spprodan with this id does not exist.")

    query, pagination = apply_pagination(spprodan, page_number=search_dict.page, page_size=search_dict.itemsPerPage)
    
    return {
        "items": query.all(),
        "itemsPerPage": pagination.page_size,
        "page": pagination.page_number,
        "total": pagination.total_results,

    }

def create_by_copy_spec_code(*, db_session, copy_dict: SpprodanCopyToCode,current_user):
    # 通过复制前的spec_code 查询数据
    copy_before_values = db_session.query(Spprodan).join(Spec).filter(Spec.spec_code==copy_dict.before_code).all()

    if not copy_before_values:
        raise HTTPException(status_code=400, detail="The spprodan with this spec_code does not exist.") 

    # 查询copy to 的spec记录
    copy_to_spec = db_session.query(Spec).filter(Spec.spec_code == copy_dict.after_code).order_by(Spec.id.desc()).first()

    if not copy_to_spec:
        raise HTTPException(status_code=400, detail="The spprodan with this spec_code does not exist.") 

    after_list = []
    other_element_list = []
    try:
        for cbv in copy_before_values:

            is_cunzai = db_session.query(Spprodan).filter(Spprodan.spec_id == copy_to_spec.id, 
                                                            Spprodan.thick_from == cbv.thick_from,
                                                            Spprodan.thick_to == cbv.thick_to).first()
                
            if is_cunzai:
                continue
            
            cbv_value = SpprodanCreate(**cbv.__dict__)
            cbv_value.created_by = current_user.email
            cbv_value_object = Spprodan(**cbv_value.dict(exclude={"flex_form_data", "spec", "mill", "other_element"}), spec=copy_to_spec, mill=cbv.mill)

            # 处理copy  other_element
            other_elements = get_by_spprodan_id(db_session=db_session, id=cbv.id)
            if len(other_elements) > 0:
                for other_element in other_elements:
                    other_value = {
                        "code": other_element.code,
                        "min_value": other_element.min_value,
                        "max_value": other_element.max_value,
                        "precision": other_element.precision,
                        "created_by":current_user.email,
                        "spprodan":cbv_value_object
                    }
                    other_element_list.append(SpprodanOtherElement(**other_value))


            after_list.append(cbv_value_object)

        if len(after_list) > 0:
            db_session.add_all(after_list)

            db_session.flush()

            if len(other_element_list)>0:
                db_session.add_all(other_element_list)
            db_session.commit()
        else:
            raise HTTPException(status_code=400, detail="There are no replicable objects.") 

    except IntegrityError:
        db_session.rollback()
        raise HTTPException(status_code=400, detail="Insertion failed, the same record already exists.")

    return True


def get_all_data(*, db_session) -> List[Optional[Spprodan]]:
    return db_session.query(Spprodan).all()


def get_all_data_dict_of_spec_id(*, db_session) -> dict:
    data = get_all_data(db_session=db_session)
    dic = {}
    for d in data:
        if d.spec_id not in dic:
            dic[d.spec_id] = []
        dic[d.spec_id].append(d)
    return dic

