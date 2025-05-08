import json
from typing import List, Optional
from datetime import datetime

from fastapi import HTTPException
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.sql import and_, asc, desc
from decimal import Decimal, ROUND_FLOOR
from dispatch.order_admin.order_item.models import OrderItem
from .models import CutSequencePlanCreate, CutSequencePlan, CutSequencePlanMove, CutSequencePlanSplit, AutoLoadPlanCreate
from dispatch.runout_admin.finished_product_load.models import FinishedProductLoadCreate, FinishedProductLoad
from dispatch.bundle_matrix.service import get_num_bars
from dispatch.runout_admin.finished_product_load.models_secondary_cut_sequence import finished_product_load_cut_sequence_plan
from dispatch.log import getLogger
from dispatch.order_admin.order_item import service as order_item_service
from dispatch.order_admin.order_group import service as order_group_service

logger = getLogger(__name__)


def auto_cut_sequence(*, db_session: Session, payload: CutSequencePlanCreate):
    # Query order items
    order_items = (
        db_session.query(OrderItem)
        .filter(OrderItem.rolling_id == payload.rolling_id, OrderItem.order_id == payload.order_id)
        .all()
    )
    if not order_items:
        raise HTTPException(status_code=400, detail="The rolling does not have any order items.")
    if (
        len(order_items)
        
        == db_session.query(CutSequencePlan)
        .filter(CutSequencePlan.rolling_id == payload.rolling_id, CutSequencePlan.order_id == payload.order_id)
        .count()
    ):
        raise HTTPException(status_code=400, detail="The rolling has been cut.")

    # Sort items by weight in descending order (optional for consistent processing)
    order_items = sorted(order_items, key=lambda x: Decimal(x.tonnage), reverse=True)

    cut_seq_list = []
    max_seq_e = (
        db_session.query(CutSequencePlan.new_seq)
        .filter(CutSequencePlan.saw_route == "E", CutSequencePlan.rolling_id == payload.rolling_id)
        .order_by(CutSequencePlan.new_seq.desc())
        .first()
        )

        # Query the highest sequence for West from the database for this route (independent of order_item_id)
    max_seq_w = (
        db_session.query(CutSequencePlan.new_seq)
        .filter(CutSequencePlan.saw_route == "W", CutSequencePlan.rolling_id == payload.rolling_id)
        .order_by(CutSequencePlan.new_seq.desc())
        .first()
    )

    # Start from 1 if no sequence exists yet, otherwise start from the last sequence number + 1
    current_seq_e = max_seq_e[0] + 1 if max_seq_e else 1
    current_seq_w = max_seq_w[0] + 1 if max_seq_w else 1

    for it in order_items:
        item_weight = Decimal(it.tonnage)
        item_bars = Decimal(it.quantity)
        weight_per_bar = item_weight / item_bars  # Calculate weight per bar

        if item_bars == 1:  # Single bar, assign fully to East
            cut_seq_list.append({
                "saw_route": "E",
                "original_saw_route": "E",
                "new_seq": current_seq_e,
                "original_seq": current_seq_e,
                "order_item_id": it.id,
                "order_id": it.order_id,
                "original_bars": int(item_bars),
                "new_bars": int(item_bars),
                "weight": item_weight,
                "rolling_id": payload.rolling_id,
                "created_by": payload.created_by,
                "updated_by": payload.updated_by,
            })
            current_seq_e += 1

        else:  # Split into 85% and 15%
            bars_e = (item_bars * Decimal("0.85")).to_integral_value(rounding=ROUND_FLOOR)
            bars_w = item_bars - bars_e

            # Calculate weights based on allocated bars
            weight_e = (bars_e * weight_per_bar).quantize(Decimal("0.001"))
            weight_w = (bars_w * weight_per_bar).quantize(Decimal("0.001"))

            # Assign 85% to East
            cut_seq_list.append({
                "saw_route": "E",
                "original_saw_route": "E",
                "new_seq": current_seq_e,
                "original_seq": current_seq_e,
                "order_item_id": it.id,
                "order_id": it.order_id,
                "original_bars": int(bars_e),
                "new_bars": int(bars_e),
                "weight": weight_e,
                "rolling_id": payload.rolling_id,
                "created_by": payload.created_by,
                "updated_by": payload.updated_by,
            })
            current_seq_e += 1

            # Assign 15% to West
            cut_seq_list.append({
                "saw_route": "W",
                "original_saw_route": "W",
                "new_seq": current_seq_w,
                "original_seq": current_seq_w,
                "order_item_id": it.id,
                "order_id": it.order_id,
                "original_bars": int(bars_w),
                "new_bars": int(bars_w),
                "weight": weight_w,
                "rolling_id": payload.rolling_id,
                "created_by": payload.created_by,
                "updated_by": payload.updated_by,
            })
            current_seq_w += 1

    # Commit to the database
    db_session.bulk_insert_mappings(CutSequencePlan, cut_seq_list)
    db_session.commit()
    return len(cut_seq_list)

def auto_cut_sequence_byrolling(*, db_session: Session, payload: CutSequencePlanCreate, mill_id: int):
    # Query all order_ids from table order_item using rolling_id
    table_a_records = (
        db_session.query(OrderItem)
        .filter(and_(OrderItem.rolling_id == payload.rolling_id, OrderItem.order_group_id == payload.order_group_id))
        .all()
    )
    if not table_a_records:
        raise HTTPException(status_code=400, detail="No record found in Table order_item for the given rolling_id.")

    # Get all unique order_ids from Table order_item
    order_ids = {record.order_id for record in table_a_records}

    # Initialize a list to store the total number of cut sequences for each order_id
    total_cut_sequences = []

    # Iterate over each order_id and execute the cutting logic
    for order_id in order_ids:
        # Query order items for the current order_id
        order_items = (
            db_session.query(OrderItem)
            .filter(and_(OrderItem.rolling_id == payload.rolling_id, OrderItem.order_id == order_id, OrderItem.order_group_id == payload.order_group_id))
            .all()
        )
        if not order_items:
            raise HTTPException(status_code=400, detail=f"The rolling does not have any order items for order_id {order_id}.")
        if (
            len(order_items) == db_session.query(CutSequencePlan)
            .filter(and_(
                CutSequencePlan.rolling_id == payload.rolling_id,
                CutSequencePlan.order_id == order_id,
                CutSequencePlan.order_group_id == payload.order_group_id,
                CutSequencePlan.is_deleted == 0
            ))
            .count()
        ):
            raise HTTPException(status_code=400, detail=f"The rolling has been cut for order_id {order_id}.")

        # Sort items by weight in descending order (optional for consistent processing)
        order_items = sorted(order_items, key=lambda x: Decimal(x.tonnage), reverse=True)

        cut_seq_list = []
        # Query the highest sequence for East and West from the database for this order_item_id and order_id
        
        max_seq_e = (
        db_session.query(CutSequencePlan.new_seq)
        .filter(and_(
            CutSequencePlan.saw_route == "E",
            CutSequencePlan.rolling_id == payload.rolling_id,
            CutSequencePlan.order_group_id == payload.order_group_id,
            CutSequencePlan.is_deleted == 0
        ))
        .order_by(CutSequencePlan.new_seq.desc())
        .first()
        )

        # Query the highest sequence for West from the database for this route (independent of order_item_id)
        max_seq_w = (
            db_session.query(CutSequencePlan.new_seq)
            .filter(and_(
                CutSequencePlan.saw_route == "W",
                CutSequencePlan.rolling_id == payload.rolling_id,
                CutSequencePlan.order_group_id == payload.order_group_id,
                CutSequencePlan.is_deleted == 0
            ))
            .order_by(CutSequencePlan.new_seq.desc())
            .first()
        )

        # Start from 1 if no sequence exists yet, otherwise start from the last sequence number + 1
        current_seq_e = max_seq_e[0] + 10 if max_seq_e else 10
        current_seq_w = max_seq_w[0] + 10 if max_seq_w else 10

        for it in order_items:
            item_weight = Decimal(it.tonnage)
            item_bars = Decimal(it.quantity)
            weight_per_bar = item_weight / item_bars  # Calculate weight per bar
            
            

            if item_bars == 1:  # Single bar, assign fully to East
                cut_seq_list.append({
                    "saw_route": "E",
                    "original_saw_route": "E",
                    "new_seq": current_seq_e,
                    "original_seq": current_seq_e,
                    "order_item_id": it.id,
                    "order_id": it.order_id,
                    "order_group_id": it.order_group_id,
                    "original_bars": int(item_bars),
                    "new_bars": int(item_bars),
                    "weight": item_weight,
                    "strps": 0,
                    "length": int(it.length_mm),
                    "rolling_id": payload.rolling_id,
                    "created_by": payload.created_by,
                    "updated_by": payload.updated_by,
                })
                current_seq_e += 10

            else:  # Split into 85% and 15%
                bars_e = (item_bars * Decimal("0.85")).to_integral_value(rounding=ROUND_FLOOR)
                bars_w = item_bars - bars_e

                # Calculate weights based on allocated bars
                weight_e = (bars_e * weight_per_bar).quantize(Decimal("0.001"))
                weight_w = (bars_w * weight_per_bar).quantize(Decimal("0.001"))

                # Assign 85% to East
                cut_seq_list.append({
                    "saw_route": "E",
                    "original_saw_route": "E",
                    "new_seq": current_seq_e,
                    "original_seq": current_seq_e,
                    "order_item_id": it.id,
                    "order_id": it.order_id,
                    "order_group_id": it.order_group_id,
                    "original_bars": int(bars_e),
                    "new_bars": int(bars_e),
                    "weight": weight_e,
                    "strps": 0,
                    "length": int(it.length_mm),
                    "rolling_id": payload.rolling_id,
                    "created_by": payload.created_by,
                    "updated_by": payload.updated_by,
                })
                current_seq_e += 10

                # Assign 15% to West
                cut_seq_list.append({
                    "saw_route": "W",
                    "original_saw_route": "W",
                    "new_seq": current_seq_w,
                    "original_seq": current_seq_w,
                    "order_item_id": it.id,
                    "order_id": it.order_id,
                    "order_group_id": it.order_group_id,
                    "original_bars": int(bars_w),
                    "new_bars": int(bars_w),
                    "weight": weight_w,
                    "strps": 0,
                    "length": int(it.length_mm),
                    "rolling_id": payload.rolling_id,
                    "created_by": payload.created_by,
                    "updated_by": payload.updated_by,
                })
                current_seq_w += 10

        # Commit to the database for the current order_id
        db_session.bulk_insert_mappings(CutSequencePlan, cut_seq_list)
        db_session.commit()

        # Append the number of cut sequences for the current order_id to the total list
        total_cut_sequences.append(len(cut_seq_list))



    # Return the total number of cut sequences for all order_ids
    #return sum(total_cut_sequences)
    return len(cut_seq_list)

def create_cut_sequence(*, db_session: Session, payload: CutSequencePlanCreate):
    order_items = (
        db_session.query(OrderItem)
        .filter(
            OrderItem.rolling_id == payload.rolling_id,
            OrderItem.order_id == payload.order_id,
            OrderItem.order_group_id == payload.order_group_id
        )
        .all()
    )
    if not order_items:
        raise HTTPException(status_code=400, detail="The rolling does not have any order items.")
    if (
        len(order_items)
        == db_session.query(CutSequencePlan)
        .filter(CutSequencePlan.rolling_id == payload.rolling_id, CutSequencePlan.order_id==payload.order_id)
        .count()
    ):
        raise HTTPException(status_code=400, detail="The rolling has been cut.")

    cut_seq_list = []
    for idx, it in enumerate(order_items, 1):
        cut_seq_list.append(
            {
                "saw_route": "E",
                "original_saw_route": "E",
                "new_seq": idx,
                "original_seq": idx,
                "order_item_id": it.id,
                "order_id": it.order_id,
                "order_group_id": it.order_group_id,
                "original_bars": it.quantity,
                "new_bars": it.quantity,
                "weight": it.tonnage,
                "rolling_id": payload.rolling_id,
                "created_by": payload.created_by,
                "updated_by": payload.updated_by,
            }
        )
    db_session.bulk_insert_mappings(CutSequencePlan, cut_seq_list)
    db_session.commit()
    return len(cut_seq_list)


def create_cut_sequence_by_order_code(*, db_session: Session, payload: CutSequencePlanCreate):
    order_group_obj = order_group_service.get(db_session=db_session, id=payload.order_group_id)
    if not order_group_obj:
        raise HTTPException(status_code=400, detail=f"The rolling does not have the order group: {payload.order_group_id}.")

    prod_type = order_group_obj.product_type
    if not prod_type:
        raise HTTPException(status_code=400, detail=f"The order group does not have the product type.")

    order_item_obj = None
    if payload.order_item_id:
        order_item_obj = order_item_service.get(
            db_session=db_session, orderItem_id=payload.order_item_id
        )
        if not order_item_obj:
            raise HTTPException(status_code=400, detail=f"The rolling does not have the order item: {payload.order_item_id}.")
        query_obj = db_session.query(CutSequencePlan).filter(
            CutSequencePlan.order_item_id == payload.order_item_id,
            CutSequencePlan.order_id == order_item_obj.order_id
        )
        cut_sequence = query_obj.filter(
            CutSequencePlan.rolling_id == payload.rolling_id,
            CutSequencePlan.order_group_id == payload.order_group_id,
            CutSequencePlan.saw_route == payload.saw_route,
            CutSequencePlan.is_deleted == 0
        ).first()
        if cut_sequence:
            raise HTTPException(
                status_code=400,
                detail=f"The order item: {payload.order_item_id} has been cut."
            )

    latest_cut_seq = db_session.query(CutSequencePlan).filter(
        CutSequencePlan.rolling_id == payload.rolling_id,
        CutSequencePlan.order_group_id == payload.order_group_id,
        CutSequencePlan.saw_route == payload.saw_route,
        CutSequencePlan.is_deleted == 0
    ).order_by(desc(CutSequencePlan.new_seq)).first()

    start_seq = 10
    if latest_cut_seq:
        start_seq = latest_cut_seq.new_seq + 10

    weight = float(prod_type.dim3) * (payload.length / 1000) * payload.new_bars
    new_cut_seq = {
        "saw_route": payload.saw_route,
        "original_saw_route": payload.saw_route,
        "new_seq": start_seq,
        "original_seq": start_seq,
        "order_item_id": order_item_obj.id if order_item_obj else None,
        "order_id": order_item_obj.order_id if order_item_obj else None,
        "order_group_id": payload.order_group_id,
        "original_bars": payload.new_bars,
        "new_bars": payload.new_bars,
        "weight": round(weight / 1000, 3),
        "strps": 0,
        "length": payload.length,
        "rolling_id": payload.rolling_id,
        "created_by": payload.created_by,
        "updated_by": payload.updated_by,
    }
    create_cut_seq = CutSequencePlan(**new_cut_seq)
    db_session.add(create_cut_seq)
    # db_session.bulk_insert_mappings(CutSequencePlan, cut_seq_list)
    db_session.commit()
    return create_cut_seq


def move_cut_sequence_plan(*, db_session: Session, payload: CutSequencePlanMove):
    if len(payload.ids) > 1 and payload.move_to_id:
        raise HTTPException(
            status_code=400,
            detail="Only select the ‘New Seq’ option when moving the position of a cut seq within the same saw line. "
                   "In other cases, please remove the 'New Seq' option. "
        )
    # Move a cut sequence plan.
    # 支持将一个saw route中的cut seq和当前saw route中的cut seq交换
    if len(payload.ids) == 1 and payload.move_to_id:
        selected_cut_seq = db_session.query(CutSequencePlan).filter(
            CutSequencePlan.id == payload.ids[0], CutSequencePlan.is_deleted == 0
        ).first()
        if not selected_cut_seq:
            raise HTTPException(status_code=400, detail="Selected cut sequence plan not found.")

        move_to_cut_seq = db_session.query(CutSequencePlan).filter(
            CutSequencePlan.id == payload.move_to_id, CutSequencePlan.is_deleted == 0
        ).first()
        if not move_to_cut_seq:
            raise HTTPException(status_code=400, detail="Move to cut sequence plan not found.")

        # 只允许同一个saw route 中的cut seq之间互相交换
        if selected_cut_seq.saw_route == move_to_cut_seq.saw_route == payload.saw_route:
            # 交换两个cut seq
            selected_new_seq_temp = selected_cut_seq.new_seq
            moved_new_seq_temp = move_to_cut_seq.new_seq
            selected_cut_seq.new_seq = moved_new_seq_temp
            selected_cut_seq.original_seq = selected_new_seq_temp
            move_to_cut_seq.new_seq = selected_new_seq_temp
            move_to_cut_seq.original_seq = moved_new_seq_temp

            db_session.add_all([selected_cut_seq, move_to_cut_seq])
            db_session.commit()
            return True
        else:
            raise HTTPException(
                status_code=400,
                detail="If want to move the position of a cut seq within the same saw line. "
                       "Please ensure that the selected cut seq is consistent with the selected saw line. "
            )

    cur_max_seq = None
    for id in payload.ids:
        cut = db_session.query(CutSequencePlan).filter(CutSequencePlan.id == id).one_or_none()
        if not cut:
            raise HTTPException(status_code=400, detail="Cut sequence plan not found.")
        if cur_max_seq is None:
            # 首次查找当前rolling_id和saw_route的最大序号 ， 或者赋值为1
            max_seq = (
                db_session.query(CutSequencePlan)
                .filter(CutSequencePlan.rolling_id == cut.rolling_id, CutSequencePlan.saw_route == payload.saw_route)
                .order_by(CutSequencePlan.new_seq.desc())
                .first()
            )
            if max_seq:
                cur_max_seq = max_seq.new_seq + 10
            else:
                cur_max_seq = 10
        else:
            cur_max_seq += 10
        cut.original_saw_route = cut.saw_route
        cut.saw_route = payload.saw_route
        cut.original_seq = cut.new_seq
        cut.new_seq = cur_max_seq
        cut.update_by = payload.updated_by
        db_session.add(cut)
    db_session.commit()
    return True


def split_cut_sequence_plan(*, db_session: Session, payload: CutSequencePlanSplit):
    cut = db_session.query(CutSequencePlan).filter(CutSequencePlan.id == payload.id).one_or_none()
    if not cut:
        raise HTTPException(status_code=400, detail="Cut sequence plan not found.")
    weight = cut.weight
    per_weight = weight / cut.new_bars

    for new in payload.items:
        if (
            db_session.query(CutSequencePlan)
            .filter(
                CutSequencePlan.rolling_id == cut.rolling_id,
                CutSequencePlan.saw_route == new.saw_route,
                CutSequencePlan.new_seq == new.new_seq,
            )
            .first()
        ):
            raise HTTPException(
                status_code=400, detail=f"The new sequence:{new.saw_route}{new.new_seq} already exists."
            )

        cut1 = CutSequencePlan(
            saw_route=new.saw_route,
            original_saw_route=cut.saw_route,
            new_seq=new.new_seq,
            original_seq=cut.new_seq,
            order_item_id=cut.order_item_id,
            original_bars=new.new_bars,
            new_bars=new.new_bars,
            weight=per_weight * new.new_bars,
            rolling_id=cut.rolling_id,
            created_by=payload.updated_by,
            updated_by=payload.updated_by,
            order_id=cut.order_id,
            rd_ri=new.rd_ri,
            load_pen=new.load_pen,
            load_no=new.load_no,
            pta_code=new.pta_code,
        )
        db_session.add(cut1)
        cut.new_bars = cut.new_bars - cut1.new_bars
        cut.weight = cut.weight - cut1.weight
        cut.updated_by = payload.updated_by
        cut.updated_at = payload.updated_at
        db_session.add(cut)
    db_session.commit()
    return True

def get_list_by_rolling_id(*, db_session, id: int) -> List[Optional[CutSequencePlan]]:
    return db_session.query(CutSequencePlan).filter(CutSequencePlan.rolling_id == id).all()

def get_list_by_rolling_id_and_route(*, db_session, id: int, route: str) -> List[Optional[CutSequencePlan]]:
    return db_session.query(CutSequencePlan).filter(CutSequencePlan.rolling_id == id, CutSequencePlan.saw_route == route).all()

def get_list_by_rolling_id_and_route_and_weight(*, db_session, id: int, route: str, weight: float) -> List[Optional[CutSequencePlan]]:
    return db_session.query(CutSequencePlan).filter(CutSequencePlan.rolling_id == id, CutSequencePlan.saw_route == route, CutSequencePlan.weight == weight).all()

def update_cut_seq(*, db_session, id, data):
    cut_seq_obj = db_session.query(CutSequencePlan).filter(CutSequencePlan.id == id).first()
    if not cut_seq_obj:
        raise HTTPException(status_code=400, detail=f"Cut sequence id: {id} is not found!")

    for key, value in data.items():
        setattr(cut_seq_obj, key, value)

    db_session.add(cut_seq_obj)
    db_session.commit()
    return cut_seq_obj

def get_cut_seq_by_id(*, db_session, cut_seq_id: int):
    cut_seq_obj = db_session.query(CutSequencePlan).filter(CutSequencePlan.id == cut_seq_id).first()
    if not cut_seq_obj:
        raise HTTPException(status_code=400, detail=f"Cut sequence id: {id} is not found!")

    return cut_seq_obj

def delete_cut_seq_by_id(*, db_session, cut_seq_id: int):
    existed = get_cut_seq_by_id(db_session=db_session, cut_seq_id=cut_seq_id)
    existed.is_deleted = 1
    db_session.commit()
    return existed

# 自动生成装车计划
def load_cut_sequences(*, db_session, cut_sequences: List[CutSequencePlan]):
    # 记录需要的load信息
    loads = []
    current_load = None
    current_load_weight = 0.0
    current_saw_route = None
    saw_route_counters = {}  # 维护每个锯切路线的车次编号

    for cut_seq in cut_sequences:
        order_item: OrderItem = cut_seq.order_item
        if order_item:
            length_mm = order_item.length_mm
            form = order_item.product_code
            product_size_code = f"{order_item.product_dim1}x{order_item.product_dim2}"
            kgm = order_item.product_dim3
            kgm = float(kgm) if kgm.find(".") > 0 else int(kgm)
            bundle_maxtrix_info = {
                "form": form,
                "size": product_size_code,
                "kg_per_metre": kgm,
                "max_bar_length": length_mm
            }
            num_bars = get_num_bars(db_session=db_session, bundle_maxtrix_info=bundle_maxtrix_info)
            if num_bars == 0:
                logger.warning(f"Not found num bars by: {bundle_maxtrix_info}")
                num_bars = cut_seq.new_bars
                # raise HTTPException(
                #     status_code=400, detail=f"Please check bundle matrix: {bundle_maxtrix_info} is not existed! {order_item.bws_store}"
                # )
        else:
            # 创建的order为111111的cut seq
            length_mm = cut_seq.length
            num_bars = cut_seq.new_bars
            kgm = cut_seq.order_group.product_type.dim3

        # 按照num bars计算当前cut seq装车重量(吨)
        weight_ton = float(round(float(length_mm / 1000) * float(kgm) * float(num_bars) / 1000, 3))

        # 获取当前cut seq的saw route
        saw_route = cut_seq.saw_route

        # 判断是否需要创建新车次
        need_new_load = False
        if current_load is not None:
            if current_saw_route != saw_route:    # 锯切路线变化
                need_new_load = True
            elif current_load_weight > 26:                 # 当前切割序列超重
                need_new_load = True

        # 若需要新车次，保存当前车次并重置状态
        if need_new_load:
            loads.append(current_load)
            current_load = None
            current_load_weight = 0.0
            current_saw_route = None
        
        # 若当前无车次或需要新车次，初始化新车次
        if current_load is None:
            # 获取当前锯切路线的车次编号
            if saw_route not in saw_route_counters:
                saw_route_counters[saw_route] = 1
            else:
                saw_route_counters[saw_route] += 1
            if cut_seq.pta_code == "ADC":
                load_name = None
            else:
                load_name = f"{saw_route}{saw_route_counters[saw_route]:03d}"

            current_load = {
                "name": load_name,
                "weight": 0.0,
                "cut_sequences": []
            }
            current_saw_route = saw_route

        # 将当前切割序列加入车次
        current_load["cut_sequences"].append((cut_seq, num_bars))
        current_load["weight"] += weight_ton
        current_load_weight += weight_ton
    
    # 处理最后一个车次
    if current_load is not None:
        loads.append(current_load)

    return loads


def auto_load_plan(*, db_session: Session, payload: AutoLoadPlanCreate, mill_id: int):
    # Auto generate load plan by bundle maxtrix
    created_cut_seqs = db_session.query(CutSequencePlan).filter(
        CutSequencePlan.rolling_id == payload.rolling_id,
        CutSequencePlan.order_group_id == payload.order_group_id,
        CutSequencePlan.is_deleted == 0
    ).order_by(asc(CutSequencePlan.saw_route), asc(CutSequencePlan.new_seq)).all()

    if not created_cut_seqs:
        raise HTTPException(
            status_code=400,
            detail=f"Can't auto load, caused: no cut sequence found!"
        )

    # Auto load plan only the cut sequences haven't been loaded
    for c_s in created_cut_seqs:
        if c_s.cut_seq_loads:
            raise HTTPException(status_code=400, detail=f"Can't auto load, caused: cut sequence id: {c_s.id} is already loaded!")

    loads = load_cut_sequences(db_session=db_session, cut_sequences=created_cut_seqs)
    need_created_loads = []
    load_cut_seq_records = []
    for load in loads:
        cut_seqs = load.get("cut_sequences", [])
        bundle_size = {}
        for cut_seq, bars in cut_seqs:
            bundle_size[cut_seq.id] = f"1*{bars}"

        load_create_obj = FinishedProductLoad(
            cut_seq_load_no=load.get("name"),
            total_weight_ton=load.get("weight"),
            bundle_size=json.dumps(bundle_size),
            updated_by=payload.updated_by,
            created_by=payload.created_by,
            rolling_id=payload.rolling_id,
            mill_id=mill_id,
            load_status="Created"
        )
        need_created_loads.append(load_create_obj)

    db_session.add_all(need_created_loads)
    db_session.commit()

    for load in need_created_loads:
        bundle_size = json.loads(load.bundle_size)
        for cut_seq_id in bundle_size.keys():
            load_cut_seq_records.append(
                {
                    "cut_sequence_plan_id": int(cut_seq_id),
                    "finished_product_load_id": load.id,
                }
            )
    # create finished product load cur sequence N to N records
    db_session.execute(finished_product_load_cut_sequence_plan.insert().values(load_cut_seq_records))
    db_session.commit()

    # update cut sequences no.load
    for cut_seq_obj in created_cut_seqs:
        cut_seq_obj.load_no = len(cut_seq_obj.cut_seq_loads)

    db_session.bulk_save_objects(created_cut_seqs)
    db_session.commit()


def get_loading_insts(*, db_session: Session, rolling_id: int, order_group_id: int):
    order_type_map = {
        87: "S", 184: "T", 274: "P"
    }
    cut_seqs = db_session.query(CutSequencePlan).filter(
        CutSequencePlan.rolling_id == rolling_id, CutSequencePlan.order_group_id == order_group_id
    ).order_by(asc(CutSequencePlan.saw_route), asc(CutSequencePlan.new_seq)).all()

    print_rows = []
    for cut_seq in cut_seqs:
        if not cut_seq.order_item or not cut_seq.order_item.order or not cut_seq.order_item.order.order_code:
            order_type = "STO"
        else:
            order_type = order_type_map.get(cut_seq.order_item.order.type_of_order, "")

        # calculate num ties
        order_export_type = cut_seq.order_item.order.order_export_type
        if cut_seq.order_item and cut_seq.order_item.length_mm:
            length = float(cut_seq.order_item.length_mm)
        else:
            length = float(cut_seq.length)

        num_ties = _calculate_num_ties(length, order_export_type)
        order_item_remarks = []
        if cut_seq.order_item:
            order_item_remarks = cut_seq.order_item.order_item_remarks

        for load in cut_seq.cut_seq_loads:
            bundle_size = json.loads(load.bundle_size)
            row_info = {
                "wt_metre": round(cut_seq.order_group.product_type.dim3, 2),
                "thick": cut_seq.rolling.thick or 0.0,
                "seq_no": f"{cut_seq.saw_route}{cut_seq.new_seq:03d}",
                "num_bars": cut_seq.new_bars,
                "length": round(length / 1000, 3),
                "quality_code": cut_seq.order_item.quality_code,
                "num_ties": num_ties,
                "bundle_size": bundle_size.get(str(cut_seq.id), ""),
                "order_type": order_type,
                "max_bars": bundle_size.get(str(cut_seq.id), "").split("*")[-1].strip(),
                "remarks": ",".join([remark.text for remark in order_item_remarks if remark.text])
            }
            print_rows.append(row_info)

    return print_rows


def _calculate_num_ties(length_mm, order_export_type):
    # calculate num ties
    if not length_mm:
        length_mm = 0

    length_m = round(float(length_mm) / 1000, 3)
    if order_export_type == "X":
        if length_m < 7:
            num_ties = 4
        elif 7 <= length_m <= 14.999:
            num_ties = 5
        else:
            num_ties = 6
    else:
        if length_m <= 12.2:
            num_ties = 3
        elif 12.2 < length_m <= 15.5:
            num_ties = 4
        elif 15.5 < length_m <= 18.3:
            num_ties = 5
        else:
            num_ties = 6

    return num_ties
