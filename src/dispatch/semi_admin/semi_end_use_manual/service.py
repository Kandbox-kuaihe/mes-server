
from dispatch.mill.models import Mill
from dispatch.product_type.models import ProductType
from .models import SemiEndUseManual, SemiEndUseManualCreate, SemiEndUseManualUpdate, SemiEndUseManualCreate, GetByCastSpec
from typing import Optional, List, Dict, Any, Tuple  
from sqlalchemy import and_  
from dispatch.cast.models import Cast
from dispatch.spec_admin.spec.models import Spec
from fastapi import HTTPException
from sqlalchemy_filters import apply_pagination
from dispatch.spec_admin.spmainel.service import spmain_union_other
from dispatch.spec_admin.spmainel.models import Spmainel

def get(*, db_session, id: int) -> Optional[SemiEndUseManual]:
    """Returns an spyield given an spyield id."""
    return db_session.query(SemiEndUseManual).filter(SemiEndUseManual.id == id).one_or_none()



def get_list_by_param(db_session, filters: List[Dict[str, Tuple[str, Any]]]) -> Optional[List[SemiEndUseManual]]:  
    """  
    Returns a list of SemiEndUseManual instances matching the given filter criteria.  
      
    Args:  
        db_session (Session): The database session to use for querying.  
        filters (List[Dict[str, Tuple[str, Any]]]): A list of dictionaries, each containing  
                              a field name, an operator ('eq' for ==, 'ne' for !=, 'is_not_null' for is not null),  
                              and a value to use as filter criteria.  
      
    Returns:  
        Optional[List[SemiEndUseManual]]: The matched instances or an empty list if no matches are found.  
        
        
    such as:
    
    filters = [  
        {'field': 'id', 'operator': 'gt', 'value': 100},  
        {'field': 'price', 'operator': 'lt', 'value': 500},  
        {'field': 'name', 'operator': 'ne', 'value': 'Special Item'},  
        {'field': 'description', 'operator': 'is_not_null', 'value': None},  
    ]  
    """  
    query = db_session.query(SemiEndUseManual)  
      
    # Build the query dynamically based on the provided filters  
    filter_conds = []  
    for filter_dict in filters:  
        field_name = filter_dict['field']  
        operator, value = filter_dict['operator'], filter_dict['value']  
          
        if operator == 'eq':  
            filter_conds.append(getattr(SemiEndUseManual, field_name) == value)  
        elif operator == 'ne':  
            filter_conds.append(getattr(SemiEndUseManual, field_name) != value)  
        elif operator == 'is_not_null':  
            filter_conds.append(getattr(SemiEndUseManual, field_name).isnot(None))  
        elif operator == 'gt':  
            filter_conds.append(getattr(SemiEndUseManual, field_name) > value)  
        elif operator == 'lt':  
            filter_conds.append(getattr(SemiEndUseManual, field_name) < value)  
        # 可
        # 可以添加更多的操作符支持，如 'lt' (小于), 'le' (小于等于), 'gt' (大于), 'ge' (大于等于) 等  
      
    if filter_conds:  
        query = query.filter(and_(*filter_conds))  
      
    # Execute the query and return the results  
    return query.all()  
  

def get_by_code(*, db_session, code: str) -> Optional[SemiEndUseManual]:
    """Returns an spyield given an spyield code address."""
    return db_session.query(SemiEndUseManual).filter(SemiEndUseManual.code == code).one_or_none()


def get_default_spyield(*, db_session ) -> Optional[SemiEndUseManual]:
    """Returns an spyield given an spyield code address."""
    return db_session.query(SemiEndUseManual).first()


def get_all(*, db_session) -> List[Optional[SemiEndUseManual]]:
    """Returns all spyields."""
    return db_session.query(SemiEndUseManual)


def create(*, db_session, manual_in: SemiEndUseManualCreate) -> SemiEndUseManual:
    """Creates an manual."""
    contact = SemiEndUseManual(**manual_in.dict(exclude={"flex_form_data", "spec", "cast", "mill", "product_type", "product_category", "flange_min", "flange_max"}),
                    flex_form_data=manual_in.flex_form_data)
    
    db_session.add(contact)
    db_session.commit()
    return contact


def cast_spec_compare(db_session, cast_id, spec_id, thick_from, thick_to) -> list[str]:
    cast = db_session.query(Cast).filter(Cast.id == cast_id).first()
    if not cast:
        raise HTTPException(status_code=400, detail="The cast with this id does not exist.")
    spmainels = db_session.query(Spmainel).filter(Spmainel.spec_id == spec_id).filter(Spmainel.thick_from < thick_from).filter(Spmainel.thick_to > thick_to )
        
    msg = []
    # cast 获取所有ch_开头的字段
    cast_val = {}
    for field in cast.__dict__:
        if field.startswith('ch_'):
            cast_val[field] = getattr(cast, field)
    for spmainel in spmainels:
        spmain_union_other(db_session=db_session,spmainel=spmainel)
        # 判断cast_val 是否在 spmainel 中
        for key, value in cast_val.items():
            col = key.replace("ch_", "")
            min_value = getattr(spmainel, f"main_el_min_value_{col}", None)
            max_value = getattr(spmainel, f"main_el_max_value_{col}", None)
            if not min_value or not max_value or not value:
                continue
            if not (min_value <= value <= max_value):
                msg.append(f"{col.upper()}:{value:.3f} not in  {min_value:.3f}-{max_value:.3f} spec_code:{spmainel.spec.spec_code}")
    return msg


def update(
    *,
    db_session,
    manual: SemiEndUseManual,
    manual_in: SemiEndUseManualUpdate,
) -> SemiEndUseManual:


    update_data = manual_in.dict(
        exclude={"flex_form_data", "spec", "mill", "product_type", "cast","flange_min", "flange_max","force"},
    )
    for field, field_value in update_data.items():
        setattr(manual, field, field_value)

    manual.flex_form_data = manual_in.flex_form_data
    db_session.add(manual)
    db_session.commit()
    return manual

def update_new(*,db_session,manual: SemiEndUseManual, manual_in:dict) -> SemiEndUseManual:
    for field, field_value in manual_in.items():
        setattr(manual, field, field_value)

    db_session.add(manual)
    db_session.commit()
    return manual


def delete(*, db_session, id: int):
    manual = db_session.query(SemiEndUseManual).filter(SemiEndUseManual.id == id).one_or_none()
    
    if manual:
        manual.is_deleted = 1
    db_session.add(manual)
    db_session.commit()

    return manual

def get_by_spec_ids_kg(*, db_session, spec_ids: List[int], kg=float) -> List[int]:
    """Returns all cast_specs by spec_ids and filters by kg within weight_min and weight_max."""
    return db_session.query(SemiEndUseManual).filter(
        SemiEndUseManual.spec_id.in_(spec_ids),
        SemiEndUseManual.weight_min <= kg,
        SemiEndUseManual.weight_max >= kg,
        SemiEndUseManual.is_deleted != 1
    ).all()

def get_by_cast_spec(*, db_session, filters:GetByCastSpec):    

    filter_conds = []
    if filters.cast_no:
        cast = db_session.query(Cast).filter(Cast.cast_code == filters.cast_no).one_or_none()
        
        if cast:
            filter_conds.append(getattr(SemiEndUseManual, "cast_id") == cast.id)
    if filters.section_code:
        spec = db_session.query(Spec).filter(Spec.section_code == filters.section_code).one_or_none()
        if spec:
            filter_conds.append(getattr(SemiEndUseManual, "spec_id") == spec.id)
    manual = db_session.query(SemiEndUseManual).filter(and_(*filter_conds))
    if not manual:
        raise HTTPException(status_code=400, detail="The manual with this id does not exist.")

    query, pagination = apply_pagination(manual, page_number=filters.page, page_size=filters.itemsPerPage)
    
    return {
        "items": query.all(),
        "itemsPerPage": pagination.page_size,
        "page": pagination.page_number,
        "total": pagination.total_results,

    }
