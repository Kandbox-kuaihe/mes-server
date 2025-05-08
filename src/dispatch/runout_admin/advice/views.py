import uuid
from datetime import datetime, UTC
from typing import List

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query

from sqlalchemy import text, or_, and_, select, case
from sqlalchemy import exists
from dispatch.runout_admin.finished_product.models import FinishedProduct, FinishedProductAdviceSplit, CombinedResponse, \
    FinishedProductRead
from .models import Advice, AdviceIDPagination, AdviceMove, AdviceRead, AdviceSplit, AdviceUpdate, \
    AdvicePagination, AdviceCreate, AdviceReturn, AdviceStatusEnum
from dispatch.database_util.service import common_parameters, search_filter_sort_paginate
from sqlalchemy.orm import Session
from sqlalchemy.sql.functions import func
from dispatch.database import get_db
from dispatch.system_admin.auth.models import DispatchUser
from dispatch.system_admin.auth.service import get_current_user
from .service import advice_tips_update, get, get_finished_product, move_to, \
    split_advice_f, create, get_advice_f, update_advice_finished_product, update_cancel, update, update_deload, \
    load_create_advice, replaced_advice, get_advice_order_item, get_store, delete_advice, get_next_srsm_advice_code, \
    get_tbm_prefix_for_business_type
from dispatch.runout_admin.finished_product.models_secondary_advice import finished_product_advice
from dispatch.runout_admin.finished_product_load.models import FinishedProductLoad
from dispatch.runout_admin.holdreason.models import HoldReason
from dispatch.runout_admin.holdreason.models_secondary import finished_product_hold
from dispatch.runout_admin.transport.models import Transport
from dispatch.area.models import Area
from dispatch.config import DEV_DATABASE_SCHEMA, ADVICE_SEQUENCE_NAME
from dispatch.runout_admin.finished_product_history.models import FinishedProductHistoryChangeTypeEnum, FinishedProductHistory
from ...message_admin.message_server.service import create_advice_xml
from ...order_admin.order_item.models import OrderItemPagination

from dispatch.log import getLogger
logger = getLogger(__name__)

router = APIRouter()


@router.get("/", response_model=AdvicePagination)
def get_all(*, common: dict=Depends(common_parameters), db_session: Session = Depends(get_db), held: str = Query(None),
            mult_done: str = Query(None), start_date_from: str = Query(None), start_date_to: str = Query(None)):

    query = db_session.query(Advice).outerjoin(FinishedProductLoad, Advice.load_id == FinishedProductLoad.id
                                             ).outerjoin(Area, Advice.curr_area_id == Area.id
                                                         ).outerjoin(Transport, Advice.transport_id == Transport.id)
    if start_date_from and start_date_to:
        query = query.filter(Advice.created_at >= start_date_from).filter(
            Advice.created_at <= start_date_to)
    if held:
        query = query.filter(
            or_(
                exists().where(
                    Advice.id == finished_product_advice.c.advice_id,
                    FinishedProduct.id == finished_product_advice.c.finished_product_id,
                    FinishedProduct.id == finished_product_hold.c.finished_product_id,
                    HoldReason.id == finished_product_hold.c.hold_reason_id
                ),
                exists().where(
                    Advice.id == finished_product_advice.c.advice_id,
                    FinishedProduct.id == finished_product_advice.c.finished_product_id,
                    and_(
                        # FinishedProduct.rework_status not in ['Complete', None],
                        # FinishedProduct.rework_status != 'Complete',
                        # FinishedProduct.rework_status != None
                        FinishedProduct.rework_type != None,
                        FinishedProduct.rework_type != 'Complete'
                    )
                ),
                # exists().where(
                #     Advice.id == finished_product_advice.c.advice_id,
                #     FinishedProduct.id == finished_product_advice.c.finished_product_id,
                #     or_(
                #         FinishedProduct.exist_flag == 'N',
                #     )
                # ),
                exists().where(
                    Advice.id == finished_product_advice.c.advice_id,
                    FinishedProduct.id == finished_product_advice.c.finished_product_id,
                    or_(
                        FinishedProduct.t_result < 8,
                        FinishedProduct.c_result < 8,
                        FinishedProduct.t_result == None,
                        FinishedProduct.c_result == None
                    )
                ),
                exists().where(
                    Advice.id == finished_product_advice.c.advice_id,
                    FinishedProduct.id == finished_product_advice.c.finished_product_id,
                    and_(
                        FinishedProduct.mult_type == 'M',
                        FinishedProduct.exist_flag == 'Y'
                    )
                )
            )
        )

    if mult_done == 'waiting':
        # query = query.filter(
        #     exists().where(
        #         Advice.id == finished_product_advice.c.advice_id,
        #         FinishedProduct.id == finished_product_advice.c.finished_product_id,
        #         and_(
        #             FinishedProduct.mult_type == 'M',
        #             FinishedProduct.exist_flag == 'Y'
        #         )
        #     )
        # )
        subquery = (
            db_session.query(
                finished_product_advice.c.advice_id,
                func.count(case([(
                    FinishedProduct.mult_type == 'M', 1
                )], else_=None)).label('total_count'),
                func.count(case([(and_(
                    FinishedProduct.mult_type == 'M',
                    FinishedProduct.exist_flag == 'Y'), 1
                )], else_=None)).label('valid_count')
            )
            .join(FinishedProduct, FinishedProduct.id == finished_product_advice.c.finished_product_id)
            .group_by(finished_product_advice.c.advice_id)
            .subquery()
        )
        query = query.filter(
            # exists().where(
            #     Advice.id == finished_product_advice.c.advice_id,
            #     FinishedProduct.id == finished_product_advice.c.finished_product_id,
            #     and_(
            #         FinishedProduct.mult_type == 'M',
            #         FinishedProduct.exist_flag != 'Y'
            #     )
            # )
            Advice.id.in_(select([subquery.c.advice_id])
                          .where(subquery.c.total_count > 0)
                          .where(subquery.c.total_count == subquery.c.valid_count))
        )
    #     query = session.query(Course).join(StudentCourses).join(Student).filter(Student.id == student_id)
    elif mult_done == 'done':
        subquery = (
            db_session.query(
                finished_product_advice.c.advice_id,
                func.count(case([(
                    FinishedProduct.mult_type == 'M', 1
                )], else_=None)).label('total_count'),
                func.count(case([(and_(
                    FinishedProduct.mult_type == 'M',
                    FinishedProduct.exist_flag != 'Y'), 1
                )], else_=None)).label('valid_count')
            )
            .join(FinishedProduct, FinishedProduct.id == finished_product_advice.c.finished_product_id)
            .group_by(finished_product_advice.c.advice_id)
            .subquery()
        )
        query = query.filter(
            Advice.id.in_(select([subquery.c.advice_id])
            .where(subquery.c.total_count > 0)
            .where(subquery.c.total_count == subquery.c.valid_count))
        )

    elif mult_done == 'na':
        subquery = (
            db_session.query(
                finished_product_advice.c.advice_id,
                func.count(
                    # case([(FinishedProduct.mult_type.is_(None), 1)], else_=None)

                ).label('total_count'),
                func.count(
                    case([(
                        FinishedProduct.mult_type.is_(None)
                        , 1)], else_=None)
                ).label('valid_count')
            )
            .join(FinishedProduct, FinishedProduct.id == finished_product_advice.c.finished_product_id)
            .group_by(finished_product_advice.c.advice_id)
            .subquery()
        )

        query = query.filter(
            Advice.id.in_(
                select([subquery.c.advice_id])
                .where(subquery.c.total_count > 0)
                .where(subquery.c.total_count == subquery.c.valid_count)
            )
        )
    common['query'] = query

    advice_item = search_filter_sort_paginate(model="Advice", **common)
    advice_items = advice_item.get("items")
    if advice_items:
        for advice in advice_items:
            max_length = 0
            total_weight = 0
            is_hold = False
            is_cover = False
            is_rework = False
            is_mult = False

            hold_reason_list = []
            cover = []
            rework = []
            mult = None
            mult_done = None
            for finished_product in advice.finished_product:
                length = finished_product.length_mm if finished_product.length_mm else 0
                # quantity = finished_product.quantity if finished_product.quantity else 0
                # dim3 = finished_product.product_type.dim3 if finished_product.product_type else 0
                weight = finished_product.estimated_weight_kg if finished_product.estimated_weight_kg else 0

                # 计算重量
                # weight = length * quantity * dim3
                total_weight += weight

                # 更新 max_length
                if length > max_length:
                    max_length = length

                if finished_product.hold_reason:
                    is_hold = True
                    for reason in finished_product.hold_reason:
                        if reason not in hold_reason_list:
                            hold_reason_list.append(reason.name)
                if finished_product.t_result is None:
                    finished_product.t_result = 0
                if finished_product.c_result is None:
                    finished_product.c_result = 0
                if int(finished_product.t_result) < 8 or int(finished_product.c_result) < 8:
                    is_cover = True
                    if finished_product.t_result not in cover:
                        cover.append(str(finished_product.t_result) + str(finished_product.c_result))
                if finished_product.rework_type and finished_product.rework_type != 'Complete':
                    is_rework = True
                    rework.append(finished_product.rework_type)
                count = db_session.query(FinishedProduct).filter(FinishedProduct.mult_id == finished_product.id)
                cut_code_list = []
                counts = 0
                if count.count() > 0:
                    for i in count.all():
                        if i.cut_code:
                            cut_code_list.append(i.cut_code)
                    counts = count.count()
                    cut_codes = ",".join(cut_code_list)

                else:
                    cut_codes = finished_product.cut_code
                    counts = 1
                finished_product.cut_codes = cut_codes if cut_codes else ""
                counts = counts if finished_product.mult_type is not None else 0
                finished_product.cut_into = counts if counts else 0
            no_products = sum(1 for product in advice.finished_product if product.exist_flag == 'Y')
            waiting_flag = db_session.query(Advice).filter(Advice.id == advice.id).filter(
                exists().where(
                    Advice.id == finished_product_advice.c.advice_id,
                    FinishedProduct.id == finished_product_advice.c.finished_product_id,
                    and_(
                        FinishedProduct.mult_type == 'M',
                        FinishedProduct.exist_flag == 'Y'
                    )
                )
            )
            done_flag = db_session.query(Advice).filter(Advice.id == advice.id).filter(
                exists().where(
                    Advice.id == finished_product_advice.c.advice_id,
                    FinishedProduct.id == finished_product_advice.c.finished_product_id,
                    and_(
                        FinishedProduct.mult_type == 'M',
                        FinishedProduct.exist_flag != 'Y'
                    )
                )
            )
            na = db_session.query(Advice).filter(Advice.id == advice.id).filter(
                exists().where(
                    Advice.id == finished_product_advice.c.advice_id,
                    FinishedProduct.id == finished_product_advice.c.finished_product_id,
                    and_(
                        FinishedProduct.mult_type == None
                    )
                )
            )
            if waiting_flag.count() > 0:
                mult_done = 'waiting'
            elif done_flag.count() > 0:
                mult_done = 'done'
            elif na.count() > 0:
                mult_done = 'na'

            advice.no_products = no_products if no_products else 0
            advice.total_weight = round(total_weight / 1000, 3)
            advice.max_length = max_length
            advice.hold_reason = hold_reason_list
            advice.cover = cover
            advice.rework = rework
            # advice.mult = mult
            advice.mult_done = mult_done
            advice.finished_products = advice.finished_product
            if is_hold or is_cover or is_rework or mult_done == 'waiting':
                advice.held = 'Q'
            else:
                advice.held = ''
    return advice_item

@router.get("/max_id", response_model=AdviceRead)
def get_max_id(
    *,
    db_session: Session = Depends(get_db),
    common: dict = Depends(common_parameters),
    current_user: DispatchUser = Depends(get_current_user),
    business_type: str = Query(None),
):
    result = AdviceCreate()
    # dispatch_organization_mes_root.advice_id_seq
    max_id = db_session.execute(text(f"SELECT last_value FROM {DEV_DATABASE_SCHEMA}.{ADVICE_SEQUENCE_NAME}")).scalar()
    mill_code = current_user.current_mill_code
    # result = get(db_session=db_session, id=max_id)
    # result.advice_code = (
    #     get_next_srsm_advice_code(db_session, int(max_id + 1)) if mill_id == 1 else str(max_id + 1)
    # )
    if mill_code == 'SRSM':
        result.advice_code = get_next_srsm_advice_code(db_session, int(max_id + 1))
    elif mill_code == 'TBM':
        result.advice_code = get_tbm_prefix_for_business_type(business_type) + str(max_id + 1)
    else:
        result.advice_code = str(max_id)
    return result

@router.post("/finished")
def get_advice(*, db_session: Session = Depends(get_db), advice_in: dict):
    advice_ids = advice_in.get('params', {}).get('advice_ids', [])
    advices = db_session.query(Advice).filter(Advice.id.in_(advice_ids)).all()
    for advice in advices:
        finished_items = advice.finished_product
        if len(finished_items) == 0:
            return "No finished product exists under the current advice. Unable to proceed with tip."
        if advice.business_type == 'bws' or advice.business_type == 'roster':
            for i in finished_items:
                if i.exist_flag not in [None, "Y"]:
                    return "The finished product under the advice is being mult"
                if i.rework_status not in [None, "Complete"]:
                    return "The finished product under the advice is being reworked"

    return True

@router.get("/split/{advice_id}")
def get_advice_finished_product(
    *,
    db_session: Session = Depends(get_db),
    advice_id: int
):
    a_f_object = get_advice_f(db_session=db_session, id=advice_id)
    return CombinedResponse(advice=a_f_object["advice"], finished_product=a_f_object["finished_product"])

@router.get("/detail/{advice_id}", response_model=AdviceRead)
def get_advice(
    *,
    db_session: Session = Depends(get_db),
    advice_id: int
):
    advice = get(db_session=db_session, id=advice_id)
    return advice

@router.post("/detail/finished_product", response_model=List[FinishedProductRead])
def get_detail_finished_product(
        *,
        db_session: Session = Depends(get_db),
        advice_in: AdviceSplit
):
    finished_objs = []
    finished_ids = set()  # 用于记录已添加的 FinishedProduct 的 id
    finished_products = db_session.query(FinishedProduct).filter(FinishedProduct.id.in_(advice_in.item_ids)).all()

    for finished in finished_products:
        if finished.id not in finished_ids:  # 检查是否已经添加过
            finished_objs.append(finished)
            finished_ids.add(finished.id)  # 将已添加的 id 加入集合
        # if finished.mult_type == "M" and finished.exist_flag == "Y":
        if finished.mult_type == "M":
            finisheds = db_session.query(FinishedProduct).filter(FinishedProduct.mult_id == finished.id).all()
            for finished_sub in finisheds:
                if finished_sub.id not in finished_ids:  # 检查是否已经添加过
                    finished_objs.append(finished_sub)
                    finished_ids.add(finished_sub.id)  # 将已添加的 id 加入集合

    return finished_objs


@router.post("/finished_product", response_model=FinishedProductAdviceSplit)
def get_advice_piece_finished_product(
    *,
    db_session: Session = Depends(get_db),
    advice_in: AdviceIDPagination
):
    finished_product = get_finished_product(db_session=db_session, advice_in=advice_in)
    return finished_product


@router.post("/move_to")
def move_finished_product_load(
    *,
    db_session: Session = Depends(get_db),
    advice_in: AdviceMove,
    current_user: DispatchUser = Depends(get_current_user)
):
    advice_in.updated_at = datetime.now()
    advice_in.updated_by = current_user.email
    return move_to(db_session=db_session, advice_in=advice_in)

@router.post("/load_create_advice")
def load_detail_create_advice(
    *,
    db_session: Session = Depends(get_db),
    advice_in: AdviceCreate,
    current_user: DispatchUser = Depends(get_current_user)
):
    advice_in.updated_at = datetime.now()
    advice_in.updated_by = current_user.email
    advice_in.mill_id = current_user.current_mill_id
    return load_create_advice(db_session=db_session, advice_in=advice_in)

@router.post("/inspect_finished_product")
def inspect_finished_products(
    *,
    db_session: Session = Depends(get_db),
    advice_in: AdviceSplit,
    current_user: DispatchUser = Depends(get_current_user)
):
    finished_products = db_session.query(FinishedProduct).filter(FinishedProduct.id.in_(advice_in.item_ids)).all()
    for finished_product in finished_products:
        advices = finished_product.advice
        for advice in advices:
            if advice.status == AdviceStatusEnum.ENROUTE:
                raise HTTPException(status_code=400, detail=f"Product {finished_product.code} is already in advice {advice.advice_code}")
    return True

@router.post("/split/{advice_id}", response_model=AdviceRead)
def split_advice(
    *,
    db_session: Session = Depends(get_db),
    advice_in: AdviceCreate,
    advice_id: int,
    current_user: DispatchUser = Depends(get_current_user)
):
    existed = get(db_session=db_session, id=advice_id)
    if not existed:
        raise HTTPException(status_code=400, detail="The Advice with this id does not exist.")
    splitd = split_advice_f(db_session=db_session, id=advice_id, advice_in=advice_in, current_user=current_user)
    return splitd

@router.post("/replace/{advice_id}", response_model=AdviceRead)
def replace_advice(
    *,
    db_session: Session = Depends(get_db),
    advice_in: AdviceCreate,
    advice_id: int,
    current_user: DispatchUser = Depends(get_current_user)
):
    advice = get(db_session=db_session, id=advice_id)
    if not advice:
        raise HTTPException(status_code=400, detail="The Advice with this id does not exist.")
    advice_in.updated_by = current_user.email
    advice_in.updated_at = datetime.now()
    replace = replaced_advice(db_session=db_session, advice_in=advice_in, advice=advice, current_user=current_user)
    return replace

@router.post("/", response_model=AdviceRead)
def create_advice(
    *,
    db_session: Session = Depends(get_db),
    advice_in: AdviceCreate,
    current_user: DispatchUser = Depends(get_current_user)
):
    advice_in.created_by = current_user.email
    advice_in.updated_at = datetime.now()
    advice_in.updated_by = current_user.email
    advice_in.mill_id = current_user.current_mill_id
    advice = create(db_session=db_session, advice_in=advice_in)
    return advice


@router.delete("/{advice_id}")
def advice_delete(
    *,
    db_session: Session = Depends(get_db),
    current_user: DispatchUser = Depends(get_current_user),
    advice_id: int
):
    advice = get(db_session=db_session, id=advice_id)
    if not advice:
        raise HTTPException(status_code=400, detail="The Advice with this id does not exist.")
    deleted = delete_advice(db_session=db_session, id=advice_id)
    return deleted

@router.put("/update_cancel")
def advice_update_cancel(
    *,
    db_session: Session = Depends(get_db),
    item_ids: AdviceSplit,
    current_user: DispatchUser = Depends(get_current_user)
):
    return update_cancel(db_session=db_session, item_ids=item_ids)

@router.put("/update_deload")
def advice_update_deload(
    *,
    db_session: Session = Depends(get_db),
    advice_in: AdviceSplit,
    current_user: DispatchUser = Depends(get_current_user)
):
    return update_deload(db_session=db_session, advice_in=advice_in)

@router.put("/tip_update", response_model=AdviceRead)
def advice_tip_update(
    *,
    background_tasks: BackgroundTasks,
    db_session: Session = Depends(get_db),
    advice_in: AdviceUpdate,
    current_user: DispatchUser = Depends(get_current_user)
):
    advice_in.updated_by = current_user.email
    advice_in.updated_at = datetime.now()
    return advice_tips_update(db_session=db_session, advice_in=advice_in, background_tasks=background_tasks, current_user=current_user)


@router.put("/{advice_id}", response_model=AdviceRead)
def advice_update(
    *,
    db_session: Session = Depends(get_db),
    advice_in: AdviceUpdate,
    advice_id: int,
    current_user: DispatchUser = Depends(get_current_user)
):
    advice = get(db_session=db_session, id=advice_id)
    if not advice:
        raise HTTPException(status_code=400, detail="The Advice with this id does not exist.")
    advice_in.mill_id = current_user.current_mill_id
    advice_in.updated_by = current_user.email
    advice_in.updated_at = datetime.now()
    return update(db_session=db_session, advice=advice, advice_in=advice_in)

@router.put("/update_finished_product/{finished_product_id}")
def finished_product_update(
    *,
    db_session: Session = Depends(get_db),
    advice_in: AdviceRead,
    finished_product_id: int,
    current_user: DispatchUser = Depends(get_current_user)
):
    advice_in.updated_at = datetime.now()
    advice_in.updated_by = current_user.email
    return update_advice_finished_product(db_session=db_session, advice_in=advice_in, finished_product_id=finished_product_id)

@router.post("/print_label/{advice_id}", response_model=AdviceRead)
def print_label(
    *,
    background_tasks: BackgroundTasks,
    db_session: Session = Depends(get_db),
    advice_in: AdviceUpdate,
    advice_id: int,
    current_user: DispatchUser = Depends(get_current_user)
):
    try:
        from ...contrib.message_admin.message_server import server as MessageServer
        message_server = MessageServer.MessageStrategyPBM04()
        message_server.send_PBM04(db_session, advice_in, advice_id, background_tasks)
    except ImportError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"ERROR sending PBM04: {e}")




@router.get("/tip/{advice_id}", response_model=AdviceRead)
def advice_tip_xml(
    *,
    background_tasks: BackgroundTasks,
    db_session: Session = Depends(get_db),
    advice_id: int,
    action: str = Query(None),
    common: dict = Depends(common_parameters)
):
    advice = get(db_session=db_session, id=advice_id)
    if not advice:
        raise HTTPException(status_code=400, detail="The Advice with this id does not exist.")
    order = advice.order
    if not order:
        raise HTTPException(status_code=400, detail="The Advice with not found order.")
    business_type = advice.business_type
    if business_type == "Internal":
        raise HTTPException(status_code=400, detail="Internal Advice with not allowed Tip message.")
    finished = []
    finished_data = db_session.query(FinishedProduct).join(
        finished_product_advice, finished_product_advice.c.finished_product_id == FinishedProduct.id
    ).filter(finished_product_advice.c.advice_id == advice.id, FinishedProduct.is_deleted == 0)
    for item in finished_data:
        finished.append(item)
    action = action or "C"
    create_advice_xml(db_session=db_session, advice=advice, order_item=finished, action=action)
    # return True
    return advice


@router.post("/return")
def advice_return(*, db_session:Session=Depends(get_db), payload:AdviceReturn, current_user: DispatchUser = Depends(get_current_user)):
    his = []
    uid = uuid.uuid4()
    for id_ in payload.ids:
        with db_session.begin():
            advice = db_session.query(Advice).filter(Advice.id == id_).one_or_none()
            if not advice:
                raise HTTPException(status_code=400, detail="The Advice with this id does not exist.")
            advice.status = AdviceStatusEnum.RETURNED
            advice.updated_at = datetime.now(UTC)
            advice.updated_by = current_user.email
            # finished_product = db_session.query(FinishedProduct).filter(FinishedProduct.advice_id == id_).all()
            finished_product = advice.finished_product

            for item in finished_product:
                item.area_id = payload.area_id
                item.updated_at = datetime.now(UTC)
                item.updated_by = current_user.email
                his.append({
                    "uuid": uid,
                    "mill_id": item.mill_id,
                    "change_type": FinishedProductHistoryChangeTypeEnum.ADVICE_RETURN,
                    "created_by": current_user.email,
                    "code": item.code,
                    'rolling_code': item.rolling.rolling_code if item.rolling else None,
                    'runout_code': item.runout.runout_code if item.runout else None,
                    'area_code': item.area.code if item.area else None,
                    'cast_no': item.cast.cast_code if item.cast else None,
                    'spec_code': item.spec.spec_code if item.spec else None,
                    'order_num': item.order.order_code if item.order else None,
                    'order_item_num': item.order_item.line_item_code if item.order_item else None,
                    'product_type': item.product_type.code if item.product_type else None,
                    "status": item.status,
                    "kg": item.kg,
                    "length_mm": item.length_mm,
                    "quantity": item.quantity,
                    "advice_no": advice.advice_code,
                    "exist_flag": item.exist_flag,
                })
            db_session.bulk_insert_mappings(
                FinishedProductHistory, his
            )
            db_session.commit()
    return True

@router.post("/order_item", response_model=OrderItemPagination)
def get_advice_order_item_interface(
    *,
    db_session: Session = Depends(get_db),
    advice_in: AdviceIDPagination
):
    order_item = get_advice_order_item(db_session=db_session, advice_in=advice_in)
    return order_item

@router.get("/store")
def get_store_code(*, db_session: Session = Depends(get_db)):
    stores = get_store(db_session=db_session)
    if not stores:
        return []
    return [str(store) for store in stores]