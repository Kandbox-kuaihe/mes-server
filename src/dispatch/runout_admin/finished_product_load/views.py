import json
from typing import List
from datetime import datetime
from decimal import Decimal

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from dispatch.config import DEV_DATABASE_SCHEMA, FINISHED_PRODUCT_LOAD_SEQUENCE_NAME, get_mill_ops, MILLEnum
from sqlalchemy import text


from dispatch.message_admin.message_server.models import PushMessageData
# from dispatch.contrib.message_admin.message_server.server import call_method
from dispatch.system_admin.auth.models import DispatchUser
from dispatch.system_admin.auth.service import get_current_user

from dispatch.database import get_db
from dispatch.database_util.service import common_parameters, search_filter_sort_paginate

from .models import (
    FinishedProductLoad,
    FinishedProductLoadCreate,
    FinishedProductLoadMove,
    FinishedProductLoadUpdate,
    LoadAutoPlanCreate,
    LoadAutoPlanRead,
    LoadCarryoutCreate,
    FinishedProductLoadRead,
    FinishedProductLoadPagination,
    CarryOutCreate,
    FinishedProductCutSeqLoadCreate
)
from .service import (
    create,
    move_to,
    tip_load,
    update,
    delete,
    get,
    get_by_code,
    auto_plan,
    get_planed_load_list,
    carry_out,
    bulk_create_load_cut_seq,
    get_loads_by_cut_seq_id,
    get_loads_by_rolling_og_route,
    update_cut_seq_load
)

from dispatch.order_admin.order_item.models import OrderItem
from dispatch.order_admin.order.models import Order
from dispatch.rolling.rolling_list.models import Rolling
from dispatch.rolling.cut_sequence_plan.models import CutSequencePlan
from sqlalchemy.inspection import inspect
from dispatch.rolling.cut_sequence_plan.service import update_cut_seq, get_cut_seq_by_id

router = APIRouter()

cur_object = 'finished product load'

@router.get("/", response_model=FinishedProductLoadPagination)
def get_all(
    *,
    db_session: Session = Depends(get_db),
    common: dict = Depends(common_parameters),
    start_date:str = Query(None), end_date:str = Query(None),
):
    query = db_session.query(FinishedProductLoad
        ).outerjoin(Rolling, FinishedProductLoad.rolling_id == Rolling.id
        ).outerjoin(OrderItem, FinishedProductLoad.order_item_id == OrderItem.id
        ).outerjoin(Order, OrderItem.order_id == Order.id
        )
                  
    if start_date and end_date:
        # query = db_session.query(FinishedProductLoad).filter(FinishedProductLoad.created_at >= start_date).filter(FinishedProductLoad.created_at <= end_date)
        # print("query",query)
        # common["query"] = query
        common["fields"].append('created_at')
        common['ops'].append('>=')
        common['values'].append(start_date)
        common["fields"].append('created_at')
        common['ops'].append('<=')
        common['values'].append(end_date)
    common['query'] = query
    all = search_filter_sort_paginate(model="FinishedProductLoad", **common)
    for i in all["items"]:
        i.advice_num = len(i.finished_products)
        i.order_id = i.order_item.order_id if i.order_item else None

    order_item_ids = {item.order_item_id for item in all["items"] if item.order_item_id}


    if not order_item_ids:
        return all  # Exit early if no order_item_id is found

    cut_sequence_columns = [c.key for c in inspect(CutSequencePlan).mapper.column_attrs]

    cut_sequences = (
        db_session.query(*[getattr(CutSequencePlan, col) for col in cut_sequence_columns])
        .filter(CutSequencePlan.order_item_id.in_(order_item_ids))
        .all()
    )


    cut_sequences_dict = {}
    for cs in cut_sequences:
        cs_dict = {col: getattr(cs, col) for col in cut_sequence_columns}
        if cs.order_item_id not in cut_sequences_dict:
            cut_sequences_dict[cs.order_item_id] = []
        cut_sequences_dict[cs.order_item_id].append(cs_dict)

    for item in all["items"]:
        item.cut_sequence = cut_sequences_dict.get(item.order_item_id, [])

    return all


@router.get("/planed_load_list/{order_item_id}", response_model=List[LoadAutoPlanRead])
def get_planed_loads(
    *,
    db_session: Session = Depends(get_db),
    order_item_id: int,
):
    planed_load_list = get_planed_load_list(db_session=db_session, order_item_id=order_item_id)
    return planed_load_list


@router.get("/max_id")
def get_max_id(*, db_session: Session = Depends(get_db), common: dict = Depends(common_parameters),
               ):
    max_id = db_session.execute(text(f"SELECT last_value FROM {DEV_DATABASE_SCHEMA}.{FINISHED_PRODUCT_LOAD_SEQUENCE_NAME}")).scalar()
    max_id = int(max_id + 1)
    return max_id
@router.get("/finished/{load_id}")
def get_advice(*, db_session: Session = Depends(get_db), load_id: int):
    load = get(db_session=db_session, id=load_id)
    finished_items = load.finished_products
    if len(finished_items) == 0:
        return "No finished product exists under the current load. Unable to proceed with tip."
    for i in finished_items:
        if i.exist_flag not in [None, "Y"]:
            return "The finished product under the load is being mult"
        if i.rework_status not in [None, "Complete"]:
            return "The finished product under the load is being reworked"

    return True

@router.post("/move_to")
def move_finished_product_load(
    *,
    request: Request,
    background_tasks:BackgroundTasks,
    db_session: Session = Depends(get_db),
    load_in: FinishedProductLoadMove,
    current_user: DispatchUser = Depends(get_current_user)
):
    move_success = move_to(db_session=db_session, load_in=load_in)
    load_obj = get_by_code(db_session=db_session,code = load_in.code)
    old_area_code = load_obj.area if load_obj.area else None
    
    if not load_obj:
        raise HTTPException(status_code=400, detail="Load not found")
    
    if get_mill_ops(current_user.current_mill_id) == MILLEnum.MILL1 and old_area_code =="ADC":
        push_msg = PushMessageData(id = 639, type ="srsmpc", msg={"load_id":load_obj.id})
        try:
            from dispatch.contrib.message_admin.message_server.server import call_method
            call_method(request=request,background_tasks = background_tasks,db_session=db_session,current_user=current_user,message=push_msg,)
        except ImportError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=200, detail=f"Sending M638/639 failed")
        
    # return move_to(db_session=db_session, load_in=load_in)
    return {"success":True, "details": "Movement complete."}
    
@router.post("/tip")
def tip_finished_product_load(
    *,
    db_session: Session = Depends(get_db),
    load_in: FinishedProductLoadMove,
    current_user: DispatchUser = Depends(get_current_user)
):
    load_in.updated_by = current_user.email
    load_in.updated_at = datetime.now()
    return tip_load(db_session=db_session, load_in=load_in)

@router.put("/carry")
def carry_finished_product_load(*, db_session: Session = Depends(get_db),common: dict = Depends(common_parameters), payload: CarryOutCreate):
    print("load_in",payload)
    # return FinishedProductLoadRead(id=1)
    load_ids = payload.load_in
    if not load_ids:
        raise HTTPException(status_code=400, detail="Load IDs are required.")

    update_load_data = []
    for load_id in load_ids:
        load_data = get(db_session=db_session, id=load_id)
        if load_data:
            load_data.load_status = "Carry Out"
            db_session.commit()
            update_load_data.append(load_data)
        else:
            raise HTTPException(status_code=400, detail=f"Load with ID {load_id} does not exist.")
    return update_load_data

    # load_data = get(db_session=db_session, id=load_in)
    # print("Load",load_data)
    # if load_data:
    #     load_data.load_status = "Carry Out"
    #     db_session.commit()
    # return load_data

@router.post("/auto_plan", response_model=List[LoadAutoPlanRead])
def create_auto_plan(
    *,
    db_session: Session = Depends(get_db),
    auto_plan_in: LoadAutoPlanCreate,
    current_user: DispatchUser = Depends(get_current_user)
):

    return auto_plan(db_session=db_session, auto_plan_in=auto_plan_in, current_user=current_user)

@router.post("/carry_out", response_model=dict[str, list])
def create_carry_out(
    *,
    db_session: Session = Depends(get_db),
    carry_out_in: LoadCarryoutCreate,
    current_user: DispatchUser = Depends(get_current_user)
):

    return carry_out(db_session=db_session, carry_out_in=carry_out_in, current_user=current_user)

@router.post("/", response_model=FinishedProductLoadRead)
def create_one(
    *,
    db_session: Session = Depends(get_db),
    create_in: FinishedProductLoadCreate,
    current_user: DispatchUser = Depends(get_current_user)
):
    
    create_in.created_by = current_user.email
    create_in.updated_by = current_user.email
    existed = create(db_session=db_session, create_in=create_in)
    return existed


@router.put("/{id}", response_model=FinishedProductLoadRead)
def update_one(
    *,
    db_session: Session = Depends(get_db),
    id: int,
    update_in: FinishedProductLoadUpdate,
    current_user: DispatchUser = Depends(get_current_user)
):
    existed = get(db_session=db_session, id=id)
    if not existed:
        raise HTTPException(status_code=400, detail=f"The {cur_object} with this id does not exist.")
    
    update_in.updated_by = current_user.email
    update_in.updated_at = datetime.now()

    updated = update(
        db_session=db_session,
        updated=existed,
        update_in=update_in,
    )
    return updated


@router.delete("/{id}", response_model=FinishedProductLoadRead)
def delete_one(
    *,
    db_session: Session = Depends(get_db),
    id: int
):
    existed = get(db_session=db_session, id=id)
    if not existed:
        raise HTTPException(status_code=400, detail=f"The {cur_object} with this id does not exist.")
    deleted = delete(db_session=db_session, deleted=existed)
    return deleted


@router.get("/{id}", response_model=FinishedProductLoadRead)
def get_one(
    *,
    db_session: Session = Depends(get_db),
    id: int
):
    existed = get(db_session=db_session, id=id)
    if not existed:
        raise HTTPException(status_code=400, detail=f"The {cur_object} with this id does not exist.")
    return existed


@router.get("/code/{code}", response_model=FinishedProductLoadRead)
def get_one_by_code(
    *,
    db_session: Session = Depends(get_db),
    code: str
):
    existed = get_by_code(db_session=db_session, code=code)
    if not existed:
        raise HTTPException(status_code=400, detail=f"The {cur_object} with this code does not exist.")
    return existed


@router.get("/cut_seq/loads", response_model=List[FinishedProductLoadRead])
def get_cut_seq_loads(*, cut_seq_id: int = Query(None), db_session: Session = Depends(get_db)):
    loads = get_loads_by_cut_seq_id(db_session=db_session, cut_seq_id=cut_seq_id)
    sorted_loads = sorted(loads, key=lambda item: item.cut_seq_load_no, reverse=False)
    return sorted_loads


@router.get("/cut_seq/load/options")
def get_load_options(
    *, rolling_id: int = Query(None), order_group_id: int = Query(None), 
    saw_route: str = Query(None), db_session: Session = Depends(get_db)
):
    loads = get_loads_by_rolling_og_route(
        db_session=db_session, rolling_id=rolling_id, order_group_id=order_group_id, route=saw_route
    )
    sorted_loads = sorted(loads, key=lambda item: item.id, reverse=True)
    latest_load = sorted_loads[0] if sorted_loads else None
    return latest_load


@router.post("/cut_seq/create")
def create_one_for_cut_seq(
    *,
    db_session: Session = Depends(get_db),
    create_in: FinishedProductCutSeqLoadCreate,
    current_user: DispatchUser = Depends(get_current_user)
):
    created_loads = []
    updated_loads = []
    need_unbundle_loads = []

    cut_seq_obj = get_cut_seq_by_id(db_session=db_session, cut_seq_id=create_in.cut_seq_id)
    # 获取已经绑定的loads
    existed_loads = cut_seq_obj.cut_seq_loads
    # 校验是否有需要和cut seq 解除绑定的load
    for ex_load in existed_loads:
        if ex_load.id not in [l["id"] for l in create_in.update_loads]:
            need_unbundle_loads.append(ex_load)

    curr_load_seq_bars = 0
    # 校验当前cut seq所有绑定的load的cut seq总根数是否和 cut seq的总根数一致
    create_in_load_no = []
    for load_in in create_in.loads:
        if load_in.cut_seq_load_no in [l.cut_seq_load_no for l in existed_loads]:
            raise HTTPException(status_code=400, detail=f"The {load_in.cut_seq_load_no} is existed.")
        if load_in.cut_seq_load_no not in create_in_load_no:
            create_in_load_no.append(load_in.cut_seq_load_no)
        else:
            raise HTTPException(status_code=400, detail=f"The {load_in.cut_seq_load_no} is existed.")

        # bundle_size_str = load_in.bundle_size
        # max_bars = 0
        # for size in bundle_size_str.split(","):
        #     bund, bars = size.split("*")
        #     _bars = int(bund) * int(bars)
        #     if _bars > max_bars:
        #         max_bars = _bars
        # curr_load_seq_bars += max_bars
    
    existed_loads = [(l.id, l.cut_seq_load_no) for l in existed_loads]
    for load_info in create_in.update_loads:
        if existed_loads and (load_info["id"], load_info["cut_seq_load_no"]) not in existed_loads:
            raise HTTPException(status_code=400, detail=f"The {load_info["cut_seq_load_no"]} is existed.")

        # 计算当前cut seq已经装了多少根
        # bundle_size_str = load_info["bundle_size"]
        # max_bars = 0
        # for size in bundle_size_str.split(","):
        #     bund, bars = size.split("*")
        #     _bars = int(bund) * int(bars)
        #     if _bars > max_bars:
        #         max_bars = _bars
        # curr_load_seq_bars += max_bars

    # cut_seq_bars = cut_seq_obj.new_bars
    # if cut_seq_bars and cut_seq_bars < curr_load_seq_bars:
    #     raise HTTPException(status_code=400, detail=f"Cut sequence plan id: {create_in.cut_seq_id} bars: {cut_seq_bars}, but planned loaded bars: {curr_load_seq_bars}!")

    if cut_seq_obj.order_item:
        cut_seq_obj.order_item.length_mm = create_in.length_mm
        # 解除需要解绑的load
        length_mm = cut_seq_obj.order_item.length_mm
        kgm = cut_seq_obj.order_item.product_dim3
        if not length_mm or not kgm:
            raise HTTPException(status_code=400, detail=f"Please check order item length_mm and kgm!")
        length_mm = int(length_mm)
        kgm = float(kgm)
    else:
        length_mm = cut_seq_obj.length
        prod_type = cut_seq_obj.order_group.product_type
        if not prod_type:
            raise HTTPException(status_code=400, detail=f"Please check order group product_type!")
        kgm = prod_type.dim3

    for need_unbundle_load in need_unbundle_loads:
        max_weight = 0
        need_unbundle_load.cut_sequences.remove(cut_seq_obj)
        curr_bundle_size = json.loads(need_unbundle_load.bundle_size)
        b_size= curr_bundle_size.pop(str(create_in.cut_seq_id))
        for size in b_size.split(","):
            bund, bars = size.split("*")
            _bars = int(bund) * int(bars)
            max_weight += _bars

        cut_seq_weight = Decimal((length_mm / 1000) * kgm * max_weight) / 1000
        need_unbundle_load.total_weight_ton -= cut_seq_weight.quantize(Decimal("0.000"))
        need_unbundle_load.bundle_size = json.dumps(curr_bundle_size)
        db_session.add(need_unbundle_load)
        db_session.commit()

    for load_in in create_in.loads:
        bundle_size_map = {}
        load_in.created_by = current_user.email
        load_in.updated_by = current_user.email
        load_in.mill_id = current_user.current_mill_id
        bundle_size_map[create_in.cut_seq_id] = load_in.bundle_size
        load_in.bundle_size = json.dumps(bundle_size_map)
        existed = create(db_session=db_session, create_in=load_in)
        created_loads.append(existed)

    # update load total weight ton
    for load_info in create_in.update_loads:
        load_info["updated_by"] = current_user.email
        updated_obj = update_cut_seq_load(db_session=db_session, cut_seq_id=create_in.cut_seq_id, update_info=load_info)
        updated_loads.append(updated_obj)
    
    cut_seq_info = {
        "pta_code": create_in.pta_code,
        "new_bars": create_in.new_bars,
        "length": create_in.length_mm,
        "strps": create_in.strps,
        "remarks": create_in.remarks,
        "weight": create_in.weight,
        "load_no": len(created_loads + updated_loads)
    }
    update_cut_seq(db_session=db_session, id=create_in.cut_seq_id, data=cut_seq_info)

    # create load cut sequence many to many record
    bulk_create_load_cut_seq(db_session=db_session, cut_seq_id=create_in.cut_seq_id, load_cut_seq_in=created_loads + updated_loads)

    return True
