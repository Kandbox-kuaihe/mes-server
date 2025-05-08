import uuid
import json
from typing import List, Optional
import math

from fastapi import HTTPException
from sqlalchemy import select, func, insert
from sqlalchemy.sql import and_

from dispatch.common.utils.func import try_float_num
from dispatch.config import LOAD_AUTO_PLAN_TONNAGE
from dispatch.runout_admin.finished_product.models_secondary_load import finished_product_load
from dispatch.runout_admin.finished_product_load.models_secondary_cut_sequence import finished_product_load_cut_sequence_plan

from .models import (
    FinishedProductLoad,
    FinishedProductLoadCreate,
    FinishedProductLoadMove,
    FinishedProductLoadUpdate,
    LoadAutoPlanCreate,
    LoadCarryoutCreate,
)
from .enums import AutoPlanType
from dispatch.runout_admin.finished_product.models import FinishedProduct
from dispatch.order_admin.order_item.models import OrderItem
from dispatch.area import service as area_service
from dispatch.runout_admin.advice.models import  Advice
from ..finished_product_history.models import FinishedProductHistoryChangeTypeEnum, FinishedProductHistory
from ..finished_product_history.service import bulk_create_finished_product_history
from dispatch.bundle_matrix.models import BundleMatrix
from dispatch.rolling.cut_sequence_plan.models import CutSequencePlan


def get(
    *,
    db_session,
    id: int
) -> Optional[FinishedProductLoad]:

    return db_session.get(FinishedProductLoad, id)


def get_by_code(
    *,
    db_session,
    code: str
) -> Optional[FinishedProductLoad]:
    
    stmt = select(FinishedProductLoad).where(FinishedProductLoad.code == code)
    return db_session.scalar(stmt)

def create(
    *,
    db_session,
    create_in: FinishedProductLoadCreate
) -> FinishedProductLoad:
    create_in.load_status = 'Created'
    his = []
    uid = uuid.uuid4()
    bind_finished_product_ids = create_in.bind_finished_product_ids
    is_create_advice = create_in.is_create_advice
    create_advice_order_item_ids = create_in.create_advice_order_item_ids
    created = FinishedProductLoad(**create_in.model_dump(exclude={
        "bind_finished_product_ids",
        "is_create_advice",
        "create_advice_order_item_ids",
    }))
    db_session.add(created)
    db_session.commit()
    if not created.code:
        created.code = created.id
        db_session.commit()
    created.max_weight_tonnage = LOAD_AUTO_PLAN_TONNAGE
    if bind_finished_product_ids:
        finished_products = db_session.query(FinishedProduct).filter(FinishedProduct.id.in_(bind_finished_product_ids)).all()
        created.finished_products.extend(finished_products)
        for finished_product_id in bind_finished_product_ids:
            finished_product_get = db_session.get(FinishedProduct, finished_product_id)
            # finished_product_get.load_id = created.id

            his.append({
                "uuid": uid,
                "mill_id": finished_product_get.mill_id,
                "change_type": FinishedProductHistoryChangeTypeEnum.LOAD_CREATE,
                "created_by": create_in.updated_by,
                "code": finished_product_get.code,
                'rolling_code': finished_product_get.rolling.rolling_code if finished_product_get.rolling else None,
                'runout_code': finished_product_get.runout.runout_code if finished_product_get.runout else None,
                'area_code': finished_product_get.area.code if finished_product_get.area else None,
                'cast_no': finished_product_get.cast.cast_code if finished_product_get.cast else None,
                'spec_code': finished_product_get.spec.spec_code if finished_product_get.spec else None,
                'order_num': finished_product_get.order.order_code if finished_product_get.order else None,
                'order_item_num': finished_product_get.order_item.line_item_code if finished_product_get.order_item else None,
                'product_type': finished_product_get.product_type.code if finished_product_get.product_type else None,
                "status": finished_product_get.status,
                "kg": finished_product_get.kg,
                "length_mm": finished_product_get.length_mm,
                "quantity": finished_product_get.quantity,
                # "advice_no": finished_product_get.advice.advice_code if finished_product_get.advice else None,
                "exist_flag": finished_product_get.exist_flag,
            })
        bulk_create_finished_product_history(db_session=db_session, finished_product_history_in=his)
        db_session.commit()
    if is_create_advice:
        for order_item_id in create_advice_order_item_ids:
            advice = Advice(load_id=created.id, order_item_id=order_item_id)
            db_session.add(advice)
            db_session.commit()
            advice.advice_code = str(advice.id)
            db_session.commit()
    return created


def new_create(
    *,
    db_session,
    create_in: FinishedProductLoadCreate,
    flush: bool = False
) -> FinishedProductLoad:
    create_in.load_status = 'Carry Out'
    his = []
    uid = uuid.uuid4()
    bind_finished_product_ids = create_in.bind_finished_product_ids
    is_create_advice = create_in.is_create_advice
    create_advice_order_item_ids = create_in.create_advice_order_item_ids
    created = FinishedProductLoad(**create_in.model_dump(exclude={
        "bind_finished_product_ids",
        "is_create_advice",
        "create_advice_order_item_ids",
    }))
    db_session.add(created)
    if flush:
        db_session.flush()
    if not created.code:
        created.code = created.id
        # db_session.commit()
    created.max_weight_tonnage = LOAD_AUTO_PLAN_TONNAGE
    if bind_finished_product_ids:
        finished_products = db_session.query(FinishedProduct).filter(FinishedProduct.id.in_(bind_finished_product_ids)).all()
        created.finished_products.extend(finished_products)
        for finished_product_id in bind_finished_product_ids:
            finished_product_get = db_session.get(FinishedProduct, finished_product_id)
            # finished_product_get.load_id = created.id

            his.append({
                "uuid": uid,
                "mill_id": finished_product_get.mill_id,
                "change_type": FinishedProductHistoryChangeTypeEnum.LOAD_CREATE,
                "created_by": create_in.updated_by,
                "code": finished_product_get.code,
                'rolling_code': finished_product_get.rolling.rolling_code if finished_product_get.rolling else None,
                'runout_code': finished_product_get.runout.runout_code if finished_product_get.runout else None,
                'area_code': finished_product_get.area.code if finished_product_get.area else None,
                'cast_no': finished_product_get.cast.cast_code if finished_product_get.cast else None,
                'spec_code': finished_product_get.spec.spec_code if finished_product_get.spec else None,
                'order_num': finished_product_get.order.order_code if finished_product_get.order else None,
                'order_item_num': finished_product_get.order_item.line_item_code if finished_product_get.order_item else None,
                'product_type': finished_product_get.product_type.code if finished_product_get.product_type else None,
                "status": finished_product_get.status,
                "kg": finished_product_get.kg,
                "length_mm": finished_product_get.length_mm,
                "quantity": finished_product_get.quantity,
                # "advice_no": finished_product_get.advice.advice_code if finished_product_get.advice else None,
                "exist_flag": finished_product_get.exist_flag,
            })
        db_session.bulk_insert_mappings(
            FinishedProductHistory, his
        )
        # bulk_create_finished_product_history(db_session=db_session, finished_product_history_in=his)
        # db_session.commit()
    return created

def update(
    *,
    db_session,
    updated: FinishedProductLoad,
    update_in: FinishedProductLoadUpdate,
) -> FinishedProductLoad:

    bind_finished_product_ids = update_in.bind_finished_product_ids
    is_create_advice = update_in.is_create_advice
    create_advice_order_item_ids = update_in.create_advice_order_item_ids
    update_data = update_in.model_dump(exclude={
        "bind_finished_product_ids",
        "is_create_advice",
        "create_advice_order_item_ids",
    })
    for field, field_value in update_data.items():
        setattr(updated, field, field_value)
    db_session.add(updated)
    db_session.commit()
    if bind_finished_product_ids:
        db_session.query(finished_product_load).filter(
            finished_product_load.c.finished_product_load_id == updated.id
        ).delete(synchronize_session=False)
        for finished_product_id in bind_finished_product_ids:
            db_session.execute(finished_product_load.insert().values(
                finished_product_id=finished_product_id,
                finished_product_load_id=updated.id
            ))
        db_session.commit()
    if is_create_advice:
        for order_item_id in create_advice_order_item_ids:
            advice_stmt = select(Advice).where(Advice.load_id==updated.id).where(Advice.order_item_id==order_item_id)
            advice_existed = db_session.scalar(advice_stmt)
            if not advice_existed:
                advice = Advice(load_id=updated.id, order_item_id=order_item_id)
                db_session.add(advice)
                db_session.commit()
                advice.advice_code = str(advice.id)
                db_session.commit()

    return updated


def delete(
    *,
    db_session,
    deleted: FinishedProductLoad,
) -> FinishedProductLoad:
    
    deleted.is_deleted = 1
    db_session.commit()
    return deleted

def move_to(*, db_session, load_in: FinishedProductLoadMove):
    # to_area = area_service.get_by_code(db_session=db_session, code=load_in.area_code)
    for code in load_in.codes:
        finished_product_obj = get_by_code(db_session=db_session, code=code)
        if finished_product_obj:
            finished_product_obj.to_area_id = load_in.area_code
            finished_product_obj.business_type = load_in.business_type
            finisheds = finished_product_obj.finished_products
            for finished in finisheds:
                finished.area_id = load_in.area_code

    
    db_session.commit()
    return True

def tip_load(*, db_session, load_in: FinishedProductLoadMove):
    his = []
    uid = uuid.uuid4()
    finished_product_obj = get_by_code(db_session=db_session, code=load_in.code)
    if finished_product_obj:
        finished_product_obj.load_status = "Unload"
        finished_product_obj.comment = load_in.comment
        finished_product_obj.to_area_id = load_in.area_id
        finished_product_obj.business_type = load_in.business_type
        finished_items = finished_product_obj.finished_products
        if len(finished_items) == 0:
            raise HTTPException(status_code=400,
                                detail="No finished product exists under the current advice. Unable to proceed with tip.")
        for finished in finished_items:
            if (finished.exist_flag == "Y" or finished.exist_flag is None) and (finished.rework_status == "Complete" or finished.rework_status is None):
                # i.load_status = "Tipped"
                # finished.area_id = load_in.area_id
                # finished.stock_type = load_in.business_type
                finished.stock_type = load_in.business_type
                finished.updated_by = load_in.updated_by
                finished.updated_at = load_in.updated_at
                his.append({
                    "uuid": uid,
                    "mill_id": finished.mill_id,
                    "change_type": FinishedProductHistoryChangeTypeEnum.LOAD_TIP,
                    "created_by": load_in.updated_by,
                    "code": finished.code,
                    'rolling_code': finished.rolling.rolling_code if finished.rolling else None,
                    'runout_code': finished.runout.runout_code if finished.runout else None,
                    'area_code': finished.area.code if finished.area else None,
                    'cast_no': finished.cast.cast_code if finished.cast else None,
                    'spec_code': finished.spec.spec_code if finished.spec else None,
                    'order_num': finished.order.order_code if finished.order else None,
                    'order_item_num': finished.order_item.line_item_code if finished.order_item else None,
                    'product_type': finished.product_type.code if finished.product_type else None,
                    "status": finished.status,
                    "kg": finished.kg,
                    "length_mm": finished.length_mm,
                    "quantity": finished.quantity,
                    # "advice_no": finished.advice.advice_code if finished.advice else None,
                    "exist_flag": finished.exist_flag,
                })
            else:
                raise HTTPException(status_code=400, detail="The finished product is not ready to be tipped")
        bulk_create_finished_product_history(db_session=db_session, finished_product_history_in=his)

    db_session.commit()
    return True

def auto_plan(
    *,
    db_session,
    auto_plan_in: LoadAutoPlanCreate,
    current_user,
) -> List[FinishedProductLoad]:
    order_item_get = db_session.get(OrderItem, auto_plan_in.work_order_item_id)
    if not order_item_get or not order_item_get.tonnage:
        raise HTTPException(status_code=400, detail="order item not found or tonnage is empty")

    if auto_plan_in.auto_plan_type == AutoPlanType.ROAD:
        planed_load_number = math.ceil(float(order_item_get.tonnage) / LOAD_AUTO_PLAN_TONNAGE)
        stmt = select(func.count(FinishedProductLoad.id)).where(FinishedProductLoad.order_item_id == auto_plan_in.work_order_item_id)
        existed_load_number = db_session.scalar(stmt)
        existed_load_number = int(existed_load_number) if existed_load_number else 0
        if existed_load_number >= planed_load_number:
            raise HTTPException(status_code=400, detail="There are already enough loads to available")

        actual_load_list = []
        actual_load_number = planed_load_number - existed_load_number
        for _ in range(actual_load_number):
            load_create = FinishedProductLoad(
                order_item_id=auto_plan_in.work_order_item_id,
                load_type=AutoPlanType.ROAD,
                created_by=current_user.email,
                updated_by=current_user.email,
            )
            db_session.add(load_create)
            db_session.commit()
            load_create.code = load_create.id
            db_session.commit()
            load_create.max_weight_tonnage = LOAD_AUTO_PLAN_TONNAGE
            actual_load_list.append(load_create)

        return actual_load_list
    elif auto_plan_in.auto_plan_type == AutoPlanType.LOAD_INSTRUCTIONS:
        bundle_matrix_id = auto_plan_in.bundle_matrix_id
        bundle_matrix = db_session.get(BundleMatrix, bundle_matrix_id)
        if not bundle_matrix:
            raise HTTPException(status_code=400, detail="The bundle matrix does not exist")

        planed_load_number = math.ceil(float(order_item_get.tonnage) / LOAD_AUTO_PLAN_TONNAGE)
        stmt = select(func.count(FinishedProductLoad.id)).where(
            FinishedProductLoad.order_item_id == auto_plan_in.work_order_item_id)
        existed_load_number = db_session.scalar(stmt)
        existed_load_number = int(existed_load_number) if existed_load_number else 0
        if existed_load_number >= planed_load_number:
            raise HTTPException(status_code=400, detail="There are already enough loads to available")

        actual_load_list = []
        actual_load_number = planed_load_number - existed_load_number
        for _ in range(actual_load_number):
            load_create = FinishedProductLoad(
                order_item_id=auto_plan_in.work_order_item_id,
                load_type=AutoPlanType.LOAD_INSTRUCTIONS,
                piece_count=0,
                bundle_size=bundle_matrix.num_bars,
                created_by=current_user.email,
                updated_by=current_user.email,
            )
            db_session.add(load_create)
            db_session.commit()
            load_create.code = load_create.id
            db_session.commit()
            load_create.max_weight_tonnage = LOAD_AUTO_PLAN_TONNAGE
            actual_load_list.append(load_create)

        return actual_load_list


def get_planed_load_list(
    *,
    db_session,
    order_item_id: int,
):
    stmt = select(FinishedProductLoad).where(
        FinishedProductLoad.order_item_id == order_item_id
    ).where(
        FinishedProductLoad.is_deleted == 0
    )
    planed_load_list = []
    for load in db_session.scalars(stmt):
        load.max_weight_tonnage = LOAD_AUTO_PLAN_TONNAGE
        planed_load_list.append(load)

    return planed_load_list


def carry_out(
    *,
    db_session,
    carry_out_in: LoadCarryoutCreate,
    current_user,
):
    stmt = select(FinishedProductLoad).where(
        FinishedProductLoad.order_item_id == carry_out_in.work_order_item_id,
        FinishedProductLoad.is_deleted == 0
    )
    loads = []
    loads_ids = []
    for load in db_session.scalars(stmt):
        load.finished_products_weight = 0.0
        if load.finished_products and len(load.finished_products) > 0:
            for bundle in load.finished_products:
                load.finished_products_weight += try_float_num(bundle.estimated_weight_kg)
        loads.append(load)
        loads_ids.append(load.id)

    stmt = select(FinishedProduct).where(
        FinishedProduct.order_item_id == carry_out_in.work_order_item_id,
        FinishedProduct.is_deleted == 0
    )
    allocated_bundles = []
    for bundle in db_session.scalars(stmt):
        if bundle.loads and len(bundle.loads) > 0:
            for bundle_load in bundle.loads:
                if bundle_load.id in loads_ids:
                    break
            else:
                allocated_bundles.append(bundle)
        else:
            allocated_bundles.append(bundle)

    def allocate_load(bundle):
        for load in loads:
            if (load.finished_products_weight + try_float_num(bundle.estimated_weight_kg)) / 1000 >  LOAD_AUTO_PLAN_TONNAGE:
                break
            else:
                load.finished_products_weight += try_float_num(bundle.estimated_weight_kg)
                load.finished_products.append(bundle)
                return True
        return False

    successful_bundle_ids = []
    failed_bundle_ids = []
    if len(allocated_bundles) > 0:
        for bundle in allocated_bundles:
            result = allocate_load(bundle)
            if result:
                successful_bundle_ids.append(bundle.id)
            else:
                failed_bundle_ids.append(bundle.id)
        db_session.commit()

    return {
        "successful_bundle_ids": successful_bundle_ids,
        "failed_bundle_ids": failed_bundle_ids,
    }


def bulk_create_load_cut_seq(*, db_session, cut_seq_id: int, load_cut_seq_in: List[FinishedProductLoadCreate]):
    data = []
    for load in load_cut_seq_in:
        res = db_session.execute(
            select(finished_product_load_cut_sequence_plan).where(
                finished_product_load_cut_sequence_plan.c.cut_sequence_plan_id == cut_seq_id
            ).where(
                finished_product_load_cut_sequence_plan.c.finished_product_load_id == load.id
            )
        )
        if not res.first():
            data.append({
                "cut_sequence_plan_id": cut_seq_id, "finished_product_load_id": load.id
            })
    if data:
        db_session.execute(finished_product_load_cut_sequence_plan.insert().values(data))
        db_session.commit()


def get_loads_by_cut_seq_id(*, db_session, cut_seq_id: int):
    cut_seq_obj = db_session.query(CutSequencePlan).filter(CutSequencePlan.id == cut_seq_id).first()
    if not cut_seq_obj:
        raise HTTPException(status_code=400, detail=f"Cut sequence plan id: {cut_seq_id} is not found!")
    return cut_seq_obj.cut_seq_loads


def get_loads_by_rolling_og_route(
        *, db_session, rolling_id: int, order_group_id: int, route: str
    ):
    cut_seqs = db_session.query(CutSequencePlan).filter(and_(
        CutSequencePlan.rolling_id == rolling_id,
        CutSequencePlan.order_group_id == order_group_id,
        CutSequencePlan.saw_route == route
    )).all()
    loads = []
    for c_s in cut_seqs:
        loads.extend(c_s.cut_seq_loads)
    
    return loads

def update_cut_seq_load(*, db_session, cut_seq_id: int, update_info:dict):
    load_id = update_info.pop("id")
    if not load_id:
        raise HTTPException(status_code=400, detail=f"Not found id by update info: {update_info}!")
    
    load_obj = db_session.query(FinishedProductLoad).filter(FinishedProductLoad.id == load_id).first()
    curr_bundle_size = json.loads(load_obj.bundle_size) if load_obj.bundle_size else {}
    curr_bundle_size[str(cut_seq_id)] = update_info.pop("bundle_size")
    load_obj.bundle_size = json.dumps(curr_bundle_size)

    for key, value in update_info.items():
        setattr(load_obj, key, value)

    db_session.add(load_obj)
    db_session.commit()
    return load_obj


def get_by_load_fp_id(db_session, load_id, finished_product_id):
    return db_session.query(finished_product_load).filter(
        finished_product_load.c.finished_product_load_id == load_id,
        finished_product_load.c.finished_product_id == finished_product_id
    ).all()


def create_by_load_fp_id(db_session, load_id, finished_product_id):
    new_fp_load = insert(finished_product_load).values(
        finished_product_load_id=load_id,
        finished_product_id=finished_product_id
    )
    db_session.execute(new_fp_load)


def update_piece_count(
    *,
    db_session,
    load_id: int
) -> None:
    count = db_session.scalar(
        select(func.count()).where(
            finished_product_load.c.finished_product_load_id == load_id
        )
    )
    db_session.query(FinishedProductLoad).filter_by(id=load_id).update(
        {"piece_count": count}
    )