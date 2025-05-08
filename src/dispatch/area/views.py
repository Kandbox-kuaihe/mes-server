from dispatch.database import get_db
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from dispatch.system_admin.auth.models import DispatchUser
from dispatch.system_admin.auth.service import get_current_user
from dispatch.site.service import get as get_site_code
from dispatch.database_util.service import common_parameters, search_filter_sort_paginate
from .models import (
    Area,
    AreaCreate,
    AreaPagination,
    AreaRead,
    AreaUpdate,
)
from .service import delete, get, get_by_code, update, new_create, get_area_codes, get_area_codes_type_all, \
    get_area_by_site, get_area_type_semi, get_area_type_finished, get_area_code_by_type_semi, \
    get_area_code_by_type_finished, get_site_code_by_type, get_site_type_code_by_type, get_type_list, \
    get_site_code_by, get_site_type_code_by, get_area_code_by_type_move
from dispatch.site_type.service import get_site_type

router = APIRouter()


@router.get("/", response_model=AreaPagination)
def get_areas(*, db_session: Session = Depends(get_db), common: dict = Depends(common_parameters),
              type: str = Query(None), ):
    query = db_session.query(Area)
    if type:
        query = query.filter(Area.type == type)
    common["query"] = query
    return search_filter_sort_paginate(model="Area", **common)


@router.get("/type", )
def get_type(db_session: Session = Depends(get_db)):
    type = get_type_list(db_session=db_session)
    return type


@router.post("/", response_model=AreaRead)
def create_area(*, db_session: Session = Depends(get_db), area_in: AreaCreate,
                current_user: DispatchUser = Depends(get_current_user)):
    """
    Create a new area contact.
    """
    area = get_by_code(db_session=db_session, code=area_in.code)

    if area and not area.is_deleted:
        raise HTTPException(status_code=400, detail="The area with this code already exists.")
    if area and area.is_deleted:
        area_in.is_deleted = 0
        area = update(
            db_session=db_session,
            area=area,
            area_in=area_in,
        )
        return area

    area_in.created_by = current_user.email
    area_in.updated_by = current_user.email
    area = new_create(db_session=db_session, area_in=area_in)
    return area


@router.get("/{area_id}", response_model=AreaRead)
def get_area(*, db_session: Session = Depends(get_db), area_id: int):
    """
    Get a area contact.
    """
    area = get(db_session=db_session, area_id=area_id)
    if not area:
        raise HTTPException(status_code=404, detail="The area with this id does not exist.")
    return area


@router.put("/{area_id}", response_model=AreaRead)
def update_area(
        *,
        db_session: Session = Depends(get_db),
        area_id: int,
        area_in: AreaUpdate, current_user: DispatchUser = Depends(get_current_user)
):
    """
    Update a area contact.
    """
    area = get(db_session=db_session, area_id=area_id)
    if not area:
        raise HTTPException(status_code=404, detail="The area with this id does not exist.")

    area_in.updated_at = datetime.now()

    area = update(
        db_session=db_session,
        area=area,
        area_in=area_in,
    )
    return area


@router.put("/area_code/{area_code}", response_model=AreaRead)
def update_area_by_code(
        *,
        db_session: Session = Depends(get_db),
        area_code: str,
        area_in: AreaUpdate, current_user: DispatchUser = Depends(get_current_user)
):
    """
    Update a area contact.
    """
    area = get_by_code(db_session=db_session, code=area_code)
    if not area:
        raise HTTPException(status_code=404, detail="The area with this id does not exist.")

    area_in.updated_by = current_user.email
    area = update(
        db_session=db_session,
        area=area,
        area_in=area_in,
    )

    return area


@router.delete("/{area_id}")
def delete_area(*, db_session: Session = Depends(get_db), area_id: int):
    """
    Delete a area contact.
    """
    area = get(db_session=db_session, area_id=area_id)
    if not area:
        raise HTTPException(status_code=404, detail="The area with this id does not exist.")

    delete(db_session=db_session, area_id=area_id)


@router.get("/item/codes")
def get_code(db_session: Session = Depends(get_db)):
    # print(id)
    ls = get_area_codes(db_session=db_session)
    return ls


@router.get("/item/codes_type")
def get_code_types(db_session: Session = Depends(get_db)):
    return get_area_codes_type_all(db_session=db_session)


@router.get("/item/codes/{area_type}")
def get_codes_type(area_type, db_session: Session = Depends(get_db)):
    return get_area_type_semi(db_session=db_session) if area_type == "semi" else get_area_type_finished(
        db_session=db_session)


@router.get("/item/get_area_by_site/{site_code}")
def get_area_by_site_views(*, db_session: Session = Depends(get_db), current_user: DispatchUser = Depends(get_current_user), site_code: str):
    # user = user_get(db_session=db_session, user_id=current_user.id)
    ls = get_area_by_site(db_session=db_session, site_code=site_code, mill_id=current_user.current_mill_id)
    return ls


@router.get("/item/get_site_by_area/{area_code}")
def get_site_by_area_code(*, db_session: Session = Depends(get_db), area_code: str):
    area_one = get_by_code(db_session=db_session, code=area_code)
    if not area_one:
        return {"area_code": "", "msg": "The area with this code does not exist."}
    site_id = area_one.site_id
    site_one = get_site_code(db_session=db_session, id=site_id)
    if not site_one:
        return {"site_code": "", "msg": "The site with this code does not exist."}
    site_type_one = get_site_type(db_session=db_session, id=site_one.site_type_id)
    if not site_type_one:
        return {"site_code": site_one.code, "site_type_code": "", "msg": "The site_type with this code does not exist."}
    return {"site_code": site_one.code, "site_type_code": site_type_one.code}


################### 新的区分 area code 的接口 ###################
@router.get("/item/code/site/{type}")
def get_site_common(*, db_session: Session = Depends(get_db), current_user: DispatchUser = Depends(get_current_user),
                    type: str):
    """
    选择semi 或finished  获取site code id
    """
    type = "s-semi" if type == "semi" else "f-finished_product"
    # user = user_get(db_session=db_session, user_id=current_user.id)
    return get_site_code_by_type(db_session=db_session, mill_id=current_user.current_mill_id, s_or_f=type)


@router.get("/item/code/site_type/{type}")
def get_site_type_common(*, db_session: Session = Depends(get_db),
                         current_user: DispatchUser = Depends(get_current_user), type: str):
    """
    选择semi 或finished  获取site type code id
    """
    type = "s-semi" if type == "semi" else "f-finished_product"
    # user = user_get(db_session=db_session, user_id=current_user.id)
    return get_site_type_code_by_type(db_session=db_session, mill_id=current_user.current_mill_id, s_or_f=type)


@router.get("/item/code/semi")
def get_area_semi(*, db_session: Session = Depends(get_db), current_user: DispatchUser = Depends(get_current_user)):
    # user = user_get(db_session=db_session, user_id=current_user.id)
    return get_area_code_by_type_semi(db_session=db_session, mill_id=current_user.current_mill_id)


@router.get("/item/code/finished")
def get_area_finished(*, db_session: Session = Depends(get_db), current_user: DispatchUser = Depends(get_current_user)):
    # user = user_get(db_session=db_session, user_id=current_user.id)
    return get_area_code_by_type_finished(db_session=db_session, mill_id=current_user.current_mill_id)


@router.get("/item/site/code/semi")
def get_site_semi(*, db_session: Session = Depends(get_db), current_user: DispatchUser = Depends(get_current_user)):
    """
    获取semi 的site id code
    """
    # user = user_get(db_session=db_session, user_id=current_user.id)
    return get_site_code_by_type(db_session=db_session, mill_id=current_user.current_mill_id, s_or_f="s-semi")


@router.get("/item/site_type/code/semi")
def get_site_type_semi(*, db_session: Session = Depends(get_db),
                       current_user: DispatchUser = Depends(get_current_user)):
    """
    获取semi 的site type id code
    """
    # user = user_get(db_session=db_session, user_id=current_user.id)
    return get_site_type_code_by_type(db_session=db_session, mill_id=current_user.current_mill_id, s_or_f="s-semi")

@router.get("/item/code/semi/move")
def get_area_semi_move(*, db_session: Session = Depends(get_db), current_user: DispatchUser = Depends(get_current_user)):
    # user = user_get(db_session=db_session, user_id=current_user.id)
    return get_area_code_by_type_move(db_session=db_session, mill_id=current_user.current_mill_id)


@router.get("/item/site/code/semi/move")
def get_site_semi_move(*, db_session: Session = Depends(get_db), current_user: DispatchUser = Depends(get_current_user)):
    """
    获取semi 的site id code
    """
    # user = user_get(db_session=db_session, user_id=current_user.id)
    return get_site_code_by(db_session=db_session, mill_id=current_user.current_mill_id, s_or_f="s-semi")

@router.get("/item/site_type/code/semi/move")
def get_site_type_semi_move(*, db_session: Session = Depends(get_db),
                       current_user: DispatchUser = Depends(get_current_user)):
    """
    获取semi 的site type id code
    """
    # user = user_get(db_session=db_session, user_id=current_user.id)
    return get_site_type_code_by(db_session=db_session, mill_id=current_user.current_mill_id, s_or_f="s-semi")


@router.get("/item/site/code/finished")
def get_area_of_finished(*, db_session: Session = Depends(get_db)):
    """
    获取finished 的area code
    """
    result = db_session.query(Area.code).filter((Area.type == "f-finished_product")).all()
    if not result:
        return []
    area_codes = []
    area_codes = [i[0] for i in result]
    return area_codes


@router.get("/item/codes/semi")
def get_area_of_finished(*, db_session: Session = Depends(get_db)):
    """
    获取semi 的area code
    """
    result = db_session.query(Area.code).filter((Area.type == "s-semi")).all()
    if not result:
        return []
    area_codes = []
    area_codes = [i[0] for i in result]
    return area_codes



###############################################################

################### 重置site type site area ####################
try:
    from dispatch.contrib.import_data.area.update_location_data import UpdateLocationData20241226, UpdateLocationData20250203

    @router.post("/reset/site_type")
    def reset_site_type(*, db_session: Session = Depends(get_db)):
        UpdateLocationData20241226.insert_site_type_location_data(db_session)
        return {"msg": "success"}


    @router.post("/reset/site")
    def reset_site(*, db_session: Session = Depends(get_db)):
        UpdateLocationData20241226.insert_site_location_data(db_session)
        return {"msg": "success"}


    @router.post("/reset/area")
    def reset_area(*, db_session: Session = Depends(get_db)):
        UpdateLocationData20241226.insert_area_location_data(db_session)
        return {"msg": "success"}


    @router.post("/reset/location")
    def reset_location(*, db_session: Session = Depends(get_db)):
        UpdateLocationData20241226.insert_site_type_location_data(db_session)
        UpdateLocationData20241226.insert_site_location_data(db_session)
        UpdateLocationData20241226.insert_area_location_data(db_session)
        return {"msg": "reset success!"}

    @router.post("/reset/20250203/location")
    def reset_202503(*, db_session: Session = Depends(get_db)):
        UpdateLocationData20250203.reset_location(db_session)
        return {"msg": "reset success!"}

    ################################################################
except ImportError as e:
    pass