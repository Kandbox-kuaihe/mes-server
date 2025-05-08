from dispatch.database import get_db
from typing import List
from datetime import datetime
from sqlalchemy import and_, exists, desc

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session, aliased
from dispatch.system_admin.auth.models import DispatchUser
from dispatch.system_admin.auth.service import get_current_user
from dispatch.runout_admin.runout_list.models import Runout
from dispatch.runout_admin.runout_list import service as runout_service
from dispatch.tests_admin.tensile_test_card.models import TestTensile
from dispatch.tests_admin.impact_test_card.models import TestImpact
from dispatch.tests_admin.test_list.models import Test
from dispatch.tests_admin.test_sample.models import TestSample

from dispatch.database_util.service import common_parameters, search_filter_sort_paginate
from .models import (
    CoverEndUse,
    CoverEndUseCreate,
    CoverEndUseUpdate,
    CoverEndUseRead,
    CoverEndUsePagination,
)
from .service import create, update, delete, get, delete_real, delete_by_runout_id, batch_update, get_by, get_finished_product, get_finished_product_rolling_cast

from dispatch.spec_admin.spec.models import Spec
from dispatch.runout_admin.finished_product.models import FinishedProductHoldReason, FinishedProduct, FinishedProductBatchHold, UnCoverUpdate, RegradePagination
from dispatch.runout_admin.finished_product.models_secondary_advice import finished_product_advice
from dispatch.runout_admin.test_coverage.service import delete_by_finished_product_id
import dispatch.runout_admin.finished_product.service as finished_product_service
from dispatch.log import getLogger
from ...config import MILLEnum, get_mill_ops
try:
    from dispatch.contrib.cover.tbm.utils import main as covering_all
    from dispatch.contrib.cover.tbm.utils import compare_finished_product_spec_result, cover_finished_product_sct
    from dispatch.contrib.cover.srsm.covering_services import srsm_compare_finished_product_spec_result, srsm_compare_finished_product_manual, run_auto_pass as srsm_run_auto_pass
except ImportError:
    def covering_all():
        raise NotImplementedError("covering_all is not available because required modules are missing.")
    def compare_finished_product_spec_result():
        raise NotImplementedError("compare_finished_product_spec_result is not available because required modules are missing.")
    def cover_finished_product_sct():
        raise NotImplementedError("cover_finished_product_sct is not available because required modules are missing.")
    def srsm_compare_finished_product_spec_result():
        raise NotImplementedError("srsm_compare_finished_product_spec_result is not available because required modules are missing.")
    def srsm_compare_finished_product_manual():
        raise NotImplementedError("srsm_compare_finished_product_manual is not available because required modules are missing.")
    def srsm_run_auto_pass():
        raise NotImplementedError("srsm_run_auto_pass is not available because required modules are missing.")

log = getLogger(__name__)


router = APIRouter()


@router.get("/", response_model=CoverEndUsePagination)
def get_cover_end_uses(*, common: dict = Depends(common_parameters)):
    return search_filter_sort_paginate(model="CoverEndUse", **common)


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
    covering = finished_product_service.get_covering(db_session=common['db_session'], runout_id=ids_list[0], covering=covering)
    return covering


@router.post("/", response_model=CoverEndUseRead)
def create_cover_end_use(*, db_session: Session = Depends(get_db), cover_end_use_in: CoverEndUseCreate,
                         current_user: DispatchUser = Depends(get_current_user)):
    # cover_end_use = get_by_code(db_session=db_session,code=cover_end_use_in.cover_end_use_code)
    # if cover_end_use:
    #     raise HTTPException(status_code=400, detail="The cover_end_use with this code already exists.")

    cover_end_use_in.created_by = current_user.email
    cover_end_use_in.updated_by = current_user.email
    cover_end_use_in.created_at = datetime.now()
    cover_end_use_in.updated_at = datetime.now()
    cover_end_use = create(db_session=db_session, cover_end_use_in=cover_end_use_in)
    return cover_end_use

@router.put("/{cover_end_use_id}", response_model=CoverEndUseUpdate)
def update_cover_end_use(
        *,
        db_session: Session = Depends(get_db),
        cover_end_use_id: int,
        cover_end_use_in: CoverEndUseUpdate, current_user: DispatchUser = Depends(get_current_user)
):
    cover_end_use = get(db_session=db_session, id=cover_end_use_id)
    if not cover_end_use:
        raise HTTPException(status_code=400, detail="The cover_end_use with this id does not exist.")

    cover_end_use_in.updated_by = current_user.email
    cover_end_use_in.updated_at = datetime.now()

    cover_end_use = update(
        db_session=db_session,
        cover_end_use=cover_end_use,
        cover_end_use_in=cover_end_use_in,
    )
    return cover_end_use

@router.delete("/{cover_end_use_id}")
def delete_cover_end_use(*, db_session: Session = Depends(get_db), cover_end_use_id: int):
    cover_end_use = get(db_session=db_session, id=cover_end_use_id)
    if not cover_end_use:
        raise HTTPException(status_code=400, detail="The cover_end_use with this id does not exist.")

    delete(db_session=db_session, cover_end_use=cover_end_use, cover_end_use_id=cover_end_use_id)

    return {"deleted": "ok"}


@router.post("/init_all")
def init_covering(*, db_session: Session = Depends(get_db)):
    covering_all(db_session=db_session)
    return


@router.post("/cover_runout/{runout_id}")
def init_covering_by_runout(*, db_session: Session = Depends(get_db), runout_id: int):
    runout = runout_service.get(db_session=db_session, runout_id=runout_id)
    if not runout:
        raise HTTPException(status_code=400, detail="The runout with this id does not exist.")
    # delete_by_runout_id(db_session=db_session, runout_id=runout_id)
    covering_all(db_session=db_session, all_runout=[runout])
    return


@router.post('/init_test/rolling_and_cast')
def update_test_rolling_and_cast(*, db_session: Session = Depends(get_db), rolling_id:int, cast_id:int, current_user: DispatchUser = Depends(get_current_user)):
    query = db_session.query(FinishedProduct).filter(FinishedProduct.rolling_id==rolling_id, FinishedProduct.cast_id == cast_id)
    subquery = (
        db_session.query(FinishedProduct.id)
       .filter(
            and_(
                # FinishedProduct.cover_status == 'W',
                FinishedProduct.mill_id == current_user.current_mill_id,
                exists().where(
                    and_(
                        TestSample.runout_id == FinishedProduct.runout_id,
                        Test.test_sample_id == TestSample.id,
                        TestImpact.test_id == Test.id
                    )
                ),
                exists().where(
                    and_(
                        TestSample.runout_id == FinishedProduct.runout_id,
                        Test.test_sample_id == TestSample.id,
                        TestTensile.test_id == Test.id
                    )
                )
            )
        )
       .distinct()
       .subquery('subquery')
    )

    # 通过子查询获取完整的 FinishedProduct 对象
    final_query = (
        query.join(subquery, FinishedProduct.id == subquery.c.id)
    )

    processed_finished_product_ids = []
    for finished_product in final_query.all():
        processed_finished_product_ids.append(finished_product.id)
        compare_finished_product_spec_result(db_session=db_session, finished_product=finished_product)

    query = query.filter(FinishedProduct.id.notin_(processed_finished_product_ids))
    for finished_product in query.order_by(desc(FinishedProduct.code)).all():
        compare_finished_product_spec_result(db_session=db_session, finished_product=finished_product)
    
    return


@router.post('/init_test/cover_all')
def update_test_rolling_and_cast(*, db_session: Session = Depends(get_db), current_user: DispatchUser = Depends(get_current_user)):
    if not current_user.current_mill_id:
        raise HTTPException(status_code=400, detail='Mill not found!')
    if get_mill_ops(current_user.current_mill_id) == MILLEnum.MILL410:
        finished_product_query = get_finished_product(db_session=db_session, mill_id=current_user.current_mill_id)
        count = 0
        pass_count = 0
        for finished_product in finished_product_query:
            if finished_product.cover_status == 'W':
                update_data = compare_finished_product_spec_result(
                    db_session=db_session,
                    finished_product=finished_product,
                    is_batch=True
                )
                if update_data:
                    count += 1
                else:
                    pass_count += 1
        finished_product_query = get_finished_product_rolling_cast(db_session=db_session, finished_product_list=finished_product_query, mill_id=current_user.current_mill_id)
        for finished_product in finished_product_query:
            update_data = compare_finished_product_spec_result(
                db_session=db_session,
                finished_product=finished_product,
                is_batch=True
            )
            if update_data:
                count += 1
            else:
                pass_count += 1
    elif get_mill_ops(current_user.current_mill_id) == MILLEnum.MILL1:
        count, pass_count = srsm_run_auto_pass(db_session=db_session)
    return {"message": f"Processed {count} finished products, skip {pass_count} finished products"}


@router.post("/init_test/{runout_id}")
def init_covering(*, db_session: Session = Depends(get_db), runout_id: int, current_user: DispatchUser = Depends(get_current_user)):
    runout = runout_service.get(db_session=db_session, runout_id=runout_id)
    if not runout.rolling_id or not runout.cast_id:
        runout_list = [runout]
    runout_list = runout_service.get_by_rolling_cast(db_session=db_session, rolling_id=runout.rolling_id, cast_id=runout.cast_id)
    runout_ids = [runout.id for runout in runout_list]
    query = db_session.query(FinishedProduct).filter(FinishedProduct.runout_id.in_(runout_ids))
    subquery = (
        db_session.query(FinishedProduct.id)
       .filter(
            and_(
                # FinishedProduct.cover_status == 'W',
                FinishedProduct.mill_id == current_user.current_mill_id,
                exists().where(
                    and_(
                        TestSample.runout_id == FinishedProduct.runout_id,
                        Test.test_sample_id == TestSample.id,
                        TestImpact.test_id == Test.id
                    )
                ),
                exists().where(
                    and_(
                        TestSample.runout_id == FinishedProduct.runout_id,
                        Test.test_sample_id == TestSample.id,
                        TestTensile.test_id == Test.id
                    )
                )
            )
        )
       .distinct()
       .subquery('subquery')
    )

    # 通过子查询获取完整的 FinishedProduct 对象
    final_query = (
        query.join(subquery, FinishedProduct.id == subquery.c.id)
    )

    processed_finished_product_ids = []

    for finished_product in final_query.all():
        processed_finished_product_ids.append(finished_product.id)
        if current_user.current_mill_code == 'SCT':
            cover_finished_product_sct(db_session=db_session, finished_product=finished_product)
        elif get_mill_ops(current_user.current_mill_id) == MILLEnum.MILL1 :
            srsm_compare_finished_product_spec_result(db_session=db_session, finished_product=finished_product)
        elif get_mill_ops(current_user.current_mill_id) == MILLEnum.MILL410:
            if finished_product.allocation_status in ['scrap']:
                continue
            if (finished_product.mult_type == 'R' and finished_product.exist_flag == 'Y') or \
                (finished_product.mult_type is None and finished_product.exist_flag is None) or \
                (finished_product.mult_type is None and finished_product.exist_flag == 'Y'):
                compare_finished_product_spec_result(db_session=db_session, finished_product=finished_product)
        else:
            raise HTTPException(status_code=400, detail=f"The Mill {current_user.current_mill_code} not support")

    query = query.filter(FinishedProduct.id.notin_(processed_finished_product_ids))

    for finished_product in query.order_by(desc(FinishedProduct.code)).all():
        if get_mill_ops(current_user.current_mill_id) == MILLEnum.MILL1 :
            srsm_compare_finished_product_spec_result(db_session=db_session, finished_product=finished_product)
        elif get_mill_ops(current_user.current_mill_id) == MILLEnum.MILL410:
            if finished_product.allocation_status in ['scrap']:
                continue
            if (finished_product.mult_type == 'R' and finished_product.exist_flag == 'Y') or \
                (finished_product.mult_type is None and finished_product.exist_flag is None) or \
                (finished_product.mult_type is None and finished_product.exist_flag == 'Y'):
                compare_finished_product_spec_result(db_session=db_session, finished_product=finished_product)
        else:
            raise HTTPException(status_code=400, detail=f"The Mill {current_user.current_mill_code} not support")
    return True

@router.post("/impact_spec_post")
def create_text_data(*, db_session: Session = Depends(get_db), create_in: CoverEndUseCreate, current_user: DispatchUser = Depends(get_current_user)):
    cover_end_use = get_by(db_session=db_session, runout_id=create_in.runout_id, spec_id=create_in.spec_id)
    if cover_end_use:
        raise HTTPException(status_code=400, detail="The cover_end_use with this code already exists.")
    create_in.added_by = current_user.email
    regrade_impact = create(db_session=db_session, cover_end_use_in=create_in)
    if regrade_impact:
        regrade_impact.auto_end_use_flag = "N"
        runout = db_session.query(Runout).filter(Runout.id == regrade_impact.runout_id).first()
        runout.auto_end_use_flag = "N"
        db_session.commit()
    return regrade_impact

@router.delete("/delete_real/{cover_end_use_id}")
def delete_one(*, db_session: Session = Depends(get_db), cover_end_use_id: int):
    cover_end_use = get(db_session=db_session, id=cover_end_use_id)
    if not cover_end_use:
        raise HTTPException(status_code=400, detail="The cover_end_use with this id does not exist.")
    delete_real(db_session=db_session, cover_end_use=cover_end_use, cover_end_use_id=cover_end_use_id)


@router.delete("/delete_all_by_runout_id/{runout_id}")
def delete_All(*, db_session: Session = Depends(get_db), runout_id: int):
    runout = db_session.query(Runout).filter(Runout.id == runout_id).first()
    if not runout:
        raise HTTPException(status_code=400, detail="The runout with this id does not exist.")
    runout.auto_end_use_flag = "N"
    delete_by_runout_id(db_session=db_session, runout_id=runout_id)


@router.get("/get_spec_by_runout", )
def get_spec_by_runout(*, db_session: Session = Depends(get_db), runout_ids: list[int] = Query(alias="runout_ids[]")):
    ce = db_session.query(CoverEndUse).filter(CoverEndUse.runout_id.in_(runout_ids)).all()
    spec_ids = [spec.spec_id for spec in ce]
    return db_session.query(Spec).filter(Spec.id.in_(spec_ids)).all()


@router.post("/batch_cover", response_model=FinishedProductBatchHold)
def batch_cover(
    *,
    background_tasks: BackgroundTasks,
    db_session: Session = Depends(get_db),
    Finished_in: FinishedProductHoldReason,
    current_user: DispatchUser = Depends(get_current_user),
    runout_code1: int = Query(None), runout_code2: int = Query(None), order_id: int = Query(None), advice_id: int = Query(None),
    rolling_id: int = Query(None),
    cast_id: int = Query(None),
    order_item_id: int = Query(None)
):
    test_ids = Finished_in.test_ids
    total_count = 0
    success_count = 0
    failure_count = 0

    query = db_session.query(FinishedProduct)
    if runout_code2 and runout_code1:
        max_code = str(max(runout_code1, runout_code2))
        min_code = str(min(runout_code1, runout_code2))
        runouts_in_range = db_session.query(Runout).filter(Runout.runout_code.between(min_code, max_code)).all()
        runout_ids = [runout.id for runout in runouts_in_range]
        query = query.filter(FinishedProduct.runout_id.in_(runout_ids))
    if order_id:
        query = query.filter(FinishedProduct.order_id == order_id)
    if order_item_id:
        query = query.filter(FinishedProduct.order_item_id == order_item_id)
    if advice_id:
        FinishedProductAdvice = aliased(finished_product_advice)
        finished_product_adive_data = db_session.query(FinishedProductAdvice).filter(FinishedProductAdvice.c.advice_id == advice_id).all()
        finished_product_id = [finished_product_advices.finished_product_id for finished_product_advices in finished_product_adive_data]
        query = query.filter(FinishedProduct.id.in_(finished_product_id))
    if rolling_id:
        query = query.filter(FinishedProduct.rolling_id == rolling_id)
    if cast_id:
        query = query.filter(FinishedProduct.cast_id == cast_id)

    subquery = (
        db_session.query(FinishedProduct.id)
        .filter(
            and_(
                # FinishedProduct.cover_status == 'W',
                FinishedProduct.mill_id == current_user.current_mill_id,
                exists().where(
                    and_(
                        TestSample.runout_id == FinishedProduct.runout_id,
                        Test.test_sample_id == TestSample.id,
                        TestImpact.test_id == Test.id
                    )
                ),
                exists().where(
                    and_(
                        TestSample.runout_id == FinishedProduct.runout_id,
                        Test.test_sample_id == TestSample.id,
                        TestTensile.test_id == Test.id
                    )
                )
            )
        )
        .distinct()
        .subquery('subquery')
    )

    # 通过子查询获取完整的 FinishedProduct 对象
    final_query = (
        query.join(subquery, FinishedProduct.id == subquery.c.id)
    )

    processed_finished_product_ids = []
    for finished_product in final_query.all():
        processed_finished_product_ids.append(finished_product.id)
        total_count += 1
        if get_mill_ops(current_user.current_mill_id) == MILLEnum.MILL1 :
            if test_ids:
                srsm = srsm_compare_finished_product_manual(db_session=db_session, finished_product=finished_product, test_ids=test_ids)
            else:
                srsm = srsm_compare_finished_product_spec_result(db_session=db_session, finished_product=finished_product)
            if srsm is None:
                failure_count += 1
            else:
                success_count += 1
        else:
            cover = compare_finished_product_spec_result(db_session=db_session, finished_product=finished_product, test_ids=test_ids, is_batch=True)
            if cover is not None:
                success_count += 1
            else:
                failure_count += 1

    query = query.filter(FinishedProduct.id.notin_(processed_finished_product_ids))

    for finished_product in query.order_by(desc(FinishedProduct.code)).all():
        total_count += 1
        if get_mill_ops(current_user.current_mill_id) == MILLEnum.MILL1 :
            if test_ids:
                srsm = srsm_compare_finished_product_manual(db_session=db_session, finished_product=finished_product, test_ids=test_ids)
            else:
                srsm = srsm_compare_finished_product_spec_result(db_session=db_session, finished_product=finished_product)
            if srsm is None:
                failure_count += 1
            else:
                success_count += 1
        else:
            if finished_product.allocation_status in ['scrap']:
                failure_count += 1
                continue
            if (finished_product.mult_type == 'R' and finished_product.exist_flag == 'Y') or \
                (finished_product.mult_type is None and finished_product.exist_flag is None) or \
                (finished_product.mult_type is None and finished_product.exist_flag == 'Y'):
                cover = compare_finished_product_spec_result(db_session=db_session, finished_product=finished_product, test_ids=test_ids, is_batch=True)
                if cover is not None:
                    success_count += 1
                else:
                    failure_count += 1
            else:
                failure_count += 1
    count = {
        "success_count": success_count,
        "failure_count": failure_count,
        "total_count": total_count
    }
    return count


@router.post("/batch_uncover")
def batch_uncover(
    *,
    background_tasks: BackgroundTasks,
    db_session: Session = Depends(get_db),
    Finished_in: FinishedProductHoldReason,
    current_user: DispatchUser = Depends(get_current_user),
    runout_code1: int = Query(None), runout_code2: int = Query(None), order_id: int = Query(None), advice_id: int = Query(None),
    rolling_id: int = Query(None),
    cast_id: int = Query(None)
):
    update_at = datetime.now()
    finisheds = []
    total_count = 0
    success_count = 0
    failure_count = 0
    finished_products_list = []
    FinishedProductAdvice = aliased(finished_product_advice)
    query = db_session.query(FinishedProduct)
    if runout_code2 and runout_code1:
        max_code = str(max(runout_code1, runout_code2))
        min_code = str(min(runout_code1, runout_code2))
        runouts_in_range = db_session.query(Runout).filter(Runout.runout_code.between(min_code, max_code))
        runout_ids = [runout.id for runout in runouts_in_range]
        query = query.filter(FinishedProduct.runout_id.in_(runout_ids))
    if order_id:
        query = query.filter(FinishedProduct.order_id == order_id)
    if advice_id:
        finished_product_adive_data = db_session.query(FinishedProductAdvice).filter(FinishedProductAdvice.c.advice_id == advice_id)
        finished_product_id = [finished_product_advices.finished_product_id for finished_product_advices in finished_product_adive_data]
        query = query.filter(FinishedProduct.id.in_(finished_product_id))
    if rolling_id:
        query = query.filter(FinishedProduct.rolling_id == rolling_id)
    if cast_id:
        query = query.filter(FinishedProduct.cast_id == cast_id)
    for finished_product in query.all():
        total_count += 1
        finished_product_in = UnCoverUpdate(id=finished_product.id)
        finished_product_in.updated_by = current_user.email
        finished_product_in.updated_at = update_at
        finished_product_in.cover_status = 'W'
        finished_products_list.append(finished_product_in.model_dump())
        delete_by_finished_product_id(db_session=db_session, finished_product_id=finished_product_in.id)
        un_over = batch_update(db_session=db_session, body=finished_products_list)
        if un_over is True:
            success_count += 1
        else:
            failure_count += 1
    return {"total_count": total_count, "success_count": success_count, "failure_count": failure_count}


@router.post("/uncover")
def uncover(
    *,
    db_session: Session = Depends(get_db),
    finished_products_in: List[int],
    current_user: DispatchUser = Depends(get_current_user)
):
    update_at = datetime.now()
    finished_products_list = []
    for finished_product_id in finished_products_in:
        finished_product_in = UnCoverUpdate(id=finished_product_id)
        finished_product_in.updated_by = current_user.email
        finished_product_in.updated_at = update_at
        finished_products_list.append(finished_product_in.model_dump())
        delete_by_finished_product_id(db_session=db_session, finished_product_id=finished_product_in.id)
    return batch_update(db_session=db_session, body=finished_products_list)
