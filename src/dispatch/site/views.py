from dispatch.database import get_db
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from dispatch.system_admin.auth.models import DispatchUser
from dispatch.system_admin.auth.service import get_current_user
from dispatch.database_util.service import common_parameters, search_filter_sort_paginate
from .models import (
    SiteBase,
    SiteRead,
    SitePagination,
    SiteUpdate
    # DepotPagination,
)
# from .service import create, delete, get, get_by_code, get_by_code_org_id, update


from .service import get_by_code,create,get,update,delete, get_site_codes, get_site_by_site_type, new_create
router = APIRouter()


from .models import Site

@router.get("/", response_model=SitePagination)
def get_sites(*, common: dict = Depends(common_parameters)):

    return search_filter_sort_paginate(model="Site", **common)




@router.post("/",response_model=SiteRead)
def create_depot(*, db_session: Session = Depends(get_db), site_in: SiteBase,
                 current_user: DispatchUser = Depends(get_current_user)):
    """
    Create a new depot contact.
    # """
    site = get_by_code(db_session=db_session,code=site_in.code)
    if site and not site.is_deleted:
        raise HTTPException(status_code=400, detail="The site with this code already exists.")
    if site and site.is_deleted:
        site_in.is_deleted = 0
        SiteObj = update(
            db_session=db_session,
            item=site,
            item_in=site_in,
        )
        return SiteObj
    Site_obj = new_create(db_session=db_session, site_in=site_in)
    return Site_obj



@router.get("/{depot_id}", response_model=SiteRead)
def get_site(*, db_session: Session = Depends(get_db), id: int):
    """
    Get a depot contact.
    """
    depot = get(db_session=db_session, id=id)
    if not depot:
        raise HTTPException(status_code=400, detail="The depot with this id does not exist.")
    return depot


@router.put("/{site_id}", response_model=SiteRead)
def update_obj(
    *,
    db_session: Session = Depends(get_db),
    site_id: int,
    site_in: SiteUpdate, current_user: DispatchUser = Depends(get_current_user)
):
    """
    Update a site .
    """
    site = get(db_session=db_session, id=site_id)
    if not site:
        raise HTTPException(status_code=400, detail="The site with this id does not exist.")

    SiteObj = update(
        db_session=db_session,
        item=site,
        item_in=site_in,
    )
    return SiteObj



@router.delete("/{site_id}")
def delete_depot(*, db_session: Session = Depends(get_db), site_id: int):
    """
    Delete a depot contact.
    """
    depot = get(db_session=db_session, id=site_id)
    if not depot:
        raise HTTPException(status_code=400, detail="The depot with this id does not exist.")

    delete(db_session=db_session, id=site_id)


@router.get("/item/codes")
def get_code(db_session: Session = Depends(get_db)):
    # print(id)
    ls = get_site_codes(db_session=db_session)
    return ls


@router.get("/item/get_site_by_site_type/{site_type_code}")
def get_area_by_site_views(*, db_session: Session = Depends(get_db), site_type_code: str):
    ls = get_site_by_site_type(db_session=db_session, site_type_code=site_type_code)
    return ls