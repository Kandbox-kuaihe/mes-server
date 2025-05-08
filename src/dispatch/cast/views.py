import numpy as np
from dispatch.database import get_db
from sqlalchemy import or_
import os
import csv
import io
import pandas as pd
from fastapi.responses import FileResponse

from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, BackgroundTasks, Request
from sqlalchemy.orm import Session
from dispatch.system_admin.auth.models import DispatchUser
from dispatch.system_admin.auth.service import get_current_user

# 不要移出 Quality QualityElement QualityOtherElement
from dispatch.spec_admin.quality.models import Quality
from dispatch.spec_admin.quality_element.models import QualityElement
from dispatch.spec_admin.quality_other_element.models import QualityOtherElement
#


from dispatch.database_util.service import common_parameters, search_filter_sort_paginate
from .models import (
    Cast,
    CastCreate,
    CastPagination,
    CastRead,
    CastUpdate,
    CastQualityCompare
)
from .service import (
    create,
    delete,
    get,
    update,
    import_file,
    get_codes,
    update_authorize_date,
    auto_generate_code,
    get_cast_by_semi_load,
    export_to_excel, import_dict_to_db_new
)
import logging
from dispatch.message_admin.message_server.models import PushMessageData
from dispatch.mill.models import Mill
from ..config import MILLEnum, get_mill_ops

logging.basicConfig(level=logging.INFO)

from dispatch.log import getLogger

log = getLogger(__name__)
router = APIRouter()


@router.get("/", response_model=CastPagination)
def get_filters(*, db_session: Session = Depends(get_db), common: dict = Depends(common_parameters), current_user: DispatchUser = Depends(get_current_user)):
    query = db_session.query(Cast).outerjoin(Quality, Cast.quality_id == Quality.id).outerjoin(Mill,
                                                                                               Cast.mill_id == Mill.id)
    if common["query_str"]:
        query_str = common["query_str"]
        common["query_str"] = ''
        common['query'] = query.filter(
            or_(Cast.cast_code.like(f'%{query_str}%'),
                Cast.bos_cast_code.like(f'%{query_str}%'),
                Quality.code.like(f'%{query_str}%'),
                )
        )
        common["query_str"] = ''

    # if common["query_str"]:
    #     common["filter_type"]  = "or"
    #     common["fields"] = ["cast_code", "bos_cast_code", "quality.code"]
    #     common["ops"] = ["like", "like", "like"]
    #     common["values"] = [f"%{common['query_str']}%", f"%{common['query_str']}%", f"%{common['query_str']}%"]
    #     common["query_str"] = ''
    result_items = search_filter_sort_paginate(model="Cast", **common)
    mill_id = current_user.current_mill_id
    items = result_items.get("items")
    for item in items:
        item.cast_semis = [semi for semi in item.cast_semi if semi.mill_id == mill_id]
    return result_items


@router.post("/", response_model=CastRead)
def create_obj(*, request: Request, background_tasks: BackgroundTasks, db_session: Session = Depends(get_db),
               request_in: CastCreate,
               current_user: DispatchUser = Depends(get_current_user)):
    """
    Create a new cast contact.
    """
    if hasattr(request_in, 'cast_semis'):
        delattr(request_in, 'cast_semis')
    if request_in.quality_id:
        quality_code = db_session.query(Quality).filter(Quality.id == request_in.quality_id).first()
        request_in.quality_code = quality_code.code

    request_in.created_by = current_user.email
    request_in.updated_by = current_user.email
    cast = create(db_session=db_session, cast_in=request_in)
    # trigger M202 message
    try:
        from dispatch.contrib.message_admin.message_server.server import call_method
        if get_mill_ops(current_user.current_mill_id) == MILLEnum.MILL1 and cast.cast_code:
            message = PushMessageData(id=202, type="srsmpc", msg=str(cast.cast_code))
            call_method(request, background_tasks, db_session, current_user, message)
    except ImportError as e:
        log.warning(f"call_method 202 fail {e}")
        # raise HTTPException(status_code=400, detail=str(e))
    return cast


@router.get("/{cast_id}", response_model=CastRead)
def get_cast(*, db_session: Session = Depends(get_db), cast_id: int):
    """
    Get a cast contact.
    """
    cast = get(db_session=db_session, id=cast_id)
    if not cast:
        raise HTTPException(status_code=400, detail="The cast with this id does not exist.")
    return cast


@router.post("/import_cast")
def import_cast(*, request: Request, background_tasks: BackgroundTasks, db_session: Session = Depends(get_db),
                files: List[UploadFile],
                current_user: DispatchUser = Depends(get_current_user)):
    cast = import_file(db_session=db_session, files=files, current_user=current_user)

    create_or_update_codes = cast.pop("create_or_update_codes", [])
    # trigger M202 message
    try:
        from dispatch.contrib.message_admin.message_server.server import call_method
        if get_mill_ops(current_user.current_mill_id) == MILLEnum.MILL1:
            for cast_code in create_or_update_codes:
                message = PushMessageData(id=202, type="srsmpc", msg=str(cast_code))
                call_method(request, background_tasks, db_session, current_user, message)
    except ImportError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return cast


@router.put("/{cast_id}", response_model=CastRead)
def update_cast(
        *,
        db_session: Session = Depends(get_db),
        cast_id: int,
        cast_in: CastUpdate, current_user: DispatchUser = Depends(get_current_user)
):
    """
    Update a cast contact.
    """
    cast = get(db_session=db_session, id=cast_id)
    if not cast:
        raise HTTPException(status_code=400, detail="The cast with this id does not exist.")

    cast = update(
        db_session=db_session,
        cast=cast,
        cast_in=cast_in,
    )

    return cast


# @router.put("/cast_code/{cast_code}", response_model=CastRead)
# def update_cast_by_code(
#     *,
#     db_session: Session = Depends(get_db),
#     cast_code: str,
#     cast_in: CastUpdate, current_user: DispatchUser = Depends(get_current_user)
# ):
#     """
#     Update a cast contact.
#     """
#     cast = get_by_code(db_session=db_session, code=cast_code)
#     if not cast:
#         raise HTTPException(status_code=400, detail="The cast with this id does not exist.")

#     cast_in.updated_by = current_user.email
#     cast = update(
#         db_session=db_session,
#         cast=cast,
#         cast_in=cast_in,
#     )

#     return cast


@router.delete("/{cast_id}", response_model=CastRead)
def delete_cast(*, db_session: Session = Depends(get_db), cast_id: int):
    """
    Delete a cast contact.
    """
    cast = get(db_session=db_session, id=cast_id)
    if not cast:
        raise HTTPException(status_code=400, detail="The cast with this id does not exist.")

    return delete(db_session=db_session, id=cast_id)


@router.get("/item/codes")
def get_code(db_session: Session = Depends(get_db)):
    # print(id)
    ls = get_codes(db_session=db_session)
    return ls


@router.get(
    "/cast_quality/item/{quality_id}",
)
def get_cast_quality(*, db_session: Session = Depends(get_db), quality_id: int):
    """
    Get a cast contact.
    """
    quality = db_session.query(QualityElement).filter(QualityElement.quality_id == quality_id).first()
    if quality:
        other_quality = db_session.query(QualityOtherElement).filter(
            QualityOtherElement.quality_element_id == quality.id).all()
        # 拼接otherElement 供cast 页对比使用
        for oth in other_quality:
            abbr = oth.element_abbr or oth.code.lower()
            setattr(quality, f"precision_{abbr}", oth.precision)
            setattr(quality, f"main_el_min_value_{abbr}", oth.min_value)
            setattr(quality, f"main_el_max_value_{abbr}", oth.max_value)
    return quality or {}


@router.get("/cast_quality/quality_list")
def get_quality_list(*, db_session: Session = Depends(get_db), common: dict = Depends(common_parameters)):
    return search_filter_sort_paginate(model="Quality", **common)


@router.put("/authorize_date/{cast_id}")
def authorize_date(*, db_session: Session = Depends(get_db), cast_id: int):
    cast = update_authorize_date(db_session=db_session, cast_id=cast_id)
    return cast


@router.get("/code/generate_code")
def generate_code(*, db_session: Session = Depends(get_db)):
    cast_code, generate_code = auto_generate_code(db_session=db_session)
    return {"cast_code": cast_code, "generate_code": generate_code}


@router.post("/cast_quality/compare")
def compare_quality(*, compare_in: CastQualityCompare, db_session: Session = Depends(get_db),
                    current_user: DispatchUser = Depends(get_current_user)):
    semi_load_ids = compare_in.semi_load_ids
    casts = get_cast_by_semi_load(db_session=db_session, semi_load_ids=semi_load_ids)
    if not casts:
        raise HTTPException(status_code=400, detail="Cast not found")

    cast_quality_result = []
    for cast in casts:
        res = {
            "cast_id": cast.id,
            "cast_code": cast.cast_code,
        }

        # cast.quality_id = 383
        # 可能会有数据没有绑定quality id，但是有quality code. 如果不存在quality，不允许tip
        if not cast.quality_id:
            """保留，避免后续需求改动
            if not cast.quality_code:
                res["isable_tip"] = False
                cast_quality_result.append(res)
                continue

            quality = quality_service.get_by_code_and_mill(
                db_session=db_session, code=cast.quality_code, mill_id=current_user.current_mill_id
            )
            if not quality:
                res["isable_tip"] = False
                cast_quality_result.append(res)
                continue

            cast.quality_id = quality.id
            """

            res["isable_tip"] = False
            cast_quality_result.append(res)
            continue

        quality_ele = db_session.query(QualityElement).filter(QualityElement.quality_id == cast.quality_id).first()
        # 如果没有 quality element, 允许tip
        if not quality_ele:
            res["isable_tip"] = True
            cast_quality_result.append(res)
            continue

        other_quality = db_session.query(QualityOtherElement).filter(
            QualityOtherElement.quality_element_id == quality_ele.id).all()
        # 拼接otherElement 供cast 页对比使用
        for oth in other_quality:
            abbr = oth.element_abbr or oth.code.lower()
            setattr(quality_ele, f"precision_{abbr}", oth.precision)
            setattr(quality_ele, f"main_el_min_value_{abbr}", oth.min_value)
            setattr(quality_ele, f"main_el_max_value_{abbr}", oth.max_value)

        out_of_range_records = []
        for attr in vars(Cast):
            if attr.startswith('ch_'):
                element = attr[3:]  # 提取元素名称
                max_attr = f'main_el_max_value_{element}'
                min_attr = f'main_el_min_value_{element}'
                # 检查 quality 模型中是否存在对应的最大值和最小值属性
                if hasattr(quality_ele, max_attr) and hasattr(quality_ele, min_attr):
                    max_value = getattr(quality_ele, max_attr)
                    min_value = getattr(quality_ele, min_attr)
                    value = getattr(cast, attr)
                    if value and all([max_value, min_value]) and (value < min_value or value > max_value):
                        out_of_range_records.append({
                            'cast_id': cast.id,
                            'element': attr,
                            'value': value,
                            'min_value': min_value,
                            'max_value': max_value
                        })
        log.info(f"Cast Quality compare err result: {out_of_range_records}")

        if out_of_range_records:
            res["isable_tip"] = False
        else:
            res["isable_tip"] = True
        cast_quality_result.append(res)

    return cast_quality_result


@router.post("/export_cast_file")
def export_rolling(*, db_session: Session = Depends(get_db), common: dict = Depends(common_parameters),
                   current_user: DispatchUser = Depends(get_current_user), start_date: str = Query(None),
                   end_date: str = Query(None)):
    query = (db_session.query(Cast).outerjoin(Quality, Cast.quality_id == Quality.id).outerjoin
             (Mill, Cast.mill_id == Mill.id))
    common['query'] = query
    common['items_per_page'] = None
    if common["query_str"]:
        query_str = common["query_str"]
        common["query_str"] = ''
        common['query'] = query.filter(
            or_(Cast.cast_code.like(f'%{query_str}%'),
                Cast.bos_cast_code.like(f'%{query_str}%'),
                Quality.code.like(f'%{query_str}%'),
                )
        )
        common["query_str"] = ''

    # 调用 export_to_excel 函数生成 Excel 文件并返回文件路径
    data = search_filter_sort_paginate(model="Cast", **common)['items']
    file_path = export_to_excel(db_session=db_session, data_list=data)

    # 如果文件生成成功，返回该文件
    if file_path:
        file_name = os.path.basename(file_path)  # 获取文件名
        response = FileResponse(
            file_path, filename=file_name
        )
        return response
    else:
        raise HTTPException(status_code=400, detail="File generation failed.")


@router.post("/import_cast_file_new")
def import_cast(*, db_session: Session = Depends(get_db), file: UploadFile = File(...),
                current_user: DispatchUser = Depends(get_current_user)):
    file_type = file.filename.split(".")[-1]
    if file_type == 'csv':
        c = file.file.read()
        csv_file = io.StringIO(c.decode('utf-8'))
        reader = csv.DictReader(csv_file)
        rows = list(reader)
    elif file_type == 'xlsx':
        df = pd.read_excel(file.file.read())
        df = df.replace({np.nan: None})
        rows = df.to_dict(orient="records")
    else:
        raise HTTPException(status_code=400, detail="The file type is not supported.")
    add_cnt, update_cnt = import_dict_to_db_new(db_session=db_session, rows=rows, curr_user=current_user.email)
    return {"add_cnt": add_cnt, "update_cnt": update_cnt}
