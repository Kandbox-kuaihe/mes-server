import json

from sqlalchemy_filters import apply_filters

from dispatch.database import get_db
from typing import List
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, aliased
from sqlalchemy import literal
from dispatch.message_admin.message_server.models import PushMessageData
from dispatch.runout_admin.finished_product.models import FinishedProduct
from dispatch.system_admin.auth.models import DispatchUser
from dispatch.system_admin.auth.service import get_current_user

from dispatch.database_util.service import common_parameters, search_filter_sort_paginate
from dispatch.tests_admin.test_piece.models import TestPiece
from dispatch.tests_admin.test_sample.models import TestSample
from .models import (
    Test,
    TestCreate,
    TestUpdate,
    TestRead,
    TestPagination,
    TestNewCreate,
    TestNewRead, TestNewUpdate, TestPrintStatus, TestBulkUpdatePrintStatus
)
from .service import create, update, delete, get, get_by_code, find_max_test_code, get_filter_print_status, \
    bulk_update_print_status, impact_spec_temp
from ...config import get_mill_ops, MILLEnum
# from ...contrib.message_admin.message_server import message_strategy
from dispatch.tests_admin.test_list.service import TestService
from dispatch.tests_admin.tensile_test_card.models import TestTensileUpdate
from dispatch.tests_admin.tensile_test_card.models import TestTensile
from dispatch.tests_admin.impact_test_card.models import TestImpact
from dispatch.tests_admin.bend_test_card.models import TestBend
from dispatch.runout_admin.finished_product.models_secondary_advice import finished_product_advice
from ...spec_admin.spec.models import Spec
from ...spec_admin.spelong.models import Spelong
from ...spec_admin.spimpact.models import Spimpact
from ...spec_admin.sptensil.models import Sptensil
from ...spec_admin.spyield.models import Spyield

router = APIRouter()

#
FUNCTION_MAPPING = {

}


@router.get("/", response_model=TestPagination)
def get_tests(*, common: dict = Depends(common_parameters)):
    def find_indices(lst, target):
        # 通过列表和列表元素获取index
        return [i for i, item in enumerate(lst) if target in item]

    if common['fields'] and any("inspector" in item for item in common['fields']):
        index = find_indices(common['fields'], "inspector")[0]
        inspector_id = common['values'][index]
        filter_statement = {
            'or': [
                {'model': 'Test', 'field': 'inspector_id_1', 'op': '==', 'value': inspector_id},
                {'model': 'Test', 'field': 'inspector_id_2', 'op': '==', 'value': inspector_id},
                {'model': 'Test', 'field': 'inspector_id_3', 'op': '==', 'value': inspector_id},
                {'model': 'Test', 'field': 'inspector_id_4', 'op': '==', 'value': inspector_id},
            ]
        }

        common['fields'].pop(index)
        common['ops'].pop(index)
        common['values'].pop(index)
        query = common['db_session'].query(Test)
        query = apply_filters(query, filter_statement)
        common['query'] = query

    # 新增standard字段过滤逻辑
    if common['fields'] and any("standard" in item for item in common['fields']):
        std_index = find_indices(common['fields'], "standard")[0]
        std_value = common['values'][std_index]

        # 构建跨表过滤条件（假设Test与TestSample通过sample属性关联）
        filter_statement = {
            'model': 'Spec',  # 指定关联表
            'field': 'standard',
            'op': '==',
            'value': std_value
        }

        # 移除已处理的参数
        common['fields'].pop(std_index)
        common['ops'].pop(std_index)
        common['values'].pop(std_index)

        # 如果已经对inspector进行了过滤，使用之前的query继续过滤
        if 'query' in common:
            query = common['query'].join(Test.spec)
        else:
            query = common['db_session'].query(Test).join(Test.spec)

        query = apply_filters(query, [filter_statement])
        common['query'] = query

    return search_filter_sort_paginate(model="Test", **common)


@router.get("/test_piece", response_model=TestPagination)
def get_test_piece(*, common: dict = Depends(common_parameters)):
    return search_filter_sort_paginate(model="TestPiece", **common)


@router.post("/", response_model=TestRead)
def create_test(*, db_session: Session = Depends(get_db), test_in: TestCreate,
                current_user: DispatchUser = Depends(get_current_user)):
    test = get_by_code(db_session=db_session, code=test_in.test_code)
    if test:
        raise HTTPException(status_code=400, detail="The test with this code already exists.")

    test_in.created_by = current_user.email
    test_in.updated_by = current_user.email
    test_in.created_at = datetime.now(timezone.utc)
    test_in.updated_at = datetime.now(timezone.utc)
    test = create(db_session=db_session, test_in=test_in)
    return test


@router.get("/code/{test_code}", response_model=TestRead)
def get_test_by_code(*, db_session: Session = Depends(get_db), test_code: str):
    test = get_by_code(db_session=db_session, code=test_code)
    if not test:
        raise HTTPException(status_code=400, detail="The test with this code does not exist.")
    return test


@router.get("/test_spec")
def get_test_spec(
        *,
        db_session: Session = Depends(get_db),
        spec_id: int,
        test_sample_id: int = None,
        test_type: str
):
    thickness_row = (
        db_session.query(TestSample.sample_thickness)
        .filter(TestSample.id == test_sample_id)
        .first()
        if test_sample_id else None
    )
    thickness = thickness_row[0] if thickness_row else None

    # 提前获取通用字段
    spec = db_session.query(Spec).filter(Spec.id == spec_id).first()
    spec_units = spec.spec_units if spec else None

    summary = spec.summary_name if spec else None
    rail_grade = None
    if summary and summary.startswith("RAIL GRADE "):
        rail_grade = summary[len("RAIL GRADE "):]
    def get_flex_data(key, field):
        try:
            return spec.flex_form_data.get(key, [{}])[0].get(field)
        except Exception:
            return None

    if test_type == "tensile":
        if not thickness:
            raise HTTPException(status_code=400, detail="The Test Sample is required.")

        sp_tensile = db_session.query(Sptensil).filter(
            Sptensil.spec_id == spec_id,
            Sptensil.thick_from <= thickness,
            Sptensil.thick_to >= thickness
        ).first()

        sp_yield = db_session.query(Spyield).filter(
            Spyield.spec_id == spec_id,
            Spyield.thick_from <= thickness,
            Spyield.thick_to >= thickness
        ).first()

        sp_elong = db_session.query(Spelong).filter(
            Spelong.spec_id == spec_id,
            Spelong.thick_from <= thickness,
            Spelong.thick_to >= thickness
        ).first()

        return {
            "spec_units": spec_units,
            "tensile_min": sp_tensile.tensile_min if sp_tensile else None,
            "tensile_max": sp_tensile.tensile_max if sp_tensile else None,
            "yield_min": sp_yield.yield_min if sp_yield else None,
            "yield_max": sp_yield.yield_max if sp_yield else None,
            "y_t_max": sp_yield.yield_tens_rat_max if sp_yield else None,
            "y_t_min": sp_yield.yield_tens_rat_min if sp_yield else None,
            "elongation_code": sp_elong.elong_guage_code if sp_elong else None,
            "elongation_min": sp_elong.elong_min_value if sp_elong else None
        }

    elif test_type == "impact":
        if not thickness:
            raise HTTPException(status_code=400, detail="The Test Sample is required.")

        sp_impact = db_session.query(Spimpact).filter(
            Spimpact.spec_id == spec_id,
            Spimpact.thick_from <= thickness,
            Spimpact.thick_to >= thickness
        ).first()

        return {
            "spec_units": spec_units,
            "avg_min": sp_impact.ave_value_1 if sp_impact else None,
            "ind_min": sp_impact.min_value_1 if sp_impact else None
        }

    elif test_type == "cleanness":
        return {
            "k_number": get_flex_data("Cleanness", "K"),
            "k_value_max": get_flex_data("Cleanness", "Max")
        }

    elif test_type == "sulphur":
        return {
            "sulphur_print_max": get_flex_data("Sulphur_Print", "Max"),
            "rail_grade": rail_grade
        }

    elif test_type == "decarburisation":
        return {
            "decarb_value_max": get_flex_data("Decarburisation", "Max")
        }
    elif test_type == "resistivity":
        return {
            "resistivity_max": get_flex_data("Resistivity", "Resist_Max"),
            "temp_max": get_flex_data("Resistivity", "Temp_Max")
        }

    else:
        raise HTTPException(status_code=400, detail="Invalid test type")


@router.get("/{test_id}", response_model=TestRead)
def get_test(*, db_session: Session = Depends(get_db), test_id: int):
    test = get(db_session=db_session, id=test_id)
    if not test:
        raise HTTPException(status_code=400, detail="The test with this id does not exist.")
    return test


@router.put("/{test_id}", response_model=TestRead)
def update_test(
        *,
        db_session: Session = Depends(get_db),
        test_id: int,
        test_in: TestUpdate, current_user: DispatchUser = Depends(get_current_user)
):
    test = get(db_session=db_session, id=test_id)
    if not test:
        raise HTTPException(status_code=400, detail="The test with this id does not exist.")

    test_in.updated_by = current_user.email
    test_in.updated_at = datetime.now()

    test = update(
        db_session=db_session,
        test=test,
        test_in=test_in,
    )
    return test


@router.delete("/{test_id}")
def delete_test(*, db_session: Session = Depends(get_db), test_id: int):
    test = get(db_session=db_session, id=test_id)
    if not test:
        raise HTTPException(status_code=400, detail="The test with this id does not exist.")

    delete(db_session=db_session, test=test, test_id=test_id)

    return {"deleted": "ok"}


@router.get('/print_status/list', response_model=List[TestPrintStatus])
def get_filter_print_status_test(from_time: str = Query(None, description="start time"),
                                 to_time: str = Query(None, description="end time"),
                                 print_status: str = Query(None, description="print status"),
                                 db_session: Session = Depends(get_db),
                                 current_user: DispatchUser = Depends(get_current_user)):
    if not current_user.current_mill_id:
        raise HTTPException(status_code=400, detail="The current mill is empty.")

    return get_filter_print_status(db_session=db_session, mill_id=current_user.current_mill_id, from_time=from_time,
                                   to_time=to_time)

@router.post('/impact/spec_temp')
def get_impact_spec_temp(data: dict,  db_session: Session = Depends(get_db)):
    return impact_spec_temp(db_session=db_session, flange_thickness=data.get('flange_thickness', None), spec_id=data.get('spec_id', None))


@router.put('/bulk_update/print_status')
def update_print_status(data: TestBulkUpdatePrintStatus, db_session: Session = Depends(get_db)):
    bulk_update_print_status(db_session=db_session, test_list=[
        {
            "id": id,
            "print_status": "Printed"
        } for id in data.ids
    ])
    return True


############################## 整合后的test接口 ##############################
@router.post("/new/create", response_model=TestNewRead)
def create_test(*, db_session: Session = Depends(get_db), data_in: TestNewCreate,
                current_user: DispatchUser = Depends(get_current_user)):
    if get_mill_ops(current_user.current_mill_id) == MILLEnum.MILL_UNKNOWN:
        generate_test_code = find_max_test_code(db_session=db_session, mill_id=current_user.current_mill_id)
        data_in.test_code = generate_test_code
    test_service = TestService(test_type=data_in.type)
    data_in.created_by = current_user.email
    data_in.sub_test_in.created_by = current_user.email
    data_in.created_at = datetime.now()
    data_in.sub_test_in.created_at = datetime.now()
    return test_service.create(db_session=db_session, test_in=data_in)


def restore_tensile_data_if_none(data_in, tensile, check_digit_field, sub_test_field_prefix, check_digit):

    if getattr(data_in.sub_test_in, check_digit_field) is None:
        # 如果不存在，就还原数据
        fields_to_update = [
            f'{sub_test_field_prefix}_tested_thickness', f'{sub_test_field_prefix}_tested_width',
            f'{sub_test_field_prefix}_tested_diameter', f'{sub_test_field_prefix}_value_mpa',
            f'{sub_test_field_prefix}_yield_tt0_5', f'{sub_test_field_prefix}_yield_high',
            f'{sub_test_field_prefix}_yield_rp0_2', f'{sub_test_field_prefix}_yield_low',
            f'{sub_test_field_prefix}_elongation_code', f'{sub_test_field_prefix}_elongation_a565',
            f'{sub_test_field_prefix}_elongation_a200', f'{sub_test_field_prefix}_elongation_a50',
            f'{sub_test_field_prefix}_elongation_8', f'{sub_test_field_prefix}_elongation_2',
            f'{sub_test_field_prefix}_elongation_a80'
        ]
        for field in fields_to_update:
            setattr(data_in.sub_test_in, field, getattr(tensile, field))
    else:
        # 如果check digit不匹配，抛出异常
        if not (getattr(data_in.sub_test_in, check_digit_field) == getattr(tensile, check_digit)):
            raise HTTPException(status_code=400, detail="Check digit is incorrect!")


@router.put("/new/update", response_model=TestNewRead)
def update_test(*, db_session: Session = Depends(get_db), data_in: TestNewUpdate,
                current_user: DispatchUser = Depends(get_current_user)):
    # if data_in.type in ['tensile', 'impact', 'bend']:
    #     if not (data_in.check_digit_1_1 == data_in.check_digit_1 and data_in.check_digit_2_2 == data_in.check_digit_2 and data_in.check_digit_3_3 == data_in.check_digit_3):
    #         raise HTTPException(status_code=400, detail="Check digit is incorrect!")
    # if current_user.full_name:
    #     data_in.update_name = "".join(word[0].upper() for word in current_user.full_name.split() if word)

    if data_in.type == 'tensile':
        tensile = data_in.tensile_object
        sub_test_in = data_in.sub_test_in
        if TestTensileUpdate(**sub_test_in.__dict__).check_digit_1_1 is None:
            # 如果不存在就还原数据，也就是不更新数据
            fields_to_update = [
                'tested_thickness', 'tested_width', 'tested_diameter', 'value_mpa',
                'yield_tt0_5', 'yield_high', 'yield_rp0_2', 'yield_low',
                'elongation_code', 'elongation_a565', 'elongation_a200', 'elongation_a50',
                'elongation_8', 'elongation_2', 'elongation_a80', 'testing_machine', 'susp'
            ]

            for field in fields_to_update:
                setattr(data_in.sub_test_in, field, getattr(tensile, field))
        else:
            if not (data_in.sub_test_in.check_digit_1_1 == tensile.check_digit_1):
                raise HTTPException(status_code=400, detail="Check digit is incorrect!")

        restore_tensile_data_if_none(data_in, tensile, 'check_digit_2_2', 'r1', 'check_digit_2')
        restore_tensile_data_if_none(data_in, tensile, 'check_digit_3_3', 'r2', 'check_digit_3')

    elif data_in.type == 'impact':
        impact = data_in.impact_object
        if data_in.sub_test_in.check_digit_1_1 is None:
            # 如果不存在就还原数据，也就是不更新数据
            fields_to_update = [
                'testing_machine', 'temp_f', 'temp_units', 'energy_1_j',
                'energy_2_j', 'energy_3_j', 'energy_average_j', 'energy_1_f',
                'energy_2_f', 'energy_3_f', 'energy_average_f', 'shear_1',
                'shear_2', 'shear_3', 'shear_average', 'energy_units', 'susp', 'impact_units'
            ]

            for field in fields_to_update:
                setattr(data_in.sub_test_in, field, getattr(impact, field))
        else:
            if not (data_in.sub_test_in.check_digit_1_1 == impact.check_digit_1):
                raise HTTPException(status_code=400, detail="Check digit is incorrect!")

        if data_in.sub_test_in.check_digit_2_2 is None:
            # 如果不存在就还原数据，也就是不更新数据
            fields_to_update = [
                'r1_temp_c', 'r1_temp_f', 'r1_energy_1_j', 'r1_energy_2_j',
                'r1_energy_3_j', 'r1_energy_average_j', 'r1_energy_1_f', 'r1_energy_2_f',
                'r1_energy_3_f', 'r1_energy_average_f', 'r1_shear_1', 'r1_shear_2',
                'r1_shear_3', 'r1_shear_average', 'r1_temp_units', 'r1_impact_units', 'r1_energy_units'
            ]

            for field in fields_to_update:
                setattr(data_in.sub_test_in, field, getattr(impact, field))
        else:
            if not (data_in.sub_test_in.check_digit_2_2 == impact.check_digit_2):
                raise HTTPException(status_code=400, detail="Check digit is incorrect!")

    elif data_in.type == 'bend':
        bend = data_in.bend_object
        if data_in.sub_test_in.check_digit_1_1 is None:
            # 如果不存在就还原数据，也就是不更新数据
            fields_to_update = [
                'code', 'test_standard', 'heat_treated_by', 'tested_by',
                'result_1'
            ]

            for field in fields_to_update:
                setattr(data_in.sub_test_in, field, getattr(bend, field))
        else:
            if not (data_in.sub_test_in.check_digit_1_1 == bend.check_digit_1):
                raise HTTPException(status_code=400, detail="Check digit is incorrect!")

    else:
        other_type_object = getattr(data_in, f"{data_in.type}_object")
        # print(type(other_type_object))
        if data_in.sub_test_in.check_digit_1_1 is None or data_in.sub_test_in.check_digit_1_1 == "":
            for field in other_type_object.model_fields.keys():
                setattr(data_in.sub_test_in, field, getattr(other_type_object, field))
        else:
            if not (data_in.sub_test_in.check_digit_1_1 == other_type_object.check_digit_1):
                raise HTTPException(status_code=400, detail="Check digit is incorrect!")



    test_service = TestService(test_type=data_in.type)
    test = get(db_session=db_session, id=data_in.id)
    if not test:
        raise HTTPException(status_code=400, detail=f"The test with the id {data_in.id} does not exist.")
    data_in.updated_by = current_user.email
    data_in.updated_at = datetime.now()
    new_test = test_service.update(db_session=db_session, test=test, test_in=data_in)
    try:
        valid_test_types = ["tensile", "hardness", "conductivity", "cleanness", "decarburisation", "sulphur", "microstructure", "hydrogen"]

        if get_mill_ops(new_test.mill_id) == MILLEnum.MILL1 and new_test.type in valid_test_types:

            message = json.dumps({"test_id": new_test.id, "test_type": new_test.type, "test_action": "Update"})
            input = {"id": 1003, "type": "srsmpc", "msg": message}
            input = PushMessageData(**input)
            from ...contrib.message_admin.message_server import message_strategy
            srsmrail = message_strategy.MessageStrategyRail()
            srsmrail.handle(db_session=db_session, message=input)
    except ImportError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=420, detail=str(e))

    return new_test


@router.delete("/new/delete/{test_id}", response_model=TestNewRead)
def delete_test(*, db_session: Session = Depends(get_db), test_id: int,
                current_user: DispatchUser = Depends(get_current_user)):
    test = get(db_session=db_session, id=test_id)
    test_service = TestService(test_type=test.type)
    if not test:
        raise HTTPException(status_code=400, detail="The test with this id does not exist.")
    test.updated_by = current_user.email
    setattr(test, f"{test.type}_object.updated_by", current_user.email)
    test.updated_at = datetime.now()
    setattr(test, f"{test.type}_object.updated_at", datetime.now())
    return test_service.delete(db_session=db_session, test=test)


@router.get("/new/get/{test_id}")
def get_test(*, db_session: Session = Depends(get_db), test_id: int):
    test = get(db_session=db_session, id=test_id)
    test_service = TestService(test_type=test.type)
    if not test:
        raise HTTPException(status_code=400, detail="The test with this id does not exist.")
    return test_service.read(db_session=db_session, test=test)



@router.get('/srsm/test_recommend')
def get_test_result(*, db_session: Session = Depends(get_db), 
    order_id: int = Query(None), 
    advice_id: int = Query(None),
    rolling_id: int = Query(None),
    order_item_id: int = Query(None)):

    query = db_session.query(FinishedProduct.id)
    if order_id:
        query = query.filter(FinishedProduct.order_id == order_id)
    if advice_id:
        FinishedProductAdvice = aliased(finished_product_advice)
        finished_product_adive_data = db_session.query(FinishedProductAdvice).filter(FinishedProductAdvice.c.advice_id == advice_id).all()
        finished_product_id = [finished_product_advices.finished_product_id for finished_product_advices in finished_product_adive_data]
        query = query.filter(FinishedProduct.id.in_(finished_product_id))
    if rolling_id:
        query = query.filter(FinishedProduct.rolling_id == rolling_id)
    if order_item_id:
        query = query.filter(FinishedProduct.order_item_id == order_item_id)
    
    # 获取finished id list
    finished_product_ids = [i.id for i in query]
    if not finished_product_ids:
        raise HTTPException(status_code=400, detail="No finished product found.")

    # 获取test sample id list
    test_sample_query = db_session.query(TestPiece.test_sample_id).filter(TestPiece.finished_id.in_(finished_product_ids))
    test_sample_ids = [i.test_sample_id for i in test_sample_query]
    if not test_sample_ids:
        raise HTTPException(status_code=400, detail="No test sample found.")
    
    impact_query  = db_session.query(TestSample.test_sample_code,TestSample.runout_id, 
                                     Test.test_code.label('test_code'),
                                     Test.ref_code.label('test_ref_code'),
                                     literal('Impact').label('test_type'),
                                     TestImpact.temp_c.label('temp_c'),
                                     TestImpact.impact_units.label('impact_units'),
                                     TestImpact.temp_units.label('temp_units'),
                                     TestImpact.energy_1_j.label('energy_1_j'),
                                     TestImpact.energy_2_j.label('energy_2_j'),
                                     TestImpact.energy_3_j.label('energy_3_j'),
                                     TestImpact.energy_1_f.label('energy_1_f'),
                                     TestImpact.energy_2_f.label('energy_2_f'),
                                     TestImpact.energy_3_f.label('energy_3_f'),
                                     TestImpact.energy_average_f.label('energy_average_f'),
                                     TestImpact.energy_average_j.label('energy_average_j'),
                                     literal(None).label('orientation'),
                                     TestImpact.standard.label('standard'),
                                     literal(None).label('value_mpa'),
                                     literal(None).label('yield_tt0_5'),
                                     literal(None).label('yield_rp0_2'),
                                     literal(None).label('elongation_code'),
                                     literal(None).label('elongation_a200'),
                                     literal(None).label('elongation_a565'),
                                     literal(None).label('elongation_a50'),
                                     literal(None).label('result_1'),
                                     Test.id.label('test_id')).join(
        Test, Test.id==TestImpact.test_id
    ).join(TestSample, Test.test_sample_id==TestSample.id).filter( Test.cast_id==TestSample.cast_id).filter(Test.test_sample_id.in_(test_sample_ids))
   
    tensile_query = db_session.query(TestSample.test_sample_code,TestSample.runout_id,
                                     Test.test_code.label('test_code'),
                                     Test.ref_code.label('test_ref_code'),
                                     literal('Tensile').label('test_type'),
                                     literal(None).label('temp_c'),
                                     literal(None).label('impact_units'),
                                     literal(None).label('temp_units'),
                                     literal(None).label('energy_1_j'),
                                     literal(None).label('energy_2_j'),
                                     literal(None).label('energy_3_j'),
                                     literal(None).label('energy_1_f'),
                                     literal(None).label('energy_2_f'),
                                     literal(None).label('energy_3_f'),
                                     literal(None).label('energy_average_f'),
                                     literal(None).label('energy_average_j'),
                                     TestTensile.orientation.label('orientation'),
                                     TestTensile.standard.label('standard'),
                                     TestTensile.value_mpa.label('value_mpa'),
                                     TestTensile.yield_tt0_5.label('yield_tt0_5'),
                                     TestTensile.yield_rp0_2.label('yield_rp0_2'),
                                     TestTensile.elongation_code.label('elongation_code'),
                                     TestTensile.elongation_a200.label('elongation_a200'),
                                     TestTensile.elongation_a565.label('elongation_a565'),
                                     TestTensile.elongation_a50.label('elongation_a50'),
                                     literal(None).label('result_1'),
                                     Test.id.label('test_id')
                                     ).join(
        Test, Test.id==TestTensile.test_id
    ).join(TestSample, Test.test_sample_id==TestSample.id).filter( Test.cast_id==TestSample.cast_id).filter(Test.test_sample_id.in_(test_sample_ids))

    bend_query = db_session.query(TestSample.test_sample_code,TestSample.runout_id,
                                  Test.test_code.label('test_code'),
                                  Test.ref_code.label('test_ref_code'),
                                  literal('Bend').label('test_type'),
                                  literal(None).label('temp_c'),
                                  literal(None).label('impact_units'),
                                  literal(None).label('temp_units'),
                                  literal(None).label('energy_1_j'),
                                  literal(None).label('energy_2_j'),
                                  literal(None).label('energy_3_j'),
                                  literal(None).label('energy_1_f'),
                                  literal(None).label('energy_2_f'),
                                  literal(None).label('energy_3_f'),
                                  literal(None).label('energy_average_f'),
                                  literal(None).label('energy_average_j'),
                                  literal(None).label('orientation'),
                                  literal(None).label('standard'),
                                  literal(None).label('value_mpa'),
                                  literal(None).label('yield_tt0_5'),
                                  literal(None).label('yield_rp0_2'),
                                  literal(None).label('elongation_code'),
                                  literal(None).label('elongation_a200'),
                                  literal(None).label('elongation_a565'),
                                  literal(None).label('elongation_a50'),
                                  TestBend.result_1.label('result_1'),
                                  TestBend.test_id.label('test_id')
                                  ).join(
        Test, Test.id==TestBend.test_id
    ).join(TestSample, Test.test_sample_id==TestSample.id).filter( Test.cast_id==TestSample.cast_id).filter(Test.test_sample_id.in_(test_sample_ids))

    combined_query = impact_query.union_all(tensile_query, bend_query)
    data = list(combined_query)
    return {
        "total":len(data),
        "items":data,
        "itemsPerPage":len(data),
        "page":1
    }