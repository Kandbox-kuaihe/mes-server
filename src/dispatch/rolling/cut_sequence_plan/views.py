import datetime
import json
import logging
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.orm import Session

from dispatch.database import get_db
from dispatch.database_util.service import search_filter_sort_paginate, common_parameters
from dispatch.rolling.rolling_list.service import get_by_id
from dispatch.system_admin.auth.models import DispatchUser
from dispatch.system_admin.auth.service import get_current_user
from dispatch.rolling.cut_sequence_plan.models import (
    CutSequencePlan, CutSequencePlanCreate, CutSequencePlanPagination, CutSequencePlanMove,
    CutSequencePlanSplit, AutoLoadPlanCreate, CutSequencePlanRead
)
from .service import (
    auto_cut_sequence_byrolling, create_cut_sequence, move_cut_sequence_plan, split_cut_sequence_plan,
    auto_cut_sequence, auto_load_plan, delete_cut_seq_by_id, get_cut_seq_by_id, create_cut_sequence_by_order_code,
    get_loading_insts
)

from ...config import get_mill_ops, MILLEnum
from dispatch.rolling.rolling_list import service as rolling_service

logging.basicConfig(level=logging.INFO)
from dispatch.log import getLogger
log = getLogger(__name__)

router = APIRouter()
try:
    from dispatch.contrib.message_admin.message_server.server import MessageStrategySRSMM107
    from ...contrib.message_admin.message_server import message_strategy
except ImportError:
    def MessageStrategySRSMM107():
        # raise NotImplementedError("MessageStrategySRSMM107 is not available because required modules are missing.")
        log.warning("MessageStrategySRSMM107 is not available because required modules are missing.")
        pass
    def message_strategy():
        raise NotImplementedError("message_strategy is not available because required modules are missing.")
m107 = MessageStrategySRSMM107()
@router.post("/autoplan")
def auto_sequence(
    *,
    current_user: DispatchUser = Depends(get_current_user),
    db_session: Session = Depends(get_db),
    payload: CutSequencePlanCreate,
):
    if get_by_id(db_session=db_session, id=payload.rolling_id) is None:
        raise HTTPException(status_code=400, detail="Rolling not found")
    payload.updated_by = current_user.email
    payload.created_by = current_user.email
    rolling = auto_cut_sequence(db_session=db_session, payload=payload)
    return rolling

@router.post("/autoplanbyrolling")
def auto_sequence_byrolling(
    *,
    current_user: DispatchUser = Depends(get_current_user),
    db_session: Session = Depends(get_db),
    payload: CutSequencePlanCreate,
):
    if get_by_id(db_session=db_session, id=payload.rolling_id) is None:
        raise HTTPException(status_code=400, detail="Rolling not found")
    payload.updated_by = current_user.email
    payload.created_by = current_user.email
    current_mill_id = current_user.current_mill_id
    rolling = auto_cut_sequence_byrolling(db_session=db_session, payload=payload, mill_id=current_mill_id)
    return rolling

@router.post("/create")
def cut_sequence(
    *,
    current_user: DispatchUser = Depends(get_current_user),
    db_session: Session = Depends(get_db),
    payload: CutSequencePlanCreate,
):
    if get_by_id(db_session=db_session, id=payload.rolling_id) is None:
        raise HTTPException(status_code=400, detail="Rolling not found")
    payload.updated_by = current_user.email
    payload.created_by = current_user.email
    if payload.order_item_id or payload.saw_route:
        rolling = create_cut_sequence_by_order_code(db_session=db_session, payload=payload)
    else:
        rolling = create_cut_sequence(db_session=db_session, payload=payload)
    return rolling


@router.get("/", response_model=CutSequencePlanPagination)
def list_cut_sequence(*, common: dict = Depends(common_parameters)):
    return search_filter_sort_paginate(model="CutSequencePlan", **common)


@router.post("/move")
def move_cut_sequence(
    *,
    current_user: DispatchUser = Depends(get_current_user),
    db_session: Session = Depends(get_db),
    payload: CutSequencePlanMove,
    background_tasks: BackgroundTasks,
):
    payload.updated_by = current_user.email
    payload.updated_at = datetime.datetime.now(datetime.UTC)
    cut_seq_plan = move_cut_sequence_plan(db_session=db_session, payload=payload)

    for cut_id in payload.ids:
        cut = db_session.query(CutSequencePlan).filter(CutSequencePlan.id == cut_id).one_or_none()
        if not cut:
            log.warning(f"CutSequencePlan with id {cut_id} not found.")
            continue

        rolling = rolling_service.get_by_id(db_session=db_session, id=cut.rolling_id)
        if not rolling:
            log.warning(f"Rolling with id {cut.rolling_id} not found.")
            continue

        if get_mill_ops(rolling.mill_id) == MILLEnum.MILL1:
            try:
                send_srsm_m247(db_session, rolling, background_tasks, current_user.current_mill_code)
            except Exception as e:
                log.error("Sending message error send_srsm_m247")
    return cut_seq_plan

def send_srsm_m247(db_session, rolling, background_tasks, current_mill_code):
    srsmm247 = message_strategy.MessageStrategyM247()
    try:
        srsmm247.send_pc_247(db_session=db_session, rolling=rolling, background_tasks=background_tasks, current_mill_code=current_mill_code)
    except Exception as e:
        msg = "Sending message error send_pc_247"
        log.error(msg)
        raise HTTPException(status_code=400, detail=msg)
    del srsmm247


@router.post("/split")
def split_cut_sequence(
    *,
    current_user: DispatchUser = Depends(get_current_user),
    db_session: Session = Depends(get_db),
    payload: CutSequencePlanSplit,
):
    payload.updated_by = current_user.email
    payload.updated_at = datetime.datetime.now(datetime.UTC)
    return split_cut_sequence_plan(db_session=db_session, payload=payload)


@router.post("/print")
def cut_sequence_print(data: dict, background_tasks: BackgroundTasks, db_session: Session = Depends(get_db), current_user: DispatchUser = Depends(get_current_user)):    
    try:
        m107.send_pc_m107(db_session=db_session, rolling_code=data['rolling_code'], quality_code=data['quality_code'], background_tasks=background_tasks, current_mill_code=current_user.current_mill_code, roll_ref=None, roll_short_code=None, route=None, weight=None)
    except Exception as e:
        msg = "Sending message error send_pc_m107"
        log.error(msg)
        raise HTTPException(status_code=400, detail=msg)
    return {
        "status": "ok",
    }


@router.post("/auto_load_plan")
def auto_load_plan_by_cut_seq(
        *,
        db_session: Session = Depends(get_db),
        current_user: DispatchUser = Depends(get_current_user),
        payload: AutoLoadPlanCreate
):
    payload.updated_by = current_user.email
    payload.created_by = current_user.email
    return auto_load_plan(db_session=db_session, payload=payload, mill_id=current_user.current_mill_id)


@router.delete("/{cut_seq_id}", response_model=CutSequencePlanRead)
def delete_cut_seq(*, db_session: Session = Depends(get_db), cut_seq_id: int):
    cut_seq_obj = get_cut_seq_by_id(db_session=db_session, cut_seq_id=cut_seq_id)
    if cut_seq_obj.order_item:
        length_mm = cut_seq_obj.order_item.length_mm
        kgm = cut_seq_obj.order_item.product_dim3
        if not length_mm or not kgm:
            raise HTTPException(status_code=400, detail=f"Please check order item length_mm and kgm!")
    else:
        length_mm = cut_seq_obj.length
        prod_type = cut_seq_obj.order_group.product_type
        if not prod_type:
            raise HTTPException(status_code=400, detail=f"Please check order group product_type!")
        kgm = prod_type.dim3

    length_mm = int(length_mm)
    kgm = float(kgm)

    cut_seq_loads = cut_seq_obj.cut_seq_loads
    # 减少load中要删除的cut seq的重量和bundle size中记录的当前cut seq 的记录
    for load in cut_seq_loads:
        total_bars = 0
        load_bundle_size = json.loads(load.bundle_size)
        cut_seq_bundle_size = load_bundle_size.pop(str(cut_seq_obj.id))
        if cut_seq_bundle_size:
            for size in cut_seq_bundle_size.split(","):
                bund, bars = size.split("*")
                total_bars += int(bund) * int(bars)
        cut_seq_weight = Decimal((length_mm / 1000) * kgm * total_bars) / 1000
        load.total_weight_ton -= cut_seq_weight.quantize(Decimal("0.000"))
        load.bundle_size = json.dumps(load_bundle_size)
        # 删除 load 和 删除的cut seq 的多对多记录
        load.cut_sequences.remove(cut_seq_obj)

    db_session.bulk_save_objects(cut_seq_loads)
    existed_obj = delete_cut_seq_by_id(db_session=db_session, cut_seq_id=cut_seq_id)
    return existed_obj


@router.get("/print/load_instructions")
def get_load_instructions(
        *,
        rolling_id: int = Query(...),
        order_group_id: int = Query(...),
        db_session: Session = Depends(get_db),
        current_user: DispatchUser = Depends(get_current_user)
):
    return get_loading_insts(db_session=db_session, rolling_id=rolling_id, order_group_id=order_group_id)
