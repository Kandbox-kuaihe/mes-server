import traceback
from sqlalchemy import func, desc, nullslast, asc
from dispatch.database import get_db
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import literal, case, and_
from dispatch.log import getLogger
from dispatch.product_type.models import ProductType
from dispatch.runout_admin.finished_product.models import FinishedProduct
from dispatch.system_admin.auth.models import DispatchUser
from dispatch.system_admin.auth.service import get_current_user

from dispatch.database_util.service import common_parameters, search_filter_sort_paginate
from .models import (
    TestSample,
    TestSampleCreate,
    TestSamplePagination,
    TestSampleRead,
    TestSampleUpdate,
)
from .service import create, delete, get, get_by_test_sample_code, update
from dispatch.runout_admin.runout_list.models import Runout
from dispatch.cast.models import Cast
from dispatch.spec_admin.spec.models import Spec
from dispatch.area.models import Area
from dispatch.tests_admin.impact_test_card.models import TestImpact
from dispatch.tests_admin.tensile_test_card.models import TestTensile
from dispatch.tests_admin.bend_test_card.models import TestBend
from dispatch.tests_admin.test_list.models import Test
from dispatch.runout_admin.test_coverage.models import TestCoverage


router = APIRouter()
log = getLogger(__file__)

@router.get("/", response_model=TestSamplePagination)
def get_testSamples(*, db_session: Session = Depends(get_db), common: dict = Depends(common_parameters),start_date:str = Query(None), end_date:str =Query(None)):
    query = db_session.query(TestSample
                                ).outerjoin(Runout, TestSample.runout_id == Runout.id
                                ).outerjoin(Cast, TestSample.cast_id == Cast.id
                                ).outerjoin(Spec, TestSample.spec_id == Spec.id
                                ).outerjoin(Area, TestSample.area_id == Area.id)
    if start_date:
        query = query.filter(TestSample.created_at >= start_date)
    if end_date:
        query = query.filter(TestSample.created_at <= end_date)
    common['query'] = query

    data =  search_filter_sort_paginate(model="TestSample", **common)
    for item in data['items']:
        t =  db_session.query(TestTensile).join(Test, Test.id==TestTensile.test_id).filter(Test.test_sample_id == item.id).all()
        item.tensiles  = t
        c = db_session.query(TestImpact).join(Test, Test.id==TestImpact.test_id).filter(Test.test_sample_id == item.id).all()
        item.impacts = c
    return data

@router.get('/test_result')
def get_test_result(*, db_session: Session = Depends(get_db), runout_id:int):
    
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
    ).join(TestSample, Test.test_sample_id==TestSample.id).filter( Test.runout_id==TestSample.runout_id).filter(TestSample.runout_id==runout_id)
   
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
    ).join(TestSample, Test.test_sample_id==TestSample.id).filter( Test.runout_id==TestSample.runout_id).filter(TestSample.runout_id==runout_id)
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
    ).join(TestSample, Test.test_sample_id==TestSample.id).filter( Test.runout_id==TestSample.runout_id).filter(TestSample.runout_id==runout_id)

    combined_query = impact_query.union_all(tensile_query, bend_query)
    data = list(combined_query)
    return {
        "total":len(data),
        "items":data,
        "itemsPerPage":len(data),
        "page":1
    }


@router.post("/", response_model=TestSampleRead)
def create_testSample(*, db_session: Session = Depends(get_db), testSample_in: TestSampleCreate,
                 current_user: DispatchUser = Depends(get_current_user)):
    """
    Create a new testSample contact.
    """
    
    testSample = get_by_test_sample_code(db_session=db_session,test_sample_code=testSample_in.test_sample_code,test_sample_part=testSample_in.test_sample_part)
    
    
    if testSample:
        raise HTTPException(status_code=400, detail="The testSample with this code already exists.")
    
    testSample_in.created_by = current_user.email
    testSample_in.updated_by = current_user.email
    testSample_in.created_at = datetime.now()
    testSample_in.updated_at = datetime.now()
    testSample = create(db_session=db_session, testSample_in=testSample_in)
    try:
        from ...contrib.message_admin.message_server import server as MessageServer
        messageStrategy126=MessageServer.MessageStrategy126()
        messageStrategy126.send_lims_126_130_131(db_session, testSample)
        del messageStrategy126
    except ImportError as e:
        log.warning(f"ERROR in import,{e}")
    except Exception as e:
        traceback.print_exc()
        log.error(f"ERROR in send_lims_126_130_131 ,{e}")

    return testSample

@router.get("/covering_usage")
def get_cover_usage(*, db_session: Session = Depends(get_db), 
                    rolling_id: int = Query(None), cast_id: int = Query(None), runout_id: int = Query(None), 
                    page: int = Query(1), items_per_page: int = Query(10,alias="itemsPerPage"),
                    current_user: DispatchUser = Depends(get_current_user)):
    query = db_session.query(
        Runout.id.label('runout_id'),
        Runout.runout_code,
        ProductType.flange_thickness,
        ProductType.web_thickness,
        Runout.runout_code,  
    ).outerjoin(ProductType, Runout.product_type_id == ProductType.id)
    query = query.filter(and_(Runout.mill_id == current_user.current_mill_id, Runout.is_deleted==0))
    if rolling_id:
        query = query.filter(Runout.rolling_id == rolling_id)
    if cast_id:
        query = query.filter(Runout.cast_id == cast_id)
    if runout_id:
        query = query.filter(Runout.id == runout_id)
    base_query = query.order_by(
        nullslast(desc(ProductType.flange_thickness)),
        nullslast(desc(ProductType.web_thickness)),
        nullslast(asc(Runout.runout_code))
    )
    count_query = base_query.statement.with_only_columns([func.count()]).order_by(None)
    total_count = db_session.execute(count_query).scalar()
    # 应用分页
    if items_per_page > 0:
        base_query = base_query.offset((page - 1) * items_per_page).limit(items_per_page)

    data =  list(map(dict,base_query.all()))

    for item in data:
        tests = db_session.query(Test.id,Test.test_sample_id).filter(Test.runout_id == item['runout_id']).all()
        test_sample_ids = [t.test_sample_id for t in tests]
        test_ids = [t.id for t in tests]
        item['bar_total']  = db_session.query(FinishedProduct).filter(FinishedProduct.runout_id == item['runout_id']).count()
        item['bar_covered'] = db_session.query(FinishedProduct).filter(FinishedProduct.runout_id == item['runout_id']).filter(FinishedProduct.cover_status == 'P').count()

        # 获取 test_sample_flag  
        item['test_sample_flag'] = []
        if test_sample_ids:
            flags = db_session.query(TestSample.web_sample, TestSample.flange_sample1).filter(TestSample.id.in_(test_sample_ids)).all()
            fset = set()
            for i in flags:
                if i.web_sample:
                    fset.add(i.web_sample)
                if i.flange_sample1:
                    fset.add(i.flange_sample1)
            item['test_sample_flag'] = list(fset)

        # 获取 inspectors
        tests = db_session.query(Test).filter(Test.id.in_(test_ids)).all()
        inspectors = set()
        for t in tests:
            if t.inspector_1:
                inspectors.add(t.inspector_1.code)
            if t.inspector_2:
                inspectors.add(t.inspector_2.code)
            if t.inspector_3:
                inspectors.add(t.inspector_3.code)
            if t.inspector_4:
                inspectors.add(t.inspector_4.code)
        #tbm inspector code
        tensile_insp_codes = db_session.query(TestTensile.insp_code).filter(
            TestTensile.test_id.in_(test_ids)
        ).all()
        for code_tuple in tensile_insp_codes:
            code = code_tuple[0]  # Query returns tuple with one element
            if code:
                inspectors.add(code)
        # Add additional inspector codes from TestImpact table
        impact_insp_codes = db_session.query(TestImpact.insp_code).filter(
            TestImpact.test_id.in_(test_ids)
        ).all()
        for code_tuple in impact_insp_codes:
            code = code_tuple[0]
            if code:
                inspectors.add(code)
        item['inspectors'] = list(inspectors)
        
        t = db_session.query(case([(TestSample.flange_sample1.isnot(None), TestSample.flange_sample1)], else_=TestSample.web_sample).label("source_type"),TestSample.standard, TestTensile.orientation,TestCoverage.covered_weight_kg).join(
            Test, Test.id==TestTensile.test_id).join(TestCoverage,TestCoverage.test_id==Test.id
                                                     ).join(TestSample,Test.test_sample_id==TestSample.id).filter(Test.id.in_(test_ids)).filter(Test.type == 'tensile')
        item['tensiles'] = [dict(tensile) for tensile in t]
        c = db_session.query(TestImpact.temp_c,TestImpact.temp_units, TestImpact.temp_f, TestCoverage.covered_weight_kg).join(Test, Test.id==TestImpact.test_id).join(TestCoverage,TestCoverage.test_id==Test.id).filter(Test.id.in_(test_ids)).filter(Test.type == 'impact').all()
        item['impacts'] = [dict(impact) for impact in c]
        
    return {
        "items": data,
        "total": total_count,
        "page": page,
        "itemsPerPage": items_per_page
    }

@router.get("/{testSample_id}", response_model=TestSampleRead)
def get_testSample(*, db_session: Session = Depends(get_db), testSample_id: int):
    """
    Get a testSample contact.
    """
    testSample = get(db_session=db_session, testSample_id=testSample_id)
    if not testSample:
        raise HTTPException(status_code=400, detail="The testSample with this id does not exist.")
    return testSample


@router.put("/{test_sample_id}", response_model=TestSampleRead)
def update_testSample(
    *,
    db_session: Session = Depends(get_db),
    test_sample_id: int,
    testSample_in: TestSampleUpdate, current_user: DispatchUser = Depends(get_current_user)
):
    """
    Update a testSample contact.
    """
    testSample = get(db_session=db_session, testSample_id=test_sample_id)
    if not testSample:
        raise HTTPException(status_code=400, detail="The testSample with this id does not exist.")
    
    testSample_in.updated_by = current_user.email
    testSample_in.updated_at = datetime.now()
    testSample = update(
        db_session=db_session,
        testSample=testSample,
        testSample_in=testSample_in,
    )
    return testSample


# @router.put("/testSample_code/{testSample_code}", response_model=TestSampleRead)
# def update_testSample_by_code(
#     *,
#     db_session: Session = Depends(get_db),
#     testSample_code: str,
#     testSample_in: TestSampleUpdate, current_user: DispatchUser = Depends(get_current_user)
# ):
#     """
#     Update a testSample contact.
#     """
#     testSample = get_by_test_sample_code(db_session=db_session,test_sample_code=testSample_in.test_sample_code,test_sample_part=testSample_in.test_sample_part)
#     if not testSample:
#         raise HTTPException(status_code=400, detail="The testSample with this id does not exist.")

#     testSample_in.updated_by = current_user.email
#     testSample = update(
#         db_session=db_session,
#         testSample=testSample,
#         testSample_in=testSample_in,
#     )

#     return testSample


@router.delete("/{testSample_id}", response_model=TestSampleRead)
def delete_testSample(*, db_session: Session = Depends(get_db), testSample_id: int):
    """
    Delete a testSample contact.
    """
    testSample = get(db_session=db_session, testSample_id=testSample_id)
    if not testSample:
        raise HTTPException(status_code=400, detail="The testSample with this id does not exist.")

    return delete(db_session=db_session, testSample_id=testSample_id)


@router.post("/reserve")
def update_reserve(data: dict, db_session: Session = Depends(get_db)):
    id_list = data["list"]
    for id in id_list:
        testSample = db_session.query(TestSample).filter(TestSample.id == id).first()
        if testSample:
            testSample.status = "R"
            db_session.add(testSample)
    db_session.commit()
    return True
@router.post("/cut")
def update_reserve(data: dict, db_session: Session = Depends(get_db)):
    id_list = data["list"]
    for id in id_list:
        testSample = db_session.query(TestSample).filter(TestSample.id == id).first()
        if testSample:
            testSample.status = "C"
            db_session.add(testSample)
    db_session.commit()
    return True