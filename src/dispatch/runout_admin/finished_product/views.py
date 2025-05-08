import math
import requests

from fastapi import Query, BackgroundTasks
from sqlalchemy import func, or_, desc, nullslast, literal
from sqlalchemy.orm import aliased

from dispatch.area.models import Area
from dispatch.cast.models import Cast
from dispatch.database import get_db
from typing import List
from sqlalchemy import and_
from datetime import datetime
import uuid
import json
from dispatch.rpc_odoo import odoo_authenticate

from fastapi import APIRouter, Depends, HTTPException,Body
from sqlalchemy.orm import Session
from dispatch.database_util.service import common_parameters, search_filter_sort_paginate
from dispatch.order_admin.order.models import Order
from dispatch.order_admin.order_item.models import OrderItem
from dispatch.runout_admin.finished_product.service import create_repeat, move_to_product, update_reserve_rework, \
    get_by_codes
from dispatch.runout_admin.runout_list.models import Runout
from dispatch.spec_admin.spec.models import Spec
from dispatch.system_admin.auth.models import DispatchUser
from dispatch.system_admin.auth.service import get_current_user
from dispatch.covering_admin.cover_end_use.models import CoverEndUse
from dispatch.rolling.rolling_list.models import Rolling
# from dispatch.contrib.message_admin.message_server.trigger_sap_message import (
#     MFGI182_ACTION,
#     handle_mfgi182,
#     handle_mfgi302,
#     handle_mfgi404,
#     handle_qmai264,
#     MFGI404_ACTION,
#     QMAI264_ACTION,
#     handle_holdunhold
# )

from ..finished_product_load.models import FinishedProductLoadRead
from .models import (
    FinishedProduct,
    FinishedProductAllocate,
    FinishedProductBySearch,
    FinishedProductCreate,
    FinishedProductCreateLoad,
    FinishedProductHoldReason,
    FinishedProductMultCreate,
    FinishedProductMultPagination,
    FinishedProductMultResponse,
    FinishedProductPagination,
    FinishedProductRead,
    FinishedProductRepeatCreate,
    FinishedProductUpdate,
    RegradePagination,
    RegradeUpdate,
    RetrieveUpdate,
    ReworkRead,
    ReworkUpdate,
    LoadUpdate,
    MultConfirm,
    GetCompliance,
    FinishedProductReworkComplete,
    ReturnUpdate,
    CutTestSample, LabelPrint
)

from dispatch.runout_admin.advice.models import AdviceStatusEnum, Advice
from dispatch.runout_admin.holdreason import service as hold_service
from dispatch.runout_admin.holdreason.models_secondary import finished_product_hold
from .models_secondary_advice import finished_product_advice
from dispatch.runout_admin.finished_product_history.service import bulk_create_finished_product_history
from dispatch.runout_admin.finished_product_history.models import FinishedProductHistoryChangeTypeEnum, FinishedProductHistory
from dispatch.certificate_finished_product import service as certificate_finished_product_service
from dispatch.runout_admin.runout_list import service as runout_service
from dispatch.product_type.models import ProductType
from dispatch.spec_admin.spec import service as spec_service
from dispatch.spec_admin.sptensil import service as sptensil_service
from dispatch.spec_admin.spelong import service as spelong_service
from dispatch.spec_admin.spyield import service as spyield_service
from dispatch.spec_admin.spimpact import service as spimpact_service
from dispatch.tests_admin.tensile_test_card import service as test_tensile_service
from dispatch.tests_admin.impact_test_card import service as test_impact_service
from dispatch.product_size import service as product_size_service
from ...config import (
    MILLEnum,
    get_mill_ops,
    ODOO_HOST,
    ODOO_DB,
    ODOO_USERNAME,
    ODOO_PASSWORD,
)
# from ...contrib.message_admin.message_server import server as message_server
from dispatch.runout_admin.test_coverage import service as test_coverage_service
# from dispatch.contrib.cover.tbm.runout_services import create_test_coverage, compare_t_result, compare_c_result
# from dispatch.contrib.cover.tbm.utils import get_stone, filter_list_by_thickness
from dispatch.runout_admin.runout_list.service import get as get_runout_by_id
from .service import (
    allocate_change_type,
    batch_update,
    check_and_trigger_rework_rebundle,
    confirm_mult,
    create,
    create_by_load,
    create_defects,
    create_mult,
    get,
    get_by_code,
    get_by_search,
    get_covering,
    get_finish_product_codes,
    get_max_cut_code,
    get_mult,
    update_finished,
    update_load,
    update_rework,
    update_rework_complete,
    update_unload,
    return_finished,
    get_store_codes,
    process_batch_hold,
    process_batch_unhold,
    update_finished_product_data,
    rebundle_update
)

# from dispatch.contrib.message_admin.message_server.server import MessageStrategySRSMM641, MessageStrategySRSMM160, MessageStrategySRSMM642, MessageStrategySRSMMTST, MessageStrategySRSMM480
from dispatch.defect_reason.models import DefectReason
from dispatch.tests_admin.test_sample.models import TestSample
from dispatch.tests_admin.test_sample import service as test_sample_service
# from dispatch.contrib.message_admin.message_server.server import MessageStrategySRSMM132
from dispatch.message_admin.message_server.models import MessageData
from dispatch.runout_admin.finished_product.enums import FinishedProductStatusEnum
from dispatch.runout_admin.finished_product.models_secondary_association import finished_product_association
from sqlalchemy.inspection import inspect
from dispatch.rolling.cut_sequence_plan.models import CutSequencePlan
from dispatch.tests_admin.bend_test_card.models import TestBend
from dispatch.tests_admin.impact_test_card.models import TestImpact
from dispatch.tests_admin.tensile_test_card.models import TestTensile
from dispatch.tests_admin.test_list.models import Test
from dispatch.runout_admin.test_coverage.models import TestCoverage

router = APIRouter()
from dispatch.log import getLogger
logger = getLogger(__name__)

@router.get("/", response_model=FinishedProductPagination)
def get_finished_products(*, db_session: Session = Depends(get_db), common: dict = Depends(common_parameters), rework_type:str = Query(None),hold_reason_id:int = Query(None),
                          product_class: str = Query(None), product_category: str = Query(None), archieved_status: str = Query(None),area_code: List[str] = Query([], alias="area_code[]"),
                          load_id: int = Query(None), load_code: str = Query(None), load_status: str = Query(None), runout_id1: int = Query(None), runout_id2: int = Query(None), advice_id: int = Query(None),
                          allocation_status: List[str] = Query([], alias="allocation_status[]"),reserved_order_id: int = Query(None), advice_status: str = Query(None),):
    # 为 reserved_order_item 创建别名
    ReservedOrderItem = aliased(OrderItem)
    
    query = db_session.query(FinishedProduct).outerjoin(Spec, FinishedProduct.spec_id == Spec.id
    ).outerjoin(Cast, FinishedProduct.cast_id == Cast.id
    ).outerjoin(Runout, FinishedProduct.runout_id == Runout.id 
    ).outerjoin(Area, FinishedProduct.area_id == Area.id  
    ).outerjoin(Order, FinishedProduct.order_id == Order.id
    ).outerjoin(OrderItem, FinishedProduct.order_item_id == OrderItem.id
    ).outerjoin(ProductType, FinishedProduct.product_type_id == ProductType.id
    ).outerjoin(ReservedOrderItem, FinishedProduct.reserved_order_item_id == ReservedOrderItem.id
    ).outerjoin(Rolling, FinishedProduct.rolling_id == Rolling.id
    ).outerjoin(DefectReason, FinishedProduct.defect_reason_id == DefectReason.id)
    # ).outerjoin(TestCoverage, FinishedProduct.id == TestCoverage.finished_product_id
    # ).outerjoin(Test, FinishedProduct.runout_id == Test.runout_id
    # ).outerjoin(TestTensile, TestTensile.test_id == Test.id
    # ).outerjoin(TestImpact, TestImpact.test_id == Test.id)

    # if len(allocation_status) > 0:
    #     query = query.filter(FinishedProduct.allocation_status.in_(allocation_status))
    # else:
    #     query = query.filter(
    #         or_(
    #             FinishedProduct.allocation_status != 'scrap',
    #             FinishedProduct.allocation_status.is_(None)
    #         )
    #     )

    if rework_type:
        rework_type = json.loads(rework_type)
        query = query.filter(func.string_to_array(FinishedProduct.rework_type, ',').op('&&')(rework_type))
    if hold_reason_id:
        query = query.filter(FinishedProduct.hold_reason.any(id=hold_reason_id))
    if load_id:
        query = query.filter(FinishedProduct.loads.any(id=load_id))
    if load_code:
        query = query.filter(FinishedProduct.loads.any(code=load_code))
    if advice_id:
        query = query.filter(FinishedProduct.advice.any(id=advice_id))
    if load_status:
        if load_status == 'Loaded':
            query = query.filter(FinishedProduct.loads.any())
        elif load_status == 'Not loaded':
            query = query.filter(~FinishedProduct.loads.any())
    # if advice_status:
    #     if advice_status == 'Adviced':
    #         query = query.filter(FinishedProduct.advice.any())
    #     elif advice_status == 'Not Adviced':
    #         query = query.filter(~FinishedProduct.advice.any())
    if advice_status == 'Adviced':
        # 查询所有具有advice且advice的状态为'unload'，且advice的type不是'internal'的finished product
        query = query.filter(
            FinishedProduct.advice.any(
                or_(
                    # 如果advice的status是'unload'且类型不是'internal'，才筛选出来
                    and_(
                        Advice.status == AdviceStatusEnum.UNLOAD,
                        Advice.business_type != 'internal'
                    ),
                    # 如果advice的status不等于'unload'，也可以被选出来，且不受type过滤
                    Advice.status != AdviceStatusEnum.UNLOAD
                )
            )
        )
    elif advice_status == 'Not Adviced':
        # 查询所有没有advice或者advice的状态是'unload'的finished product
        query = query.filter(
            or_(
                FinishedProduct.advice.any(
                    and_(
                        Advice.status == AdviceStatusEnum.UNLOAD,
                        Advice.business_type == 'internal'
                    )
                ),
                ~FinishedProduct.advice.any()  # 没有advice的finished product
            )
        )
    if area_code:
       query = query.filter(Area.code.in_(area_code) & (Area.type == "f-finished_product"))
    if product_class:
        query = query.filter(ProductType.code.like(f'{product_class}%'))
    if runout_id1 and runout_id2:
        runout_code1 = db_session.query(Runout).filter(Runout.id == runout_id1).first()
        runout_code2 = db_session.query(Runout).filter(Runout.id == runout_id2).first()
        if runout_code1 and runout_code2:
            max_code = max(runout_code1.runout_code, runout_code2.runout_code)
            min_code = min(runout_code1.runout_code, runout_code2.runout_code)
            query = query.filter(Runout.runout_code.between(min_code, max_code))
    if product_category:
        query = query.filter(ProductType.code.like(f'%{product_category}%'))
    if archieved_status == 'Archieved':
        query = query.filter(FinishedProduct.status == 'archieve')
    if archieved_status == 'Current':
        query = query.filter(or_(FinishedProduct.status != 'archieve', FinishedProduct.status.is_(None))) 
    # 处理排序
    if common.get('sort_by') and 'reserved_order_item.line_item_code' in common['sort_by']:
        index = common['sort_by'].index('reserved_order_item.line_item_code')
        is_desc = common.get('descending', [])[index] if common.get('descending') else False
        
        # 修改排序规则，使用 nullslast 确保 NULL 值排在最后
        if is_desc:
            query = query.order_by(nullslast(desc(ReservedOrderItem.line_item_code)))
        else:
            query = query.order_by(nullslast(ReservedOrderItem.line_item_code))
            
        # 从排序列表中移除已处理的排序
        common['sort_by'].pop(index)
        if common.get('descending'):
            common['descending'].pop(index)

    if reserved_order_id:
        query = query.filter(ReservedOrderItem.order_id == reserved_order_id)


    if common['fields'] and ('advice_id' in common['fields']):
        advice_id_index = common['fields'].index('advice_id')
        common_advice_id = common['values'][advice_id_index]
        common['fields'].pop(advice_id_index)
        common['ops'].pop(advice_id_index)
        common['values'].pop(advice_id_index)
        query = query.join(finished_product_advice, finished_product_advice.c.finished_product_id == FinishedProduct.id
        ).filter(
            finished_product_advice.c.advice_id == common_advice_id
        )
    common['query'] = query
    # demo
    # common["filter_type"]  = [['or', 'or']]
    # common["fields"] = ["status", "status"]
    # common["ops"] = [ "!=", "is_null"]
    # common["values"] = ["archieve",True ]

    finished_product = search_filter_sort_paginate(model="FinishedProduct", **common)

    finished_data = finished_product["items"]

    
    if finished_data:
        order_item_ids = {item.order_item_id for item in finished_data if item.order_item_id}
        if order_item_ids:
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

            for item in finished_data:
                item.cut_sequence = cut_sequences_dict.get(item.order_item_id, [])

            # New block: Retrieve insp_code values for each finished product
        # New block: Retrieve related TestTensile and TestImpact records
        # New block: Retrieve related TestTensile and TestImpact records using finished_product.runout_id
        # 1. Get all unique runout_ids from finished_data
        finished_runout_ids = {fp.runout_id for fp in finished_data if fp.runout_id is not None}

        # 2. Query the Test table to get tests matching these runout_ids
        tests = db_session.query(Test.runout_id, Test.id).filter(Test.runout_id.in_(finished_runout_ids)).all()

        # Build a mapping from runout_id to list of test_ids
        runout_to_test_ids = {}
        for runout_id, test_id in tests:
            runout_to_test_ids.setdefault(runout_id, []).append(test_id)

        # Get a set of all test_ids from the tests query
        all_test_ids = list({test_id for _, test_id in tests})

        # 3. Query TestTensile records and convert them to dicts
        tensile_columns = [c.key for c in inspect(TestTensile).mapper.column_attrs]
        tensile_results = db_session.query(TestTensile).filter(TestTensile.test_id.in_(all_test_ids)).all()
        tensile_dict = {}
        for tensile in tensile_results:
            t_dict = {col: getattr(tensile, col) for col in tensile_columns}
            tensile_dict.setdefault(tensile.test_id, []).append(t_dict)

        # 4. Query TestImpact records and convert them to dicts
        impact_columns = [c.key for c in inspect(TestImpact).mapper.column_attrs]
        impact_results = db_session.query(TestImpact).filter(TestImpact.test_id.in_(all_test_ids)).all()
        impact_dict = {}
        for impact in impact_results:
            i_dict = {col: getattr(impact, col) for col in impact_columns}
            impact_dict.setdefault(impact.test_id, []).append(i_dict)

        # 5. Attach the related TestTensile and TestImpact records to each finished product,
        #    based on the finished_product.runout_id mapping to test IDs.
        for fp in finished_data:
            test_ids = runout_to_test_ids.get(fp.runout_id, [])
            tensile_list = []
            impact_list = []
            for tid in test_ids:
                tensile_list.extend(tensile_dict.get(tid, []))
                impact_list.extend(impact_dict.get(tid, []))
            fp.test_tensile = tensile_list
            fp.test_impact = impact_list

            
        for finished in finished_data:
            # 将finished_product_hold中间表的comment查出来
            for hold in finished.hold_reason:
                is_hold = (
                    db_session.query(finished_product_hold)
                    .filter(
                        finished_product_hold.c.finished_product_id == finished.id,
                        finished_product_hold.c.hold_reason_id == hold.id,
                    )
                    .first()
                )
                if is_hold:
                    hold.comment = is_hold.comment
            # if spec find test_result
            if finished.spec:
                finished.test_result = int(f"{finished.t_result if finished.t_result else 0}{finished.c_result if finished.c_result else 0}")
            if finished.t_runout:
                r = get_runout_by_id(db_session=db_session, runout_id=finished.t_runout)
                finished.t_runout_code = r.runout_code if r else None
            if finished.c_runout:
                r = get_runout_by_id(db_session=db_session,runout_id= finished.c_runout)
                finished.c_runout_code = r.runout_code if r else None

            defect_reason_count = 0
            if finished.defect_reason_id:
                # 查询 defect_reason_id 出现的次数
                defect_reason_count = (
                    db_session.query(func.count(FinishedProduct.id))
                    .filter(FinishedProduct.defect_reason_id == finished.defect_reason_id)
                    .scalar()
                )
                finished.defect_reason_no = defect_reason_count
            quantity = finished.quantity if finished.quantity else 0
            finished.qualified_quantity = quantity - defect_reason_count
            # if advice_status == 'Adviced':
            finished.advice = [advice for advice in finished.advice if advice.status not in ['unload', 'return']]
            
    return finished_product

@router.get("/mult", response_model=FinishedProductMultPagination)
def get_mults(*, common: dict = Depends(common_parameters)):

    resp = search_filter_sort_paginate(model="FinishedProduct", **common)
    return resp


@router.post('/test_cover')
def get_test_cover(*, db_session: Session = Depends(get_db), test_in: dict, current_user: DispatchUser = Depends(get_current_user)):
    test_ids = test_in.get('params', {}).get('test_ids', [])
    ImpactModel = TestImpact
    TensileModel = TestTensile
    impact_columns = [
        Test.id.label("test_id"),
        Test.test_code.label('test_code'),
        TestSample.test_sample_code,
        Test.ref_code.label('test_ref_code'),
        TestSample.runout_id,
        literal('Impact').label('test_type'),
        ImpactModel.temp_c.label('temp_c'),
        ImpactModel.temp_units.label('temp_units'),
        ImpactModel.energy_1_j.label('energy_1_j'),
        ImpactModel.energy_2_j.label('energy_2_j'),
        ImpactModel.energy_3_j.label('energy_3_j'),
        literal(None).label('orientation'),
        ImpactModel.standard.label('standard'),
        literal(None).label('value_mpa'),
        literal(None).label('yield_tt0_5'),
        literal(None).label('elongation_a200'),
        literal(None).label('result_1')
    ]

    # Impact test query
    impact_query = db_session.query(*impact_columns).join(
        Test, Test.id == ImpactModel.test_id
    ).join(
        TestSample, Test.test_sample_id == TestSample.id
    ).filter(
        Test.id.in_(test_ids)  # 使用 test_id 作为过滤条件
    )

    # Tensile test query
    tensile_query = db_session.query(
        Test.id.label("test_id"),
        Test.test_code.label('test_code'),
        TestSample.test_sample_code,
        Test.ref_code.label('test_ref_code'),
        TestSample.runout_id,
        literal('Tensile').label('test_type'),
        literal(None).label('temp_c'),
        literal(None).label('temp_units'),
        literal(None).label('energy_1_j'),
        literal(None).label('energy_2_j'),
        literal(None).label('energy_3_j'),
        TensileModel.orientation.label('orientation'),
        TensileModel.standard.label('standard'),
        TensileModel.value_mpa.label('value_mpa'),
        TensileModel.yield_tt0_5.label('yield_tt0_5'),
        TensileModel.elongation_a200.label('elongation_a200'),
        literal(None).label('result_1')
    ).join(
        Test, Test.id == TensileModel.test_id
    ).join(
        TestSample, Test.test_sample_id == TestSample.id
    ).filter(
        Test.id.in_(test_ids)  # 使用 test_id 作为过滤条件
    )

    # Bend test query
    bend_query = db_session.query(
        Test.id.label("test_id"),
        Test.test_code.label('test_code'),
        TestSample.test_sample_code,
        Test.ref_code.label('test_ref_code'),
        TestSample.runout_id,
        literal('Bend').label('test_type'),
        literal(None).label('temp_c'),
        literal(None).label('temp_units'),
        literal(None).label('energy_1_j'),
        literal(None).label('energy_2_j'),
        literal(None).label('energy_3_j'),
        literal(None).label('orientation'),
        literal(None).label('standard'),
        literal(None).label('value_mpa'),
        literal(None).label('yield_tt0_5'),
        literal(None).label('elongation_a200'),
        TestBend.result_1.label('result_1')
    ).join(
        Test, Test.id == TestBend.test_id
    ).join(
        TestSample, Test.test_sample_id == TestSample.id
    ).filter(
        Test.id.in_(test_ids)  # 使用 test_id 作为过滤条件
    )

    combined_query = impact_query.union_all(tensile_query, bend_query)

    data = list(combined_query)

    return {
        "total": len(data),
        "items": data,
        "itemsPerPage": len(data),
        "page": 1
    }


@router.get("/mult/{finished_product_id}", response_model=FinishedProductMultResponse)
def get_mult_by_id(*, db_session: Session = Depends(get_db), finished_product_id: int):
    
    return get_mult(db_session=db_session, id=finished_product_id)

# @router.post("/mult", response_model=FinishedProductMultRead)
# def create_mult_finished_product(
#     *,
#     db_session: Session = Depends(get_db),
#     mult_finished_product_in: FinishedProductMultSingleCreate,
#     current_user: DispatchUser = Depends(get_current_user),
# ):
#     mult_finished_product = create_by_mult(db_session=db_session, mult_finished_product_in=mult_finished_product_in)
#     return mult_finished_product

@router.put("/mult/confirm")
def confirm_mult_finished_product(
    *,
    db_session: Session = Depends(get_db),
    mult_confirm_in: MultConfirm,
    current_user: DispatchUser = Depends(get_current_user),
):
    for finished_product_id in mult_confirm_in.ids:
        finished_product = get(db_session=db_session, id=finished_product_id)
        if finished_product and finished_product.advice and len(finished_product.advice) > 0:
            for advice in finished_product.advice:
                if advice.status != AdviceStatusEnum.UNLOAD:
                    raise HTTPException(status_code=400, detail=f"The finished product with this code {finished_product.code} has advice not tipped")
        if not finished_product:
            raise HTTPException(status_code=400, detail="The finished product with this id does not exists.")

        if finished_product.exist_flag == 'N':
            raise HTTPException(status_code=400, detail="The finished product with this id does not real exists.")

    confirm_mult(db_session=db_session, mult_confirm_in=mult_confirm_in ,current_user=current_user)

    return { "status": "ok" }

@router.put("/allocate_mult", response_model=FinishedProductMultResponse)
def create_mult_finished_products(
    *,
    background_tasks: BackgroundTasks,
    db_session: Session = Depends(get_db),
    mult_in: FinishedProductMultCreate,
    current_user: DispatchUser = Depends(get_current_user),
):
    bundles = []
    if len(mult_in.ids) > 0:
        for finished_product_id in mult_in.ids:
            finished_product = get(db_session=db_session, id=finished_product_id)
            bundles.append(finished_product)
            # if not finished_product:
            #     raise HTTPException(status_code=400, detail="The finished product with this id does not exists.")
            # if finished_product.mult_type == 'M':
            #     raise HTTPException(status_code=400, detail="The finished product with this "+finished_product.code+" is a mult.")
    
    # if len(mult_in.regulars) <=1:
    #     total_length = sum([float(mult_in.mult.length_mm) * int(mult_in.mult.quantity)])
    #     computed_waste_length = float(finished_product.length_mm) - total_length
    #     cut_sample_length_mm = mult_in.mult.cut_sample_length_mm
    # else:
    #     total_length = sum([float(regular.length_mm) * int(regular.quantity) for regular in mult_in.regulars])
    #     computed_waste_length = float(finished_product.length_mm) - total_length
    #     cut_sample_length_mm = sum([float(regular2.cut_sample_length_mm) for regular2 in mult_in.regulars])
    # if total_length + cut_sample_length_mm > float(finished_product.length_mm):
    #     raise HTTPException(status_code=400, detail="The total length of regulars is great than the length of mult.")
    # if computed_waste_length - cut_sample_length_mm != float(mult_in.mult.waste_length):
    #     raise HTTPException(status_code=400, detail="The waste length of finished product is not correct")
    try:
        resp = create_mult(db_session=db_session, current_user=current_user, mult_in=mult_in, bundles=bundles, background_tasks=background_tasks)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    try:
        from dispatch.contrib.message_admin.message_server.trigger_sap_message import (
            handle_mfgi302,
            handle_mfgi404,
            MFGI404_ACTION
        )
        for id in mult_in.ids:
            handle_mfgi302(db_session=db_session, finished_product_id=id, background_tasks=background_tasks)
        if get_mill_ops(current_user.current_mill_id) == MILLEnum.MILL1:
            try:
                from dispatch.contrib.message_admin.message_server.server import MessageStrategySRSMM641
                srsmm641 = MessageStrategySRSMM641()
                res1 = srsmm641.send_pc_m641(db_session=db_session, bundles_=bundles, prev_allocation_status="", background_tasks=background_tasks, current_mill_code=current_user.current_mill_code)
                resp.message_triggered_result = res1
            except ImportError as e:
                raise HTTPException(status_code=400, detail=str(e))
            except Exception as e:
                logger.error(f"MessageStrategySRSMM641 is wrong. Caused: {e}, input is : {FinishedProductMultCreate}")
        if mult_in.mult.allocation_status == "scrap" and (get_mill_ops(current_user.current_mill_id) == MILLEnum.MILL410 or get_mill_ops(current_user.current_mill_id) == MILLEnum.MILL1):
            for id in mult_in.ids:
                handle_mfgi404(db_session=db_session, finished_product_id=id, action_e=MFGI404_ACTION.SCRAP, background_tasks=background_tasks)

        return resp
        # return create_mult(db_session=db_session, current_user=current_user, mult_in=mult_in)
    except ImportError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/rework", response_model=List[ReworkRead])
def rework_finished_product(
    *,
    background_tasks: BackgroundTasks,
    db_session: Session = Depends(get_db),
    rework_in: ReworkUpdate,
    current_user: DispatchUser = Depends(get_current_user),
):
    resp = update_rework(db_session=db_session, update_in=rework_in, current_user=current_user, background_tasks=background_tasks)
    # moved mfgi182 to /allocate_mult
    # for id in rework_in.ids:
    #     handle_mfgi182(db_session=db_session, finished_product_id=id, background_tasks=background_tasks)
    try:
        from dispatch.contrib.message_admin.message_server.trigger_sap_message import handle_qmai264, QMAI264_ACTION
        for id in rework_in.ids:
            handle_qmai264(db_session=db_session, finished_product_id=id, action_e=QMAI264_ACTION.REJECTED,
                           background_tasks=background_tasks)

        return resp
    except ImportError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/rework/complete")
def rework_finished_product_complete(
    *,
    background_tasks: BackgroundTasks,
    db_session: Session = Depends(get_db),
    finished_product_in: FinishedProductReworkComplete,
    current_user: DispatchUser = Depends(get_current_user),
):
    finished_product_list = []
    for finished_product_id in finished_product_in.ids:
        finished_product = get(db_session=db_session, id=finished_product_id)
        if not finished_product:
            raise HTTPException(status_code=400, detail="The finished product with this id does not exists.")
        if finished_product.rework_status != 'Rework':
            raise HTTPException(status_code=400, detail="The finished product with this id is not rework.")
        finished_product.updated_by = current_user.email
        finished_product_list.append(finished_product)

    update_rework_complete(db_session=db_session, data_list=finished_product_list, finished_product_in=finished_product_in, background_tasks=background_tasks, current_mill_code=current_user.current_mill_code)

    return {"status": "ok"}




@router.put("/load/{id}")
def load_finished_product(
    *,
    db_session: Session = Depends(get_db),
    id: int,
    load_in: LoadUpdate,
    current_user: DispatchUser = Depends(get_current_user),
):
    finished_product = get(db_session=db_session, id=id)
    if not finished_product:
        raise HTTPException(status_code=400, detail="The finished product with this id does not exists.")
    finished_product.updated_by = current_user.email
    finished_product.updated_at = datetime.now()
    return update_load(db_session=db_session, get_data=finished_product, load_in=load_in)

@router.put("/unload/{id}")
def unload_finished_product(
    *,
    db_session: Session = Depends(get_db),
    id: int,
    current_user: DispatchUser = Depends(get_current_user),
):
    finished_product = get(db_session=db_session, id=id)
    if not finished_product:
        raise HTTPException(status_code=400, detail="The finished product with this id does not exists.")
    finished_product.updated_by = current_user.email
    finished_product.updated_at = datetime.now()
    return update_unload(db_session=db_session, get_data=finished_product)

@router.post("/batch_hold", response_model=List[FinishedProductRead])
def batch_hold(
    *,
    background_tasks: BackgroundTasks,
    db_session: Session = Depends(get_db),
    Finished_in: FinishedProductHoldReason,
    current_user: DispatchUser = Depends(get_current_user),
    runout_code1: int = Query(None), runout_code2: int = Query(None), order_id: int = Query(None), advice_id: int = Query(None),
    rolling_id: int = Query(None), order_item_id: int = Query(None), rolling_dim3: int = Query(None)
):
    finisheds = []
    FinishedProductAdvice = aliased(finished_product_advice)
    if runout_code2 and runout_code1:
        max_code = str(max(runout_code1, runout_code2))
        min_code = str(min(runout_code1, runout_code2))
        runouts_in_range = db_session.query(Runout).filter(Runout.runout_code.between(min_code, max_code)).all()
        runout_ids = [runout.id for runout in runouts_in_range]
        finisheds = db_session.query(FinishedProduct).filter(FinishedProduct.runout_id.in_(runout_ids)).all()
    if order_item_id:
        finisheds = db_session.query(FinishedProduct).filter(FinishedProduct.order_item_id == order_item_id).all()
    if advice_id:
        finished_product_adive_data = db_session.query(FinishedProductAdvice).filter(FinishedProductAdvice.c.advice_id == advice_id).all()
        finished_product_id = [finished_product_advices.finished_product_id for finished_product_advices in finished_product_adive_data]
        finisheds = db_session.query(FinishedProduct).filter(FinishedProduct.id.in_(finished_product_id)).all()
    if rolling_id:
        if rolling_dim3:
            rolling_data = db_session.query(Rolling).filter(Rolling.rolling_dim3 == str(rolling_dim3)).all()
            rolling_data_id = [rolling_data.id for rolling_data in rolling_data]
            finisheds = db_session.query(FinishedProduct).filter(FinishedProduct.rolling_id.in_(rolling_data_id)).all()
        else:
            finisheds = db_session.query(FinishedProduct).filter(FinishedProduct.rolling_id == rolling_id).all()

    history_data = process_batch_hold(
        db_session=db_session,
        finisheds=finisheds,
        finished_in=Finished_in,
        current_user_email=current_user.email,
        hold_service=hold_service,
        background_tasks=background_tasks,
        current_mill_code=current_user.current_mill_code
    )

    return finisheds

@router.post("/batch_unHold", response_model=List[FinishedProductRead])
def update_delete_hold(
    *,
    background_tasks: BackgroundTasks,
    db_session: Session = Depends(get_db),
    Finished_in: FinishedProductHoldReason,
    current_user: DispatchUser = Depends(get_current_user),
    runout_code1: int = Query(None), runout_code2: int = Query(None), order_id: int = Query(None),
    advice_id: int = Query(None),rolling_id: int = Query(None)
):
    finisheds = []
    FinishedProductAdvice = aliased(finished_product_advice)
    if runout_code2 and runout_code1:
        max_code = str(max(runout_code1, runout_code2))
        min_code = str(min(runout_code1, runout_code2))
        runouts_in_range = db_session.query(Runout).filter(Runout.runout_code.between(min_code, max_code)).all()
        runout_ids = [runout.id for runout in runouts_in_range]
        finisheds = db_session.query(FinishedProduct).filter(FinishedProduct.runout_id.in_(runout_ids)).all()
    if order_id:
        finisheds = db_session.query(FinishedProduct).filter(FinishedProduct.order_id == order_id).all()
    if advice_id:
        finished_product_adive_data = db_session.query(FinishedProductAdvice).filter(
            FinishedProductAdvice.c.advice_id == advice_id).all()
        finished_product_id = [finished_product_advices.finished_product_id for finished_product_advices in finished_product_adive_data]
        finisheds = db_session.query(FinishedProduct).filter(FinishedProduct.id.in_(finished_product_id)).all()
    if rolling_id:
        finisheds = db_session.query(FinishedProduct).filter(FinishedProduct.rolling_id == rolling_id).all()

    released_finished_products = process_batch_unhold(
        db_session=db_session,
        finisheds=finisheds,
        finished_in=Finished_in,
        current_user_email=current_user.email,
        hold_service=hold_service,
        background_tasks=background_tasks,
        current_mill_code=current_user.current_mill_code
    )

    return released_finished_products


@router.post("/update_add_hold", response_model=List[FinishedProductRead])
def update_add_hold(
    *,
    background_tasks: BackgroundTasks,
    db_session: Session = Depends(get_db),
    Finished_in: FinishedProductHoldReason,
    current_user: DispatchUser = Depends(get_current_user)
):

    finisheds = db_session.query(FinishedProduct).filter(FinishedProduct.id.in_(Finished_in.finished_ids)).all()
    hold_data = []
    hold_by = current_user.email
    for finished in finisheds:

        for hold in Finished_in.hold_list:
            hold_id = hold.get("hold_id")
            hold_comment = hold.get("comment") if hold.get("comment") else None

            # 查找 hold 是否已存在
            is_hold = (
                db_session.query(finished_product_hold)
                .filter(
                    finished_product_hold.c.finished_product_id == finished.id,
                    finished_product_hold.c.hold_reason_id == hold_id,
                )
                .first()
            )

            if is_hold:
                # 对已存在的 多对多记录 进行comment 修改

                update_hold = (
                    finished_product_hold.update()
                    .where(
                        finished_product_hold.c.finished_product_id == finished.id,
                        finished_product_hold.c.hold_reason_id == hold_id,
                    )
                    .values(comment=hold_comment)
                )

                db_session.execute(update_hold)

            else:

                hold_reason = hold_service.get(db_session=db_session, id=hold_id)

                hold_data.append(
                    {
                        "finished_product_id": finished.id,
                        "hold_reason_id": hold_reason.id,
                        "mill_id": hold_reason.mill_id if hold_reason.mill_id else None,
                        "comment": hold_comment,
                        "hold_by": hold_by,
                    }
                )
                if get_mill_ops(current_user.current_mill_id) == MILLEnum.MILL1:
                    if "TEST" not in hold_reason.name.upper():
                        try:
                            from dispatch.contrib.message_admin.message_server.server import MessageStrategySRSMMTST
                            srsmmtst = MessageStrategySRSMMTST()
                            res1 = srsmmtst.send_pc_mtst(db_session=db_session, bundle_=finished, releaseFlag="N", background_tasks=background_tasks, current_mill_code=current_user.current_mill_code)
                        except ImportError as e:
                            raise HTTPException(status_code=400, detail=str(e))
                        except Exception as e:
                            logger.error(f"ERROR in send_pc_mtst:{e}")
    if len(hold_data) > 0:
        db_session.execute(finished_product_hold.insert(), hold_data)
    db_session.commit()

    his = []
    uid = uuid.uuid4()
    for his_f in finisheds:
        for his_d in his_f.hold_reason:
            comment = None
            is_hold = (
                db_session.query(finished_product_hold)
                .filter(
                    finished_product_hold.c.finished_product_id == his_f.id,
                    finished_product_hold.c.hold_reason_id == his_d.id,
                )
                .first()
            )
            if is_hold:
                comment = is_hold.comment
            his.append(
                {
                    "mill_id": his_f.mill_id,
                    "change_type": FinishedProductHistoryChangeTypeEnum.HOLD,
                    "created_by": current_user.email,
                    "uuid": uid,
                    "code": his_f.code,
                    'rolling_code': his_f.rolling.rolling_code if his_f.rolling else None,
                    'runout_code': his_f.runout.runout_code if his_f.runout else None,
                    'area_code': his_f.area.code if his_f.area else None,
                    'cast_no': his_f.cast.cast_code if his_f.cast else None,
                    'spec_code': his_f.spec.spec_code if his_f.spec else None,
                    'order_num': his_f.order.order_code if his_f.order else None,
                    'order_item_num': his_f.order_item.line_item_code if his_f.order_item else None,
                    'product_type': his_f.product_type.code if his_f.product_type else None,
                    "status_change_reason": his_d.code,
                    "comment": comment,
                }
            )
    try:
        from ...contrib.message_admin.message_server import server as message_server
        strategy = message_server.MessageStrategy320()
        strategy.send_pc_320(db_session, his, background_tasks, current_user.current_mill_code)
    except ImportError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"ERROR in send_pc_320:{e}")   
    try:
        from dispatch.contrib.message_admin.message_server.trigger_sap_message import (
            handle_holdunhold,
            handle_mfgi404,
            handle_qmai264,
            QMAI264_ACTION,
            MFGI404_ACTION,
        )
        handle_holdunhold(db_session=db_session, finished_products=his, background_tasks=background_tasks)
        bulk_create_finished_product_history(db_session=db_session, finished_product_history_in=his)

        if get_mill_ops(current_user.current_mill_id) == MILLEnum.MILL410 or  get_mill_ops(current_user.current_mill_id) == MILLEnum.MILL1:
            for id in Finished_in.finished_ids:
                handle_mfgi404(db_session=db_session, finished_product_id=id, action_e=MFGI404_ACTION.BLOCK, background_tasks=background_tasks)
                handle_qmai264(db_session=db_session, finished_product_id=id, action_e=QMAI264_ACTION.REJECTED,
                               background_tasks=background_tasks)

        return finisheds
    except ImportError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/update_delete_hold", response_model=List[FinishedProductRead])
def update_delete_hold(
    *,
    background_tasks: BackgroundTasks,
    db_session: Session = Depends(get_db),
    Finished_in: FinishedProductHoldReason,
    current_user: DispatchUser = Depends(get_current_user)
):
    finisheds = db_session.query(FinishedProduct).filter(FinishedProduct.id.in_(Finished_in.finished_ids)).all()
    released_finished_products = []

    his = []

    uid = uuid.uuid4()
    try:
        from dispatch.contrib.message_admin.message_server.trigger_sap_message import (
            handle_holdunhold,
            handle_mfgi404,
            handle_qmai264,
            QMAI264_ACTION,
            MFGI404_ACTION,
        )
        for finished in finisheds:
            for hold in Finished_in.hold_list:

                # 查找 hold 是否已存在
                is_hold = (
                    db_session.query(finished_product_hold)
                    .filter(
                        finished_product_hold.c.finished_product_id == finished.id,
                        finished_product_hold.c.hold_reason_id == hold,
                    )
                    .first()
                )

                if is_hold:
                    hold_reason = hold_service.get(db_session=db_session, id=hold)
                    his.append({
                        "mill_id": finished.mill_id,
                        "change_type": FinishedProductHistoryChangeTypeEnum.UNHOLD,
                        "created_by": current_user.email,
                        "uuid": uid,
                        "code": finished.code,
                        'rolling_code': finished.rolling.rolling_code if finished.rolling else None,
                        'runout_code': finished.runout.runout_code if finished.runout else None,
                        'area_code': finished.area.code if finished.area else None,
                        'cast_no': finished.cast.cast_code if finished.cast else None,
                        'spec_code': finished.spec.spec_code if finished.spec else None,
                        'order_num': finished.order.order_code if finished.order else None,
                        'order_item_num': finished.order_item.line_item_code if finished.order_item else None,
                        'product_type': finished.product_type.code if finished.product_type else None,
                        "status_change_reason": hold_reason.code,
                        "comment": is_hold.comment,
                    })
                    db_session.execute(
                        finished_product_hold.delete().where(
                            finished_product_hold.c.finished_product_id == finished.id,
                            finished_product_hold.c.hold_reason_id == hold,
                        )
                    )
                    released_finished_products.append(finished)
                    if get_mill_ops(current_user.current_mill_id) == MILLEnum.MILL1:
                        if "TEST" in hold_reason.name.upper():
                            try:
                                from dispatch.contrib.message_admin.message_server.server import MessageStrategySRSMMTST
                                srsmmtst = MessageStrategySRSMMTST()
                                res1 = srsmmtst.send_pc_mtst(db_session=db_session, bundle_=finished, releaseFlag="Y", background_tasks=background_tasks, current_mill_code=current_user.current_mill_code)
                            except ImportError as e:
                                raise HTTPException(status_code=400, detail=str(e))
                else:
                    logger.info(f"Unable to realse finished_product {finished.code}, no hold found.")
                    continue

            if finished.rework_status != 'Rework' and (not finished.defect_reason_id) and (not finished.hold_reason):
                handle_qmai264(db_session=db_session, finished_product_id=finished.id, action_e=QMAI264_ACTION.ACCEPTED,
                               background_tasks=background_tasks)
        try:
            from ...contrib.message_admin.message_server import server as message_server
            strategy = message_server.MessageStrategy325()
            strategy.send_pc_325(db_session, released_finished_products, background_tasks, current_user.current_mill_code)
        except ImportError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"ERROR in send_pc_325:{e}")
        db_session.commit()

        if len(his)>0:
            bulk_create_finished_product_history(db_session=db_session, finished_product_history_in=his)

        if get_mill_ops(current_user.current_mill_id) == MILLEnum.MILL410 or get_mill_ops(current_user.current_mill_id) == MILLEnum.MILL1:
            for id in Finished_in.finished_ids:
                handle_mfgi404(db_session=db_session, finished_product_id=id, action_e=MFGI404_ACTION.UNBLOCK, background_tasks=background_tasks)

        return released_finished_products
    except ImportError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{id}", response_model=FinishedProductRead)
def get_finished_product(*, db_session: Session = Depends(get_db), id: int, current_user: DispatchUser = Depends(get_current_user)):

    finished_product = get(db_session=db_session, id=id)
    if not finished_product:
        raise HTTPException(status_code=400, detail="The finished product with this id does not exist.")

    if finished_product.rolling and finished_product.rolling.rolling_code:
        pro_size_code = "-".join(finished_product.rolling.rolling_code.split("-")[:-1])
        product_size = product_size_service.get_by_mill_and_code(db_session=db_session, mill_id=current_user.current_mill_id, code=pro_size_code)
        finished_product.roll_ref_code = product_size.roll_ref_code if product_size and product_size.roll_ref_code else None

    if finished_product.defect_reason_id:
        # 查询 defect_reason_id 出现的次数
        defect_reason_count = (
            db_session.query(func.count(FinishedProduct.id))
            .filter(FinishedProduct.defect_reason_id == finished_product.defect_reason_id)
            .scalar()
        )
        finished_product.defect_reason_no = defect_reason_count

    if finished_product.hold_reason:
        # 将finished_product_hold中间表的comment查出来
        for hold in finished_product.hold_reason:
            is_hold = (
                db_session.query(finished_product_hold)
                .filter(
                    finished_product_hold.c.finished_product_id == finished_product.id,
                    finished_product_hold.c.hold_reason_id == hold.id,
                )
                .first()
            )
            if is_hold:
                hold.comment = is_hold.comment
    return finished_product

@router.post("/repeat_create")
def repeat_create_finished_product(
    *,
    db_session: Session = Depends(get_db),
    finished_product_in: FinishedProductRepeatCreate,
    current_user: DispatchUser = Depends(get_current_user)
):
    cre = create_repeat(db_session=db_session, finished_product_in=finished_product_in, current_user=current_user)
    return cre


@router.post("/", response_model=FinishedProductRead)
def create_finished_product(
    *,
    db_session: Session = Depends(get_db),
    finished_product_in: FinishedProductCreate,
    current_user: DispatchUser = Depends(get_current_user)
):

    existed = get_by_code(db_session=db_session, code=finished_product_in.code)
    if existed:
        raise HTTPException(status_code=400, detail="The finished product with this code already exists.")

    finished_product_in.created_by = current_user.email
    finished_product_in.updated_by = current_user.email
    finished_product_in.created_at = datetime.now()
    finished_product_in.updated_at = datetime.now()
    created = create(db_session=db_session, finished_product_in=finished_product_in)
    return created


@router.put("/{id}", response_model=FinishedProductRead)
def update_finished_product(
    *,
    background_tasks: BackgroundTasks,
    db_session: Session = Depends(get_db),
    id: int,
    finished_product_in: FinishedProductUpdate,
    current_user: DispatchUser = Depends(get_current_user)
):

    finished_product = get(db_session=db_session, id=id)
    if not finished_product:
        raise HTTPException(status_code=400, detail="The finished product with this id does not exist.")
    t_runout = finished_product_in.t_runout
    old_t_runout = finished_product.t_runout
    c_runout = finished_product_in.c_runout
    old_c_runout = finished_product.c_runout
    try:
        from dispatch.contrib.cover.tbm.runout_services import create_test_coverage, compare_t_result, compare_c_result
        from dispatch.contrib.cover.tbm.utils import get_stone, filter_list_by_thickness
        if t_runout and t_runout != old_t_runout:
            if finished_product.status == "despatched":
                msg = "Finished product is despatched"
                logger.info(msg)
                raise HTTPException(status_code=400, detail=msg)
            if (finished_product.mult_type == 'M' or (finished_product.mult_type == 'R' and finished_product.exist_flag == 'N')):
                msg = "Finished product is multing"
                logger.info(msg)
                raise HTTPException(status_code=400, detail=msg)
            if finished_product.allocation_status in ['scrap']:
                msg = f"Finished product is {finished_product.allocation_status}"
                logger.info(msg)
                raise HTTPException(status_code=400, detail=msg)
            certificate_finished_product = certificate_finished_product_service.get_by_finished_product_id(
                db_session=db_session, finished_product_id_list=[finished_product.id])
            if certificate_finished_product:
                msg = "Certificate finished product is already exist"
                logger.info(msg)
                raise HTTPException(status_code=400, detail=msg)

            if not finished_product.spec_id:
                msg = "spec is required"
                logger.error(msg)
                raise HTTPException(status_code=400, detail=msg)
            spec_id = finished_product.spec_id

            runout = runout_service.get(db_session=db_session, runout_id=t_runout)
            old_runout = runout_service.get(db_session=db_session, runout_id=old_t_runout) if old_t_runout else runout_service.get(db_session=db_session, runout_id=finished_product.runout_id)
            product_type = runout.product_type
            old_product_type = old_runout.product_type
            if not product_type or not old_product_type:
                msg = "product_type is required"
                logger.error(msg)
                raise HTTPException(status_code=400, detail=msg)
            section_weight = product_type.dim3
            flange_thickness = product_type.flange_thickness
            old_flange_thickness = old_product_type.flange_thickness
            if not flange_thickness or not old_flange_thickness:
                msg = "flange_thickness is required"
                logger.error(msg)
                raise HTTPException(status_code=400, detail="The flange_thickness is required.")
            try:
                test_type_flag = int(finished_product.spec.test_type_flag)
            except Exception:
                test_type_flag = None
            test_sub_type = finished_product.spec.test_sub_type
            ton_limit = get_stone(test_type_flag, test_sub_type, section_weight=section_weight) * 1000

            finished_weight = finished_product.estimated_weight_kg if finished_product.estimated_weight_kg is not None else 0
            rolling_id = finished_product.runout.rolling_id if finished_product.runout and finished_product.runout.rolling_id else None
            inspector_code = []
            spec = spec_service.get(db_session=db_session, id=finished_product.spec_id)
            if spec.inspector:
                for inspector in spec.inspector:
                    inspector_code.append(inspector.code)
            sptensile_list = sptensil_service.get_by_spec_id(db_session=db_session, spec_id=spec_id)
            sptensile_list = filter_list_by_thickness(sptensile_list, old_flange_thickness, spec=spec)

            spelong_list = spelong_service.get_by_spec_id(db_session=db_session, spec_id=spec_id)
            spelong_list = filter_list_by_thickness(spelong_list, old_flange_thickness, spec=spec)

            spyield_list = spyield_service.get_by_spec_id(db_session=db_session, spec_id=spec_id)
            spyield_list = filter_list_by_thickness(spyield_list, old_flange_thickness, spec=spec)

            test_sample_list = test_sample_service.get_by_runout_id(db_session=db_session, runout_id=t_runout)
            test_sample_id = None
            t_test_sample_id_list = []
            test_coverage_service.delete_by_finished_product_id_type(db_session=db_session, finished_product_id=finished_product.id, type='tensile')
            for test_sample in test_sample_list:
                if filter_list_by_thickness(sptensile_list, flange_thickness, spec=spec) and filter_list_by_thickness(spelong_list, flange_thickness, spec=spec) and filter_list_by_thickness(spyield_list, flange_thickness, spec=spec):
                    t_total_weight_self = db_session.query(func.sum(TestCoverage.covered_weight_kg)).\
                        join(Test, Test.id == TestCoverage.test_id).\
                        filter(Test.test_sample_id == test_sample.id).\
                        filter(Test.type == 'tensile').scalar()
                    t_total_weight_self = t_total_weight_self if t_total_weight_self is not None else 0
                    if (t_total_weight_self + finished_weight) < ton_limit or finished_product.runout_id == t_runout:
                        if inspector_code:
                            test_result_tensile_dict = test_tensile_service.get_all_data_dict_of_spec_id_tbm(db_session=db_session,test_sample_ids=[test_sample.id], inspector_code=inspector_code)
                        else:
                            test_result_tensile_dict = test_tensile_service.get_all_data_dict_of_spec_id_tbm_inspector_is_none(db_session=db_session,test_sample_ids=[test_sample.id])
                        if test_result_tensile_dict:
                            test_sample_id = test_sample.id
                            t_test_sample_id_list.append(test_sample_id)
                            continue
                        else:
                            test_result_tensile_dict = test_tensile_service.get_all_data_dict_of_spec_id_tbm(db_session=db_session,test_sample_ids=[test_sample.id], inspector_code=inspector_code)
                            if test_result_tensile_dict:
                                test_sample_id = test_sample.id
                                t_test_sample_id_list.append(test_sample_id)
                                continue
            if not test_sample_id:
                msg = "No available test."
                logger.error(msg)
                raise HTTPException(status_code=400, detail=msg)
            test_runout, finished_product_in.t_result, test_sample_t_id, test_t_result_id = compare_t_result(sptensile_list,spec, t_test_sample_id_list, test_result_tensile_dict,spelong_list,spyield_list,runout,flange_thickness,finished_product)
            finished_product_in.overall_ten_result = finished_product_in.t_result
            create_test_coverage(db_session=db_session, type="tensile", test_sample_id=test_sample_t_id, finished_product=finished_product, test_type_id=test_t_result_id, spec=spec_id, runout_id=test_runout, rolling_id=rolling_id)



        elif c_runout and c_runout != old_c_runout:
            if finished_product.status == "despatched":
                msg = "Finished product is despatched"
                logger.info(msg)
                raise HTTPException(status_code=400, detail=msg)
            if (finished_product.mult_type == 'M' or (finished_product.mult_type == 'R' and finished_product.exist_flag == 'N')):
                msg = "Finished product is multing"
                logger.info(msg)
                raise HTTPException(status_code=400, detail=msg)
            if finished_product.allocation_status in ['scrap']:
                msg = f"Finished product is {finished_product.allocation_status}"
                logger.info(msg)
                raise HTTPException(status_code=400, detail=msg)
            certificate_finished_product = certificate_finished_product_service.get_by_finished_product_id(
                db_session=db_session, finished_product_id_list=[finished_product.id])
            if certificate_finished_product:
                msg = "Certificate finished product is already exist"
                logger.info(msg)
                raise HTTPException(status_code=400, detail=msg)

            if not finished_product.spec_id:
                msg = "spec is required"
                logger.error(msg)
                raise HTTPException(status_code=400, detail=msg)

            runout = runout_service.get(db_session=db_session, runout_id=c_runout)
            old_runout = runout_service.get(db_session=db_session, runout_id=old_c_runout)  if old_c_runout else runout_service.get(db_session=db_session, runout_id=finished_product.runout_id)
            product_type = runout.product_type
            old_product_type = old_runout.product_type
            spec_id = finished_product.spec_id
            if not product_type or not old_product_type:
                msg = "product_type is required"
                logger.error(msg)
                raise HTTPException(status_code=400, detail=msg)
            section_weight = product_type.dim3
            flange_thickness = product_type.flange_thickness
            old_flange_thickness = old_product_type.flange_thickness
            if not flange_thickness or not old_flange_thickness:
                msg = "flange_thickness is required"
                logger.error(msg)
                raise HTTPException(status_code=400, detail="The flange_thickness is required.")
            try:
                test_type_flag = int(finished_product.spec.test_type_flag)
            except Exception:
                test_type_flag = None
            test_sub_type = finished_product.spec.test_sub_type
            ton_limit = get_stone(test_type_flag, test_sub_type, section_weight=section_weight) * 1000
            spec = spec_service.get(db_session=db_session, id=finished_product.spec_id)

            spimpact_list = spimpact_service.get_by_spec_id(db_session=db_session, spec_id=spec_id)
            spimpact_list = filter_list_by_thickness(spimpact_list, flange_thickness, spec=spec)
            inspector_code = []
            if spec.inspector:
                for inspector in spec.inspector:
                    inspector_code.append(inspector.code)
            finished_weight = finished_product.estimated_weight_kg if finished_product.estimated_weight_kg is not None else 0
            rolling_id = finished_product.runout.rolling_id if finished_product.runout and finished_product.runout.rolling_id else None
            test_sample_list = test_sample_service.get_by_runout_id(db_session=db_session, runout_id=c_runout)
            test_sample_id = None
            c_test_sample_id_list = []

            test_coverage_service.delete_by_finished_product_id_type(db_session=db_session, finished_product_id=finished_product.id, type='impact')
            for test_sample in test_sample_list:
                if filter_list_by_thickness(spimpact_list, flange_thickness, spec=spec):
                    c_total_weight_self = db_session.query(func.sum(TestCoverage.covered_weight_kg)).\
                        join(Test, Test.id == TestCoverage.test_id).\
                        filter(Test.test_sample_id == test_sample.id).\
                        filter(Test.type == 'impact').scalar()
                    c_total_weight_self = c_total_weight_self if c_total_weight_self is not None else 0
                    if (c_total_weight_self + finished_weight) < ton_limit or finished_product.runout_id == c_runout:
                        if inspector_code:
                            test_result_impact_dict = test_impact_service.get_all_data_dict_of_spec_id_tbm(db_session=db_session,test_sample_ids=[test_sample.id], inspector_code=inspector_code)
                        else:
                            test_result_impact_dict = test_impact_service.get_all_data_dict_of_spec_id_tbm_inspector_is_none(db_session=db_session,test_sample_ids=[test_sample.id])
                        if test_result_impact_dict:
                            test_sample_id = test_sample.id
                            c_test_sample_id_list.append(test_sample_id)
                            break
                        else:
                            test_result_impact_dict = test_impact_service.get_all_data_dict_of_spec_id_tbm(db_session=db_session,test_sample_ids=[test_sample.id], inspector_code=inspector_code)
                            if test_result_impact_dict:
                                test_sample_id = test_sample.id
                                c_test_sample_id_list.append(test_sample_id)
                                break
            if not test_sample_id:
                msg = "No available test."
                logger.error(msg)
                raise HTTPException(status_code=400, detail=msg)
            test_result_impact_dict = test_impact_service.get_all_data_dict_of_spec_id_tbm(db_session=db_session,test_sample_ids=c_test_sample_id_list, inspector_code=inspector_code)
            test_runout, finished_product_in.c_result, test_sample_c_id, test_c_result_id = compare_c_result(test_result_impact_dict,spec, list(test_result_impact_dict.keys()), spimpact_list, runout, flange_thickness, finished_product, rolling_id, db_session)
            finished_product_in.overall_imp_result = finished_product_in.c_result
    except ImportError as e:
        raise HTTPException(status_code=400, detail=str(e))
    finished_product_in.updated_by = current_user.email
    finished_product_in.updated_at = datetime.now()
    finished_product_updated = update_finished(
        db_session=db_session,
        finished_product=finished_product,
        finished_product_in=finished_product_in,
    )

    if get_mill_ops(current_user.current_mill_id) == MILLEnum.MILL1:
        finished_product_after = get(db_session=db_session, id=id)
        # if finished_product_before.quantity != finished_product_after.quantity:
        try:
            from dispatch.contrib.message_admin.message_server.server import MessageStrategySRSMM160, MessageStrategySRSMM642
            srsmm160 = MessageStrategySRSMM160()
            bundles = []
            bundles.append(finished_product_after)
            res1 = srsmm160.send_pc_m160(db_session=db_session, bundles_=bundles, background_tasks=background_tasks, current_mill_code=current_user.current_mill_code)
                #finished_product_updated.srsmmonesixzero = res1
            #if finished_product_before.length_mm != finished_product_after.length_mm:
            srsmm642 = MessageStrategySRSMM642()
            res2 = srsmm642.send_pc_m642(db_session=db_session, bundle_=finished_product_after, background_tasks=background_tasks, current_mill_code=current_user.current_mill_code)
        except ImportError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"ERROR in send_pc_m160 or m642: {str(e)}")
        #finished_product_updated.srsmmsixfourtwo = res2

    return finished_product_updated

@router.delete("/{id}", response_model=FinishedProductRead)
def delete_finished_product(*, db_session: Session = Depends(get_db), id: int, remove_reason: str = Body(..., embed=True)):

    finished_product = get(db_session=db_session, id=id)
    if not finished_product:
        raise HTTPException(status_code=400, detail="The finished product with this id does not exist.")

    # 软删除：记录删除原因，并将状态标记为删除
    finished_product.remove_reason = remove_reason
    finished_product.is_deleted = 1
    finished_product.updated_at = datetime.now()  # 更新时间
    db_session.commit()

    return finished_product




@router.post("/get_by_search_dict", response_model=FinishedProductRead)
def get_by_search_dict(*, db_session: Session = Depends(get_db), search_dict: FinishedProductBySearch):

    finished_product = get_by_search(db_session=db_session, search_dict=search_dict)

    if not finished_product:
        raise HTTPException(status_code=400, detail="No relevant records found.")

    return finished_product

@router.post("/allocate_change_type",response_model= List[FinishedProductRead])
def allocate_change_type_view(*, db_session: Session = Depends(get_db), finished_product_in: FinishedProductAllocate, current_user: DispatchUser = Depends(get_current_user)):

    finished_product = allocate_change_type(db_session=db_session, finished_product_in=finished_product_in, current_user=current_user)

    return finished_product


@router.get("/item/stock_type")
def get_code(db_session: Session = Depends(get_db)):
    # print(id)
    ls = get_finish_product_codes(db_session=db_session)
    return ls


@router.get("/covering/{ids}", response_model=RegradePagination)
def get_covering_by_runout(*, ids: str, common: dict = Depends(common_parameters)):
    # 检查ids列表中的元素是否都一致
    ids_list = [int(i) for i in ids.split(',') if i and i.strip().isdigit()]
    if len(set(ids_list)) > 1:
        raise HTTPException(status_code=400, detail="The 'ids' parameters passed in are inconsistent. Please ensure that all 'id' values are the same.")
    elif len(set(ids_list)) < 1:
        raise HTTPException(status_code=400, detail="Runout could not be found.")

    value_list = list(set(ids_list))
    # value_list.extend([[8, 9],[8, 9]])
    # common["filter_type"] = "and"
    # common["fields"] = ["runout_id", "tensile_score", "impact_score"]
    # common["ops"] = ["==", "in", "in"]
    # common["values"] = value_list

    common["filter_type"] = "and"
    common["fields"] = ["runout_id"]
    common["ops"] = ["=="]
    common["values"] = value_list
    if not common["sort_by"] or common["sort_by"] == "test_result":
        common["sort_by"] = ["tensile_score", "impact_score"]
        common["descending"] = [True, True]
    if common["query_str"]:
        common["fields"].append("spec.spec_code")
        common["ops"].append("like")
        common["values"].append(f"%{common['query_str']}%")

    covering = search_filter_sort_paginate(model="CoverEndUse", **common)
    covering = get_covering(db_session=common['db_session'], runout_id=ids_list[0], covering=covering)
    return covering


@router.post("/force_regrade")
def batch_update_force_regrade(
    *,
    db_session: Session = Depends(get_db),
    finished_products_in: List[RegradeUpdate],
    current_user: DispatchUser = Depends(get_current_user)
):
    update_at = datetime.now()
    finished_products_list = []
    for finished_product_in in finished_products_in:
        finished_product_in.updated_by = current_user.email
        finished_product_in.updated_at = update_at
        if finished_product_in.regrade_reason:
            finished_product_in.regrade_reason_id = finished_product_in.regrade_reason.get('id')
            finished_product_in.regrade_reason_code = finished_product_in.regrade_reason.get('code')
        else:
            finished_product_in.regrade_reason_id = None
        finished_products_list.append(finished_product_in.model_dump(exclude={"regrade_reason", "created_at", "created_by", "is_deleted", "flex_form_data"}))
    return batch_update(db_session=db_session, body=finished_products_list)


@router.post("/regrade")
def batch_update_regrade(
    *,
    db_session: Session = Depends(get_db),
    finished_products_in: List[RegradeUpdate],
    current_user: DispatchUser = Depends(get_current_user)
):
    update_at = datetime.now()
    finished_products_list = []
    for finished_product_in in finished_products_in:
        runout_id = get(db_session=db_session, id=finished_product_in.id).runout_id
        spec_id = finished_product_in.spec_id
        if not db_session.query(CoverEndUse).filter(
                    CoverEndUse.spec_id == spec_id,
                    CoverEndUse.runout_id == runout_id).first():
            raise HTTPException(status_code=400, detail="This spec does not conform to covering")

        finished_product_in.updated_by = current_user.email
        finished_product_in.updated_at = update_at
        if finished_product_in.regrade_reason:
            finished_product_in.regrade_reason_id = finished_product_in.regrade_reason.get('id')
            finished_product_in.regrade_reason_code = finished_product_in.regrade_reason.get('code')
        else:
            finished_product_in.regrade_reason_id = None
        finished_products_list.append(finished_product_in.model_dump(exclude={"regrade_reason", "created_at", "created_by", "is_deleted", "flex_form_data"}))
    return batch_update(db_session=db_session, body=finished_products_list)


@router.post("/move_to")
def move_to(data: dict, background_tasks: BackgroundTasks, db_session: Session = Depends(get_db), current_user: DispatchUser = Depends(get_current_user)):
    # print(data)
    move_to_product(data=data, db_session=db_session,current_user=current_user, background_tasks=background_tasks)
    return True


@router.post("/reserve")
def update_reserve(data: dict, db_session: Session = Depends(get_db), current_user: DispatchUser = Depends(get_current_user)):
    id_list = data["list"]
    order_item_id = data["order_item_id"]
    update_reserve_rework(id_list=id_list, db_session=db_session, current_user=current_user, order_item_id=order_item_id)
    return True


@router.get("/reserve/", response_model=FinishedProductPagination)
def reserve_finished_products(*,speccode: str = Query(None),order_length: int = Query(None),order_item: str = Query(None), db_session: Session = Depends(get_db), common: dict = Depends(common_parameters)):
    # 为 reserved_order_item 创建别名
    ReservedOrderItem = aliased(OrderItem)

    query = db_session.query(FinishedProduct).outerjoin(Spec, FinishedProduct.spec_id == Spec.id
    ).outerjoin(Cast, FinishedProduct.cast_id == Cast.id
    ).outerjoin(Runout, FinishedProduct.runout_id == Runout.id
    ).outerjoin(Area, FinishedProduct.area_id == Area.id
    ).outerjoin(Order, FinishedProduct.order_id == Order.id
    ).outerjoin(OrderItem, FinishedProduct.order_item_id == OrderItem.id
    ).outerjoin(ReservedOrderItem, FinishedProduct.reserved_order_item_id == ReservedOrderItem.id
    ).outerjoin(ProductType, FinishedProduct.product_type_id == ProductType.id
    ).outerjoin(CoverEndUse,and_(FinishedProduct.spec_id ==
                                 CoverEndUse.spec_id, FinishedProduct.runout_id == CoverEndUse.runout_id)
    )

    if order_item:
        query = query.filter(or_(FinishedProduct.reserved_order_item_id == order_item, FinishedProduct.reserved_order_item_id.is_(None)))
    query = query.filter(FinishedProduct.order_item_id.is_(None))

    if order_length:
        query = query.filter(FinishedProduct.length_mm >= order_length)

    if common.get('sort_by') and 'reserved_order_item.line_item_code' in common['sort_by']:
        index = common['sort_by'].index('reserved_order_item.line_item_code')
        is_desc = common.get('descending', [])[index] if common.get('descending') else False

        # 修改排序规则，使用 nullslast 确保 NULL 值排在最后
        if is_desc:
            query = query.order_by(nullslast(desc(ReservedOrderItem.line_item_code)))
        else:
            query = query.order_by(nullslast(ReservedOrderItem.line_item_code))

        # 从排序列表中移除已处理的排序
        common['sort_by'].pop(index)
        if common.get('descending'):
            common['descending'].pop(index)

    query = query.filter(~FinishedProduct.advice.any())

    common['query'] = query
    finished_product = search_filter_sort_paginate(model="FinishedProduct", **common)
    finished_data = finished_product["items"]
    speccode_filter = speccode is not None
    if finished_data:
        for finished in finished_data:
            # 默认值统一初始化
            finished.t_result = 0
            finished.c_result = 0

            if not speccode_filter:
                continue

            runout_id = finished.runout_id
            if not runout_id:
                continue

            spec = db_session.query(Spec).filter(
                Spec.spec_code == speccode,
                Spec.mill_id == finished.mill_id
            ).first()
            if not spec:
                continue

            result = db_session.query(CoverEndUse).filter(
                CoverEndUse.spec_id == spec.id,
                CoverEndUse.runout_id == runout_id
            ).first()

            if result:
                finished.t_result = result.tensile_score
                finished.c_result = result.impact_score
    return finished_product

@router.post("/get_compliance")
def get_compliance(*,db_session: Session = Depends(get_db),current_user: DispatchUser = Depends(get_current_user),data: GetCompliance):
    # Corvering

    test_result = None
    if data.spec_code:
        spec_id = spec_service.get_by_code_m(db_session=db_session, code=data.spec_code, mill_id=current_user.current_mill_id)
    test_result_data = db_session.query(CoverEndUse).filter(CoverEndUse.spec_id == spec_id.id,
                                                                   CoverEndUse.runout_id == data.runout_id).first()
    if test_result_data:
        # test_result = int(f"{test_result_data.tensile_score}{test_result_data.impact_score}")
        tensile_score = test_result_data.tensile_score if test_result_data.tensile_score else 0
        impact_score = test_result_data.impact_score if test_result_data.impact_score else 0
        test_result = int(f"{tensile_score}{impact_score}")
    
    return test_result


@router.post("/defects")
def defect(data: dict, background_tasks: BackgroundTasks, db_session: Session = Depends(get_db)):
    create_defects(db_session=db_session,data=data)
    try:
        from dispatch.contrib.message_admin.message_server.trigger_sap_message import (
            MFGI182_ACTION,
            handle_qmai264,
            handle_mfgi182,
            QMAI264_ACTION,
        )
        if data.get('codes'):
            finished_products = get_by_codes(db_session=db_session, codes=data.get('codes'))
            for finished_product in finished_products:
                handle_qmai264(db_session=db_session, finished_product_id=finished_product.id, action_e=QMAI264_ACTION.REJECTED,
                       background_tasks=background_tasks)
                if finished_product.defect_quantity > 0 and finished_product.defect_quantity != finished_product.quantity:
                    handle_mfgi182(db_session,
                                   finished_product_id=finished_product.id,
                                   action_e=MFGI182_ACTION.REWORK,
                                   background_tasks=background_tasks,
                                   defect_report=True
                                   )
        return True
    except ImportError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/load_create", response_model=FinishedProductLoadRead)
def finished_product_create_load(*, db_session: Session = Depends(get_db), finished_product_in: FinishedProductCreateLoad, current_user: DispatchUser = Depends(get_current_user)):

    finished_product_in.created_by = current_user.email
    finished_product_in.updated_by = current_user.email
    finished_product_in.updated_at = datetime.now()
    return create_by_load(db_session=db_session, finished_product_in=finished_product_in, current_user=current_user)


@router.post("/retrieve")
def retrieve_finished_products(*, db_session: Session = Depends(get_db), current_user: DispatchUser = Depends(get_current_user),data:RetrieveUpdate):
    his = []
    uid = uuid.uuid4()
    for fid in data.finished_ids:
        finished_product = get(db_session=db_session, id=fid)
        if finished_product:
            finished_product.status = FinishedProductStatusEnum.CREATED
            finished_product.updated_at = datetime.now()
            finished_product.updated_by = current_user.email
            finished_product.comment = data.comment

        his.append({
            "uuid": uid,
            "mill_id": finished_product.mill_id,
            "change_type": FinishedProductHistoryChangeTypeEnum.RETRIEVE,
            "created_by": current_user.email,
            "code": finished_product.code,
            'rolling_code': finished_product.rolling.rolling_code if finished_product.rolling else None,
            'runout_code': finished_product.runout.runout_code if finished_product.runout else None,
            'area_code': finished_product.area.code if finished_product.area else None,
            'cast_no': finished_product.cast.cast_code if finished_product.cast else None,
            'spec_code': finished_product.spec.spec_code if finished_product.spec else None,
            'order_num': finished_product.order.order_code if finished_product.order else None,
            'order_item_num': finished_product.order_item.line_item_code if finished_product.order_item else None,
            'product_type': finished_product.product_type.code if finished_product.product_type else None,
            "comment": data.comment,
            "status": 'current',
        })
    db_session.commit()
    bulk_create_finished_product_history(db_session=db_session, finished_product_history_in=his)
    return True

@router.post("/archieve")
def retrieve_finished_products(*, db_session: Session = Depends(get_db), current_user: DispatchUser = Depends(get_current_user),data:RetrieveUpdate):
    his = []
    uid = uuid.uuid4()
    for fid in data.finished_ids:
        finished_product = get(db_session=db_session, id=fid)
        if finished_product:
            finished_product.status = FinishedProductStatusEnum.ARCHIVED
            finished_product.updated_at = datetime.now()
            finished_product.updated_by = current_user.email
            finished_product.comment = data.comment

        his.append({
            "uuid": uid,
            "mill_id": finished_product.mill_id,
            "change_type": FinishedProductHistoryChangeTypeEnum.RETRIEVE,
            "created_by": current_user.email,
            "code": finished_product.code,
            'rolling_code': finished_product.rolling.rolling_code if finished_product.rolling else None,
            'runout_code': finished_product.runout.runout_code if finished_product.runout else None,
            'area_code': finished_product.area.code if finished_product.area else None,
            'cast_no': finished_product.cast.cast_code if finished_product.cast else None,
            'spec_code': finished_product.spec.spec_code if finished_product.spec else None,
            'order_num': finished_product.order.order_code if finished_product.order else None,
            'order_item_num': finished_product.order_item.line_item_code if finished_product.order_item else None,
            'product_type': finished_product.product_type.code if finished_product.product_type else None,
            "comment": data.comment,
            "status": 'archieve',
        })
    db_session.commit()
    bulk_create_finished_product_history(db_session=db_session, finished_product_history_in=his)
    return True

@router.post("/return")
def return_finished_products(*, db_session: Session = Depends(get_db), current_user: DispatchUser = Depends(get_current_user),data:ReturnUpdate):
    return return_finished(data=data, db_session=db_session, current_user=current_user)

@router.post("/combine", response_model=FinishedProductRead)
def create_finished_product(
    *,
    background_tasks: BackgroundTasks,
    db_session: Session = Depends(get_db),
    finished_product_in: FinishedProductCreate,
    current_user: DispatchUser = Depends(get_current_user)
):

    total_quantity = 0
    total_kg = 0
    total_defect_quantity = 0
    # total_defect_kg = 0
    outcome_kg = 0
    finished_ids = []
    rolling_ids= []
    temp_code = "Code_" + str(uuid.uuid4())[:8]

    if len(finished_product_in.codes) != 1:
        for item in finished_product_in.codes:
            existed_update = get_by_code(db_session=db_session, code=item)
            if existed_update:
                rolling_ids.append(existed_update.rolling_id)
                finished_ids.append(existed_update.id)
                quantity = existed_update.quantity if existed_update.quantity else 0
                kg = float(existed_update.kg if existed_update.kg else 0) * quantity
                defect_quantity = existed_update.defect_quantity if existed_update.defect_quantity else 0
                # defect_kg = (defect_quantity / (existed_update.quantity if existed_update.quantity else 1)) * kg

                total_quantity += quantity
                total_kg += kg
                total_defect_quantity += defect_quantity
                # total_defect_kg += defect_kg
                outcome_kg = round(total_kg / total_quantity if total_quantity else 1 , 2)
                existed_update.status = "archieve"
                db_session.commit()

    finished_product_in.quantity = total_quantity
    finished_product_in.kg = str(outcome_kg)
    finished_product_in.defect_quantity = total_defect_quantity
    finished_product_in.created_by = current_user.email
    finished_product_in.updated_by = current_user.email
    finished_product_in.created_at = datetime.now()
    finished_product_in.updated_at = datetime.now()
    if not finished_product_in.code:
        finished_product_in.code = temp_code
    created = create(db_session=db_session, finished_product_in=finished_product_in)
    if finished_product_in.code == temp_code:
        edit_data = update_finished_product_data(db_session=db_session, finished_product_id=created.id, rolling_ids=rolling_ids, temp_code=temp_code)
    for item_id in finished_ids:
        association_data = {
            "finished_product_id": created.id,
            "finished_product_association_id": item_id
        }
        db_session.execute(finished_product_association.insert().values(association_data))
    db_session.commit()
    if get_mill_ops(current_user.current_mill_id) == MILLEnum.MILL1:
        parent_bundles = []
        for code in finished_product_in.codes:
            bundle = get_by_code(db_session=db_session, code=code)
            parent_bundles.append(bundle)
        try:
            from dispatch.contrib.message_admin.message_server.server import MessageStrategySRSMM480
            srsmm480 = MessageStrategySRSMM480()
            res2 = srsmm480.send_pc_m480(db_session=db_session, parentBundles_=parent_bundles, childBundles_=[created],background_tasks=background_tasks, current_mill_code=current_user.current_mill_code)
        except ImportError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"ERROR in send_pc_m480: {str(e)}")
    return created

@router.post("/split")
def update_split(background_tasks: BackgroundTasks, data: dict, db_session: Session = Depends(get_db),current_user: DispatchUser = Depends(get_current_user)):

    finished_id = data.get("id")
    split_list = data.get("split", [])
    defect_reason_no = 0
    if not finished_id or not split_list:
        raise HTTPException(status_code=400, detail="Invalid input data")

    finished_product = get(db_session=db_session, id=finished_id)
    if not finished_product:
        raise HTTPException(status_code=400, detail="The finished product with this id does not exist.")

    if finished_product.defect_reason_id:
        # 查询 defect_reason_id 出现的次数
        defect_reason_count = (
            db_session.query(func.count(FinishedProduct.id))
            .filter(FinishedProduct.defect_reason_id == finished_product.defect_reason_id)
            .scalar()
        )
        defect_reason_no = defect_reason_count
    quantity = (finished_product.quantity or 0) - defect_reason_no
    if quantity < 0:
        raise HTTPException(status_code=400, detail="Available quantity is negative after considering defect reasons.")
    split_quantity = sum(split.get("bars", 0) for split in split_list)
    if split_quantity > quantity:
        raise HTTPException(status_code=400, detail="Split quantity exceeds available quantity.")
    finished_product_dict = {k: v for k, v in finished_product.__dict__.items() if k not in ['id', 'code', 'defect_reason_id', 'defect_quantity']}
    repeat_code = []
    new_finished_products = []

    for split in split_list:
        split_code = split.get("code")
        # 检查数据库中是否已经存在相同的 code
        existing_product = db_session.query(FinishedProduct).filter(FinishedProduct.code == split_code).first()
        if existing_product:
            repeat_code.append(split_code)
            continue

        finished_product_dict.update({"code": split_code, "quantity": split.get("bars"),
                                      "updated_at": datetime.now(), "updated_by": current_user.email,
                                      "created_at": datetime.now(), "created_by": current_user.email})
        finished_product_in = FinishedProductCreate(**finished_product_dict)
        new_finished_products.append(finished_product_in)  # 收集需要创建的对象

    if repeat_code:
        raise HTTPException(status_code=400, detail=f"Duplicate codes found: {', '.join(repeat_code)}")

    split_bundle_list = []
    # 创建新的 FinishedProduct 对象
    for finished_product_in in new_finished_products:
        split_bundles = create(db_session=db_session, finished_product_in=finished_product_in)
        split_bundle_list.append(split_bundles)
        # 创建中间表数据
        association_data = {
            "finished_product_id": split_bundles.id,
            "finished_product_association_id": finished_id
        }
        db_session.execute(finished_product_association.insert().values(association_data))

    # 更新原始的 FinishedProduct 对象
    finished_product.quantity = quantity - split_quantity
    if finished_product.quantity == 0:
        finished_product.is_deleted = 1
    finished_product.updated_at = datetime.now()
    finished_product.updated_by = current_user.email
    db_session.add(finished_product)
    db_session.commit()
    if get_mill_ops(current_user.current_mill_id) == MILLEnum.MILL1:
        try:
            from dispatch.contrib.message_admin.message_server.server import MessageStrategySRSMM480
            srsmm480 = MessageStrategySRSMM480()
            res2 = srsmm480.send_pc_m480(db_session=db_session, parentBundles_=[finished_product], childBundles_=split_bundle_list, background_tasks=background_tasks, current_mill_code=current_user.current_mill_code)
        except ImportError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"ERROR in send_pc_m480: {str(e)}")
    return True

@router.post("/comments/rebundle")
def update_rebundle(background_tasks: BackgroundTasks, data: dict, db_session: Session = Depends(get_db),current_user: DispatchUser = Depends(get_current_user)):
    rolling_ids = data.get('rolling_ids')
    finished_ids = data.get('finished_ids')
    runout_id = data.get("runout_id")
    type = data.get("type")
    cast_id = data.get("cast_id")
    status = data.get("status")
    exist_flag = data.get("exist_flag")
    allocate_status = data.get("allocate_status")
    estimated_length_mm = data.get("estimated_length_mm")
    width_mm = data.get("width_mm")
    mill_id = data.get("mill_id")
    estimated_weight_kg = data.get("estimated_weight_kg")
    product_type_id = data.get('product_type_id')
    rolling_id = data.get('rolling_id')
    other_code = data.get("other_code")
    datas = data.get('rebundel')
    temp_code = "Code_" + str(uuid.uuid4())[:8]
    update_quantity = data.get("update_quantity")
    newLength = data.get("new_length")
    new_finished_products = []
    new_finished_product_ids = []
    spec_id = None
    quality_code = None
    for items in datas:
        raw_quantity = items.get("quantity")
        quantity = raw_quantity if raw_quantity else "0"
        comment = items.get("comment")
        length = items.get("length")
        code = items.get("code")
        order_items = items.get("order_items")
        order_item = items.get("order_item")
        if other_code:
            finished_code = db_session.query(FinishedProduct).filter(FinishedProduct.code.in_(other_code)).first()
            spec_id = finished_code.spec_id
            quality_code = finished_code.quality_code
        if code is not None:
            if other_code and isinstance(other_code, list) and code in other_code:
                other_code.remove(code)
        else:
            if other_code:
                rebundle_update(db_session=db_session, other_code=other_code)
        if update_quantity == 1:
            data_product = db_session.query(FinishedProduct).filter(FinishedProduct.code == code).first()
            products = db_session.query(FinishedProduct).filter(FinishedProduct.code.in_(other_code)).first()
            if products is not None:
                if data_product.length_mm != length:
                    if data_product.rework_type is not None:
                        rework_type_list = data_product.rework_type.split(',')
                        if "CUT" not in rework_type_list:
                            rework_type_list.append("CUT")
                            data_product.rework_type = rework_type_list
                    else:
                        rework_type_list = ["CUT"]
                        data_product.rework_type = rework_type_list
                    data_product.rework_type = ",".join(rework_type_list)
                    db_session.commit()
                total_length = int(data_product.quantity) * data_product.length_mm
                if newLength > total_length:
                    data_length = newLength - total_length
                    if products is not None:
                        product_length = products.length_mm
                        if product_length > 0:
                            reduction_factor = data_length / product_length
                            reduction_quantity = math.ceil(reduction_factor) if reduction_factor < 2 else math.ceil(reduction_factor)
                            data_quantity = max(0, products.quantity - reduction_quantity)
                            data_estimated_weight_kg = round(int(data_quantity) * estimated_weight_kg, 0)
                            products.quantity = data_quantity
                            products.estimated_weight_kg = data_estimated_weight_kg
                            db_session.commit()
        estimated_weight_kgs = float(estimated_length_mm) * float(length)
        total_estimated_weight_kg = round(int(quantity) * estimated_weight_kgs, 1)
        if code and order_item:
            existing_product = db_session.query(FinishedProduct).filter(FinishedProduct.code == code).first()
            if existing_product.status == "despatched":
                raise HTTPException(status_code=400, detail="This product has already been despatched and cannot be modified. Please contact the technical team for further assistance.")
            if existing_product.length_mm != length:
                if existing_product.rework_type is not None:
                    rework_type_list = existing_product.rework_type.split(',')
                    if "CUT" not in rework_type_list:
                        rework_type_list.append("CUT")
                else:
                    rework_type_list = ["CUT"]
                existing_product.rework_type = ",".join(rework_type_list)
            if existing_product:
                existing_product.order_item_id = order_items
                existing_product.quantity = quantity
                existing_product.estimated_weight_kg = total_estimated_weight_kg
                existing_product.comment = comment
                existing_product.length_mm = length
                existing_product.updated_at = datetime.utcnow()
                existing_product.updated_by = current_user.email
                db_session.commit()

        else:
            finished_product_dict = {
                "quantity": quantity,
                "comment": comment,
                "code": temp_code,
                "runout_id": runout_id,
                "product_type_id": product_type_id,
                "mill_id": mill_id,
                "status": status,
                "length_mm": length,
                "width_mm": width_mm,
                "estimated_weight_kg": total_estimated_weight_kg,
                "cast_id": cast_id,
                "order_item_id": order_items,
                "spec_id": spec_id,
                "quality_code": quality_code,
                "type": type,
                "exist_flag": exist_flag,
                "rolling_id": rolling_id,
                "allocation_status": allocate_status,
                "updated_at": datetime.now(),
                "updated_by": current_user.email,
                "created_at": current_user.created_at,
                "created_by": current_user.email
            }
            finished_product_in = FinishedProductCreate(**finished_product_dict)
            new_finished_products.append(finished_product_in)
    for finished_product_in in new_finished_products:
        split_bundles = create(db_session=db_session, finished_product_in=finished_product_in)
        if split_bundles:
            for item_id in finished_ids:
                association_data = {
                    "finished_product_id": split_bundles.id,
                    "finished_product_association_id": item_id
                }
                db_session.execute(finished_product_association.insert().values(association_data))
            db_session.commit()
        if split_bundles.code == temp_code:
            fp = update_finished_product_data(db_session=db_session, finished_product_id=split_bundles.id,
                                         rolling_ids=rolling_ids, temp_code=temp_code)
            finished_product_history_data = (db_session.query(FinishedProductHistory)
                                             .filter(FinishedProductHistory.code == temp_code).first())
            if finished_product_history_data:
                finished_product_history_data.code = fp.code
                db_session.commit()
            new_finished_product_ids.append(fp.id)
    try:
        check_and_trigger_rework_rebundle(db_session=db_session, background_tasks=background_tasks, org_fp_ids=finished_ids, new_fp_ids=new_finished_product_ids)
    except:
        logger.exception('Error preparing MFGI404 Rework message')
    return new_finished_products

@router.get("/store/code", response_model=List[str])
def get_store_code(*, db_session: Session = Depends(get_db)):
    store_codes = get_store_codes(db_session=db_session)
    if not store_codes:
        return []
    return [str(code) for code in store_codes]

@router.post("/cut_test_sample/{source}", response_model=List[FinishedProductRead])
def cut_sample(
    *,
    background_tasks: BackgroundTasks,
    db_session: Session = Depends(get_db),
    Finished_in: CutTestSample,
    source: str,
    current_user: DispatchUser = Depends(get_current_user)
):  
    ##  先把finished_ids 进行排序 
    sorted_finished_ids = sorted(Finished_in.finished_ids)
    finisheds = db_session.query(FinishedProduct).filter(FinishedProduct.id.in_(sorted_finished_ids)).all()
    finisheds.sort(key=lambda x: x.code)

    test_sample_data = []
    hold_data=[]
    add_hold = False
    updated_by = current_user.email
    ## 先根据cut source不同 给出不同的值
    if source == 'PartSawn':
        reason_code = 'MT'
        source = 'TF84-Part-Sawn'
        add_hold = True
    elif source == 'Reserve':
        reason_code = 'MT'
        source = 'TD17-Reserve'
    elif source == 'Allocate':
        reason_code = 'UG'
        source = 'TE13-Allocate'

    for finished in finisheds:

        # 查找 test sample 是否已存在 (按照runout / finished product)
        is_sample = (
            db_session.query(TestSample)
            .filter(
                TestSample.runout_id == finished.runout_id,
                or_(TestSample.status == 'A', TestSample.status == 'C')
            )
            .first()
        )
        if is_sample:
            raise HTTPException(status_code=400, detail="Sample is already requested, please request tech team to allocate directly")

        else:

            runout = runout_service.get(db_session=db_session, runout_id= finished.runout_id)
            stash_comment=finished.comment 
            test_sample_data.append(
                {
                    "runout_id": finished.runout_id if finished.runout_id else None,
                    "test_sample_code":runout.runout_code if runout and runout.runout_code else None,
                    "test_sample_part":"F",
                    "product_name": runout.product_code if runout and runout.product_code else (finished.product_type.name if finished.product_type else None),
                    "concast_code":runout.concast_code if runout and runout.concast_code else None,
                    "retest": 0 ,
                    "orientation": "L",
                    "cast_id": finished.cast_id if finished.cast_id else None,   ## 或者从关联的runout 取cast id
                    "spec_id": finished.spec_id if finished.spec_id else None,
                    "rolling_id": runout.rolling_id if runout.rolling_id else None,
                    "mill_id": finished.mill_id if finished.mill_id else None,
                    "area_id": finished.area_id if finished.area_id else None,
                    "size_mm": finished.cut_sample_length_mm if finished.cut_sample_length_mm else 500,
                    "cut_code": finished.cut_code if finished.cut_code else None,
                    "sample_thickness": finished.thickness_mm if finished.thickness_mm else None,
                    "status":"A",
                    "reason_code":reason_code,
                    "source": source,
                    "comment":(stash_comment if stash_comment else "") + "",
                    "finished_product_id": finished.id,
                    "updated_by": updated_by,
                }
            )           

            if len(test_sample_data) > 0:
                # db_session.execute(TestSample.insert(), test_sample_data)
                try:
                    print("Executing insert with data:", test_sample_data)  # 打印要插入的数据
                    db_session.bulk_insert_mappings(TestSample, test_sample_data)
                    print("Insert executed successfully.")  # 插入操作成功的信息
                except Exception as e:
                    print("Error occurred during insert:", e)  # 捕获插入操作中的异常

            if hasattr(finished, 'length_mm') and hasattr(finished, 'orig_length_mm'):
                finished.orig_length_mm = finished.length_mm
                # 将 length_mm 的值减去 500
                finished.length_mm -= 500
                db_session.add(finished)

            db_session.commit()
            
            ###  If source ==PartSawn: create test sample then finished product add hold
            if add_hold:
                hold_reason = hold_service.get_by_code(db_session=db_session, code="PartSawn")
                if not hold_reason:
                    raise HTTPException(status_code=400, detail="Can't hold. Reason PartSawn not found")

                hold_data.append(
                            {
                                "finished_product_id": finished.id,
                                "hold_reason_id": hold_reason.id,
                                "mill_id": hold_reason.mill_id if hold_reason.mill_id else None,
                                "hold_by": updated_by,
                            }
                        )
                    
                if len(hold_data) > 0:
                    db_session.execute(finished_product_hold.insert(), hold_data)
                db_session.commit()

    return finisheds



@router.post("/label_print", response_model=MessageData)
def label_print(data: LabelPrint, background_tasks: BackgroundTasks, db_session: Session = Depends(get_db), current_user: DispatchUser = Depends(get_current_user)):
    print('2222222222222222222333', data)
    finished_product = get(db_session=db_session, id=data.finished_product_id)
    try:
        from dispatch.contrib.message_admin.message_server.server import MessageStrategySRSMM132
        m132 = MessageStrategySRSMM132()
        message = m132.send_pc_m132(db_session=db_session, bundle_=finished_product, printer=data.printer,
                                    format=data.format, copies=data.copies, transaction_code=data.transaction_code,
                                    background_tasks=background_tasks, current_mill_code=current_user.current_mill_code)
    except ImportError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"ERROR in send_pc_m132:{e}")
    return message

@router.get("/get_max_cut_code/{runout_id}")
def get_cut_code(*, runout_id: int, db_session: Session = Depends(get_db)):
    ''' 获取下一个code 和 cut code '''
    runout_code, cut_code = get_max_cut_code(db_session = db_session, runout_id = runout_id)
    cut_code = chr(ord(cut_code) + 1) if cut_code != None else "A"
    if runout_code == None:
        runout_data = db_session.query(Runout.runout_code).filter(Runout.id == runout_id).first()
        runout_code = runout_data.runout_code if runout_data else None
    return {
        "runout_code": runout_code,
        "cut_code": cut_code
    }

@router.post("/update_odoo/{fp_id}")
def post_update_odoo(*, fp_id: int, db_session: Session = Depends(get_db)):
    uid = odoo_authenticate()
    if uid:
        fp = get(db_session=db_session, id=fp_id)
        if not fp:
            raise HTTPException(status_code=400, detail="the finished product not found")
        elif not fp.order_item:
            raise HTTPException(status_code=400, detail="the finished product has not order item")

        data = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "service": "object",
                "method": "execute",
                "args": [
                    ODOO_DB,
                    uid,
                    ODOO_PASSWORD,
                    "sale.order",
                    "mes_call_update_order",
                    [fp.order_item.order.sap_order_code],
                ],
            },
            "id": 2
        }

        url = ODOO_HOST + '/jsonrpc'
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, data=json.dumps(data), headers=headers)
        print(response.json())
    else:
        print("认证失败，请检查用户名或密码。")

    return {"status": "ok"}