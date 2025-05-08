from dispatch.database import get_db
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from dispatch.system_admin.auth.models import DispatchUser
from dispatch.system_admin.auth.service import get_by_ids, get_current_user, get_or_set_user_redis,get_user_by_id
from dispatch.database_util.service import common_parameters, search_filter_sort_paginate
from .models import (
    MillCreate,
    MillPagination,
    MillOwnerRead,
    MillUpdate,
    MillSelectRespone,
    MillSelect
)
from .service import create, delete, get, get_by_code, update, get_all_select,get_by_user_id,get_mill_codes,get_all,sync_mill_from_odoo_data
from dispatch.system_admin.auth.service import get as user_get
router = APIRouter()


def update_user_current_mill(db_session,mill,is_delete = False):
    # 判断dispatch_user，里current_mill_id 是否存在(是否在mill 列表里)，不存在改成当前的mill
    all_mill = get_all_select(db_session=db_session)
    all_mill_ids = [inner_mill.id for inner_mill in all_mill]

    for user in mill.dispatch_user:
        if not user.current_mill_id or  user.current_mill_id ==-1 or user.current_mill_id not in all_mill_ids:
            current_mill_id = mill.id
            current_mill_code = mill.code
            if is_delete:
                mill_list = get_by_user_id(db_session=db_session,user_id=user.id)
                current_mill_id = mill_list[0].id if mill_list else -1 
                current_mill_code = mill_list[0].code if mill_list else "" 

            _user = db_session.query(DispatchUser).filter(DispatchUser.id == user.id).first()
            if _user:
                user.current_mill_id = current_mill_id
                user.current_mill_code = current_mill_code
                db_session.commit()

            get_or_set_user_redis(user_email=user.email, reload=True)


@router.get("/", response_model=MillPagination)
def get_mills(*, common: dict = Depends(common_parameters), 
              db_session: Session = Depends(get_db),
              current_user: DispatchUser = Depends(get_current_user)):
    # 判断如果不是sys角色的用户 只能查看到自己的mill
    my = user_get(db_session = db_session,user_id = current_user.id)
    if all([role.name !='sys' for role in  my.role]):
        all_mill = get_by_user_id(db_session=db_session,user_id=current_user.id)
        mill_id_list = [mill.id for mill in all_mill ]
        common["fields"] = ["id"]
        common["ops"] = ["in"]
        common["values"] = [mill_id_list]

    return search_filter_sort_paginate(model="Mill", **common)


@router.post("/", response_model=MillOwnerRead)
def create_mill(*, db_session: Session = Depends(get_db), mill_in: MillCreate,
                 current_user: DispatchUser = Depends(get_current_user)):
    """
    Create a new mill contact.
    """
    
    mill = get_by_code(db_session=db_session,code=mill_in.code)
    
    
    if mill:
        raise HTTPException(status_code=400, detail="The mill with this code already exists.")
    user_ids = mill_in.user_ids
    user_list = []
    if user_ids:
        user_list = get_by_ids(db_session=db_session,user_id=user_ids)
    mill_in.dispatch_user = user_list
    mill_in.created_by = current_user.email
    mill_in.updated_by = current_user.email
    mill = create(db_session=db_session, mill_in=mill_in)
    # 判断dispatch_user，里current_mill_id 是否存在(是否在mill 列表里)，不存在改成当前的mill
    update_user_current_mill(db_session,mill)

    mill = get_by_code(db_session=db_session,code=mill_in.code)
    return mill


@router.get("/{mill_id}", response_model=MillOwnerRead)
def get_mill(*, db_session: Session = Depends(get_db), mill_id: int):
    """
    Get a mill contact.
    """
    mill = get(db_session=db_session, mill_id=mill_id)
    if not mill:
        raise HTTPException(status_code=400, detail="The mill with this id does not exist.")
    return mill


@router.put("/{mill_id}", response_model=MillOwnerRead)
def update_mill(
    *,
    db_session: Session = Depends(get_db),
    mill_id: int,
    mill_in: MillUpdate, current_user: DispatchUser = Depends(get_current_user)
):
    """
    Update a mill contact.
    """
    mill = get(db_session=db_session, mill_id=mill_id)
    if not mill:
        raise HTTPException(status_code=400, detail="The mill with this id does not exist.")

    user_ids = mill_in.user_ids
    user_list = []
    if user_ids:
        user_list = get_by_ids(db_session=db_session,user_id=user_ids)
    mill_in.dispatch_user = user_list

    mill = update(
        db_session=db_session,
        mill=mill,
        mill_in=mill_in,
    )
    # 判断dispatch_user，里current_mill_id 是否存在(是否在mill 列表里)，不存在改成当前的mill
    update_user_current_mill(db_session,mill)
    
    mill = get(db_session=db_session, mill_id=mill_id)

    return mill


@router.put("/mill_code/{mill_code}", response_model=MillOwnerRead)
def update_mill_by_code(
    *,
    db_session: Session = Depends(get_db),
    mill_code: str,
    mill_in: MillUpdate, current_user: DispatchUser = Depends(get_current_user)
):
    """
    Update a mill contact.
    """
    mill = get_by_code(db_session=db_session, code=mill_code)
    if not mill:
        raise HTTPException(status_code=400, detail="The mill with this id does not exist.")

    mill_in.updated_by = current_user.email
    mill = update(
        db_session=db_session,
        mill=mill,
        mill_in=mill_in,
    )

    return mill


@router.delete("/{mill_id}", response_model=MillOwnerRead)
def delete_mill(*, db_session: Session = Depends(get_db), mill_id: int):
    """
    Delete a mill contact.
    """
    mill = get(db_session=db_session, mill_id=mill_id)
    if not mill:
        raise HTTPException(status_code=400, detail="The mill with this id does not exist.")

    data =  delete(db_session=db_session, mill_id=mill_id)

    update_user_current_mill(db_session,mill,is_delete = True  )

    return data


@router.get("/data/millSelect", response_model=MillSelectRespone)
def getRoleSelect(*, db_session: Session = Depends(get_db), current_user: DispatchUser = Depends(get_current_user)):
    """
    """
    my = user_get(db_session = db_session,user_id = current_user.id)
    mill_id_list = []
    if all([role.name !='sys' for role in  my.role]):
        all_mill = get_by_user_id(db_session=db_session,user_id=current_user.id)
        mill_id_list = [mill.id for mill in all_mill ] 

    data_list = get_all_select(db_session=db_session )
    
    result_list = []
    for row in data_list:
        if  mill_id_list and row.id not in mill_id_list:
            continue
        result_list.append( MillSelect( id = row.id,  code = row.code  ) ) 
 
    return MillSelectRespone(options=result_list)

@router.get("/item/codes")
def get_codes(db_session: Session = Depends(get_db)):
    return get_mill_codes(db_session=db_session)

@router.get("/all_mill_codes/")
def get_all_mill_codes(db_session: Session = Depends(get_db)):

    return get_all_select(db_session=db_session)



@router.post("/sync_mill_from_odoo")
def sync_mill_from_odoo(
        *,
        db_session: Session = Depends(get_db),
        mill_in: dict,
        current_user: DispatchUser = Depends(get_current_user)
):
    """
    Sync mill from odoo.
    """
    result = sync_mill_from_odoo_data(session=db_session, mill_in=mill_in)

    return result