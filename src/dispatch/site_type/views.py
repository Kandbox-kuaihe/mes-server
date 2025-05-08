from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from dispatch.database import get_db
from dispatch.system_admin.auth.models import DispatchUser
from dispatch.system_admin.auth.service import get_current_user

from .service import get_site_type_codes_list, get_site_type, get_site_type_by_code, create_site_type, update_site_type, delete_site_type, get_site_types_by_mill_id, get_site_types_by_mill_code
from .models import SiteType, SiteTypeCreate, SiteTypeUpdate, SiteTypeRead, SiteTypePagination
from dispatch.database_util.service import common_parameters, search_filter_sort_paginate


router = APIRouter()


@router.get("/", response_model=SiteTypePagination)
def get_sites(*, common: dict = Depends(common_parameters)):
    if common["sort_by"] == ['mill_code']:
        common["sort_by"] = ["mill.code"]
    return search_filter_sort_paginate(model="SiteType", **common)


@router.post("/", response_model=SiteTypeRead)
def create_site_type_view(*, db_session: Session = Depends(get_db), site_type_in: SiteTypeCreate,
                          current_user: DispatchUser = Depends(get_current_user)):
    """
    创建一个新的 SiteType
    """
    existing_site_type = get_site_type_by_code(db_session=db_session, code=site_type_in.code)
    if existing_site_type and not existing_site_type.is_deleted:
        raise HTTPException(status_code=400, detail="SiteType with this code already exists.")
    if existing_site_type and existing_site_type.is_deleted:
        site_type_in.is_deleted = 0
        updated_site_type = update_site_type(db_session=db_session, site_type=existing_site_type, site_type_in=site_type_in)
        return updated_site_type
    site_type_in.created_by = current_user.email
    site_type = create_site_type(db_session=db_session, site_type_in=site_type_in)
    return site_type


@router.get("/{site_type_id}", response_model=SiteTypeRead)
def get_site_type_view(*, db_session: Session = Depends(get_db), site_type_id: int):
    """
    获取指定 ID 的 SiteType
    """
    site_type = get_site_type(db_session=db_session, id=site_type_id)
    if not site_type:
        raise HTTPException(status_code=400, detail="The SiteType with this id does not exist.")
    return site_type


@router.put("/{site_type_id}", response_model=SiteTypeRead)
def update_site_type_view(*, db_session: Session = Depends(get_db), site_type_id: int, site_type_in: SiteTypeUpdate,
                          current_user: DispatchUser = Depends(get_current_user)):
    """
    更新指定 ID 的 SiteType
    """
    site_type = get_site_type(db_session=db_session, id=site_type_id)
    if not site_type:
        raise HTTPException(status_code=400, detail="The SiteType with this id does not exist.")
    site_type_in.updated_by = current_user.email
    updated_site_type = update_site_type(db_session=db_session, site_type=site_type, site_type_in=site_type_in)
    return updated_site_type


@router.delete("/{site_type_id}")
def delete_site_type_view(*, db_session: Session = Depends(get_db), site_type_id: int):
    """
    删除指定 ID 的 SiteType
    """
    site_type = get_site_type(db_session=db_session, id=site_type_id)
    if not site_type:
        raise HTTPException(status_code=400, detail="The SiteType with this id does not exist.")

    success = delete_site_type(db_session=db_session, id=site_type_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to delete SiteType.")
    return {"message": "SiteType deleted successfully."}


@router.get("/by_mill/{mill_id}", response_model=List[SiteTypeRead])
def get_site_types_by_mill_view(*, db_session: Session = Depends(get_db), mill_id: int):
    """
    获取指定 mill_id 下的所有 SiteType
    """
    site_types = get_site_types_by_mill_id(db_session=db_session, mill_id=mill_id)
    return site_types


@router.get("/item/codes")
def get_code(db_session: Session = Depends(get_db)):
    # print(id)
    ls = get_site_type_codes_list(db_session=db_session)
    return ls

@router.get("/items/codes")
def get_codes(*, db_session: Session = Depends(get_db), mill_code: str):
    codes = get_site_types_by_mill_code(db_session=db_session, mill_code=mill_code)
    return [site.code for site in codes] 