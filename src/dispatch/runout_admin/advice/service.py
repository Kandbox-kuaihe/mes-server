import logging
import uuid
from datetime import datetime
from typing import Optional

from fastapi import HTTPException

from dispatch.area.models import Area
from dispatch.mill.models import Mill
from dispatch.order_admin.order.models import Order
from dispatch.order_admin.order_item.models import OrderItem
from dispatch.runout_admin.finished_product.models import FinishedProduct
# from dispatch.runout_admin.finished_product import service as finished_product_service
from dispatch.runout_admin.finished_product_load.models import FinishedProductLoad
from dispatch.shiftAdmin.shift.models import Shift
from .models import Advice, AdviceCreate, AdviceMove, AdviceRead, AdviceSplit, AdviceUpdate, AdviceIDPagination, \
    AdviceStatusEnum
from sqlalchemy_filters import apply_pagination
from ..finished_product.models_secondary_advice import finished_product_advice
from ..finished_product.models_secondary_load import finished_product_load
from ..finished_product_history.models import FinishedProductHistoryChangeTypeEnum
from ..finished_product_history.service import bulk_create_finished_product_history
from ..transport.models import Transport, TransportStatusEnum
from dispatch.config import get_mill_ops, MILLEnum

logging.basicConfig(level=logging.INFO)

from dispatch.log import getLogger
log = getLogger(__name__)

def get(*, db_session, id: int) -> Optional[Advice]:
    return db_session.query(Advice).filter(Advice.id == id).one_or_none()

def get_by_code(*, db_session, advice_code: str) -> Optional[Advice]:
    return db_session.query(Advice).filter(Advice.advice_code == advice_code).one_or_none()

def get_finished_product(*, db_session, advice_in: AdviceIDPagination):
    # advice = get_by_code(db_session=db_session, advice_code=advice_in.advice_code)
    # if advice.load_id is None:
    #     finished_product = db_session.query(FinishedProduct).filter(False)
    # else:
    # finished_product = db_session.query(FinishedProduct).filter(and_(FinishedProduct.advice_id == advice.id, FinishedProduct.is_deleted == 0))

    finished_product = db_session.query(FinishedProduct).join(
        finished_product_advice, finished_product_advice.c.finished_product_id == FinishedProduct.id
    ).filter(
        finished_product_advice.c.advice_id == advice_in.advice_id, FinishedProduct.exist_flag == 'Y'
    )
    query, pagination = apply_pagination(finished_product, page_number=advice_in.page, page_size=advice_in.itemsPerPage)
    data = list(query)
    for item in data:
        count = db_session.query(FinishedProduct).filter(FinishedProduct.mult_id == item.id)
        cut_code_list = []
        counts = 0
        if count.count() > 0:
            for i in count.all():
                if i.cut_code:
                    cut_code_list.append(i.cut_code)
            counts = count.count()
            cut_codes = ",".join(cut_code_list)

        else:
            cut_codes = item.cut_code
            counts = 1
        item.cut_codes = cut_codes if cut_codes else ""
        counts = counts if item.mult_type is not None else 0
        item.cut_into = counts if counts else 0
    return {
        "items": data,
        "itemsPerPage": pagination.page_size,
        "page": pagination.page_number,
        "total": pagination.total_results
    }

def split_advice_f(*, db_session, id: int, advice_in: AdviceCreate, current_user) -> Advice:
    try:
        db_session.query(finished_product_advice).filter(finished_product_advice.c.advice_id == id, finished_product_advice.c.finished_product_id.in_(advice_in.finished_ids)).delete(synchronize_session=False)
        advice_in.updated_at = datetime.now()
        advice_in.updated_by = current_user.email
        advice_in.mill_id = current_user.current_mill_id
        advice = create(db_session=db_session, advice_in=advice_in)
        db_session.commit()
    except Exception as e:
        db_session.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Error: {str(e)}"
        )
    return advice

def get_tbm_prefix_for_business_type(business_type: str) -> str:
    """Returns the appropriate prefix based on business type."""
    if business_type == "bws":
        return "T"
    elif business_type == "service_center":
        return "T"
    elif business_type == "roster":
        return "C"
    elif business_type == "scrap":
        return "S"
    elif business_type == "internal":
        return ""  # No prefix for Internal
    else:
        return ""

def validate_finished_products(db_session, finished_products_or_ids, business_type):
    # 判断传入的是 IDs 还是对象
    if isinstance(finished_products_or_ids, list):
        if all(isinstance(fp, FinishedProduct) for fp in finished_products_or_ids):
            # 直接使用已查询的对象
            finished_products = finished_products_or_ids
        elif all(isinstance(fp, (int, str)) for fp in finished_products_or_ids):
            # 查询数据库
            finished_products = db_session.query(FinishedProduct).filter(
                FinishedProduct.id.in_(finished_products_or_ids)).all()
        else:
            raise HTTPException(status_code=400,
                                detail="Invalid input: must be a list of IDs or FinishedProduct objects.")
    else:
        raise HTTPException(status_code=400, detail="Invalid input: finished_products_or_ids must be a list.")

    if business_type in ['bws', 'roster']:
        # 检查是否有 order_id 为空的情况
        missing_orders = [fp.code for fp in finished_products if not fp.order_id]
        if missing_orders:
            raise HTTPException(
                status_code=400,
                detail=f"The following finished products are missing order: {', '.join(missing_orders)}"
            )
        # 检查 order_id 是否一致
        order_ids = {fp.order_id for fp in finished_products}
        if len(order_ids) > 1:
            raise HTTPException(status_code=400,
                                detail="The current finished product orders are inconsistent. Please select a new one")

        # 检查是否 mult or rework
        for finished_product in finished_products:
            if finished_product.exist_flag not in [None, "Y"]:
                raise HTTPException(status_code=400,
                                    detail=f"At present, the {finished_product.code} finished product is being mult")
            if finished_product.rework_type not in [None, "Complete"]:
                raise HTTPException(status_code=400,
                                    detail=f"At present, the {finished_product.code} finished product is being rework")
    elif business_type == 'scrap':
        for finished_product in finished_products:
            if finished_product.allocation_status != 'scrap':
                raise HTTPException(status_code=400,
                                    detail=f"The finished product must be in scrap state")

def get_next_srsm_advice_code(db_session, new_id: int):
    letter_sequence = ["B", "C", "D", "E", "F", "G", "H", "J", "K"]  # 跳过 "I"

    # 查询当前最新的 SRSM 代码
    latest_advice = (
        db_session.query(Advice)
        .filter(Advice.advice_code.like("SM%"))
        .order_by(Advice.advice_code.desc())
        .first()
    )

    if not latest_advice:
        current_letter = "B"  # 初始字母
    else:
        latest_code = latest_advice.advice_code  # 例如 "SMB9999"
        current_letter = latest_code[2]  # "B"

        # 检查是否需要更新字母
        last_id = latest_advice.id  # 获取最近的 ID
        if str(last_id)[-4:] == "9999":  # 如果 ID 的最后四位是 9999
            letter_index = letter_sequence.index(current_letter)
            current_letter = (
                "B" if letter_index == len(letter_sequence) - 1 else letter_sequence[letter_index + 1]
            )

    # 截取 ID 的最后四位
    new_number = str(new_id)[-4:]
    return f"SM{current_letter}{new_number}"

def create(*, db_session, advice_in: AdviceCreate):
    his = []
    uid = uuid.uuid4()
    order = None
    order_item = None
    from_area = None
    to_area = None
    shift = None
    load = None
    transport = None
    curr_area = None
    mill = None
    finished_products = []
    
    if advice_in.order_id:
        order = db_session.query(Order).filter(Order.id == advice_in.order_id).one_or_none()
    if advice_in.order_item_id:
        order_item = db_session.query(OrderItem).filter(OrderItem.id == advice_in.order_item_id).one_or_none()
    if advice_in.from_area_id:
        from_area = db_session.query(Area).filter(Area.id == advice_in.from_area_id).one_or_none()
    if advice_in.to_area_id:
        to_area = db_session.query(Area).filter(Area.id == advice_in.to_area_id).one_or_none()
    if advice_in.shift_id:
        shift = db_session.query(Shift).filter(Shift.id == advice_in.shift_id).one_or_none()
    if advice_in.load_id:
        load = db_session.query(FinishedProductLoad).filter(FinishedProductLoad.id == advice_in.load_id).one_or_none()
    if advice_in.transport_id:
        transport = db_session.query(Transport).filter(Transport.id == advice_in.transport_id).one_or_none()
    if advice_in.curr_area_id:
        curr_area = db_session.query(Area).filter(Area.id == advice_in.curr_area_id).one_or_none()

    if advice_in.mill_id:
        mill = db_session.query(Mill).filter(Mill.id == advice_in.mill_id).one_or_none()
    # business_type = advice_in.business_type
    # prefix = get_prefix_for_business_type(business_type)
    finished_product_ids = advice_in.finished_ids
    if finished_product_ids:
        finished_products = db_session.query(FinishedProduct).filter(FinishedProduct.id.in_(finished_product_ids)).all()
        validate_finished_products(db_session, finished_products, advice_in.business_type)
        for finished_product in finished_products:
            advices = finished_product.advice
            for advice in advices:
                if advice.status == AdviceStatusEnum.ENROUTE:
                    raise HTTPException(status_code=400,
                                        detail=f"Product {finished_product.code} is already in advice {advice.advice_code}")
    else:
        raise HTTPException(status_code=400,
                            detail="Please add at least one finished product")
    if not advice_in.advice_code:
        advice_in.advice_code = str(uuid.uuid4())
    advice = Advice(**advice_in.dict(
        exclude={"flex_form_data", "order", "order_item", "from_area", "to_area", "shift", "load", "finished_ids",
                 "transport", "curr_area", "mill", "is_load_status"}
    ),order=order, order_item=order_item, from_area=from_area, to_area=to_area, shift=shift, load=load,
                    transport=transport, curr_area=curr_area, mill=mill)
    db_session.add(advice)
    db_session.commit()
    db_session.refresh(advice)  # 确保获取 ID

    # 检查 ID 是否导致 SRSM advice_code 变成 0000
    if str(advice.id)[-4:] == "0000":
        db_session.delete(advice)
        db_session.commit()

        # 重新创建 Advice
        advice = Advice(**advice_in.dict(
            exclude={"flex_form_data", "order", "order_item", "from_area", "to_area", "shift", "load", "finished_ids",
                     "transport", "curr_area", "mill", "is_load_status"}
        ), order=order, order_item=order_item, from_area=from_area, to_area=to_area, shift=shift, load=load,
                        transport=transport, curr_area=curr_area, mill=mill)

        db_session.add(advice)
        db_session.commit()
        db_session.refresh(advice)  # 确保 ID 更新

    # 生成 advice_code
    # advice.advice_code = (
    #     get_next_srsm_advice_code(db_session, advice.id) if advice_in.mill_id == 1 else str(advice.id)
    # )

    if get_mill_ops(mill.id) == MILLEnum.MILL1:
        # get_mill_ops(mill.code) == MILLEnum.MILL1
        advice.advice_code = get_next_srsm_advice_code(db_session, advice.id)
    elif get_mill_ops(mill.id) == MILLEnum.MILL410:
        advice.advice_code = get_tbm_prefix_for_business_type(advice_in.business_type) + str(advice.id)
    else:
        advice.advice_code = str(advice.id)
    advice.haulier = str(advice.haulier)
    advice.finished_product.extend(finished_products)
    is_load_status = advice_in.is_load_status
    if is_load_status:
        db_session.query(FinishedProductLoad).filter(FinishedProductLoad.id == advice_in.load_id).update({
            'load_status': 'Carry Out'
        })
    for finished in finished_products:
        advice_num = finished.advice
        if len(advice_num) != 0:
            finished.advice_status = "Adviced"
        else:
            finished.advice_status = None
        # finished = finished_product_service.get(db_session=db_session, id=finished)
        # finished = db_session.query(FinishedProduct).filter(FinishedProduct.id == finished).one_or_none()
        his.append({
            "uuid": uid,
            "mill_id": finished.mill_id,
            "change_type": FinishedProductHistoryChangeTypeEnum.ADVICE_CREATE,
            "created_by": advice_in.updated_by,
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
            "advice_no": advice.advice_code,
            "exist_flag": finished.exist_flag,
        })
    bulk_create_finished_product_history(db_session=db_session, finished_product_history_in=his)
    db_session.add(advice)
    db_session.commit()
    return advice

def get_advice_f(*, db_session, id: int):
    advice = db_session.query(Advice).filter(Advice.id == id).one_or_none()
    finishd_product = advice.finished_product
    return {
        "advice": advice,
        "finished_product": finishd_product
    }


def update(*, db_session, advice: Advice, advice_in: AdviceUpdate) -> Advice:
    order = None
    order_item = None
    from_area = None
    to_area = None
    shift = None
    mill = None
    load = None
    transport = None
    curr_area = None
    
    if advice_in.order_id:
        order = db_session.query(Order).filter(Order.id == advice_in.order_id).one_or_none()
    if advice_in.order_item_id:
        order_item = db_session.query(OrderItem).filter(OrderItem.id == advice_in.order_item_id).one_or_none()
    if advice_in.from_area_id:
        from_area = db_session.query(Area).filter(Area.id == advice_in.from_area_id).one_or_none()
    if advice_in.to_area_id:
        to_area = db_session.query(Area).filter(Area.id == advice_in.to_area_id).one_or_none()
    if advice_in.shift_id:
        shift = db_session.query(Shift).filter(Shift.id == advice_in.shift_id).one_or_none()
    if advice_in.mill_id:
        mill = db_session.query(Mill).filter(Mill.id == advice_in.mill_id).one_or_none()
    if advice_in.load_id:
        load = db_session.query(FinishedProductLoad).filter(FinishedProductLoad.id == advice_in.load_id).one_or_none()
    if advice_in.transport_id:
        transport = db_session.query(Transport).filter(Transport.id == advice_in.transport_id).one_or_none()
    if advice_in.curr_area_id:
        curr_area = db_session.query(Area).filter(Area.id == advice_in.curr_area_id).one_or_none()

    # business_type = advice_in.business_type
    # prefix = get_prefix_for_business_type(business_type)

    update_data = advice_in.dict(
        exclude={"flex_form_data", "order", "order_item", "from_area", "to_area", "shift", "mill", "load", "finished_ids", "transport", "curr_area"}
    )

    for key, value in update_data.items():
        setattr(advice, key, value)
    advice.order = order
    advice.order_item = order_item
    advice.from_area = from_area
    advice.to_area = to_area
    advice.shift = shift
    advice.mill = mill
    advice.load = load
    advice.transport = transport
    advice.curr_area = curr_area
    # advice.advice_code = str(advice.id)

    # 处理 finished_product_ids
    # finished_product_ids = advice_in.finished_ids
    # if finished_product_ids:
    #     # 首先将所有与当前 advice 关联的 finished products 的 advice_id 置为 None
    #     db_session.query(FinishedProduct).filter(FinishedProduct.advice_id == advice.id).update(
    #         {"advice_id": None}, synchronize_session=False
    #     )
    #     # 然后将新的 finished products 关联到当前 advice
    #     db_session.query(FinishedProduct).filter(FinishedProduct.id.in_(finished_product_ids)).update(
    #         {"advice_id": advice.id}, synchronize_session=False
    #     )

    finished_product_ids = advice_in.finished_ids
    if finished_product_ids:
        # finished_products = db_session.query(FinishedProduct).filter(FinishedProduct.id.in_(finished_product_ids)).all()
        validate_finished_products(db_session, finished_product_ids, advice_in.business_type)
        # for finished_product in finished_products:
        #     advices = finished_product.advice
        #     for advice in advices:
        #         if advice.status == AdviceStatusEnum.ENROUTE:
        #             raise HTTPException(status_code=400,
        #                                 detail=f"Product {finished_product.code} is already in advice {advice.advice_code}")
        # 1. 首先将所有与当前 advice 关联的 finished products 从中间表中删除
        db_session.query(finished_product_advice).filter(
            finished_product_advice.c.advice_id == advice.id
        ).delete(synchronize_session=False)

        # 2. 然后将新的 finished products 关联到当前 advice
        # 为每个 finished_product_id 插入一条记录到中间表
        for finished_product_id in finished_product_ids:
            db_session.execute(finished_product_advice.insert().values(
                finished_product_id=finished_product_id,
                advice_id=advice.id
            ))
    else:
        raise HTTPException(status_code=400,
                            detail="Please add at least one finished product")
    db_session.commit()

    return advice

# def advice_tips_update(*, db_session, id: int, advice_in: AdviceUpdate) -> Advice:
#     area = db_session.query(Area).filter(Area.code == advice_in.area_code).one_or_none()
#     item = db_session.query(Advice).filter(Advice.id == id).one_or_none()
#     item.updated_at = advice_in.tipped_date
#     item.comment = advice_in.comment
#     item.to_area_id = area.id
#     item.status = TIPPED
#     db_session.commit()
#     return item

def advice_tips_update(*, db_session, advice_in: AdviceUpdate, background_tasks, current_user) -> Advice:
    his = []
    uid = uuid.uuid4()
    area = db_session.query(Area).filter(Area.id == advice_in.area_id).one_or_none()
    item = db_session.query(Advice).filter(Advice.advice_code == advice_in.advice_code).one_or_none()
    new_advice = {
    "updated_at": advice_in.updated_at,
    "updated_by": advice_in.updated_by,
    "comment": advice_in.comment,
    "to_area_id": advice_in.area_id,
    "status": AdviceStatusEnum.UNLOAD,
    "own_state": 'mill' if advice_in.business_type == "internal" else 'store',
    }

    if advice_in.business_type:
        new_advice["business_type"] = advice_in.business_type

    db_session.query(Advice).filter(Advice.id.in_(advice_in.advice_ids)).update(new_advice)

    advices = db_session.query(Advice).filter(Advice.id.in_(advice_in.advice_ids)).all()
    transport_ids = {advices.transport_id for advices in advices if advices.transport_id}
    if transport_ids:
        db_session.query(Transport).filter(Transport.id.in_(transport_ids)).update({"status": TransportStatusEnum.DELOAD})
    # item.updated_at = advice_in.updated_at
    # item.updated_by = advice_in.updated_by
    # item.comment = advice_in.comment
    # item.curr_area_id = area.id
    # item.own_state = "store"
    # item.status = AdviceStatusEnum.UNLOAD
    # item.business_type = advice_in.business_type
    # if advice_in.business_type == "internal":
    #     item.own_state = "mill"
    for i in advice_in.advice_ids:
        item = db_session.query(Advice).filter(Advice.id == i).one_or_none()
        finished_items = item.finished_product
        if len(finished_items) == 0:
            raise HTTPException(status_code=400, detail="No finished product exists under the current advice. Unable to proceed with tip.")

        validate_finished_products(db_session, finished_items, item.business_type)
        for finished in finished_items:
            finished.stock_type = advice_in.business_type
            finished.updated_by = advice_in.updated_by
            finished.updated_at = advice_in.updated_at
            # added back by qiyang, 2025-01-29 08:13:50
            finished.area_id = area.id
            finished.advice_id = None
            his.append({
                "uuid": uid,
                "mill_id": finished.mill_id,
                "change_type": FinishedProductHistoryChangeTypeEnum.ADVICE_TIP,
                "created_by": advice_in.updated_by,
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
                "advice_no": item.advice_code,
                "exist_flag": finished.exist_flag,
            })
        bulk_create_finished_product_history(db_session=db_session, finished_product_history_in=his)
    db_session.commit()
    try:
        from ...contrib.message_admin.message_server import server as MessageServer
        #Trigger
        if item:
            current_mill_code = current_user.current_mill_code
            #Trigger For M410
            messageStrategy410=MessageServer.MessageStrategy410()
            messageStrategy410.send_pc_410(db_session, item, background_tasks, current_mill_code)
            del messageStrategy410

            #Trigger For M400
            messageStrategy400=MessageServer.MessageStrategy400()
            messageStrategy400.send_pc_400(db_session, item, background_tasks, current_mill_code)
            del messageStrategy400

        db_session.commit()
    except ImportError as e:
        # raise HTTPException(status_code=400, detail=str(e))
        log.warning(f"import error {str(e)}")
    except Exception as e:
        # raise HTTPException(status_code=400, detail=str(e)
        log.warning(f"send message fail {str(e)}")
    return item
    
def delete_advice(*, db_session, id: int):
    item = db_session.query(Advice).filter(Advice.id == id).update({"is_deleted": 1})
    db_session.commit()
    return item


def update_cancel(*, db_session, item_ids: AdviceSplit):
    for id in item_ids.item_ids:
        db_session.query(Advice).filter(Advice.id == id).update({"status": AdviceStatusEnum.CANCELLED})
    db_session.commit()
    return True


def update_deload(*, db_session, advice_in: AdviceSplit):
    try:
        if not advice_in.item_ids:
            raise HTTPException(status_code=400, detail="No advice IDs provided.")
        
        advices = db_session.query(Advice).filter(Advice.id.in_(advice_in.item_ids)).all()
        for advice in advices:
            advice.status = AdviceStatusEnum.DELOAD
            db_session.query(FinishedProductLoad).filter(FinishedProductLoad.id == advice.load_id).update(
                {"load_status": "Deload"}
            )
            db_session.query(finished_product_load).filter(finished_product_load.c.finished_product_load_id == advice.load_id).delete(synchronize_session=False)
        db_session.commit()
        return True
    except Exception as e:
        db_session.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    

def move_to(*, db_session, advice_in: AdviceMove):
    his = []
    uid = uuid.uuid4()
    # to_area = area_service.get_by_code(db_session=db_session, code=advice_in.area_code)
    advice = get_by_code(db_session=db_session, advice_code=advice_in.code)
    advice.business_type = advice_in.business_type
    advice.to_area_id = advice_in.to_area_id
    advice.updated_at = advice_in.updated_at
    advice.updated_by = advice_in.updated_by
    finisheds = advice.finished_product
    for finished in finisheds:
        finished.area_id = advice_in.to_area_id

        his.append({
            "uuid": uid,
            "mill_id": finished.mill_id,
            "change_type": FinishedProductHistoryChangeTypeEnum.ADVICE_MOVE,
            "created_by": advice_in.updated_by,
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
            "advice_no": advice.advice_code,
            "exist_flag": finished.exist_flag,
        })
    bulk_create_finished_product_history(db_session=db_session, finished_product_history_in=his)
    
    db_session.commit()
    return True

def update_advice_finished_product(*, db_session, advice_in: AdviceRead, finished_product_id: int):
    # db_session.query(FinishedProduct).filter(FinishedProduct.id == finished_product_id).update({
    #     "updated_at": advice_in.updated_at,
    #     "updated_by": advice_in.updated_by,
    #     # "advice_id": advice_in.id,
    # })
    db_session.execute(finished_product_advice.insert().values(
        advice_id=advice_in.id,
        finished_product_id=finished_product_id
    ))
    db_session.commit()
    return True

def group_by_order(item_ids: list, db_session) -> dict:
    finished_products = db_session.query(FinishedProduct).filter(FinishedProduct.id.in_(item_ids)).all()

    grouped = {}
    for product in finished_products:
        if product.order is not None:
            order = product.order
            if order not in grouped:
                grouped[order] = []
            grouped[order].append(product)
        else:
            if None not in grouped:
                grouped[None] = []
            grouped[None].append(product)
    return grouped

def load_create_advice(*, db_session, advice_in: AdviceCreate):
    # 按 order_item 分组
    grouped_products = group_by_order(advice_in.finished_ids, db_session)
    # 为每个分组创建对应的 advice
    for order, products in grouped_products.items():
        # 创建每个分组对应的 advice 对象
        advice_obj_in = AdviceCreate()
        # advice_obj_in.load_id = load_obj_in.id
        advice_obj_in.finished_ids = [product.id for product in products]  # 获取分组中的所有产品 ID
        advice_obj_in.order_id = order.id if order else None
        # advice_obj_in.business_type = (
        #     "bws" if order and order.order_order_item and all(item.bws_store for item in order.order_order_item) else "internal"
        # )
        advice_obj_in.business_type = "bws" if order and any(
            item.bws_store for item in order.order_order_item) else "internal"

        advice_obj_in.load_id = advice_in.load_id
        advice_obj_in.updated_by = advice_in.updated_by
        advice_obj_in.updated_at = advice_in.updated_at
        advice_obj_in.mill_id = advice_in.mill_id
        advice_obj_in.transport_type = advice_in.transport_type
        advice_obj_in.transport_id = advice_in.transport_id
        generate_advice = create(db_session=db_session, advice_in=advice_obj_in)
    return True

def replaced_advice(*, db_session, advice_in: AdviceCreate, advice, current_user):
    advice.created_by = advice_in.updated_by
    advice.updated_at = advice_in.updated_at
    advice.updated_by = advice_in.updated_by
    advice.status = AdviceStatusEnum.CANCELLED
    finished_list = advice.finished_product
    if finished_list:
        advice_in.finished_ids = [finished.id for finished in finished_list]
    advice_in.created_by = current_user.email
    advice_in.updated_at = datetime.now()
    advice_in.updated_by = current_user.email
    advice_in.mill_id = current_user.current_mill_id
    new_advice = create(db_session=db_session, advice_in=advice_in)
    db_session.commit()
    return new_advice

def get_advice_order_item(*, db_session, advice_in: AdviceIDPagination):
    advice = get(db_session=db_session, id=advice_in.advice_id)
    # finished_product = db_session.query(FinishedProduct).filter(and_(FinishedProduct.advice_id == advice.id, FinishedProduct.is_deleted == 0))
    finished_product = db_session.query(FinishedProduct).join(
        finished_product_advice, finished_product_advice.c.finished_product_id == FinishedProduct.id
    ).filter(
        finished_product_advice.c.advice_id == advice.id  # 用你要查询的 Advice ID 替代
    )
    order_item_id_list = list(set(item.order_item_id for item in finished_product))
    order_item = db_session.query(OrderItem).filter(OrderItem.id.in_(order_item_id_list))
    data_list = []
    for item in order_item:
        # order_finished = (db_session.query(FinishedProduct).filter(FinishedProduct.advice_id == advice.id,
        #                               FinishedProduct.order_item_id == item.id, FinishedProduct.is_deleted == 0))
        order_finished = db_session.query(FinishedProduct).join(
            finished_product_advice, finished_product_advice.c.finished_product_id == FinishedProduct.id
        ).filter(
                finished_product_advice.c.advice_id == advice.id,
                FinishedProduct.order_item_id == item.id,
                FinishedProduct.is_deleted == 0
        )
        total_weight = sum(
            # (batch.length_mm or 0) * (batch.quantity or 0) * (batch.product_type.dim3 if batch.product_type else 0)
            batch.estimated_weight_kg
            for batch in order_finished
        )
        max_length = max(batch.length_mm or 0 for batch in order_finished)
        item.total_weight = total_weight
        item.max_length = max_length
        data_list.append(item)

    query, pagination = apply_pagination(order_item, page_number=advice_in.page, page_size=advice_in.itemsPerPage)
    return {
        "items": query.all(),
        "itemsPerPage": pagination.page_size,
        "page": pagination.page_number,
        "total": pagination.total_results
    }


def get_store(*, db_session):
    stores = db_session.query(Advice.store).filter(Advice.store != None).distinct().all()
    return [store[0] for store in stores]