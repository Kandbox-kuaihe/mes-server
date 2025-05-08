import os
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Body,Query, BackgroundTasks
from fastapi.responses import FileResponse
from datetime import datetime, timezone

from sqlalchemy import func, case, distinct, Integer
from sqlalchemy.orm import Session
from dispatch.mill.models import Mill
from dispatch.product_class.models import ProductClass
from dispatch.product_type.models import ProductType
from dispatch.system_admin.auth.models import DispatchUser
from dispatch.system_admin.auth.service import get_current_user
from dispatch.database import get_db
from .models import (
    RollingCreate, RollingPagination, RollingRead, RollingUpdate, RollingUpdateStatus, 
    Rolling, RollingStatistics
)
from dispatch.runout_admin.runout_list.models import Runout
from dispatch.database_util.service import common_parameters, search_filter_sort_paginate


from .service import (
    delete, get, update, import_file, update_status, new_create_rolling, get_codes,
    get_by_code, export_to_excel, get_rolling_start_and_end_date,get_runout_list_by_rolling_id, 
    get_rolling_id_codes, import_csv_file, export_to_csv, order_item_kg_rolling_id
)
from dispatch.order_admin.order_item.service import order_item_group_need_fields
from dispatch.semi_admin.semi.models import SemiPagination
from dispatch.message_admin.message_server.service import sort_by_dim3, \
    allocated_block_v4
from dispatch.message_admin.message_server.models import PushMessageData
import logging
from ...order_admin.order_group.models import OrderGroup
from ...cast.models import Cast
from ...runout_admin.finished_product.models import FinishedProduct
from dispatch.common.utils.ftp_util import FTPTool
from dispatch.config import FTP_CONFIG
from fastapi.responses import JSONResponse
from fastapi import Request
logging.basicConfig(level=logging.INFO)

from dispatch.log import getLogger
log = getLogger(__name__)

router = APIRouter()


@router.get("/", response_model=RollingPagination)
def get_rolling(*, common: dict = Depends(common_parameters),db_session: Session = Depends(get_db), start_date:str = Query(None), end_date:str =Query(None)):
    query = db_session.query(Rolling).outerjoin(ProductClass, Rolling.product_class_id == ProductClass.id
                                    ).outerjoin(ProductType, Rolling.product_type_id == ProductType.id
                                    ).outerjoin(Mill, Rolling.mill_id == Mill.id)
                                                
    if start_date:
        query = query.filter(Rolling.created_at >= start_date)
    if end_date:
        query = query.filter(Rolling.created_at <= end_date)


    common['query'] = query
    if common["query_str"]:
        common["filter_type"]  = "and"
        common["fields"].extend(["rolling_code"])
        common["ops"].extend(["like"])
        common["values"].extend([f"%{common['query_str']}%"])
        common["query_str"] = ''
    result = search_filter_sort_paginate(model="Rolling", **common)
    for item in result["items"]:
        kg = order_item_kg_rolling_id(db_session, rolling_id=item.id)
        item.ordered_tons = kg
    return result


@router.get("/{id}", response_model=RollingRead)
def get_rolling_by_id(*, db_session: Session = Depends(get_db), id: int):
    """
    Update a rolling.
    """
    rolling = get(db_session=db_session, id=id)
    if not rolling:
        raise HTTPException(status_code=400, detail="The operation log with this id does not exist.")
    rolling.ordered_tons = order_item_kg_rolling_id(db_session, rolling_id=rolling.id)
    return rolling


@router.post("/", response_model=RollingRead)
def create_rolling(*, db_session: Session = Depends(get_db), rolling_in: RollingCreate,
                    current_user: DispatchUser = Depends(get_current_user),):
    """
    Create a new rolling.
    """
    if get_by_code(db_session=db_session, code=rolling_in.rolling_code, mill_id=current_user.current_mill_id):
        log.warning(f"The rolling code {rolling_in.rolling_code} already exists.")
        raise HTTPException(status_code=400, detail=f"The rolling code {rolling_in.rolling_code} already exists.")
    rolling_in.updated_by = current_user.email
    rolling_in.created_by = current_user.email
    rolling = new_create_rolling(db_session=db_session, rolling_in=rolling_in)
    return rolling


@router.put("/{id}", response_model=RollingRead)
def update_rolling(
    *, db_session: Session = Depends(get_db), id: int, rolling_in: RollingUpdate,
    current_user: DispatchUser = Depends(get_current_user),
):
    """
    Update a rolling.
    """
    rolling = get(db_session=db_session, id=id)
    if not rolling:
        raise HTTPException(status_code=400, detail="The rolling with this id does not exist.")

    rolling_in.updated_by = current_user.email
    rolling_in.updated_at = datetime.now(timezone.utc)
    rolling = update(db_session=db_session, rolling=rolling, rolling_in=rolling_in)
    return rolling


@router.delete("/{id}", response_model=RollingRead)
def delete_rolling(*, db_session: Session = Depends(get_db), id: int):
    """
    Delete a rolling.
    """

    rolling = get(db_session=db_session, id=id)
    if not rolling:
        raise HTTPException(status_code=400, detail="The rolling with this id does not exist.")
    delete(db_session=db_session, id=id)

    return RollingRead(id=id)

@router.post("/import_rolling_file")
def import_rolling(*,db_session: Session = Depends(get_db),file: UploadFile = File(...),
                   current_user: DispatchUser = Depends(get_current_user)):
    rolling = import_file(db_session=db_session, file=file, current_user=current_user)

    return rolling


@router.post("/import_rolling_file_from_ftp")
def import_rolling_from_ftp(*,db_session: Session = Depends(get_db), current_user: DispatchUser = Depends(get_current_user)):
    curr_mill_code = current_user.current_mill_code
    host = FTP_CONFIG[curr_mill_code]["mes_ftp"]["host"]
    user = FTP_CONFIG[curr_mill_code]["mes_ftp"]["username"]
    password = FTP_CONFIG[curr_mill_code]["mes_ftp"]["password"]
    port = FTP_CONFIG[curr_mill_code]["mes_ftp"]["port"]
    import_filename = FTP_CONFIG[curr_mill_code]["mes_ftp"]["filename"]
    
    # download file from ftp server
    with FTPTool(host=host, user=user, password=password, port=port) as ftp_tool:
        if ftp_tool:
            remote_filepath = import_filename
            temp_file_path = ftp_tool.download_file(remote_file_path=remote_filepath)
            info = import_csv_file(db_session=db_session, file=temp_file_path, current_user=current_user)
            return info

        raise HTTPException(status_code=400, detail="FTP connection failed.")
    return True


@router.post("/export_rolling_file")
def export_rolling(*, db_session: Session = Depends(get_db), common: dict = Depends(common_parameters),
                   current_user: DispatchUser = Depends(get_current_user), start_date:str = Query(None), end_date:str =Query(None)):
    # 调用 export_to_excel 函数生成 Excel 文件并返回文件路径
    query = db_session.query(Rolling).outerjoin(ProductClass, Rolling.product_class_id == ProductClass.id
                                    ).outerjoin(ProductType, Rolling.product_type_id == ProductType.id
                                    ).outerjoin(Mill, Rolling.mill_id == Mill.id)
    if start_date:
        query = query.filter(Rolling.created_at >= start_date)
    if end_date:
        query = query.filter(Rolling.created_at <= end_date)
    common['query'] = query
    common['items_per_page'] = None
    if common["query_str"]:
        common["filter_type"] = "and"
        common["fields"].extend(["rolling_code"])
        common["ops"].extend(["like"])
        common["values"].extend([f"%{common['query_str']}%"])
        common["query_str"] = ''
    data =  search_filter_sort_paginate(model="Rolling", **common)['items']
    file_path = export_to_excel(db_session=db_session,data_list=data)

    # 如果文件生成成功，返回该文件
    if file_path:
        file_name = os.path.basename(file_path)  # 获取文件名
        response = FileResponse(
            file_path,filename=file_name
        )
        return response
    else:
        raise HTTPException(status_code=400, detail="File generation failed.")
    

@router.post("/export_rolling_file_to_ftp")
def export_rolling_to_ftp(*, db_session: Session = Depends(get_db), common: dict = Depends(common_parameters),
                   current_user: DispatchUser = Depends(get_current_user), start_date:str = Query(None), end_date:str =Query(None)):
    # 调用 export_to_excel 函数生成 Excel 文件并返回文件路径
    query = db_session.query(Rolling).outerjoin(ProductClass, Rolling.product_class_id == ProductClass.id
                                    ).outerjoin(ProductType, Rolling.product_type_id == ProductType.id
                                    ).outerjoin(Mill, Rolling.mill_id == Mill.id)
    if start_date:
        query = query.filter(Rolling.created_at >= start_date)
    if end_date:
        query = query.filter(Rolling.created_at <= end_date)
    common['query'] = query
    common['items_per_page'] = None
    if common["query_str"]:
        common["filter_type"] = "and"
        common["fields"].extend(["rolling_code"])
        common["ops"].extend(["like"])
        common["values"].extend([f"%{common['query_str']}%"])
        common["query_str"] = ''
    data = search_filter_sort_paginate(model="Rolling", **common)['items']
    file_path = export_to_csv(data_list=data)

    # 如果文件生成成功，返回该文件
    if file_path:
        curr_mill_code = current_user.current_mill_code
        host = FTP_CONFIG[curr_mill_code]["pcc_ftp"]["host"]
        user = FTP_CONFIG[curr_mill_code]["pcc_ftp"]["username"]
        password = FTP_CONFIG[curr_mill_code]["pcc_ftp"]["password"]
        port = FTP_CONFIG[curr_mill_code]["pcc_ftp"]["port"]
        export_filename = FTP_CONFIG[curr_mill_code]["pcc_ftp"]["filename"]
        # Upload the file to FTP server
        with FTPTool(host=host, user=user, password=password, port=port) as ftp_tool:
            if ftp_tool:
                remote_file_path = export_filename
                res = ftp_tool.upload_file(local_file_path=file_path, remote_file_path=remote_file_path)
                return res
            raise HTTPException(status_code=400, detail="FTP connection failed.")
    else:
        raise HTTPException(status_code=400, detail="File generation failed.")


@router.post("/allocate_blocks")
def rolling_allocate_blocks(*,
        request: Request, 
        background_tasks: BackgroundTasks,
        db_session: Session = Depends(get_db),
        id: int=Body(..., embed=True),
        current_user: DispatchUser = Depends(get_current_user)):
    
    mill_id = current_user.current_mill_id
    if not mill_id:
        raise HTTPException(status_code=400, detail="Mill ID not found.")
    # one_rolling 参数：【False】 不开启点击一个rolling的allocated只生成该rolling的order group
    # mill_id = 1
    order_item_list = order_item_group_need_fields(db_session=db_session, mill_id=mill_id, rolling_id=id, one_rolling=False)
    if not order_item_list:
        raise HTTPException(status_code=400, detail="The order item list does not exist.")
    # 第一次调用为建立不存在的group
    # allocated_block(db_session=db_session, order_items=order_item_list, mill_id=mill_id)
    # 第二次是将其二次分配和更新数据
    order_group_ids = allocated_block_v4(db_session=db_session, order_items=order_item_list, mill_id=mill_id)
    # 拿到order_group_ids 后触发m240消息
    if len(order_group_ids):
        message = PushMessageData(id=240, type='srsmpc', msg=str(order_group_ids))
    try:
        from dispatch.contrib.message_admin.message_server.server import call_method
        call_method(request, background_tasks, db_session=db_session, current_user=current_user, message=message)
    except ImportError as e:
        log.warning(f"import error: {e}")
    except Exception as e:
        log.warning(f'Sending srsmpc-240 failed, reason: {e}')
    # sort_by_dim3(db_session=db_session)
    # 计算semi kg总和
    # semi_ton_spec_group(db_session=db_session)
    # computer_weight_spec_group(db_session=db_session)
    # # 找到最大的length
    # find_max_length(db_session=db_session)
    import time
    start = time.time()
    sort_by_dim3(db_session=db_session, mill_id=mill_id)
    end = time.time()
    log.warning(f"Sort by Dim3 spend time: {round((end - start), 3)}s")

    return 1 


@router.get("/print_charge_list/{id}", response_model=SemiPagination)
def print_charge_list(*,common: dict = Depends(common_parameters), id: int):
    common["fields"] = ["rolling_id"]
    common["ops"] = ["=="]
    common["values"] = [id]

    # 执行搜索、过滤、排序和分页
    result = search_filter_sort_paginate(model="Semi", **common)
    return result

@router.put("/change_rolling_status/{id}", response_model=RollingRead)
def update_rolling_status(
    *, db_session: Session = Depends(get_db), id: int, rolling_in: RollingUpdateStatus,
    current_user: DispatchUser = Depends(get_current_user),
):
    """
    Update a rolling status.
    """
    rolling = get(db_session=db_session, id=id)
    if not rolling:
        raise HTTPException(status_code=400, detail="The rolling with this id does not exist.")

    rolling_in.updated_by = current_user.email
    if rolling_in.rolling_status == "Open":
        rolling_in.open_time = datetime.now(timezone.utc)
    elif rolling_in.rolling_status == "Complete":
        rolling_in.complete_time = datetime.now(timezone.utc)
    rolling = update_status(db_session=db_session, rolling=rolling, rolling_in=rolling_in)
    return rolling


@router.get("/item/codes")
def get_code(db_session: Session = Depends(get_db)):
    # print(id)
    ls = get_codes(db_session=db_session)
    return ls


@router.get("/item/options")
def get_options(code: str, db_session: Session = Depends(get_db)):
    rollings = get_rolling_id_codes(db_session=db_session, code=code)
    options = [{"value": r[0], "text": r[1]} for r in rollings]
    return options


@router.get("/statistics/", response_model=RollingStatistics)
def get_statistic(db_session: Session = Depends(get_db), common: dict = Depends(common_parameters), start_date:str = Query(None), end_date:str =Query(None)):
    query = db_session.query(Rolling).outerjoin(Runout, Rolling.id == Runout.rolling_id)
    if start_date:
        query = query.filter(Runout.created_at >= start_date)
    if end_date:
        query = query.filter(Runout.created_at <= end_date)
    common["query"] = query
    common["items_per_page"] = None
    rolling = search_filter_sort_paginate(model="Rolling", **common)
    if rolling["items"]:
        for item in rolling["items"]:
            rolling_code = item.rolling_code if hasattr(item, "rolling_code") else None
            id = item.id if hasattr(item, "id") else None
            start_datetime, runout_from, end_datetime, runout_to = get_rolling_start_and_end_date(db_session=db_session, rolling_id=item.id)
            runout_from = str(runout_from) if runout_from is not None else None
            runout_from = runout_from.replace("(","").replace("'","").replace(")","").replace(",","") if runout_from is not None else None
            runout_to = str(runout_to) if runout_to is not None else None
            runout_to = runout_to.replace("(","").replace("'","").replace(")","").replace(",","") if runout_to is not None else None
            runout = get_runout_list_by_rolling_id(db_session=db_session, rolling_id=id)
            if runout is not None:
                no_bars_rolled = len(runout)
            else:
                no_bars_rolled = None
            item.rolling_code = rolling_code
            item.start_datetime = start_datetime
            item.end_datetime = end_datetime
            item.runout_from = runout_from
            item.runout_to = runout_to
            item.no_bars_rolled = no_bars_rolled
        rolling['items'].sort(key=lambda x: x.start_datetime if x.start_datetime else datetime.min, reverse=True)
    if start_date or end_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d') if start_date else None
        end_date = datetime.strptime(end_date, '%Y-%m-%d') if end_date else None
        rolling["items"] = [
            item for item in rolling["items"]
            if (start_date is None or item.start_datetime >= start_date) and
               (end_date is None or item.end_datetime <= end_date)
        ]
    return rolling

@router.get("/finished_count/{rolling_id}")
def get_finished_count(rolling_id: int, db_session: Session = Depends(get_db)):
    results = (
        db_session.query(
            FinishedProduct.cast_id,
            func.max(Cast.cast_code).label("cast_no"),
            func.count(FinishedProduct.id).label("no_bars"),
            func.count(distinct(FinishedProduct.runout_id)).label("no_runout"),
            func.sum(case([(FinishedProduct.cover_status == 'P', 1)], else_=0)).label("no_covered"),
            func.sum(case([(FinishedProduct.cover_status == 'W', 1)], else_=0)).label("no_waiting"),
            func.sum(case([(FinishedProduct.cover_status == 'F', 1)], else_=0)).label("no_failed"),
            case([
                (func.count(FinishedProduct.id) == func.sum(case([(FinishedProduct.cover_status == 'P', 1)], else_=0)),
                 "FC"),
                (func.sum(case([(FinishedProduct.cover_status == 'P', 1)], else_=0)) > 0, "PC"),
                (func.count(FinishedProduct.id) == func.sum(case([(FinishedProduct.cover_status != 'P', 1)], else_=0)),
                 "Fail")
            ], else_="").label("cover_status")
        )
        .join(Cast, FinishedProduct.cast_id == Cast.id)
        .filter(FinishedProduct.rolling_id == rolling_id)
        .group_by(FinishedProduct.cast_id)
        .all()
    )

    return {
        "items": [
            {
                "cast_id": row.cast_id,
                "cast_no": row.cast_no,
                "cover_status": row.cover_status,
                "no_runout": row.no_runout,
                "no_bars": row.no_bars,
                "no_covered": row.no_covered,
                "no_waiting": row.no_waiting,
                "no_failed": row.no_failed
            }
            for row in results
        ],
        "total": len(results)
    }

@router.put("/update_status_by_code/upstatus", response_model=RollingRead)
def update_rolling_status_by_code(
    *, 
    db_session: Session = Depends(get_db),
    rolling_code: str = Query(..., description="Rolling Code"),
    rolling_status: str = Query(..., description="Status"), 
    current_user: DispatchUser = Depends(get_current_user),
    ):
    """
    Update rolling status by rolling code
    """
    # 根据rolling code获取记录
    rolling = get_by_code(db_session=db_session, code=rolling_code, mill_id=current_user.current_mill_id)
    if not rolling:
        raise HTTPException(status_code=404, detail="Rolling not found with this code")

    # 创建更新对象
    rolling_in = RollingUpdateStatus(
        rolling_status=rolling_status,
        updated_by=current_user.email
    )

    # 调用已有update_status方法
    return update_status(
        db_session=db_session,
        rolling=rolling,
        rolling_in=rolling_in
    )





@router.post("/update_rolling_status_batch")
async def update_rolling_status_batch(
    *,
    request: Request,
    db_session: Session = Depends(get_db),
    current_user: DispatchUser = Depends(get_current_user),
):
    """
    批量更新最近40条Open状态的Rolling记录为Planning Complete
    """
    try:
        # 显式读取请求体（避免422验证错误）
        body = await request.body()
        if body:
            raise HTTPException(status_code=400, detail="This endpoint does not accept request body")
        # 获取最近更新的40条Open状态记录
        target_records = (
            db_session.query(Rolling)
            .filter(
                Rolling.rolling_status == "Open",
                Rolling.mill_id == current_user.current_mill_id
            )
            .order_by(Rolling.updated_at.desc())
            .limit(40)
            .all()
        )
        logging.info(f"Target records---------------->: {target_records}")

        if not target_records:
            return JSONResponse(
                status_code=200,
                content={"message": "No Open status records found in last 40 updates","updated_count": 0}
            )

        # 批量更新状态
        updated_ids = []
        for record in target_records:
            rolling_in = RollingUpdateStatus(
                rolling_status="Planning Complete",
                updated_by=current_user.email
            )
            updated_record = update_status(
                db_session=db_session,
                rolling=record,
                rolling_in=rolling_in
            )
            updated_ids.append(updated_record.id)

        # 提交事务
        db_session.commit()
        
        return {
            "updated_count": len(updated_ids),
            "updated_ids": updated_ids
        }

    except Exception as e:
        db_session.rollback()
        raise HTTPException(status_code=500, detail=f"update failed: {str(e)}")

@router.post("/send_pc_m240", response_model=RollingRead)
def delete_in_pc(*, 
                request: Request, 
                background_tasks: BackgroundTasks,
                db_session: Session = Depends(get_db),
                current_user: DispatchUser = Depends(get_current_user),
                rolling_ids: List[int]=Body(...,embed=True)):
    """
    Send m240 when click Delete in PC.
    """
    order_group_ids = []
    for id in rolling_ids:
        rolling = get(db_session=db_session, id=id)
        if rolling:
            order_groups = db_session.query(OrderGroup).filter(OrderGroup.rolling_id == id).all()
            for order_group in order_groups:
                order_group_ids.append(order_group.id)
        # send message to SRSM
    if len(order_group_ids):
        message = PushMessageData(id=240, type='srsmpc', msg=str(order_group_ids))
        try:
            call_method(request, background_tasks, db_session=db_session, current_user=current_user, message=message)
        except Exception as e:
            print(f'Sending srsmpc-240 failed, reason: {e}')

    return {"order_group_ids": order_group_ids}


##  查询当前正在进行中的rolling / 即将开始的rolling
@router.get("/semi_reblocking/get_rolling")
def get_c_rolling(db_session: Session = Depends(get_db)):
    current_time = datetime.now()
    # 先尝试查询 programmed_start_date + duration_minutes 大于当前时间且 programmed_start_date 小于当前时间的记录
    query = db_session.query(Rolling).filter(
        (Rolling.programmed_start_date + func.make_interval(0, 0, 0, 0, func.cast(Rolling.duration_minutes, Integer))) > current_time,
        Rolling.programmed_start_date < current_time
    )
    result = query.first()
    if result is None:
        # 如果没有符合条件的记录，查询 programmed_start_date 小于当前时间且最接近当前时间的记录
        query = db_session.query(Rolling).filter(
            Rolling.programmed_start_date < current_time
        ).order_by(Rolling.programmed_start_date.desc())
        result = query.first()

    return result
