import re
from sqlalchemy import func
from sqlalchemy.sql import and_

from dispatch.common.utils.str_util import build_str
from dispatch.database import get_db

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from dispatch.common.utils.func import try_str
from dispatch.system_admin.auth.models import DispatchUser
from dispatch.system_admin.auth.service import get_current_user

from dispatch.database_util.service import common_parameters, search_filter_sort_paginate
from .models import (
    OrderItem,
    OrderItemCreate,
    OrderItemPagination,
    OrderItemRead,
    OrderItemRollingPagination,
    OrderItemUpdate,
    OrderItemStatisticsPagination
)
from dispatch.runout_admin.finished_product.models import FinishedProduct
from dispatch.runout_admin.advice.models import Advice, AdviceStatusEnum
from dispatch.message_admin.message_server.service import allocated_block, sort_by_dim3
from dispatch.order_admin.order_group.service import find_max_length, computer_weight_spec_group
from .service import create, delete, get, get_by_code, get_by_orderId, update, get_max_bundle_weight, move_to_order_item, get_by_rolling_order_group_id
from dispatch.order_admin.order.models import Order
from dispatch.rolling.rolling_list.models import Rolling
from dispatch.runout_admin.finished_product import service as finished_product_service
from ...spec_admin.spec.models import Spec
from dispatch.order_admin.order import service as order_service
from dispatch.spec_admin.spmainel import service as spmainel_service
from dispatch.spec_admin.spimpact import service as spimpact_service
from dispatch.spec_admin.sptensil import service as sptensile_service
from dispatch.spec_admin.spelong import service as spelong_service
from dispatch.spec_admin.spyield import service as spyield_service

# from ...decorators import background_task
import logging
logging.basicConfig(level=logging.INFO)

from dispatch.log import getLogger
log = getLogger(__name__)


router = APIRouter()

TYPE_OF_ORDER = 184
PRODUCT_FORM = "SEMI"


@router.get("/order_item_rolling", response_model=OrderItemRollingPagination)
def get_order_item_rolling(*,db_session: Session = Depends(get_db), common: dict = Depends(common_parameters)):
    order_item = search_filter_sort_paginate(model="OrderItem", **common)
    product_num = []
    if order_item["items"]:
        for orderitem in order_item["items"]:
            product_num.append(len(orderitem.order_item_finished_product))
            despatched_finished = (db_session.query(FinishedProduct).filter(
                FinishedProduct.order_item_id == orderitem.id, FinishedProduct.status == "despatched").count())
            orderitem.despatched_bars = despatched_finished
    order_item["product_num"] = product_num
    return order_item


@router.get("/", response_model=OrderItemPagination)
def get_orderItems(*, db_session: Session = Depends(get_db), common: dict = Depends(common_parameters), start_date:str = Query(None), end_date:str = Query(None), dim3: int = Query(None)):

    common['query'] = db_session.query(OrderItem).outerjoin(Order, Order.id == OrderItem.order_id
                                                            ).outerjoin(Rolling, Rolling.id == OrderItem.rolling_id)
    if start_date:
        common['query'] = common['query'].filter(OrderItem.created_at >= start_date)
    if end_date:
        common['query'] = common['query'].filter(OrderItem.created_at <= end_date)
    if dim3:
        common['query'] = common['query'].filter(OrderItem.product_dim3.like(f"%{dim3}%"))
    order_item = search_filter_sort_paginate(model="OrderItem", **common)
    order_item_data = order_item["items"]

    if order_item["items"]:
        for orderitem in order_item_data:
            if orderitem.spec_code:
                result = db_session.query(Spec).filter(
                    Spec.spec_code == orderitem.spec_code).first()
                if result:
                    orderitem.spec_short_name = result.short_name

            bras = orderitem.amended_quantity if orderitem.amended_quantity else orderitem.quantity
            finished = db_session.query(FinishedProduct).filter(FinishedProduct.order_item_id == orderitem.id).count()
            if finished != 0 and finished >= bras:
                orderitem.completion_status = "completed"

            # orderitem.advice_bars = db_session.query(FinishedProduct).filter(
            #     FinishedProduct.order_item_id == orderitem.id,  FinishedProduct.advice.any()).count()

            # 通用过滤条件
            base_filter = FinishedProduct.order_item_id == orderitem.id

            # advice_bars: 非 internal/scrap 的 advice
            advice_bars = db_session.query(func.coalesce(func.sum(FinishedProduct.quantity), 0)) \
                .filter(base_filter) \
                .filter(FinishedProduct.advice.any(Advice.business_type.notin_(['internal', 'scrap']))) \
                .scalar()
            orderitem.advice_bars = advice_bars

            # advice_tip_bars: advice status = UNLOAD
            advice_tip_bars = db_session.query(func.coalesce(func.sum(FinishedProduct.quantity), 0)) \
                .filter(base_filter) \
                .filter(FinishedProduct.advice.any(Advice.status == AdviceStatusEnum.UNLOAD)) \
                .scalar()
            orderitem.advice_tip_bars = advice_tip_bars

            # status-based统计：returned, despatched
            status_list = ['returned', 'despatched']
            status_sums = dict.fromkeys(status_list, 0)

            results = db_session.query(FinishedProduct.status, func.coalesce(func.sum(FinishedProduct.quantity), 0)) \
                .filter(base_filter) \
                .filter(FinishedProduct.status.in_(status_list)) \
                .group_by(FinishedProduct.status) \
                .all()

            for status, total in results:
                status_sums[status] = total

            status_list_advice = ['enroute', 'return']
            status_sums_advice = dict.fromkeys(status_list_advice, 0)

            results_advice = db_session.query(Advice.status, func.coalesce(func.sum(FinishedProduct.quantity), 0)) \
                .join(FinishedProduct.advice) \
                .filter(base_filter) \
                .filter(Advice.status.in_(status_list_advice)) \
                .group_by(Advice.status) \
                .all()

            for status, total in results_advice:
                status_sums_advice[status] = total

            quantity_enroute = status_sums_advice['enroute']
            # quantity_return = status_sums_advice['return']

            orderitem.returned_bars = status_sums['returned']
            orderitem.despatched_bars = quantity_enroute

            # allocation_status == 'allocate'
            allocate_bars = db_session.query(func.coalesce(func.sum(FinishedProduct.quantity), 0)) \
                .filter(base_filter, FinishedProduct.allocation_status == "allocate") \
                .scalar()
            orderitem.allocate_bars = allocate_bars
    return order_item

@router.get("/order_id/{order_id}", response_model=OrderItemPagination)
def get_orderItems(*, order_id: int, common: dict = Depends(common_parameters)):

    return get_by_orderId(order_id=order_id, **common)


@router.post("/", response_model=OrderItemRead)
def create_orderItem(*, db_session: Session = Depends(get_db), orderItem_in: OrderItemCreate,
                 current_user: DispatchUser = Depends(get_current_user)):
    """
    Create a new orderItem contact.
    """
    
    # orderItem = get_by_code(db_session=db_session,code=orderItem_in.code)
    
    
    # if orderItem:
    #     raise HTTPException(status_code=400, detail="The orderItem with this code already exists.")
    
    orderItem_in.created_by = current_user.email
    orderItem_in.updated_by = current_user.email
    orderItem = create(db_session=db_session, orderItem_in=orderItem_in)
    return orderItem


@router.post("/send_to_pcc/{order_item_id}")
def send_to_pcc(
    *,
    db_session: Session = Depends(get_db),
    order_item_id: int,
    current_user: DispatchUser = Depends(get_current_user),
    background_tasks: BackgroundTasks,
):
    order_item = get(db_session=db_session, orderItem_id=order_item_id)
    if not order_item:
        raise HTTPException(status_code=400, detail='order item does not exist')
    order_87, order_274 = None, None
    wo_no, bs_order = None, None
    if order_item.order.type_of_order == 87:
        order_87 = order_item.order
        order_274 = order_service.get_by_work_order_and_type(db_session=db_session, work_order=order_87.work_order, order_type=274)
    else:
        order_274 = order_item.order
        order_87 = order_service.get_by_work_order_and_type(db_session=db_session, work_order=order_274.work_order, order_type=87)
    wo_no = ''
    msm_cust_no, msm_addr_no = '0' * 7, '0' * 3
    if order_87:
        wo_no = build_str(order_87.work_order, 6)
        bs_order = build_str(order_87.business_order_code, 6)
        if order_87.delivery_address_id:
            msm_cust_no = build_str(order_87.delivery_address_id[:7], 7)
            msm_addr_no = build_str(order_87.delivery_address_id[7:], 3)
    if order_274:
        wo_no = build_str(order_274.work_order, 6)
        bs_order = build_str(order_274.business_order_code, 6)
    
    max_bundle_weight = int(get_max_bundle_weight(db_session=db_session, order_item_id=order_item.id))
    finished_product = finished_product_service.get_one_by_order_item_id(db_session=db_session, order_item_id=order_item_id)
    spec = order_item.spec
    line_item_code = build_str(order_item.line_item_code[:-1], 3)
    bws_store = None
    if order_item.rolling_code == '806S':
        bws_store = 'ASD'
    elif order_item.rolling_code == '826S':
        bws_store = 'AJNS'
    elif order_item.rolling_code == '824S':
        bws_store = 'MTA2'
    spare5 = {
            "spec_code": build_str(spec.spec_code if spec else None, 4),
            "bws_flag": 'Y' if bws_store else 'N',
            "msm_cust_no": msm_cust_no,
            "msm_addr_no": msm_addr_no,
            "bws_store": build_str(bws_store, 4)
        }
    spare6 = {
            "s4order": build_str(order_item.order.order_code, 10),
            "s4item": build_str(line_item_code+' '*3, 6),
            "s4ordertype": "P" if order_item.order and order_item.order.type_of_order == 274 else ' ',
            "s4shape": build_str(order_item.product_code, 2),
            "s4dim1": build_str(order_item.product_dim1, 3),
            "s4dim2": str.ljust(order_item.product_dim2, 3),
            "s4dim3": str.ljust(order_item.product_dim3, 5),
        }
    def _sort_by_product(s: str):
        try:
            s = str(s).strip() if s else s
            if not s:
                log.warning("bundle info is empty")
                return []

            # Use regex to match 'NxM' pattern in the string
            matches = re.findall(r'(\d+)x(\d+)', s)
            if not matches:
                log.warning(f"input format should be number x number: {s}")
                return []

            # Convert the matches into tuples of integers
            pairs = [(int(a), int(b)) for a, b in matches]

            # Sort by product in descending order
            sorted_pairs = sorted(pairs, key=lambda x: x[0] * x[1], reverse=True)

            log.info(f"Sorted result: {sorted_pairs}")
            return sorted_pairs

        except Exception as e:
            log.error(f"Error processing input: {s[:100]}... (truncated), Error: {e}", exc_info=True)
            return []
        
    bundle_list = _sort_by_product(finished_product.bundle if finished_product else '')
    product_code = order_item.product_code
    if product_code == 'UB':
        product_code = 'U BEAM'
    elif product_code == 'UC':
        product_code = 'U COLUMN'
    msg_to_pcc = {
        'transaction_id': 'M199',
        "wo_no":  wo_no,
        "bs_order": bs_order,
        "item": line_item_code,
        "format": build_str(order_item.label_template.code if order_item.label_template else '1', 8), # ?? Label format
        "sect_size": build_str(product_code + " " + try_str(order_item.product_dim1) + "X" + try_str(order_item.product_dim2) + "X" + try_str(order_item.product_dim3), 30),
        "length": build_str(build_str(order_item.length_mm)+' mm', 30),
        "quality": build_str(spec.full_name if spec else None, 30),
        "ord_item": build_str(bs_order + "/" + line_item_code, 30),
        "weight": ' '*30,
        "mark1": build_str(order_item.general_remark_1, 30),
        "mark2": build_str(order_item.general_remark_2, 30),
        "mark3": build_str(order_item.general_remark_3, 30),
        "mark4": build_str(order_item.general_remark_4, 30),
        "mark5": build_str(order_item.general_remark_5, 30),
        "product_id": build_str(order_item.product_code, 30),
        "lr_ind": build_str(order_item.lr_ind, 30),
        "customer_bc": build_str(order_item.customer_spec_code, 30),
        "spare3": ' ' * 30,
        "spare4": " " * 30,
        "spare5": build_str("".join(spare5.values()), 30),
        "spare6": build_str( "".join(spare6.values()), 30),
        "spare7": build_str(order_item.spec_code, 30),
        "spare8": " " * 30,
        "spare9": " " * 30,
        "print_ind": "Y",
        "check_ind": 'N',
        "metric_ind": "M", # set 'M' or 'I' depending on the order, trigger this message manually
        "copies": '0001',
        "max_wt": build_str(max_bundle_weight, 5),
        "len_range_ind": " ", 
        "wt_mask_ind": "Y",
        "adc_ind": "Y", # ?? finished_product.area.code like '%ADC%', Y, else N
        "bundle_amt": build_str(bundle_list[0][0], 6) if len(bundle_list)>0 else ' ' * 6,
        "bundle_bars": build_str(bundle_list[0][1], 6) if len(bundle_list)>0 else ' ' * 2,
        "rem_bundle_amt": build_str(bundle_list[1][0], 6) if len(bundle_list)>1 else ' ' * 6,
        "rem_bundle_bars": build_str(bundle_list[1][1], 6) if len(bundle_list)>1 else ' ' * 2,
    }
    msg_content = "".join(str(v) for v in msg_to_pcc.values())
    print(msg_content)
    try:
        from dispatch.contrib.message_admin.message_server.trigger_message_service import send_request
        background_tasks.add_task(send_request, msg_content=msg_content, msg_id=199, msg_type="srsmpc")
        # handle_m199(db_session=db_session, msg_in=msg_to_pcc, background_tasks=background_tasks)
    except ImportError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"status": "ok"}


@router.get("/{orderItem_id}", response_model=OrderItemRead)
def get_orderItem(*, db_session: Session = Depends(get_db), orderItem_id: int):
    """
    Get a orderItem contact.
    """
    orderItem = get(db_session=db_session, orderItem_id=orderItem_id)
    if not orderItem:
        raise HTTPException(status_code=400, detail="The orderItem with this id does not exist.")
    return orderItem

@router.post("/move")
def move_to(data: dict, background_tasks: BackgroundTasks, db_session: Session = Depends(get_db), current_user: DispatchUser = Depends(get_current_user)):
    mill_id = current_user.current_mill_id
    order_item_list = move_to_order_item(data=data, db_session=db_session,current_user=current_user, background_tasks=background_tasks)
    allocated_block(db_session=db_session, order_items=order_item_list, mill_id=mill_id)
    number = allocated_block(db_session=db_session, order_items=order_item_list, mill_id=mill_id)
    computer_weight_spec_group(db_session=db_session)
    find_max_length(db_session=db_session)
    sort_by_dim3(db_session=db_session, mill_id=mill_id)
    return 1 if number >= 1 else 0

# @router.put("/amend_rolling")
# def amend_rolling(*, db_session: Session = Depends(get_db)):
#     result = amend_rolling_attach(db_session=db_session)
#
#     return {"status": "ok"}


@router.put("/{orderItem_id}", response_model=OrderItemRead)
def update_orderItem(
    *,
    background_tasks: BackgroundTasks,
    db_session: Session = Depends(get_db),
    orderItem_id: int,
    orderItem_in: OrderItemUpdate, current_user: DispatchUser = Depends(get_current_user)
):
    """
    Update a orderItem contact.
    """
    orderItem = get(db_session=db_session, orderItem_id=orderItem_id)
    if not orderItem:
        raise HTTPException(status_code=400, detail="The orderItem with this id does not exist.")

    orderItem = update(
        db_session=db_session,
        orderItem=orderItem,
        orderItem_in=orderItem_in,
    )
    try:
        from ...contrib.message_admin.message_server import server as MessageServer
        message_server = MessageServer.MessageStrategyPICKSRSM()
        message_server.send_picksrsm(db_session=db_session, target_order_item=orderItem, background_tasks=background_tasks, flag="A", current_mill_code=current_user.current_mill_code)
    except ImportError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        log.error(f"ERROR in send_picksrsm: {e}")
    return orderItem


@router.put("/orderItem_code/{orderItem_code}", response_model=OrderItemRead)
def update_orderItem_by_code(
    *,
    db_session: Session = Depends(get_db),
    orderItem_code: str,
    orderItem_in: OrderItemUpdate, current_user: DispatchUser = Depends(get_current_user)
):
    """
    Update a orderItem contact.
    """
    orderItem = get_by_code(db_session=db_session, code=orderItem_code)
    if not orderItem:
        raise HTTPException(status_code=400, detail="The orderItem with this id does not exist.")

    orderItem_in.updated_by = current_user.email
    orderItem = update(
        db_session=db_session,
        orderItem=orderItem,
        orderItem_in=orderItem_in,
    )

    return orderItem


@router.delete("/{orderItem_id}")
def delete_orderItem(*, db_session: Session = Depends(get_db), orderItem_id: int):
    """
    Delete a orderItem contact.
    """
    orderItem = get(db_session=db_session, orderItem_id=orderItem_id)
    if not orderItem:
        raise HTTPException(status_code=400, detail="The orderItem with this id does not exist.")

    return delete(db_session=db_session, orderItem_id=orderItem_id)


# order item 统计报表
@router.get("/order_items/statistics", response_model=OrderItemStatisticsPagination)
def get_orderItem_statistics(*, db_session: Session = Depends(get_db), common: dict = Depends(common_parameters), delivery_date:str = Query(None)):
    common['query'] = db_session.query(
        OrderItem.line_item_desc, OrderItem.product_code, OrderItem.caster, OrderItem.spec_code, 
        OrderItem.delivery_date, func.sum(OrderItem.quantity_tonnage).label('total_quantity_tonnage')
    ).join(Order, Order.id == OrderItem.order_id)

    if delivery_date:
        filter_cond = and_(
            OrderItem.delivery_date >= func.to_date(delivery_date, 'yyyy-mm-dd'),
            Order.type_of_order == TYPE_OF_ORDER,
            OrderItem.product_form == PRODUCT_FORM,
        )
    else:
        filter_cond = and_(
            Order.type_of_order == TYPE_OF_ORDER,
            OrderItem.product_form == PRODUCT_FORM,
        )
    
    common['query'] = common['query'].filter(filter_cond).group_by(
                        OrderItem.line_item_desc,
                        OrderItem.product_code,
                        OrderItem.caster,
                        OrderItem.spec_code,
                        OrderItem.delivery_date
                    ).order_by(
                        OrderItem.delivery_date
                    )

    order_item = search_filter_sort_paginate(model="OrderItem", **common)
    return order_item

@router.get("/has_order_item/{rolling_id}")
def get_has_order_item(*, db_session: Session = Depends(get_db), rolling_id: int):
    order_item =  db_session.query(OrderItem).filter(OrderItem.rolling_id == rolling_id).count() > 0
    return order_item


@router.get("/cut_seq/options")
def get_order_item_options(
        *,
        db_session: Session = Depends(get_db),
        rolling_id: int = Query(None),
        order_group_id: int = Query(None)
):
    options = []
    order_items = get_by_rolling_order_group_id(
        db_session=db_session, rolling_id=rolling_id, order_group_id=order_group_id
    )
    for order_item in order_items:
        options.append({
            "id": order_item.id,
            "line_item_code": order_item.line_item_code,
            "bars": order_item.quantity,
            "length_mm": order_item.length_mm,
            "order_info": {
                "id": order_item.order.id,
                "order_code": order_item.order.order_code
            }
        })

    return options

@router.get("/info/spec_by_order")
def get_get_spec_by_order(db_session: Session = Depends(get_db), order_item_id: int = Query(...)):
    order_item = get(db_session=db_session, orderItem_id=order_item_id)
    if not order_item:
        raise HTTPException(status_code=400, detail="The orderItem with this id does not exist.")
    spec = order_item.spec
    if not spec:
        raise HTTPException(status_code=400, detail="The spec with this id does not exist.")
    product_type = order_item.product_type

    if not product_type:
        raise HTTPException(status_code=400, detail="The product type with this id does not exist.")
    if not product_type.flange_thickness:
        raise HTTPException(status_code=400, detail="The flange thickness with this id does not exist.")
    
    insp_list = [order_item.inspector_code_1, order_item.inspector_code_2, order_item.inspector_code_3]
    insp_list = list(filter(lambda x: x, insp_list))
    sptensile = sptensile_service.get_sptensil_by_spec_id_and_flange_thickness(db_session=db_session, spec_id=spec.id, flange_thickness=product_type.flange_thickness)
    spmainel = spmainel_service.get_spmainel_by_spec_id_and_flange_thickness(db_session=db_session, spec_id=spec.id, flange_thickness=product_type.flange_thickness)
    spimpact = spimpact_service.get_spimpact_by_spec_id_and_flange_thickness(db_session=db_session, spec_id=spec.id, flange_thickness=product_type.flange_thickness)
    spelong = spelong_service.get_spelong_by_spec_id_and_flange_thickness(db_session=db_session, spec_id=spec.id, flange_thickness=product_type.flange_thickness)
    spyield = spyield_service.get_spyield_by_spec_id_and_flange_thickness(db_session=db_session, spec_id=spec.id, flange_thickness=product_type.flange_thickness)
    cast_list = finished_product_service.get_cast_list_by_order_item(db_session=db_session, order_item_id=order_item.id)
    return {
        "insp_list": insp_list,
        "spec": spec or {},
        "sptensile":sptensile or {},
        "spmainel":spmainel or {},
        "spimpact":spimpact or {},
        "spelong":spelong or {},
        "spyield":spyield or {},
        "cast_list": [ i.cast_code for i in cast_list]
    }
