from dispatch.database import get_db
from typing import List, Optional

from copy import copy
from sqlalchemy import tuple_
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from dispatch.database_util.service import common_parameters, search_filter_sort_paginate
from dispatch.semi_admin.semi import service as semi_service
from dispatch.semi_admin.semi.models import SemiPagination,Semi
from dispatch.spec_admin.spec.models import Spec
from dispatch.cast.models import Cast
from dispatch.area.models import Area
from dispatch.product_type.models import ProductType
from dispatch.rolling.rolling_list.models import Rolling
from dispatch.order_admin.order_group.models import OrderGroup
from dispatch.system_admin.auth.models import DispatchUser
from dispatch.system_admin.auth.service import get_current_user

from .models import (
    CastSpec,
    CastSpecPagination,
)
from .service import get_max_cast_id, delete_by_cast_id, get_unique_cast_ids_by_spec_ids
from .service import create, delete, get, get_max_cast_id, reset_sequence_to_max_id, batch_insert_cast_spec, delete_by_cast_id, get_unique_cast_ids_by_spec_ids
from ..config import get_mill_ops, MILLEnum
from ..semi_admin.semi.service import update_semi_by_move

router = APIRouter()

# spec_id list 类型， get =>  semi 列表

from dispatch.spec_admin.spec import service as spec_service
from dispatch.product_type import service as product_type_service
from dispatch.cast import service as cast_service
from dispatch.semi_admin.semi_end_use_manual import service as semi_end_use_manual_service
from dispatch.order_admin.order_group import service as order_group_service
from dispatch.spec_admin.alt_quality_code import service as alt_quality_code_service
from dispatch.semi_admin.alternative_semi_size.models import AlternativeSemiSize
from dispatch.semi_admin.semi.service import get_hold_semi


# @router.get("/")
def get_result(
    db_session: Session = Depends(get_db),
    spec_ids: List[int] = Query([], alias="spec_ids[]"),
    spec_codes: List[str] = Query([], alias="spec_codes[]"),
):

    if spec_codes:
        specs = spec_service.get_by_spec_codes(db_session=db_session, spec_codes=spec_codes)
        spec_ids = [item.id for item in specs]
    spec_ids = list(set(spec_ids))
    semilist = semi_service.get_by_spec_ids(db_session=db_session, spec_ids=spec_ids)
    return semilist


@router.get("/", response_model=SemiPagination)
def get_results(
    *,
    common: dict = Depends(common_parameters),
    spec_ids: List[int] = Query([], alias="spec_ids[]"),
    order_group_id: int=Query(int, alias="order_group_id"),
    spec_codes: List[str] = Query([], alias="spec_codes[]"),
    semi_size:List[str] = Query([], alias="semi_size[]"),
    rolling_id: Optional[int]=Query(None, alias="rolling_id")
):
    query = common["db_session"].query(Semi).outerjoin(Area, Semi.area_id == Area.id
        ).outerjoin(Cast, Semi.cast_id == Cast.id 
        ).outerjoin(OrderGroup, Semi.order_group_id == OrderGroup.id
        ).outerjoin(Rolling, Semi.rolling_id == Rolling.id)
    cast_fields = common["fields"]
    cast_ops = common["ops"]
    cast_values = common["values"]
    if spec_codes:
        specs = spec_service.get_by_spec_codes(db_session=common["db_session"], spec_codes=spec_codes)
        spec_ids = [item.id for item in specs]
    cast_ids = get_unique_cast_ids_by_spec_ids(db_session=common["db_session"], spec_ids=spec_ids)
    order_group = order_group_service.get(db_session=common["db_session"], id=order_group_id)
    kg = order_group.product_type.dim3
    m_end_use = semi_end_use_manual_service.get_by_spec_ids_kg(db_session=common["db_session"], spec_ids=spec_ids, kg=kg)
    if m_end_use:
        cast_ids.extend([m_cast.cast_id for m_cast in m_end_use if m_cast.cast])

    common["filter_type"]  = [['or','or'], "and", "and", "and"]
    common["fields"] = ["rework_status", "rework_status", "cast_id", "area.charge_status", "defect_reason_id"]
    common["ops"] = ["is_null", "==", "in", "==", "=="]
    common["values"] = [True, "Complete", cast_ids, 'Y', None]
    if get_mill_ops(common['current_user'].current_mill_id) == MILLEnum.MILL1:
        order_spec_group_list = order_group_service.get_order_spec_group_by_order_group(db_session=common["db_session"], order_group_id=order_group_id)
        quality_code_list = [spec_group.quality_code for spec_group in  order_spec_group_list if spec_group.quality_code]
        for code in quality_code_list:
            query_result = alt_quality_code_service.get_by_quality(db_session=common["db_session"], code=code)
            if query_result:
                for result in  query_result:
                    if result.alt_quality_code and result.alt_quality_code not in quality_code_list:
                        quality_code_list.append(result.alt_quality_code)
        
        common["filter_type"].append("and")
        common["fields"].append("cast.quality_code")
        common["ops"].append("in")
        common["values"].append(quality_code_list)
        
    if cast_values:
        common["filter_type"].extend(["and"] * len(cast_fields))
        common["fields"].extend(cast_fields)
        common["ops"].extend(cast_ops)
        common["values"].extend(cast_values)

    semi_hold_list = get_hold_semi(db_session=common["db_session"])

    not_in_locations = ['TBM_Furnace', 'TBM_Rolling', 'Rolled', "COGG", "BANK", "SAW", "FURN"]
    common["filter_type"].append(['or', 'or'])
    common["fields"].extend(['location', 'location'])
    common["ops"].extend(["==", "not_in"])
    common["values"].extend([None, not_in_locations])
    # 模拟 not in 条件转换为 and 多个!= 条件
    new_filter_types = []
    new_fields = []
    new_ops = []
    new_values = []
    for semi_hold in semi_hold_list:
        if semi_hold:
            new_filter_types.append('and')
            new_fields.append('id')
            new_ops.append('!=')
            new_values.append(semi_hold.semi_id)


    common["filter_type"].extend(new_filter_types)
    common["fields"].extend(new_fields)
    common["ops"].extend(new_ops)
    common["values"].extend(new_values)
    alternative_semi_size_info = common["db_session"].query(AlternativeSemiSize).filter(AlternativeSemiSize.product_type_id == order_group.product_id,
                                                                                        AlternativeSemiSize.mill_id == common['current_user'].current_mill_id
                                                                                        ).order_by(AlternativeSemiSize.rank_seq.asc())
    dim_pairs = []
    if alternative_semi_size_info:
        dim_pairs = [(alt_semi_size.semi_size.width_mm, alt_semi_size.semi_size.thick_mm) for alt_semi_size in alternative_semi_size_info]

    query = query.filter(
    tuple_(Semi.dim1, Semi.dim2).in_([tuple(dim_pair) for dim_pair in dim_pairs]))

    if semi_size:
        query = query.filter( tuple_(Semi.dim1, Semi.dim2).in_([tuple([int(i) for i in size.split('x')]) for size in semi_size]))
    if rolling_id:
        query = query.filter(Semi.rolling_id == rolling_id)
    
    common['query'] = query
    common = semi_service.sort_semi(common=common, order_group=order_group, dim_pairs=dim_pairs)
    semi_info = search_filter_sort_paginate(model="Semi", **common)
    return semi_info


@router.post("/reverse")
def get_reverse(
    *,data: dict,
    db_session: Session = Depends(get_db),
    common: dict = Depends(common_parameters),
    spec_ids: List[int] = Query([], alias="spec_ids[]"),
):

    id_list = data["list"]
    rolling_id = data["rolling_id"]
    records_to_update = db_session.query(Semi).filter(
        Semi.id.in_(id_list),
        Semi.rolling_id == rolling_id,
        Semi.is_deleted == 0
    ).order_by(Semi.semi_charge_seq).all()
    # 按照数量更新其semi_charge_seq字段
    new_seq_values = {record.id: len(records_to_update) - i - 1 for i, record in enumerate(records_to_update)}
    update_mappings = [
        {'id': record.id, 'semi_charge_seq': new_seq_values[record.id]}
        for record in records_to_update
    ]
    db_session.bulk_update_mappings(Semi, update_mappings)
    print(update_mappings)
    db_session.commit()
    return True


@router.post("/init_all")
def init_all(db_session: Session = Depends(get_db), current_user: DispatchUser = Depends(get_current_user)):
    cast_list = cast_service.get_by_mill(db_session=db_session, mill_id=current_user.current_mill_id)
    # reset_sequence_to_max_id(db_session=db_session)
    max_cast_id = get_max_cast_id(db_session=db_session)
    for cast in cast_list:
        if cast.id > max_cast_id and cast.ch_c and cast.ch_mn and cast.ch_cr:
            try:
                from dispatch.contrib.cover.get_spec_service.utils import batch_insert
                batch_insert(db_session=db_session, cast=cast, mill_id=current_user.current_mill_id)
            except ImportError as e:
                raise HTTPException(status_code=400, detail=str(e))
    return True


@router.post("/run_end_use/{cast_id}")
def run_end_use(*, db_session: Session = Depends(get_db), cast_id: int, current_user: DispatchUser = Depends(get_current_user)):
    cast = cast_service.get(db_session=db_session, id=cast_id)
    if not cast:
        raise HTTPException(status_code=400, detail="The cast with this id does not exist.")
    if not cast.ch_c:
        raise HTTPException(status_code=400, detail="The cast  is missing element information.")
    delete_by_cast_id(db_session=db_session, cast_id=cast_id)
    if get_mill_ops(current_user.current_mill_id) == MILLEnum.MILL1:
        try:
            from dispatch.contrib.cover.get_spec_service.utils_srsm import batch_insert as srsm_batch_insert
            srsm_batch_insert(db_session=db_session, cast=cast, mill_id=current_user.current_mill_id)
        except ImportError as e:
            raise HTTPException(status_code=400, detail=str(e))
    else:
        try:
            from dispatch.contrib.cover.get_spec_service.utils import batch_insert
            batch_insert(db_session=db_session, cast=cast, mill_id=current_user.current_mill_id)
        except ImportError as e:
            raise HTTPException(status_code=400, detail=str(e))
    return

@router.post("/run_end_use_sct/{cast_id}")
def run_end_use(*, db_session: Session = Depends(get_db), cast_id: int, current_user: DispatchUser = Depends(get_current_user)):
    cast = cast_service.get(db_session=db_session, id=cast_id)
    if not cast:
        raise HTTPException(status_code=400, detail="The cast with this id does not exist.")
    if not cast.ch_c:
        raise HTTPException(status_code=400, detail="The cast  is missing element information.")
    delete_by_cast_id(db_session=db_session, cast_id=cast_id)
    try:
        product_type = product_type_service.get_by_mill(db_session=db_session, mill_id=current_user.current_mill_id)
        specs = spec_service.get_all(db_session=db_session)
        order_spec_ids = list(set([item.id for item in specs if item.id is not None]))

        all_cast_spec = []
        for pro in product_type:
            if pro.flange_thickness:
                spec_ids = copy(order_spec_ids)

                for spec_id in spec_ids:
                    kwargs = {"spec_id": spec_id, "cast_id": cast.id, "product_type_id": pro.id}
                    all_cast_spec.append(kwargs)
        batch_insert_cast_spec(db_session=db_session, cast_spec_ins=all_cast_spec)
    except ImportError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return


@router.get("/cast_spec_list/{cast_id}", response_model=CastSpecPagination)
def get_cast_spec_list(cast_id,db_session=Depends(get_db), common: dict = Depends(common_parameters)):

    query = db_session.query(CastSpec).outerjoin(Spec, CastSpec.spec_id == Spec.id)
    common['query'] = query
    if common["sort_by"] == ['spec_id']:
        common["sort_by"] = ["spec.spec_code"]
    common['fields'].append("cast_id")
    common['ops'].append("==")
    common['values'].append(cast_id)
    q = common["query_str"]
    if q:
        common["filter_type"]  = "or"
        common["fields"] = [ "spec.spec_code"]
        common["ops"] = ["like"] 
        common["values"] = [f'%{q}%']
        common['query_str'] = ''
    
    return search_filter_sort_paginate(model="CastSpec", **common)  


@router.get("/cast_spec_all", response_model=CastSpecPagination)
def get_cast_spec_list(
    db_session=Depends(get_db),
    common: dict = Depends(common_parameters)
):
    """
    Get a list of CastSpec with associated AlternativeSemiSize based on product_type_id.
    """
    # Base query for CastSpec only
    query = (
        db_session.query(CastSpec)
        .outerjoin(Spec, CastSpec.spec_id == Spec.id)
        .outerjoin(Cast, CastSpec.cast_id == Cast.id)
        .outerjoin(ProductType, CastSpec.product_type_id == ProductType.id)
    )

    # Assign query to common for search, filter, and pagination
    common['query'] = query

    # Apply filters based on query string
    q = common.get("query_str")
    if q:
        common["filter_type"] = "or"
        common["fields"] = ["spec.spec_code", "cast.cast_code"]
        common["ops"] = ["like", "like"]
        common["values"] = [f'%{q}%', f'%{q}%']
        common['query_str'] = ''  # Clear the query string

    sort_list = []
    if common["sort_by"]:
        for key in common["sort_by"]:
            if key == 'spec_code':
                sort_list.append("spec.spec_code")
            elif key == 'cast_code':
                sort_list.append("cast.cast_code")
            elif key == 'weights':
                sort_list.append("product_type.dim3")
            elif key == 'product_category':
                sort_list.append("product_type.code")
        common["sort_by"] = sort_list

    # Fetch paginated CastSpec results
    cast_spec_result = search_filter_sort_paginate(model="CastSpec", **common)

    # Extract product_type_ids from the CastSpec results
    product_type_ids = [
        cast_spec.product_type_id for cast_spec in cast_spec_result["items"] if cast_spec.product_type_id
    ]

    # Fetch all AlternativeSemiSize records for the relevant product_type_ids
    if product_type_ids:
        alt_semi_sizes = (
            db_session.query(AlternativeSemiSize)
            .filter(AlternativeSemiSize.product_type_id.in_(product_type_ids))
            .order_by(AlternativeSemiSize.rank_seq.asc())
            .all()
        )
    else:
        alt_semi_sizes = []

    # Map AlternativeSemiSize to their respective product_type_id
    alt_semi_map = {}
    for alt_semi in alt_semi_sizes:
        if alt_semi.product_type_id not in alt_semi_map:
            alt_semi_map[alt_semi.product_type_id] = []
        alt_semi_map[alt_semi.product_type_id].append(alt_semi)

    # Attach AlternativeSemiSize to each CastSpec
    for cast_spec in cast_spec_result["items"]:
        if cast_spec.product_type_id in alt_semi_map:
            # Attach only the top-ranked semi size
            ranked_semi_sizes = sorted(alt_semi_map[cast_spec.product_type_id], key=lambda x: x.rank_seq)
            cast_spec.alt_semi_sizes = ranked_semi_sizes[:1]
        else:
            cast_spec.alt_semi_sizes = []

    # Return the paginated response
    return CastSpecPagination(
        total=cast_spec_result["total"],
        items=cast_spec_result["items"],
        itemsPerPage=cast_spec_result["itemsPerPage"],
        page=cast_spec_result["page"],
    )
