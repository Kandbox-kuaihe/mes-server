from datetime import datetime
from enum import Enum
from typing import Optional
from dispatch.area.models import Area
from dispatch.database import get_db

from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks, Query
from sqlalchemy.orm import Session
from dispatch.semi_admin.semi.models import Semi
from dispatch.system_admin.auth.models import DispatchUser
from dispatch.system_admin.auth.service import get_current_user

from dispatch.database_util.service import common_parameters, search_filter_sort_paginate
from .models import (
    SemiLoadCreate,
    SemiLoadPagination,
    SemiLoadRead,
    SemiLoadTip,
    SemiLoadUpdate,
    SemiLoadReceiving,
    SemiLoadDespatch
)
from .service import create, delete, get, get_by_code, update, update_semi_to_semi_load
# from dispatch.contrib.message_admin.message_server.server import call_method
from dispatch.message_admin.message_server.models import PushMessageData
from ...config import get_mill_ops, MILLEnum

router = APIRouter()

# 定义一个201消息枚举类
class MessageM201(Enum):
    id = 201
    type = "M"


@router.get("/", response_model=SemiLoadPagination)
def get_SemiLoads(*, location: Optional[str] = None, common: dict = Depends(common_parameters), status: Optional[str] = None):
    if location:
        common["fields"].append("location")
        common["ops"].append("eq")
        common["values"].append(location)
    if status:
        common["fields"].append("status")
        common["ops"].append("eq")
        common["values"].append(status)

    return search_filter_sort_paginate(model="SemiLoad", **common)


@router.post("/", response_model=SemiLoadRead)
def create_SemiLoad(*, request: Request, background_tasks: BackgroundTasks, db_session: Session = Depends(get_db), semi_load_in: SemiLoadCreate,
                 current_user: DispatchUser = Depends(get_current_user)):
    """
    Create a new SemiLoad contact.
    """
    
    semiLoad = get_by_code(db_session=db_session,code=semi_load_in.semi_load_code)
    
    
    if semiLoad:
        raise HTTPException(status_code=400, detail="The semiLoad with this code already exists.")
    
    semi_load_in.created_by = current_user.email
    semi_load_in.updated_by = current_user.email
    semi_load_in.mill_id = current_user.current_mill_id
    semi = create(db_session=db_session, semi_load_in=semi_load_in)

    # trigger M201 message
    if get_mill_ops(current_user.current_mill_id) == MILLEnum.MILL1:
        message = PushMessageData(id=201, type="srsmpc", msg=str(semi.id))
        try:
            from dispatch.contrib.message_admin.message_server.server import call_method
            call_method(request, background_tasks, db_session, current_user, message)
        except ImportError as e:
            raise HTTPException(status_code=400, detail=str(e))

    return semi


@router.get("/{semi_load_id}", response_model=SemiLoadRead)
def get_semi(*, db_session: Session = Depends(get_db), semi_load_id: int):
    """
    Get a semi contact.
    """
    semi = get(db_session=db_session, id=semi_load_id)
    if not semi:
        raise HTTPException(status_code=400, detail="The semi with this id does not exist.")
    return semi


@router.put("/{semi_load_id}", response_model=SemiLoadRead)
def update_semi(
    *,
    db_session: Session = Depends(get_db),
    semi_load_id: int,
    semi_load_in: SemiLoadUpdate, current_user: DispatchUser = Depends(get_current_user)
):
    """
    Update a semi contact.
    """
    semi = get(db_session=db_session, id=semi_load_id)
    if not semi:
        raise HTTPException(status_code=400, detail="The semi with this id does not exist.")

    semi = update(
        db_session=db_session,
        semi=semi,
        semi_load_in=semi_load_in,
    )
    return semi


@router.put("/update_semi/{semi_id}")
def finished_product_update(
    *,
    db_session: Session = Depends(get_db),
    semi_load_in: SemiLoadRead,
    semi_id: int,
    current_user: DispatchUser = Depends(get_current_user)
):
    semi_load_in.updated_at = datetime.now()
    semi_load_in.updated_by = current_user.email
    return update_semi_to_semi_load(db_session=db_session, semi_load_in=semi_load_in, semi_id=semi_id)


@router.put("/semi_code/{semi_code}", response_model=SemiLoadRead)
def update_semi_by_code(
    *,
    db_session: Session = Depends(get_db),
    semi_code: str,
    semi_load_in: SemiLoadUpdate, current_user: DispatchUser = Depends(get_current_user)
):
    """
    Update a semi contact.
    """
    semi = get_by_code(db_session=db_session, code=semi_code)
    if not semi:
        raise HTTPException(status_code=400, detail="The semi load with this id does not exist.")

    semi_load_in.updated_by = current_user.email
    semi = update(
        db_session=db_session,
        semi=semi,
        semi_load_in=semi_load_in,
    )

    return semi


@router.delete("/{semi_load_id}", response_model=SemiLoadRead)
def delete_semi(*, db_session: Session = Depends(get_db), semi_load_id: int):
    """
    Delete a semi contact.
    """
    semi = get(db_session=db_session, id=semi_load_id)
    if not semi:
        raise HTTPException(status_code=400, detail="The semi with this id does not exist.")

    return delete(db_session=db_session, id=semi_load_id)


@router.post("/update_status")
def update_semi_load_receiving(*, db_session: Session = Depends(get_db), semi_load_ids: SemiLoadReceiving):
    """
    Update a semi load status.
    """

    if len(semi_load_ids.ids) <=0:
        raise HTTPException(status_code=400, detail="Please select at least one semi load.")
    
    for semi_load_id in semi_load_ids.ids:
        semi = db_session.query(Semi).filter(Semi.semi_load_id==semi_load_id).all()
        if len(semi) <= 0:
            raise HTTPException(status_code=400, detail="No associated Semi information.")

        if not semi_load_ids.is_overwrite:
            # check semi spec id
            spec_id_set = set([s.spec_id for s in semi if s.spec_id])
            if len(spec_id_set) == 0:
                raise HTTPException(status_code=400, detail=f"Selected semi load's spec is not exist. Please select overwrite option.")

            if len(spec_id_set) > 1:
                raise HTTPException(status_code=400, detail=f"Selected semi load's spec is not same. Please select overwrite option.")
        
        semi_load = get(db_session=db_session, id=semi_load_id)
        semi_load.status = "received"
        db_session.add(semi_load)
    db_session.commit()
    return "success"


@router.post("/tip")
def update_semi_load_tip(*, db_session: Session = Depends(get_db), semi_load_tip: SemiLoadTip):

    if len(semi_load_tip.ids) <=0:
        raise HTTPException(status_code=400, detail="Please select at least one semi load.")
    
    area = db_session.query(Area).filter(Area.id==semi_load_tip.to_area_id).first()

    if not area:
        raise HTTPException(status_code=400, detail="The area does not exist.")
    
    semis = db_session.query(Semi).filter(Semi.semi_load_id.in_(semi_load_tip.ids)).all()


    if semis:
        if not semi_load_tip.is_overwrite:
            # check semi spec id
            spec_id_set = set([semi.spec_id for semi in semis if semi.spec_id])
            if len(spec_id_set) == 0:
                raise HTTPException(status_code=400, detail=f"Selected semi load's spec is not exist. Please select overwrite option.")

            if len(spec_id_set) > 1:
                raise HTTPException(status_code=400, detail=f"Selected semi load's spec is not same. Please select overwrite option.")

        for semi in semis:
            semi.area_id = area.id
            semi.semi_status = "Tip"
            semi.updated_at = datetime.now()
            db_session.add(semi)
    for load_id in semi_load_tip.ids:
        semi_load = get(db_session=db_session, id=load_id)
        semi_load.status = "received"
        semi_load.to_area_id = area.id
        semi_load.location = "Default Location"
        db_session.add(semi_load)

    db_session.commit()
    return "success"


@router.get("/cast/get")
def get_cast_by_semi_load(*, semi_load_ids: str = Query(...), db_session: Session = Depends(get_db)):
    casts = []
    for semi_load_id in semi_load_ids.split(","):
        semi = db_session.query(Semi).filter(Semi.semi_load_id==int(semi_load_id)).first()
        if semi:
            casts.append({
                "id": semi.cast.id if semi.cast else None,
                "cast_code": semi.cast.cast_code if semi.cast else None,
            })
    
    return casts


@router.post("/dispatch")
def despatch_semi_load(
    *,
    db_session: Session = Depends(get_db),
    semi_load_despatch: SemiLoadDespatch
):
    """
    Mark selected semi‑loads as dispatched.
    """
    if not semi_load_despatch.ids:
        raise HTTPException(status_code=400, detail="Please select at least one semi load.")

    # semis = (
    #     db_session.query(Semi)
    #     .filter(Semi.semi_load_id.in_(semi_load_despatch.ids))
    #     .all()
    # )
    # if not semi_load_despatch.is_overwrite:
    #     # check semi spec id
    #     spec_id_set = set([s.spec_id for s in semis if s.spec_id])
    #     if len(spec_id_set) == 0:
    #         raise HTTPException(status_code=400, detail=f"Selected semi load's spec is not exist. Please select overwrite option.")

    #     if len(spec_id_set) > 1:
    #         raise HTTPException(status_code=400, detail=f"Selected semi load's spec is not same. Please select overwrite option.")
    
    for load_id in semi_load_despatch.ids:
        semi_load = get(db_session=db_session, id=load_id)
        if not semi_load:
            raise HTTPException(
                status_code=400,
                detail=f"The semi load with id {load_id} does not exist."
            )
        semi_load.status = "In Transit"
        semi_load.location = "DESPATCHED"
        db_session.add(semi_load)

    db_session.commit()
    return "success"