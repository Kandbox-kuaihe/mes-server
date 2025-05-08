import csv
import io
from uuid import uuid4

import numpy as np
import pandas as pd
import os
from fastapi.responses import FileResponse

from dispatch.database import get_db
from typing import List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, BackgroundTasks, Query, Request
from sqlalchemy import select
from sqlalchemy.orm import Session
from dispatch.runout_admin.runout_list.models import Runout
from dispatch.order_admin.order_group.models import OrderGroup
from dispatch.rolling.rolling_list.models import Rolling
from dispatch.system_admin.auth.models import DispatchUser
from dispatch.system_admin.auth.service import get_current_user
from dispatch.semi_admin.semi_hold_reason import service as hold_service
from dispatch.semi_admin.semi_hold_reason.models_secondary import semi_hold 
# from dispatch.contrib.message_admin.message_server.server import call_method
from dispatch.message_admin.message_server.models import PushMessageData
from dispatch.spec_admin.quality.models import Quality

from dispatch.database_util.service import common_parameters, search_filter_sort_paginate
from .models import (
    SemiHoldReason,
    ReworkRead,
    ReworkUpdate,
    ReworkComplete,
)
from .service import (
    get_by_semi_code_rolling_code,
    get_area_location,
    bulk_get_semi,
    block_unblock_semi,
    update_semi_by_move,
    update_rework,
    update_rework_complete,
    create_defects, update_semi_scrap,
    reserve_unreserve_semi, update_semi_return,
    trigger_m249,
    bulk_semi_bloom_move,
    compute_bloom_total,
    export_to_excel,
    import_dict_to_db_new, import_cast_semi_to_db,
)
from dispatch.semi_admin.semi_move_history.service import bulk_create_move_history
from dispatch.area.service import get_by_code as get_by_area_code
from dispatch.site.service import get_by_code as get_by_site_code
from .models import Semi, SemiCreate, SemiPagination, SemiRead, SemiUpdate, SemiBatchUpdate
from .service import create, delete, get, get_by_code, update, find_max_semi_code_by_cast, get_semi_query
from dispatch.semi_admin.semi_move_history.models import SemiMoveHistory, SemiMoveHistoryChangTypeEnum
from dispatch.area.models import Area
from ..semi_load.models import SemiLoad
from ...cast.models import Cast
from ...config import get_mill_ops, MILLEnum
from ...defect_reason.models import DefectReason
from ...site.models import Site
# from ...contrib.message_admin.message_server import message_strategy, server as MessageServer
from dispatch.semi_admin.semi_load import service as semi_load_service

import logging

logging.basicConfig(level=logging.INFO)

from dispatch.log import getLogger
log = getLogger(__name__)


router = APIRouter()
logger = getLogger(__name__)


BLOOM_SIZE_SUFFIX_MAPPING = {
    "290 * 231": "D",
    "254 * 254": "L",
    "355 * 305": "R",
    "330 * 254": "T",
    "283 * 230": "J",
    "240 * 240": "H",
    "290 * 230": "B",
    "180 * 180": "U"
}


@router.get("/", response_model=SemiPagination)
def get_semis(*, common: dict = Depends(common_parameters), db_session: Session = Depends(get_db)):
    query = db_session.query(Semi).outerjoin(Site, Semi.site_id == Site.id
                                ).outerjoin(Area, Semi.area_id == Area.id
                                ).outerjoin(Rolling, Semi.rolling_id == Rolling.id
                                ).outerjoin(OrderGroup, Semi.order_group_id == OrderGroup.id
                                ).outerjoin(Runout, Semi.id == Runout.semi_id)
    
    common['query'] = query
    if common["sort_by"] == ['curren_allocated_rolling']:
        common["sort_by"] = ["rolling.rolling_code"]
    if common["sort_by"] == ['curren_allocated_block']:
        common["sort_by"] = ["order_group.group_code"]
    if common["sort_by"] == ['cast_code']:
        common["sort_by"] = ["cast.cast_code"]
    if common["sort_by"] == ['runout_code']:
        common["sort_by"] = ["runout.runout_code"]


    if common["query_str"]:
        common["filter_type"] = "and"
        # common["fields"] = ["semi_code", "rolling.rolling_code"]
        # common["ops"] = ["like", "like"]
        # common["values"] = [f"%{common['query_str']}%", f"%{common['query_str']}%"]
        semi_ids = get_by_semi_code_rolling_code(db_session = common["db_session"], 
                                                 semi_code = common['query_str'],
                                                   rolling_code = common['query_str'],
                                                 area_code = common['query_str'],
                                                 group_code = common['query_str'])
        if common.get("fields") and common.get("ops") and common.get("values"):
            common["fields"].append("id")
            common["ops"].append("in")
            common["values"].append([i[0] for i in semi_ids])
            # common["filter_type"] = "or"
        else:
            # common["filter_type"] = "or"
            common["fields"] = ["id"]
            common["ops"] = ["in"]
            common["values"] = [[i[0] for i in semi_ids]]


        # 清空原来的查询字符串
        common["query_str"] = ''
    result_item = search_filter_sort_paginate(model="Semi", **common)
    result = get_semi_query(db_session=common['db_session'], result_item=result_item)
    return result


@router.get("/get_all/{request_first_flag}", response_model=SemiPagination)
def get_semis_new(*, db_session: Session = Depends(get_db), request_first_flag,  common: dict = Depends(common_parameters), area_code: List[str] = Query([], alias="area_code[]")):
    query = db_session.query(Semi).outerjoin(Rolling, Semi.rolling_id == Rolling.id
                                ).outerjoin(OrderGroup, Semi.order_group_id == OrderGroup.id
                                ).outerjoin(Area, Semi.area_id == Area.id
                                ).outerjoin(SemiLoad, Semi.semi_load_id == SemiLoad.id).outerjoin(Cast, Semi.cast_id == Cast.id)

    if area_code:
        query = query.filter(Area.code.in_(area_code) & (Area.type == "s-semi"))

    common['query'] = query

    if common["sort_by"] == ['curren_allocated_rolling']:
        common["sort_by"] = ["rolling.rolling_code"]
    if common["sort_by"] == ['curren_allocated_block']:
        common["sort_by"] = ["order_group.group_code"]
    if common["sort_by"] == ['cast_code']:
        common["sort_by"] = ["cast.cast_code"]


    if common["query_str"]:
        # common["filter_type"] = "or"
        # common["fields"] = ["semi_code", "rolling.rolling_code"]
        # common["ops"] = ["like", "like"]
        # common["values"] = [f"%{common['query_str']}%", f"%{common['query_str']}%"]
        semi_ids = get_by_semi_code_rolling_code(db_session = common["db_session"],
                                                 semi_code = common['query_str'],
                                                   rolling_code = common['query_str'],
                                                 area_code = common['query_str'],
                                                 group_code = common['query_str'])
        if common.get("fields") and common.get("ops") and common.get("values"):
            common["fields"].append("id")
            common["ops"].append("in")
            common["values"].append([i[0] for i in semi_ids])
            # common["filter_type"] = "or"
        else:
            # common["filter_type"] = "or"
            common["fields"] = ["id"]
            common["ops"] = ["in"]
            common["values"] = [[i[0] for i in semi_ids]]
        # 清空原来的查询字符串
        common["query_str"] = ''

    data = search_filter_sort_paginate(model="Semi", **common)
    semi_data = data["items"]

    if semi_data:
        for semi in semi_data:
            
            for hold in semi.semi_hold_reason:
                is_hold = (
                    db_session.query(semi_hold)
                    .filter(
                        semi_hold.c.semi_id == semi.id,
                        semi_hold.c.hold_reason_id == hold.id,
                    )
                    .first()
                )
                if is_hold:
                    hold.comment = is_hold.comment
    return data

@router.get("/get_semi/{rolling_id}", response_model=SemiPagination)
def get_semis_new(*, rolling_id, common: dict = Depends(common_parameters)):
    if rolling_id == "undefined" or not rolling_id.isdigit():
        return {"error": "Invalid rolling_id provided."}
    common["fields"] = ["rolling_id"]
    common["ops"] = ["=="]
    common["values"] = [rolling_id]


    # 执行搜索、过滤、排序和分页
    result_item = search_filter_sort_paginate(model="Semi", **common)
    result = get_semi_query(db_session=common['db_session'], result_item=result_item)
    return result

@router.get("/get_semi_spec/{cast_id}", response_model=SemiPagination)
def get_semi_spec(cast_id, common: dict = Depends(common_parameters)):
    if common["sort_by"] == ['cast_code']:
        common["sort_by"] = ["cast.cast_code"]
    common["fields"] = ["cast_id","semi_type"]
    common["ops"] = ["==","!="]
    common["values"] = [cast_id,'BLM']
    
    return search_filter_sort_paginate(model="Semi", **common)


@router.post("/", response_model=SemiRead)
def create_semi(
        *,
        request: Request,
        background_tasks: BackgroundTasks,
        db_session: Session = Depends(get_db),
        semi_in: SemiCreate,
        current_user: DispatchUser = Depends(get_current_user)
):
    """
    Create a new semi contact.
    """
    semi = get_by_code(db_session=db_session, code=semi_in.semi_code)
    if semi:
        raise HTTPException(status_code=400, detail="The semi with this code already exists.")

    if semi_in.quality_id:
        quality_code = db_session.query(Quality).filter(Quality.id == semi_in.quality_id).first()
        semi_in.quality_code = quality_code.code

    semi_in.created_by = current_user.email
    semi_in.updated_by = current_user.email
    semi = create(db_session=db_session, semi_in=semi_in)

    # trigger M200 message
    if get_mill_ops(current_user.current_mill_id) == MILLEnum.MILL1 and semi_in.semi_status == "created":
        message = PushMessageData(id=200, type="srsmpc", msg=str(semi.id))
        try:
            from dispatch.contrib.message_admin.message_server.server import call_method
            call_method(request, background_tasks, db_session, current_user, message)
        except ImportError as e:
            raise HTTPException(status_code=400, detail=str(e))

     # Log create operation
    history_entry = {
        "uuid": str(uuid4()),
        "created_by": current_user.email,
        "change_type": SemiMoveHistoryChangTypeEnum.CREATE,
        "code": semi.semi_code,
        "semi_id": semi.id,
        "area_no": semi.area.code if semi.area else None,
        "site_no": semi.site.code if semi.site else None,
        "location": semi.location,
        "rolling_code": semi.rolling.rolling_code if semi.rolling else None,
        "cast_no": semi.cast.cast_code if semi.cast else None,
        "order_group_code": semi.order_group.group_code if semi.order_group else None,
        "quality_code": semi.quality_code if semi.quality_code else None,
        "scarfed_status": semi.scarfed_status if semi.scarfed_status else None,
        "skelp_no": semi.skelp_code if semi.skelp_code else None,
        "semi_no": semi.semi_code if semi.semi_code else None,
        "semi_status": semi.semi_status if semi.semi_status else None,
        "width": semi.width_mm if semi.width_mm else None,
        "thickness": semi.thickness_mm if semi.thickness_mm else None,
        "length": semi.length_mm if semi.length_mm else None,
        "estimated_weight": semi.estimated_weight_kg if semi.estimated_weight_kg else None,
        "semi_load": semi.semi_load if semi.semi_load else None,
        "semi_charge_seq": semi.semi_charge_seq if semi.semi_charge_seq else None,
        "semi_cut_seq": semi.semi_cut_seq if semi.semi_cut_seq else None,
        "semi_type": semi.semi_type if semi.semi_type else None,
        "hold_reason": semi.hold_reason if semi.hold_reason else None,
        "comment": semi.comment if semi.comment else None,
    }
    bulk_create_move_history(db_session=db_session, semi_move_histories_in=[history_entry])
    return semi

@router.put("/rework", response_model=List[ReworkRead])
def rework_semi(
    *,
    db_session: Session = Depends(get_db),
    rework_in: ReworkUpdate,
    current_user: DispatchUser = Depends(get_current_user),
):
    """
    Perform rework updates for semis and log history.
    """
    uuid = uuid4()
    his = []

    # Call the update_rework function
    result = update_rework(db_session=db_session, update_in=rework_in, current_user=current_user)

    # Log the operation for each semi
    for id in rework_in.ids:
        semi = get(db_session=db_session, semi_id=id)
        his.append({
            "uuid": uuid,
            "semi_id": semi.id,
            "created_by": current_user.email,
            "change_type": SemiMoveHistoryChangTypeEnum.REWORK,
            "code": semi.semi_code,
            "area_no": semi.area.code if semi.area else None,
            "site_no": semi.site.code if semi.site else None,
            "location": semi.location,
            "rolling_code": semi.rolling.rolling_code if semi.rolling else None,
            "cast_no": semi.cast.cast_code if semi.cast else None,
            "order_group_code": semi.order_group.group_code if semi.order_group else None,
            "quality_code": semi.quality_code if semi.quality_code else None,
            "rework_comment": semi.rework_comment if semi.rework_comment else None, 
            "rework_type": semi.rework_type if semi.rework_type else None,
            "rework_area": semi.area_id if semi.area_id else None,
        })

    # Create history entries
    bulk_create_move_history(db_session=db_session, semi_move_histories_in=his)

    return result

@router.put("/return")
def return_semi(
    *,
    db_session: Session = Depends(get_db),
    semi_in: SemiUpdate,
    current_user: DispatchUser = Depends(get_current_user),
):
    semi_in.updated_at = datetime.now()
    semi_in.updated_by = current_user.email
    return update_semi_return(db_session=db_session, semi_in=semi_in)


@router.put("/scrap/{semi_id}", response_model=SemiRead)
def scrap_semi(
        *,
        db_session: Session = Depends(get_db),
        semi_id: int,
        current_user: DispatchUser = Depends(get_current_user),
        semi_in: SemiUpdate,
):
    semi = get(db_session=db_session, semi_id=semi_id)
    if not semi:
        raise HTTPException(status_code=404, detail="Semi not found")

    defect = db_session.query(DefectReason).filter(DefectReason.id == semi_in.defect_reason_id).first()
    if not defect:
        raise HTTPException(status_code=404, detail="Defect Reason not found")

    semi_in.updated_by = current_user.email
    semi_in.updated_at = datetime.now()
    return update_semi_scrap(db_session=db_session, semi=semi, semi_in=semi_in)


@router.put("/rework/complete")
def rework_semi_complete(
    *,
    db_session: Session = Depends(get_db),
    rework_complete_in: ReworkComplete,
    current_user: DispatchUser = Depends(get_current_user),
):
    history_entries = []
    stmt = select(Semi).where(Semi.id.in_(rework_complete_in.ids))
    for semi in db_session.scalars(stmt):
        if not semi:
            raise HTTPException(status_code=400, detail=f"The semi with this id {semi.id} does not exists.")
        if semi.rework_status != 'Rework':
            raise HTTPException(status_code=400, detail=f"The semi with this id  {semi.id} is not rework.")
        if semi.semi_status in ['Transit', 'In Transit']:
            raise HTTPException(status_code=400, detail="The semi is Transit or In Transit")
        history_entry = {
            "uuid": str(uuid4()),
            "semi_id": semi.id,
            "created_by": current_user.email,
            "change_type": SemiMoveHistoryChangTypeEnum.REWORK_COMPLETE,
            "code": semi.semi_code,
            "area_no": semi.area.code if semi.area else None,
            "site_no": semi.site.code if semi.site else None,
            "location": semi.location,
            "rolling_code": semi.rolling.rolling_code if semi.rolling else None,
            "cast_no": semi.cast.cast_code if semi.cast else None,
            "order_group_code": semi.order_group.group_code if semi.order_group else None,
            "quality_code": semi.quality_code if semi.quality_code else None,
            "scarfed_status": semi.scarfed_status if semi.scarfed_status else None,
            "skelp_no": semi.skelp_code if semi.skelp_code else None,
            "semi_no": semi.semi_code if semi.semi_code else None,
            "semi_status": semi.semi_status if semi.semi_status else None,
            "width": semi.width_mm if semi.width_mm else None,
            "thickness": semi.thickness_mm if semi.thickness_mm else None,
            "length": semi.length_mm if semi.length_mm else None,
            "estimated_weight": semi.estimated_weight_kg if semi.estimated_weight_kg else None,
            "semi_load": semi.semi_load if semi.semi_load else None,
            "semi_charge_seq": semi.semi_charge_seq if semi.semi_charge_seq else None,
            "semi_cut_seq": semi.semi_cut_seq if semi.semi_cut_seq else None,
            "semi_type": semi.semi_type if semi.semi_type else None,
            "hold_reason": semi.hold_reason if semi.hold_reason else None,
            "comment": semi.comment if semi.comment else None,
        }
        history_entries.append(history_entry)

    bulk_create_move_history(db_session=db_session, semi_move_histories_in=history_entries)

    update_rework_complete(db_session=db_session, rework_complete_in=rework_complete_in)

    return {"status": "ok"}


@router.get("/{semi_id}", response_model=SemiRead)
def get_semi(*, db_session: Session = Depends(get_db), semi_id: int):
    """
    Get a semi contact.
    """
    semi = get(db_session=db_session, semi_id=semi_id)
    if not semi:
        raise HTTPException(status_code=400, detail="The semi with this id does not exist.")
    # 将semi_hold中间表的comment查出来
    if semi.semi_hold_reason:
        for hold in semi.semi_hold_reason:
            is_hold = (
                db_session.query(semi_hold)
                .filter(
                    semi_hold.c.finished_product_id == semi.id,
                    semi_hold.c.hold_reason_id == hold.id,
                )
                .first()
            )
            if is_hold:
                hold.comment = is_hold.comment
    return semi



@router.put("/{semi_id}", response_model=SemiRead)
def update_semi(
        *,
        background_tasks: BackgroundTasks,
        db_session: Session = Depends(get_db),
        semi_id: int,
        semi_in: SemiUpdate,
        current_user: DispatchUser = Depends(get_current_user)
):
    """
    Update a semi contact.
    """
    semi = get(db_session=db_session, semi_id=semi_id)
    if not semi:
        raise HTTPException(status_code=400, detail="The semi with this id does not exist.")
    semi.updated_by = current_user.email
    semi.comment = semi_in.comment
    db_session.add(semi)
    db_session.commit()
    # Log update operation
    # history_entry = {
    #     "uuid": str(uuid4()),
    #     "semi_id": semi.id,
    #     "created_by": current_user.email,
    #     "change_type": SemiMoveHistoryChangTypeEnum.UPDATE,
    #     "code": semi.semi_code,
    #     "area_no": semi.area.code if semi.area else None,
    #     "site_no": semi.site.code if semi.site else None,
    #     "location": semi.location,
    #     "rolling_code": semi.rolling.rolling_code if semi.rolling else None,
    #     "cast_no": semi.cast.cast_code if semi.cast else None,
    #     "order_group_code": semi.order_group.group_code if semi.order_group else None,
    #     "quality_code": semi.quality_code if semi.quality_code else None,
    #     "scarfed_status": semi.scarfed_status if semi.scarfed_status else None,
    #     "skelp_no": semi.skelp_code if semi.skelp_code else None,
    #     "semi_no": semi.semi_code if semi.semi_code else None,
    #     "semi_status": semi.semi_status if semi.semi_status else None,
    #     "width": semi.width_mm if semi.width_mm else None,
    #     "thickness": semi.thickness_mm if semi.thickness_mm else None,
    #     "length": semi.length_mm if semi.length_mm else None,
    #     "estimated_weight": semi.estimated_weight_kg if semi.estimated_weight_kg else None,
    #     "semi_load": semi.semi_load if semi.semi_load else None,
    #     "semi_charge_seq": semi.semi_charge_seq if semi.semi_charge_seq else None,
    #     "semi_cut_seq": semi.semi_cut_seq if semi.semi_cut_seq else None,
    #     "semi_type": semi.semi_type if semi.semi_type else None,
    #     "hold_reason": semi.hold_reason if semi.hold_reason else None,
    #     "comment": semi.comment if semi.comment else None,
    # }
    if semi_in.quality_id:
        quality_code = db_session.query(Quality.code).filter(Quality.id == semi_in.quality_id).scalar()
        semi_in.quality_code = quality_code
    try:
        from ...contrib.message_admin.message_server import server as MessageServer
        strategy = MessageServer.MessageStrategy71()
        strategy.send_pc_71(db_session, semi, background_tasks, current_user.current_mill_code)
    except ImportError as e:
        logger.warning(f"ERROR in import: {str(e)}")
    except Exception as e:
        logger.error(f"ERROR in send_pc_71: {str(e)}")
    # bulk_create_move_history(db_session=db_session, semi_move_histories_in=[history_entry])
    update(db_session=db_session, semi=semi, semi_in=semi_in)

    return semi


@router.put("/semi_code/{semi_code}", response_model=SemiRead)
def update_semi_by_code(
        *,
        db_session: Session = Depends(get_db),
        semi_code: str,
        semi_in: SemiUpdate,
        current_user: DispatchUser = Depends(get_current_user)
):
    """
    Update a semi contact.
    """
    semi = get_by_code(db_session=db_session, code=semi_code)
    if not semi:
        raise HTTPException(status_code=400, detail="The semi with this id does not exist.")

    semi_in.updated_by = current_user.email
    semi = update(
        db_session=db_session,
        semi=semi,
        semi_in=semi_in,
    )

    return semi


@router.get("/semi_code/{semi_code}", response_model=SemiRead)
def get_semi_by_code(
        *,
        db_session: Session = Depends(get_db),
        semi_code: str,
        current_user: DispatchUser = Depends(get_current_user)
):
    """
    Get a semi by its semi code.
    """
    semi = get_by_code(db_session=db_session, code=semi_code)
    if not semi:
        raise HTTPException(status_code=404, detail="Semi not found")
    return semi

@router.post("/block")
def block_semis(
        *,
        db_session: Session = Depends(get_db),
        semis_in: List[SemiBatchUpdate],
        current_user: DispatchUser = Depends(get_current_user)
):
    """
    Block semis.
    """
    updated_at = datetime.now()
    uuid = uuid4()
    his = []
    msg = "Block Success"

    # Call the block_unblock_semi function
    flag = block_unblock_semi(db_session=db_session, semis_in=semis_in)

    for semi_in in semis_in:
        semi = get(db_session=db_session, semi_id=semi_in.id)
        his.append({
            "uuid": uuid,
            "semi_id": semi.id,
            "created_by": current_user.email,
            "change_type": SemiMoveHistoryChangTypeEnum.BLOCK,
            "code": semi.semi_code,
            "block_quantity": semi_in.block_quantity,
            "semi_charge_seq": semi_in.semi_charge_seq,
            "area_no": semi.area.code if semi.area else None,
            "site_no": semi.site.code if semi.site else None,
            "location": semi.location,
            "rolling_code": semi.rolling.rolling_code if semi.rolling else None,
            "cast_no": semi.cast.cast_code if semi.cast else None,
            "order_group_code": semi.order_group.group_code if semi.order_group else None,
        })

    bulk_create_move_history(db_session=db_session, semi_move_histories_in=his)
    return flag, msg


@router.post("/unblock")
def unblock_semis(
        *,
        background_tasks: BackgroundTasks,
        db_session: Session = Depends(get_db),
        semis_in: List[SemiBatchUpdate],
        current_user: DispatchUser = Depends(get_current_user)
):
    """
    Unblock semis.
    """
    updated_at = datetime.now()
    uuid = uuid4()
    his = []
    msg = "UnBlock Success"
    # Call the block_unblock_semi function
    flag = block_unblock_semi(db_session=db_session, semis_in=semis_in)

    for semi_in in semis_in:
        semi = get(db_session=db_session, semi_id=semi_in.id)
        if not semi_in.semi_code:
            if semi_in.rolling_id and semi_in.order_group_id:
                change = SemiMoveHistoryChangTypeEnum.BLOCK
                msg = "Block Success"
            else:
                change = SemiMoveHistoryChangTypeEnum.UNBLOCK
                try:
                    from ...contrib.message_admin.message_server import  server as MessageServer
                    strategy = MessageServer.MessageStrategy6()
                    strategy.send_pc_6(db_session, semi, background_tasks, current_user.current_mill_code)
                except ImportError as e:
                    log.warning("ImportError fail")
                except Exception as e:
                    log.warning("send_pc_6 fail")
                msg = "UnBlock Success"
            his.append({
                "uuid": uuid,
                "semi_id": semi.id,
                "created_by": current_user.email,
                "change_type": SemiMoveHistoryChangTypeEnum.UNBLOCK,
                "code": semi.semi_code,
                "semi_charge_seq": semi_in.semi_charge_seq,
                "area_no": semi.area.code if semi.area else None,
                "site_no": semi.site.code if semi.site else None,
                "location": semi.location,
                "rolling_code": semi.rolling.rolling_code if semi.rolling else None,
                "cast_no": semi.cast.cast_code if semi.cast else None,
                "order_group_code": semi.order_group.group_code if semi.order_group else None,
            })
    bulk_create_move_history(db_session=db_session, semi_move_histories_in=his)
    return flag, msg

@router.post("/reserve")
def reserve_semis(
        *,
        db_session: Session = Depends(get_db),
        semis_in: List[SemiBatchUpdate],
        current_user: DispatchUser = Depends(get_current_user)
):
    """
    Reserve semis.
    """
    updated_at = datetime.now()
    uuid = uuid4()
    his = []
    msg = "Reserve Success"
    reserve_unreserve_semi(db_session=db_session, semis_in=semis_in)
    for semi_in in semis_in:
        semi = get(db_session=db_session, semi_id=semi_in.id)
        his.append({
            "uuid": uuid,
            "semi_id": semi.id,
            "created_by": current_user.email,
            "change_type": SemiMoveHistoryChangTypeEnum.RESERVE,
            "code": semi.semi_code,
            "semi_charge_seq": semi_in.semi_charge_seq,
            "area_no": semi.area.code if semi.area else None,
            "site_no": semi.site.code if semi.site else None,
            "location": semi.location,
            "rolling_code": semi.rolling.rolling_code if semi.rolling else None,
            "cast_no": semi.cast.cast_code if semi.cast else None,
            "order_group_code": semi.reserved_order_group.group_code if semi.reserved_order_group else None,
        })
    bulk_create_move_history(db_session=db_session, semi_move_histories_in=his)
    return msg

@router.post("/unreserve")
def unreserve_semis(
        *,
        db_session: Session = Depends(get_db),
        semis_in: List[SemiBatchUpdate],
        current_user: DispatchUser = Depends(get_current_user)
):
    """
    Unreserve semis.
    """
    updated_at = datetime.now()
    uuid = uuid4()
    his = []
    msg = "Unreserve Success"
    reserve_unreserve_semi(db_session=db_session, semis_in=semis_in)
    for semi_in in semis_in:
        semi = get(db_session=db_session, semi_id=semi_in.id)
        his.append({
            "uuid": uuid,
            "semi_id": semi.id,
            "created_by": current_user.email,
            "change_type": SemiMoveHistoryChangTypeEnum.UNRESERVE,
            "code": semi.semi_code,
            "semi_charge_seq": semi_in.semi_charge_seq,
            "area_no": semi.area.code if semi.area else None,
            "site_no": semi.site.code if semi.site else None,
            "location": semi.location,
            "rolling_code": semi.rolling.rolling_code if semi.rolling else None,
            "cast_no": semi.cast.cast_code if semi.cast else None,
            "order_group_code": semi.reserved_order_group.group_code if semi.reserved_order_group else None,
        })
    bulk_create_move_history(db_session=db_session, semi_move_histories_in=his)
    return msg

@router.delete("/{semi_id}")
def delete_semi(*, db_session: Session = Depends(get_db), semi_id: int, current_user: DispatchUser = Depends(get_current_user)):
    """
    Delete a semi contact.
    """
    semi = get(db_session=db_session, semi_id=semi_id)

    if not semi:
        raise HTTPException(status_code=400, detail="The semi with this id does not exist.")

    history_entry = {
        "uuid": str(uuid4()),
        "semi_id": semi.id,
        "created_by": current_user.email,
        "change_type": SemiMoveHistoryChangTypeEnum.DELETE,
        "code": semi.semi_code,
        "area_no": semi.area.code if semi.area else None,
        "site_no": semi.site.code if semi.site else None,
        "location": semi.location,
        "rolling_code": semi.rolling.rolling_code if semi.rolling else None,
        "cast_no": semi.cast.cast_code if semi.cast else None,
        "order_group_code": semi.order_group.group_code if semi.order_group else None,
        "quality_code": semi.quality_code if semi.quality_code else None,
        "scarfed_status": semi.scarfed_status if semi.scarfed_status else None,
        "skelp_no": semi.skelp_code if semi.skelp_code else None,
        "semi_no": semi.semi_code if semi.semi_code else None,
        "semi_status": semi.semi_status if semi.semi_status else None,
        "width": semi.width_mm if semi.width_mm else None,
        "thickness": semi.thickness_mm if semi.thickness_mm else None,
        "length": semi.length_mm if semi.length_mm else None,
        "estimated_weight": semi.estimated_weight_kg if semi.estimated_weight_kg else None,
        "semi_load": semi.semi_load if semi.semi_load else None,
        "semi_charge_seq": semi.semi_charge_seq if semi.semi_charge_seq else None,
        "semi_cut_seq": semi.semi_cut_seq if semi.semi_cut_seq else None,
        "semi_type": semi.semi_type if semi.semi_type else None,
        "hold_reason": semi.hold_reason if semi.hold_reason else None,
        "comment": semi.comment if semi.comment else None,
    }
    bulk_create_move_history(db_session=db_session, semi_move_histories_in=[history_entry])

    db_session.query(SemiMoveHistory).filter(SemiMoveHistory.id == semi_id).delete()
   
    return delete(db_session=db_session, semi_id=semi_id)



@router.post("/update_semi")
def update_semi(background_tasks: BackgroundTasks, item: dict, db_session: Session = Depends(get_db),current_user: DispatchUser = Depends(get_current_user)):
    ids = []

    history_list = []
    updated_field_list = []
    updated_semi_load_objs = []
    if not item:
        raise HTTPException(status_code=400, detail="Receive data is null.")
    data = item['requestData']
    mergeBloom = item['mergeBloom'] if 'mergeBloom' in item else False
    max_id_record = max(data, key=lambda x: x['id'])
    area_code = data[0]['area_code']
    site_code = data[0]['site_code']
    location = data[0]['location']
    for i in data:
        ids.append(i['id'])
    area_one = get_by_area_code(db_session=db_session, code=area_code)
    site_one = get_by_site_code(db_session=db_session, code=site_code)
    if not (area_one and site_one):
        raise HTTPException(status_code=400, detail="Area id or Site id not exist.")
    area_id = area_one.id
    site_id = site_one.id
    # print(area_id, site_id)
    # 获取所有存在对象的 id
    semi_ids_exist = [semi.id for semi in bulk_get_semi(db_session=db_session, ids=ids)]
    # 找到不存在的对象 id
    missing_ids = set(ids) - set(semi_ids_exist)
    # 如果有不存在的 id, 直接抛出
    if missing_ids:
        raise HTTPException(status_code=400, detail="The selected semi contains non-existent IDs..")
    res = get_area_location(db_session=db_session, semi_ids=ids)

    print(max_id_record['id'])
    
    uuid = str(uuid4())
    for i, id, information in zip(res, ids, data):

        if mergeBloom:     
            if id == max_id_record['id']:
                total_length = max(res_d.length_mm for res_d in res)
                total_quantity = sum(res_d2.quantity for res_d2 in res)
                total_weight = sum(res_d3.estimated_weight_kg if res_d3.estimated_weight_kg else 0 for res_d3 in res)
                
                width = int(i.width_mm) if i.width_mm else 0
                thickness = int(i.thickness_mm) if i.thickness_mm else 0
                semi_size = f"{width} * {thickness}"
                new_semi_code_suffix = BLOOM_SIZE_SUFFIX_MAPPING.get(semi_size)
                if not new_semi_code_suffix:
                    raise HTTPException(status_code=400, detail=f"The semi code suffix is not supported by semi size: {semi_size}!")

                if not i.cast or not i.cast.cast_code:
                    raise HTTPException(status_code=400, detail="Cast not found in Semi, or cast code not found in Cast!")

                new_semi_code = f"{i.cast.cast_code.strip()}{new_semi_code_suffix}"
                if not i.generate_code:
                    raise HTTPException(status_code=400, detail="Generate code not found in Semi!")

                new_long_semi_code = f"{i.generate_code}{new_semi_code}"

                updated_field_information = {
                    "id": id,
                    "semi_code": new_semi_code, 
                    "long_semi_code": new_long_semi_code,
                    "site_id": site_id,  # 通过site code 获取 id
                    "area_id": area_id,  # 通过area code 获取 id
                    "location": location,  # 新 location
                    "length_mm": total_length,
                    "quantity": total_quantity,
                    "estimated_weight_kg": total_weight,
                    "skelp_code": new_semi_code_suffix,
                    "semi_status": "Stock"  # merge 之后状态由 In Transit 改为 Stock
                }

                # i 转 字典
                history_information = {
                    "uuid": uuid,
                    "semi_id": id,
                    "created_by": current_user.email,
                    "change_type": SemiMoveHistoryChangTypeEnum.MOVE,
                    "code": i.semi_code,
                    "area_no": area_code,
                    "site_no": site_code ,
                    "skelp_no": i.skelp_code, 
                    "location": location,  # 源 location
                    "rolling_code": i.rolling.rolling_code if i.rolling else None,
                    "cast_no": i.cast.cast_code if i.cast else None,
                    "order_group_code": i.order_group.group_code if i.order_group else None,
                }
            else:
                updated_field_information = {
                    "id": id,
                    "is_deleted": 1
                }
                updated_field_semi_load_information = {
                    "id": i.semi_load_id,
                    "is_deleted": 1
                }
                updated_semi_load_objs.append(updated_field_semi_load_information)

                history_information = {
                    "uuid": uuid,
                    "semi_id": id,
                    "created_by": current_user.email,
                    "change_type": SemiMoveHistoryChangTypeEnum.DELETE,
                    "code": i.semi_code,
                    "area_no": i.area.code if i.area else None,
                    "site_no": i.site.code if i.site else None,
                    "location": i.location,
                    "rolling_code": i.rolling.rolling_code if i.rolling else None,
                    "cast_no": i.cast.cast_code if i.cast else None,
                    "order_group_code": i.order_group.group_code if i.order_group else None,
                    "quality_code": i.quality_code if i.quality_code else None,
                    "scarfed_status": i.scarfed_status if i.scarfed_status else None,
                    "skelp_no": i.skelp_code if i.skelp_code else None,
                    "semi_no": i.semi_code if i.semi_code else None,
                    "semi_status": i.semi_status if i.semi_status else None,
                    "width": i.width_mm if i.width_mm else None,
                    "thickness": i.thickness_mm if i.thickness_mm else None,
                    "length": i.length_mm if i.length_mm else None,
                    "estimated_weight": i.estimated_weight_kg if i.estimated_weight_kg else None,
                    "semi_load": i.semi_load if i.semi_load else None,
                    "semi_charge_seq": i.semi_charge_seq if i.semi_charge_seq else None,
                    "semi_cut_seq": i.semi_cut_seq if i.semi_cut_seq else None,
                    "semi_type": i.semi_type if i.semi_type else None,
                    "hold_reason": i.hold_reason if i.hold_reason else None,
                    "comment": i.comment if i.comment else None,
                }
        
        else:
            # i 转 字典
            history_information = {
                "uuid": uuid,
                "semi_id": id,
                "created_by": current_user.email,
                "change_type": SemiMoveHistoryChangTypeEnum.MOVE,
                "code": i.semi_code,
                "area_no": area_code,
                "site_no":site_code ,
                "location": location,  # 源 location
                "rolling_code": i.rolling.rolling_code if i.rolling else None,
                "cast_no": i.cast.cast_code if i.cast else None,
                "order_group_code": i.order_group.group_code if i.order_group else None,
            }
            updated_field_information = {
                "id": id,
                "site_id": site_id,  # 通过site code 获取 id
                "area_id": area_id,  # 通过area code 获取 id
                "location": location,  # 新 location
            }
        # 历史信息保存
        history_list.append(history_information)
        # 被更新字段信息保存
        updated_field_list.append(updated_field_information)
    # 批量更新字段
    flag = update_semi_by_move(db_session=db_session, semi_body=updated_field_list)
    if not flag:
        raise HTTPException(status_code=400, detail="Failed to update the related information.")

    if updated_semi_load_objs:
        updated_semi_load_flag = semi_load_service.update_semi_by_move(db_session=db_session, semi_load_body=updated_semi_load_objs)
        if not updated_semi_load_flag:
            raise HTTPException(status_code=400, detail="Failed to update the semi load information.")

    # 批量创建历史记录
    create_flag = bulk_create_move_history(db_session=db_session, semi_move_histories_in=history_list)
    if not create_flag:
        raise HTTPException(status_code=400, detail="Failed to create the related history information.")

    # Send M249
    semi = get(db_session=db_session, semi_id=ids[0])
    if get_mill_ops(semi.mill_id) == MILLEnum.MILL1 and semi.semi_type != "Bloom":
        try:
            send_srsm_m249(db_session, semi, 0, background_tasks, current_user.current_mill_code)
        except Exception as e:
            log.error("ERROR in send_srsm_m249: {e}")
    return {"code": 2001, "data": ""}

def send_srsm_m249(db_session, semi, to_from, background_tasks, current_mill_code):
    try:
        from ...contrib.message_admin.message_server import message_strategy
        srsmm249 = message_strategy.MessageStrategyM249()
        srsmm249.send_pc_249(db_session, semi, to_from, background_tasks, current_mill_code)
        del srsmm249
    except ImportError as e:
        raise HTTPException(status_code=400, detail=str(e))

# @router.post("/import_semi_file")
# def import_semi(*,db_session: Session = Depends(get_db),file: UploadFile = File(...),
#                    current_user: DispatchUser = Depends(get_current_user)):
#
#     file_type = file.filename.split(".")[-1]
#     if file_type == 'csv':
#         c = file.file.read()
#         csv_file = io.StringIO(c.decode('utf-8'))
#         reader = csv.DictReader(csv_file)
#         rows = list(reader)
#     elif file_type == 'xlsx':
#         df = pd.read_excel(file.file.read())
#         df = df.replace({np.nan: None})
#         rows = df.to_dict(orient="records")
#     else:
#         raise HTTPException(status_code=400, detail="The file type is not supported.")
#     add_cnt, update_cnt = import_csv.import_dict_to_db(db_session=db_session, rows=rows, curr_user=current_user.email)
#     return {"add_cnt": add_cnt, "update_cnt": update_cnt}

@router.post("/import_semi_file")
def import_semi(*,db_session: Session = Depends(get_db),file: UploadFile = File(...),
                   current_user: DispatchUser = Depends(get_current_user),):
    file_type = file.filename.split(".")[-1]
    rows = []
    if file_type == 'xlsx':
        excel_data = pd.ExcelFile(file.file.read())
        # 读取Sheet1和Sheet2
        sheet_names = ['Anlyses Import', 'Semi Import']
        for sheet_name in sheet_names:
            df = excel_data.parse(sheet_name)
            df = df.replace({np.nan: None})
            sheet_rows = df.to_dict(orient='records')
            for row in sheet_rows:
                row['sheet_name'] = sheet_name
                rows.append(row)
    else:
        raise HTTPException(status_code=400, detail="The file type is not supported.")

    cast_add_cnt, cast_update_cnt, semi_add_cnt, semi_update_cnt = import_cast_semi_to_db(db_session=db_session, rows=rows, curr_user=current_user)
    return {"cast_add_cnt": cast_add_cnt, "cast_update_cnt": cast_update_cnt,
            "semi_add_cnt": semi_add_cnt, "semi_update_cnt": semi_update_cnt}

@router.get("/find/max_code/{semi_code}")
def find_max_code(semi_code, db_session: Session = Depends(get_db)):
    max_semi_code = find_max_semi_code_by_cast(db_session=db_session, semi_code=semi_code)
    return max_semi_code


@router.post("/defects")
def defect(
    *,
    db_session: Session = Depends(get_db),
    data: dict,
    current_user: DispatchUser = Depends(get_current_user),
):
    """
    Create defects for semis.
    """
    uuid = uuid4()
    his = []

    # Perform defect creation
    result = create_defects(db_session=db_session, data=data)

    # Log the operation for each semi
    for semi_id in data["ids"]:
        semi = get(db_session=db_session, semi_id=semi_id)
        his.append({
            "uuid": uuid,
            "semi_id": semi.id,
            "created_by": current_user.email,
            "change_type": SemiMoveHistoryChangTypeEnum.DEFECT,
            "code": semi.semi_code,
            "area_no": semi.area.code if semi.area else None,
            "site_no": semi.site.code if semi.site else None,
            "location": semi.location,
            "rolling_code": semi.rolling.rolling_code if semi.rolling else None,
            "cast_no": semi.cast.cast_code if semi.cast else None,
            "order_group_code": semi.order_group.group_code if semi.order_group else None,
            "quality_code": semi.quality_code if semi.quality_code else None,
            "defect_reason": semi.defect_reason.name if semi.defect_reason else None,
            "comment": semi.comment if semi.comment else None,
            "defect_quantity":semi.defect_quantity if semi.defect_quantity else None
        })

    # Save history entries
    bulk_create_move_history(db_session=db_session, semi_move_histories_in=his)

    return result


@router.post("/update_add_hold", response_model=List[SemiRead])
def update_add_hold(
    *,
    db_session: Session = Depends(get_db),
    Finished_in: SemiHoldReason,
    current_user: DispatchUser = Depends(get_current_user)
):

    semis = db_session.query(Semi).filter(Semi.id.in_(Finished_in.semi_ids)).all()
    hold_data = []
    hold_by = current_user.email
    for finished in semis:

        for hold in Finished_in.hold_list:
            hold_id = hold.get("hold_id")
            hold_comment = hold.get("comment") if hold.get("comment") else None

            # 查找 hold 是否已存在
            is_hold = (
                db_session.query(semi_hold)
                .filter(
                    semi_hold.c.semi_id == finished.id,
                    semi_hold.c.hold_reason_id == hold_id,
                )
                .first()
            )

            if is_hold:
                # 对已存在的 多对多记录 进行comment 修改

                update_hold = (
                    semi_hold.update()
                    .where(
                        semi_hold.c.semi_id == finished.id,
                        semi_hold.c.hold_reason_id == hold_id,
                    )
                    .values(comment=hold_comment)
                )

                db_session.execute(update_hold)

            else:

                hold_reason = hold_service.get(db_session=db_session, id=hold_id)

                hold_data.append(
                    {
                        "semi_id": finished.id,
                        "hold_reason_id": hold_reason.id,
                        "mill_id": hold_reason.mill_id if hold_reason.mill_id else None,
                        "comment": hold_comment,
                        "hold_by": hold_by,
                    }
                )

    if len(hold_data) > 0:
        db_session.execute(semi_hold.insert(), hold_data)
    db_session.commit()

    his = []
    uuid = uuid4()
    for his_f in semis:
        for his_d in his_f.semi_hold_reason:
            comment = None
            is_hold = (
                db_session.query(semi_hold)
                .filter(
                    semi_hold.c.semi_id == his_f.id,
                    semi_hold.c.hold_reason_id == his_d.id,
                )
                .first()
            )
            his.append(
                {
                    "uuid": uuid,
                    "semi_id": finished.id,
                    "created_by": current_user.email,
                    "change_type": SemiMoveHistoryChangTypeEnum.HOLD,
                    "code": his_f.semi_code,
                    # 'area_no': his_f.area.code if his_f.area else None,
                    # 'site_no': his_f.area.code if his_f.area else None,
                    # 'location': his_f.location if his_f.location else None,
                    # 'rolling_code': his_f.rolling.rolling_code if his_f.rolling else None,
                    # 'cast_no': his_f.cast.cast_code if his_f.cast else None,
                    # 'order_item_code': his_f.order_item.line_item_code if his_f.order_item else None,
                    # 'product_type': his_f.product_type.code if his_f.product_type else None,
                    # "hold_reason": his_f.code,
                    # "comment": is_hold.comment if is_hold.comment else None,
                }
            )
    bulk_create_move_history(db_session=db_session, semi_move_histories_in=his)

    return semis


@router.post("/update_delete_hold", response_model=List[SemiRead])
def update_delete_hold(
    *,
    background_tasks: BackgroundTasks,
    db_session: Session = Depends(get_db),
    Finished_in: SemiHoldReason,
    current_user: DispatchUser = Depends(get_current_user)
):

    semis = db_session.query(Semi).filter(Semi.id.in_(Finished_in.semi_ids)).all()
    released_finished_products = []

    his = []

    uuid = uuid4()
    for finished in semis:
        for hold in Finished_in.hold_list:

            # 查找 hold 是否已存在
            is_hold = (
                db_session.query(semi_hold)
                .filter(
                    semi_hold.c.semi_id == finished.id,
                    semi_hold.c.hold_reason_id == hold,
                )
                .first()
            )

            if is_hold:
                hold_reason = hold_service.get(db_session=db_session, id=hold)
                his.append({
                    "change_type": SemiMoveHistoryChangTypeEnum.UNHOLD,
                    "created_by": current_user.email,
                    "uuid": uuid,
                    "semi_id": finished.id,
                    "code": finished.semi_code,
                    #  "mill_id": finished.mill_id,
                    # 'rolling_code': finished.rolling.rolling_code if finished.rolling else None,
                    # 'runout_code': finished.runout.runout_code if finished.runout else None,
                    # 'area_code': finished.area.code if finished.area else None,
                    # 'cast_no': finished.cast.cast_code if finished.cast else None,
                    # 'spec_code': finished.spec.spec_code if finished.spec else None,
                    # 'order_num': finished.order.order_code if finished.order else None,
                    # 'order_item_num': finished.order_item.line_item_code if finished.order_item else None,
                    # 'product_type': finished.product_type.code if finished.product_type else None,
                    # "hold_reason_code": hold_reason.code,
                    # "comment": is_hold.comment,
                })
                db_session.execute(
                    semi_hold.delete().where(
                        semi_hold.c.semi_id == finished.id,
                        semi_hold.c.hold_reason_id == hold,
                    )
                )
                released_finished_products.append(finished)
            else:
                logger.info(f"Unable to realse semi {finished.code}, no hold found.")
                continue
    # strategy = MessageServer.MessageStrategy325()
    # strategy.send_pc_325(db_session, released_finished_products, background_tasks)
    # db_session.commit()

    if len(his)>0:
        bulk_create_move_history(db_session=db_session, semi_move_histories_in=his)

    return released_finished_products

@router.post("/send_to_pcc_m249/{semi_id}")
def send_to_pcc_m249(
    *,
    db_session: Session = Depends(get_db),
    semi_id: int,
    current_user: DispatchUser = Depends(get_current_user),
    background_tasks: BackgroundTasks,
):

    trigger_m249(db_session=db_session, semi_id=semi_id, background_tasks=background_tasks)
    return {"status": "ok"}


@router.post("/bloom/move")
def semi_bloom_move(data: dict, db_session: Session = Depends(get_db)):
    bulk_semi_bloom_move(db_session=db_session, semi_in_list=data['requestData'])
    return {
        "status": "Move Successfully!",
    }

@router.get("/bloom/total/{cast_id}")
def semi_bloom_total(cast_id: str, db_session: Session = Depends(get_db), current_user: DispatchUser = Depends(get_current_user)):
    if cast_id is None:
        return {
        "total_num": 0,
    }
    total_num = compute_bloom_total(db_session=db_session, cast_id=int(cast_id), mill_id=current_user.current_mill_id)
    return {
        "total_num": total_num,
    }


@router.post("/export_semi_file")
def export_rolling(*, db_session: Session = Depends(get_db), common: dict = Depends(common_parameters),area_code: List[str] = Query([], alias="area_code[]")):
    query = db_session.query(Semi).outerjoin(Rolling, Semi.rolling_id == Rolling.id
                                 ).outerjoin(OrderGroup, Semi.order_group_id == OrderGroup.id
                                 ).outerjoin(Area, Semi.area_id == Area.id
                                 ).outerjoin(SemiLoad, Semi.semi_load_id == SemiLoad.id
                                 ).outerjoin(Cast, Semi.cast_id == Cast.id)
    if area_code:
        query = query.filter(Area.code.in_(area_code) & (Area.type == "s-semi"))

    common['query'] = query
    common['items_per_page'] = None
    if common["query_str"]:
        common["filter_type"] = "and"
        semi_ids = get_by_semi_code_rolling_code(db_session=common["db_session"],
                                                 semi_code=common['query_str'],
                                                 rolling_code=common['query_str'],
                                                 area_code=common['query_str'],
                                                 group_code=common['query_str'])
        if common.get("fields") and common.get("ops") and common.get("values"):
            common["fields"].append("id")
            common["ops"].append("in")
            common["values"].append([i[0] for i in semi_ids])
        else:
            common["fields"] = ["id"]
            common["ops"] = ["in"]
            common["values"] = [[i[0] for i in semi_ids]]

        # 清空原来的查询字符串
        common["query_str"] = ''


    # 调用 export_to_excel 函数生成 Excel 文件并返回文件路径
    data = search_filter_sort_paginate(model="Semi", **common)['items']
    file_path = export_to_excel(db_session=db_session, data_list=data)

    # 如果文件生成成功，返回该文件
    if file_path:
        file_name = os.path.basename(file_path)  # 获取文件名
        response = FileResponse(
            file_path,filename=file_name
        )
        return response
    else:
        raise HTTPException(status_code=400, detail="File generation failed.")


@router.post("/import_semi_file_new")
def import_semi(*,db_session: Session = Depends(get_db),file: UploadFile = File(...),
                   current_user: DispatchUser = Depends(get_current_user)):

    file_type = file.filename.split(".")[-1]
    if file_type == 'csv':
        c = file.file.read()
        csv_file = io.StringIO(c.decode('utf-8'))
        reader = csv.DictReader(csv_file)
        rows = list(reader)
    elif file_type == 'xlsx':
        df = pd.read_excel(file.file.read())
        df = df.replace({np.nan: None})
        rows = df.to_dict(orient="records")
    else:
        raise HTTPException(status_code=400, detail="The file type is not supported.")
    add_cnt, update_cnt = import_dict_to_db_new(db_session=db_session, rows=rows, curr_user=current_user.email)
    return {"add_cnt": add_cnt, "update_cnt": update_cnt}