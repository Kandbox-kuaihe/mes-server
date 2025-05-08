import json

from datetime import datetime
from fastapi import Request, HTTPException, status
from sqlalchemy.exc import IntegrityError
from fastapi.responses import Response, JSONResponse
import requests
import traceback

from sqlalchemy.orm import Session
from dispatch.database import get_db
from fastapi import APIRouter, Depends, BackgroundTasks

from dispatch.runout_admin.finished_product.models import FinishedProduct
from dispatch.system_admin.auth.models import DispatchUser
from dispatch.system_admin.auth.service import get_current_user
from dispatch.message_admin.message_server.service import (
    save_to_message_log_all,
    push_message_7001_service,
    create_cast,
)
from dispatch.message_admin.message_server.models import PushMessageData, PushMessageDataRead, PushMessageSemiData
from dispatch.semi_admin.semi.service import insert_json_semi
from dispatch.semi_admin.semi.service import get_by_code as get_semi_by_code
from dispatch.semi_admin.semi.models import Semi
from dispatch.cast.service import get_by_code, create, update
from dispatch.cast.models import CastCreate, CastUpdate
from dispatch.area import service as area_service
from dispatch.site import service as site_service
from dispatch.site_type import service as site_type_service
from dispatch.site_type.models import SiteTypeCreate
from dispatch.site.models import SiteCreate
from dispatch.area.models import AreaCreate
from dispatch.config import ENABLE_MESSAGE_FORWARD, IGNORE_MESSAGES_LOCAL, FORWARD_URLS, DEFAULT_EMAIL
from dispatch.message_admin.message_server.service import log_xml_to_file
from typing import Union, List, Final
from dispatch.message_admin.message_log.models import MessageLogCreate
from dispatch.message_admin.message_log.service import create as message_log_create
from dispatch.message_admin.message_server.service import save_to_message_log_all_7001
from re import search as re_search
from urllib.parse import parse_qs
import xml.etree.ElementTree as ET
# from dispatch.cprofile_util.profile_main import profile_start
from dispatch.message_admin.message_server.models import PushMessage7xxxDataRead
from dispatch.mill import service as mill_service



import asyncio
import logging

from concurrent.futures import ThreadPoolExecutor

logging.basicConfig(
    level=logging.INFO)

from dispatch.log import getLogger
log = getLogger(__name__)

router = APIRouter()


# 创建线程池
executor = ThreadPoolExecutor(max_workers=4)



# Forward message 7001
def forward_message_7001(request):
    if not ENABLE_MESSAGE_FORWARD: return
    request_body = request.body()
    log.info(f'FORWARD_URLS 7001 are: {FORWARD_URLS}, request_in: {request_body}')
    for url in FORWARD_URLS:
        if url.endswith("/"): url=url[:-1]
        url = url+request.url.path
        try:
            requests.post(url, json=request_body, headers=request.headers, timeout=0.01)
        except Exception as e:
            log.info(f'forward message sap error: {e}')
            # Async request and ignore result. So need to capture exception and no need to print
            pass

# 接受消息
@router.post("/push_message_1", response_model=PushMessageDataRead, summary="push message.")
# @profile_start(enable_profiler=True)
async def push_message(
        *,
        request: Request,
        background_tasks: BackgroundTasks,
        db_session: Session = Depends(get_db),
        request_in: PushMessageData,
        current_user: DispatchUser = Depends(get_current_user)
):
    # forward_message_7001(request)
    try:
        from dispatch.contrib.message_admin.message_server.server import handle_incoming_message
        result = handle_incoming_message(request, db_session, current_user, request_in, background_tasks)
    except ImportError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return result


async def forward_sap(request):
    if not ENABLE_MESSAGE_FORWARD:
        return
    log.info(f'FORWARD_URLS sap are: {FORWARD_URLS}')
    for url in FORWARD_URLS:
        if url.endswith("/"):
            url = url[:-1]
        url = url + request.url.path
        log.info(f'forward url: {url}')
        try:
            xml_body = await request.body()
            requests.post(url, data=xml_body, headers=request.headers, timeout=0.01)
        except Exception as e:
            log.info(f'forward message sap error: {e}')
            # Async request and ignore result. So need to capture exception and no need to print
            pass


# 接受消息 auth
@router.post("/push_message/sap_087_auth")
# @profile_start(enable_profiler=True)
async def send_message_sap_087_auth(
    *,
    request: Request,
    db_session: Session = Depends(get_db),
    current_user: DispatchUser = Depends(get_current_user)
):
    # 安全导入
    try:
        from dispatch.contrib.message_admin.message_server.message_sap_views import process_sap_087_auth_message
        return await process_sap_087_auth_message(request, db_session)
    except ImportError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/push_message/sap_184_auth")
# # @profile_start(enable_profiler=True)
async def send_message_sap_184_auth(
    *,
    request: Request,
    db_session: Session = Depends(get_db),
    current_user: DispatchUser = Depends(get_current_user)
):
    try:
        from dispatch.contrib.message_admin.message_server.message_sap_views import process_sap_184_auth_message
        return await process_sap_184_auth_message(request, db_session)
    except ImportError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/push_message/sap_274_auth")
async def send_message_sap_274_auth(
    *,
    request: Request,
    db_session: Session = Depends(get_db),
    current_user: DispatchUser = Depends(get_current_user)
):
    try:
        from dispatch.contrib.message_admin.message_server.message_sap_views import process_sap_274_auth_message
        return await process_sap_274_auth_message(request, db_session)
    except ImportError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/push_message/sap_275_auth")
async def send_message_sap_275_auth(
    *,
    request: Request,
    db_session: Session = Depends(get_db),
    current_user: DispatchUser = Depends(get_current_user)
):
    sap_type = "275"
    raw_body = None
    try:
        error_msg = f"Received a {sap_type} sap message."
        save_to_message_log_all(db_session, sap_type, error_msg, "info")
        if request.headers.get("content-type", None) != "application/xml":
            error_msg = "Request content type is not application/xml."
            save_to_message_log_all(db_session, sap_type, error_msg, "error")
            raise HTTPException(status_code=400, detail=error_msg)

        raw_body = await request.body()

        if not raw_body:
            error_msg = "Request body is empty."
            save_to_message_log_all(db_session, sap_type, error_msg, "error")
            raise HTTPException(status_code=400, detail=error_msg)
        else:
            save_to_message_log_all(db_session, sap_type, raw_body, "info")

        create_cast(raw_body, db_session, sap_type)

        response_xml = """<?xml version="1.0" encoding="UTF-8"?><Reply>
                <Response>Processed</Response>
                </Reply>"""
        return Response(content=response_xml, media_type="application/xml")
    except Exception as e:
        log.error("sap_error: ")
        traceback.print_exc()
        if raw_body is not None:
            log_xml_to_file(raw_body.decode('utf-8'), sap_type)
        response_xml = """<?xml version="1.0" encoding="UTF-8"?><Reply>
                <Response>Processed</Response>
                </Reply>"""
        return Response(content=response_xml, media_type="application/xml")


@router.post("/push_message/sap_genesis_auth")
async def send_message_sap_genesis_auth(
    *,
    request: Request,
    db_session: Session = Depends(get_db),
    current_user: DispatchUser = Depends(get_current_user)
):
    raw_body = await request.body()
    msg_type = 'sap'
    sap_type = 900
    message_log = MessageLogCreate(
        message_id= sap_type,
        type = msg_type,
        msg = raw_body,
        interact= "Recieve",
        created_at= datetime.now(),
        updated_at= datetime.now(),
        message_status = "Recieved",
    )
    message_log_create(db_session=db_session, message_log_in=message_log)
    response_xml = """<?xml version="1.0" encoding="UTF-8"?><Reply>
        <Response>Processed</Response>
        </Reply>"""
    try:        
        # Validate XML message - Empty body check
        if not raw_body:
            error_msg = "Request body is empty."
            raise HTTPException(status_code=400, detail=error_msg)
        from dispatch.contrib.message_admin.message_server.message_strategy import MessageStrategy900

        ms_900 = MessageStrategy900()
        ms_900.handle(db_session=db_session, message=message_log)
        return Response(content=response_xml, media_type="application/xml")
    except ImportError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as error:
        log.exception("sap_error:")
        if raw_body is not None:
            log_xml_to_file(raw_body.decode('utf-8'), 'genesis')
        message_log.message_status = "Failed"
        message_log.msg = str(error)
        message_log_create(db_session=db_session, message_log_in=message_log)
        return Response(content=response_xml, media_type="application/xml")


# 接受消息
@router.post("/push_message/sap_087")
async def send_message_sap_087(*, request: Request, db_session: Session = Depends(get_db)):
    try:
        from dispatch.contrib.message_admin.message_server.message_sap_views import process_sap_087_message
        return await process_sap_087_message(request, db_session)
    except ImportError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/push_message/sap_184")
async def send_message_sap_184(*, request: Request, db_session: Session = Depends(get_db)):
    try:
        from dispatch.contrib.message_admin.message_server.message_sap_views import process_sap_184_message
        return await process_sap_184_message(request, db_session)
    except ImportError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/push_message/sap_274")
async def send_message_sap_274(*, request: Request, db_session: Session = Depends(get_db)):
    try:
        from dispatch.contrib.message_admin.message_server.message_sap_views import process_sap_274_message
        return await process_sap_274_message(request, db_session)
    except ImportError as e:
        raise HTTPException(status_code=400, detail=str(e))


#  {'id': '60', 'type': 'pc', 'msg': '" 60000120241202161331  "'}


# Forward message
def forward_message(request, request_in, headers):
    if not ENABLE_MESSAGE_FORWARD: return
    request_path = request.url.path
    message_type = request_in.get("type")
    log.info(f'FORWARD_URLS messages are: {FORWARD_URLS}, request_in: {request_in}')
    for url in FORWARD_URLS:
        log.info(f"Start forward message, type: {message_type}, URL: {url}")
        json_response = None
        if url.endswith("/"): url=url[:-1]
        try:
            response = requests.post(url+request_path, json=request_in, headers=headers)
            if response.status_code != 200:
                log.info(f"Forward failed："+str(response))
            json_response = JSONResponse(
                status_code=response.status_code,
                content=response.json() if response.content else {"message": "No content"}
            )
        except Exception as e:
            log.info(f"Forward exception：{e}")
            json_response = JSONResponse(
                status_code=status.HTTP_200_OK,  # Return HTTP 200 to tell TBM trigger to move on
                content={
                    "code": 400,
                    "data": {
                        "tip": f"Server error",
                        "details": "message has been received but error occurred: " + str(e)
                    },
                    "message": "fail",
                },
            )

    return json_response

@router.post("/push_message", response_model=Union[PushMessageData, List[PushMessageData]])
def push_message_all(
    *,
    request: Request,
    background_tasks: BackgroundTasks,
    db_session: Session = Depends(get_db),
    request_in: dict,
    current_user: DispatchUser = Depends(get_current_user),
):
    ingore_messages_local = request_in.get("type").lower() in IGNORE_MESSAGES_LOCAL
    forward_response = forward_message(request, request_in, request.headers)
    if ingore_messages_local:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "code": 200,
                "data": {
                    "tip": 'success',
                    "details": 'success',
                },
                "message": 'success',
            },
        )

    log.info(f"i_received_msg_dict: {request_in}")
    message_log = MessageLogCreate(
        message_id=int(request_in["id"]),
        type=request_in["type"],
        msg=request_in["msg"],
        interact="Recieve",
        created_at=datetime.now(),
        updated_at=datetime.now(),
        message_status="Recieved",
    )
    message_log_create(db_session=db_session, message_log_in=message_log)

    try:
        # Verify whether the message is sent by the MES.
        request_in_f = PushMessageData(**request_in)
        from dispatch.contrib.message_admin.message_server.server import get_interact_type
        _, _, msg_type = get_interact_type(request_in_f)
        if msg_type == 0:
            log.warning(f"Message: {request_in} is sent by the MES. Callback messages will not be processed.")
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=f"Message: {request_in} is sent by the MES. Callback messages will not be processed."
            )
    except ImportError as e:
        log.error(f"import error: {e}")
    except Exception as err:
        log.error(err)
        raise HTTPException(status_code=400, detail=f"Failed to decode message {request_in}")

    request_in = request_in_f
    request_in.msg = request_in.msg.strip('"').lstrip()
    log.info(request_in.msg)

    try:
        from dispatch.contrib.message_admin.message_server.server import call_method
        return call_method(request, background_tasks, db_session, current_user, request_in)
    except ImportError as e:
        log.error(f"import error: {e}")
    except IntegrityError as exc:
        log.error(f"IntegrityError: {exc}\nURL: {request.url}\nHeaders: {request.headers}")

        # Extract duplicate key information
        error_detail = str(exc.orig)  # Access the underlying database exception
        match = re_search(r'duplicate key value violates unique constraint "(.*?)"', error_detail)
        duplicate_key = match.group(1) if match else "unknown"

        return JSONResponse(
            status_code=status.HTTP_200_OK,  # Return HTTP 200 to tell TBM trigger to move on
            content={
                "code": 400,
                "data": {
                    "tip": f"Duplicate key error on '{duplicate_key}', please check your input.",
                    "details": "message has been received but error occurred: " + error_detail,
                },
                "message": "fail",
            },
        )
    except Exception as e:
        request_info = {
            "method": request.method,
            "url": str(request.url),
            "headers": dict(request.headers),
            "client": request.client.host,
        }

        # 判断请求是否有 body
        request_body = None
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                # 缓存请求体以防止多次读取
                if not hasattr(request, "_body"):
                    request._body = request.body()

                content_type = request.headers.get("Content-Type", "")

                if "application/json" in content_type:
                    request_body = json.loads(request._body.decode("utf-8"))
                elif "application/x-www-form-urlencoded" in content_type:
                    request_body = parse_qs(request._body.decode("utf-8"))
                else:
                    request_body = request._body.decode("utf-8")
            except Exception as e:
                request_body = f"Failed to read request body: {str(e)}"

        err = (
            f"Unknown error: request: {request_info}\n"
            f"Request body: {request_body}\n"
            f"Error Details: {str(e)}\n"
            f"Traceback: {traceback.format_exc()}"
        )
        log.error(err)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "code": 400,
                "data": {
                    "tip": str(e),
                    "details": err,
                },
                "message": "fail",
            },
        )



    
@router.post("/push_message/pc_semi_7001", response_model=PushMessage7xxxDataRead)
# @profile_start(enable_profiler=False)
async def push_message_7001(request: Request, data: dict, db_session: Session = Depends(get_db)):
    try:
        forward_message_7001(request)
    except Exception as e:
        print(f'forward_message_7001 error: {e}')
    try:
        piece = data["message"]["pieces"]["piece"]
        weight = float(piece.get('@actualQuantity', ""))
        # 提取需要的字段
        chars = {char["@name"]: char["value"] for char in piece.get("chars", {}).get("char", [])}

        semi_code = f"{chars.get('Cast_No', '')}-{chars.get('Strand_Number', '').lstrip('0')}{chars.get('Skelp_Letter', 'A')}{chars.get('Slab_Number', '1')}"

        dim_1 = float(chars.get('Section_Width', ''))
        dim_2 = float(chars.get('Section_Thick', ''))
        length = float(chars.get('Length', ''))
        width = float(chars.get('Width', ''))
        quality_code = chars.get('Grade_BOS_Qual', '')
        cast_code = chars.get('Cast_No', '')
        skelp_code = f"{chars.get('Strand_Number', '').lstrip('0')}{chars.get('Skelp_Letter', 'A')}{chars.get('Slab_Number', '1')}"

        message_log_dict = {
            "semi_code": semi_code,
            "dim_1": dim_1,
            "dim_2": dim_2,
            "length": length,
            "width": width,
            "quality_code": quality_code,
            "cast_code": cast_code,
            "skelp_code": skelp_code,
            'semi_type': 'Slab'
        }
        # 必填字段列表
        required_fields = [semi_code, cast_code]
        # 7001消息默认mill为 Unknown
        MILL_CODE: Final = "Unknown"
        mill = mill_service.get_by_code(db_session=db_session, code=MILL_CODE)
        if not mill:
            raise HTTPException(status_code=400, detail=f"Mill (mill code: {MILL_CODE}) not found")
        mill_id = mill.id
        # 检查必填字段是否为空
        if any(not field for field in required_fields):
            save_to_message_log_all_7001(db_session=db_session, type=7001, msg_json_dict=message_log_dict,
                                         msg="Message semi_code and cast_code cannot be empty.", msg_status="Error")
            raise HTTPException(status_code=400, detail="semi_code and cast_code cannot be empty.")

        result = get_by_code(db_session=db_session, code=cast_code)
        if not result:
            cast_data = {
                    "updated_at": datetime.now(),
                    "updated_by": f"{DEFAULT_EMAIL}",
                    "created_at": datetime.now(),
                    "created_by": f"{DEFAULT_EMAIL}",
                    "bos_cast_code": f"6V{cast_code}",
                    "cast_code": cast_code,
                    "quality_code": "0218",
                    "mill_id": 410,
                }
            new_cast = CastCreate(**cast_data)
            result = create(db_session=db_session, cast_in=new_cast)

        cast_id = result.id
        semi_exist = get_semi_by_code(db_session=db_session, code=semi_code)
        # print(f"id: {id}, cast_code: {cast_code}")
        if semi_exist:
            save_to_message_log_all_7001(db_session=db_session, type=7001, msg_json_dict=message_log_dict,
                                         msg=f"semi_id: {semi_exist.id} (semi code: {semi_code}) is already exist.",
                                         msg_status="Error")
            raise HTTPException(status_code=400, detail=f"semi_id: {semi_exist.id} is already exist.")
        area_code = "SCU Slab Yard"
        site_code = "Slab Yard"
        site_type_code = "Slab Yard"
        # 查询是否存在site type code 如果不存在那么创建一个
        site_type_one = site_type_service.get_site_type_by_code(db_session=db_session, code=site_type_code)
        if not site_type_one:
            site_type_service.create_site_type(db_session=db_session,
                                               # id 设置大一点 防止重复
                                               site_type_in=SiteTypeCreate(id=67592,
                                                                           code=site_type_code,
                                                                           type="s-semi",
                                                                           name=site_type_code,
                                                                           desc=site_type_code,
                                                                           )
                                               )
        # 获取其id
        site_type_one_id = site_type_service.get_site_type_by_code(db_session=db_session, code=site_type_code).id
        # 查询是否存在site code 如果不存在那么创建一个
        site_one = site_service.get_by_code(db_session=db_session, code=site_code)
        # print(f"site_type_one_id: {site_type_one_id}")
        if not site_one:
            site_service.create(db_session=db_session, site_in=SiteCreate(
                id=57592,
                code=site_code,
                name=site_code,
                desc=site_code,
                site_type_id=site_type_one_id,
            ))
        # 获取其id
        site_one_id = site_service.get_by_code(db_session=db_session, code=site_code).id
        # 查询是否存在area code 如果不存在 那就创建一个
        area_one = area_service.get_by_code(db_session=db_session, code=area_code)
        # print(f"site_one_id: {site_one_id}")
        if not area_one:
            area_service.create(db_session=db_session, area_in=AreaCreate(
                id=55212,
                code=area_code,
                type="s-semi",
                desc=area_code,
                site_id=site_one_id,
            ))
        # 获取其id
        area_one_id = area_service.get_by_code(db_session=db_session, code=area_code).id


        new_semi = Semi(
            semi_code=semi_code,
            dim1=dim_1,
            dim2=dim_2,
            quality_code=quality_code,
            cast_id=cast_id,
            length_mm=length,
            width_mm=width,
            estimated_weight_kg=weight,
            skelp_code=skelp_code,
            area_id=area_one_id,
            semi_type='Slab',
            thickness_mm=dim_2
        )

        insert_json_semi(db_session=db_session, semi_body=new_semi)

        update_cast_data = {
            "updated_at": datetime.now(),
            "updated_by": f"{DEFAULT_EMAIL}",
            "created_at": datetime.now(),
            "created_by": f"{DEFAULT_EMAIL}",
            "bos_cast_code": f"6V{cast_code}",
            "cast_code": cast_code,
            "quality_code": "0218",
            "mill_id": 410,
            "ch_c": 0.12575,
            "ch_si": 0.19075,
            "ch_mn": 1.476,
            "ch_p": 0.0165,
            "ch_s": 0.0025,
            "ch_s_p": None,
            "ch_cr": 0.01075,
            "ch_mo": 0.00325,
            "ch_ni": 0.01375,
            "ch_al": 0.0365,
            "ch_b": 0.000275,
            "ch_co": 0.00625,
            "ch_cu": 0.006,
            "ch_nb": 0.001,
            "ch_sn": 0.00175,
            "ch_ti": 0.001325,
            "ch_v": 0.09575,
            "ch_ca": 0.000125,
            "ch_n": 0.007075,
            "ch_o": None,
            "ch_h": 0.00022,
            "ch_solal": None,
            "ch_as": 0.00225,
            "ch_bi": 0.001,
            "ch_ce": None,
            "ch_pb": 0.001,
            "ch_sb": 0.0001,
            "ch_w": 0.000425,
            "ch_zn": None,
            "ch_zr": None,
            "ch_te": 0.001,
            "ch_rad": 0.02
        }

        save_to_message_log_all_7001(db_session=db_session, type=7001 ,msg_json_dict=message_log_dict, msg="Received a 7001 message!")

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(executor,
                                   async_update,
                                   db_session,
                                   result,
                                   CastUpdate(**update_cast_data)
                                   )
        return PushMessage7xxxDataRead(**{"status": 200, "detail": "Import Success!"})

    except HTTPException as e:
        raise e
    except Exception as e:
        raise e


def async_update(db_session, cast, cast_in):
    update(db_session=db_session, cast=cast, cast_in=cast_in)


@router.post("/push_message/pc_7001", response_model=PushMessage7xxxDataRead)
def new_push_message_7001(data: PushMessageSemiData, db_session: Session = Depends(get_db)):
    return push_message_7001_service(db_session, data)

@router.post("/push_message/pc_7xxx", response_model=PushMessage7xxxDataRead)
def push_message_7xxx(data: dict, db_session: Session = Depends(get_db)):
    try:
        from dispatch.contrib.message_admin.message_server.message_strategy import Message7xxxService
        message_7xxx_service = Message7xxxService(content=data)
        message_7xxx_service.process_message(db_session=db_session)
        return PushMessage7xxxDataRead(**{
            "status": 200,
            "detail": "Import Success!",
        })
    except ImportError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/push_message/sap_900_auth")
# # @profile_start(enable_profiler=True)
async def send_message_sap_despatch(
        *,
        request: Request,
        db_session: Session = Depends(get_db),
):
    sap_type = 0
    # error_msg = f"Received a {sap_type} sap message."
    if request.headers.get("content-type", None) != "application/xml":
        msg = "Request content type is not application/xml."
        save_to_message_log_all(db_session, sap_type, msg, "Failed")
        raise HTTPException(status_code=400, detail=msg)
    raw_body = await request.body()
    raw_body_str = raw_body.decode()
    log.debug(f'The raw XML we received from SAP is:\n{raw_body_str}')
    
    root = ET.fromstring(raw_body)
    import_batch = []
    batch_ids = {batch.find('BatchID').text for batch in root.findall('.//Batch')}

    from sqlalchemy import update


    # 批量更新 reserve_status
    db_session.execute(
        update(FinishedProduct)
        .where(FinishedProduct.code.in_(batch_ids))
        .values({FinishedProduct.status: 'despatched'})
    )
    db_session.commit()

    msg = raw_body
    # save_to_message_log_all(db_session, sap_type, msg, "Success")

    msg_info = {'message_id': sap_type, 'msg': msg, 'type': "xml", 'message_status': "Success", 'interact': 'FECC to MES',
                'interact_from': 'FECC', 'interact_to': 'MES', 'msg_type': 1}
    message_log_create(db_session=db_session, message_log_in=MessageLogCreate(**msg_info))

    return {"code": 200, "detail": "Import Success!", "batch_ids": batch_ids, "import_batch": import_batch}


@router.post("/trigger_message/{msg_type}")
async def trigger_message(
    *,
    msg_type: str,
    msg_in: dict,
    db_session: Session = Depends(get_db),
    background_tasks: BackgroundTasks,
):
    try:
        from dispatch.contrib.message_admin.message_server.trigger_message_service import (
            handle_m107,
            handle_m199,
            handle_m249,
        )

        from dispatch.contrib.message_admin.message_server.trigger_sap_message import (
            handle_mfgi182,
            handle_mfgi302,
            handle_mfgi404,
            handle_qmai264,
        )
        match msg_type:
            case 'm107':
                handle_m107(db_session=db_session, msg_in=msg_in, background_tasks=background_tasks)
            case 'm199':
                handle_m199(db_session=db_session, msg_in=msg_in, background_tasks=background_tasks)
            case 'm249':
                handle_m249(db_session=db_session, msg_in=msg_in, background_tasks=background_tasks)
            case 'mfgi182':
                handle_mfgi182(db_session=db_session, finished_product_id=msg_in["finished_product_id"], background_tasks=background_tasks)
            case 'mfgi302':
                handle_mfgi302(db_session=db_session, finished_product_id=msg_in["finished_product_id"], background_tasks=background_tasks)
            case 'mfgi404':
                handle_mfgi404(db_session=db_session, finished_product_id=msg_in["finished_product_id"], action_e=msg_in["action"], background_tasks=background_tasks)
            case 'qmai264':
                handle_qmai264(db_session=db_session, finished_product_id=msg_in["finished_product_id"], action_e=msg_in["action"], background_tasks=background_tasks)

        return {"status": "ok"}
    except ImportError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/trigger_xml_message/{msg_type}")
async def trigger_message(
        *,
        msg_type: str,
        request: Request,
        db_session: Session = Depends(get_db),
        background_tasks: BackgroundTasks,
):
    if request.headers.get("content-type", None) != "application/xml":
        msg = "Request content type is not application/xml."
        raise HTTPException(status_code=400, detail=msg)
    raw_body = await request.body()
    raw_body_str = raw_body.decode()
    try:
        from dispatch.contrib.message_admin.message_server.trigger_sap_message import handle_SLB294
        match msg_type:
            case 'SLB294':
                handle_SLB294(db_session=db_session, request=raw_body_str, background_tasks=background_tasks)
            case 'SLBM294':
                handle_SLB294(db_session=db_session, request=raw_body_str, background_tasks=background_tasks)

        return {"status": "ok"}
    except ImportError as e:
        raise HTTPException(status_code=400, detail=str(e))
@router.post("/log_message", response_model=Union[PushMessageData, List[PushMessageData]])
def log_message_all(*, 
                        request: Request, 
                        background_tasks: BackgroundTasks,
                        db_session: Session = Depends(get_db), 
                        request_in: dict, 
                        current_user: DispatchUser = Depends(get_current_user)):

    log.info(f"i_received_msg_dict: {request_in}")
    message_log = MessageLogCreate(
        message_id= int(request_in["id"]),
        type = request_in["type"],
        msg = request_in["msg"],
        interact= "Recieve",
        created_at= datetime.now(),
        updated_at= datetime.now(),
        message_status = "Recieved",
    )
    message_log_create(db_session=db_session, message_log_in=message_log)

    return {"status": "ok"}


@router.post("/call_method/proxy")
def call_method_by_msg_type(
        *,
        request: Request,
        msg_in: PushMessageData,
        db_session: Session = Depends(get_db),
        current_user: DispatchUser = Depends(get_current_user),
        background_tasks: BackgroundTasks
):
    try:
        return call_method(request, background_tasks, db_session, current_user, msg_in)
    except Exception as e:
        log.error(f"ERROR in call_method_by_msg_type: {msg_in.type}-{msg_in.id} :{e}!")
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "code": 400,
                "data": {
                    "tip": str(e),
                    "details": f"ERROR in call_method_by_msg_type: {msg_in.type}-{msg_in.id} :{e}!",
                },
                "message": "fail",
            },
        )



##############################################  消息重发接口  ##############################################
@router.post("/push_message/repeat", response_model=Union[PushMessageData, List[PushMessageData]])
def push_message_all_repeat(
    *,
    request: Request,
    background_tasks: BackgroundTasks,
    db_session: Session = Depends(get_db),
    request_in: dict,
    current_user: DispatchUser = Depends(get_current_user),
):
    ingore_messages_local = request_in.get("type").lower() in IGNORE_MESSAGES_LOCAL
    forward_response = forward_message(request, request_in, request.headers)
    if ingore_messages_local:
        return forward_response

    log.info(f"i_received_msg_dict: {request_in}")
    message_log = MessageLogCreate(
        message_id=int(request_in["id"]),
        type=request_in["type"],
        msg=request_in["msg"],
        interact="Recieve",
        created_at=datetime.now(),
        updated_at=datetime.now(),
        message_status="Recieved",
        repeat_flah=1
    )
    message_log_create(db_session=db_session, message_log_in=message_log)

    try:
        # Verify whether the message is sent by the MES.
        request_in_f = PushMessageData(**request_in)
        _, _, msg_type = get_interact_type(request_in_f)
        if msg_type == 0:
            log.warning(f"Message: {request_in} is sent by the MES. Callback messages will not be processed.")
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=f"Message: {request_in} is sent by the MES. Callback messages will not be processed."
            )
    except Exception:
        raise HTTPException(status_code=400, detail=f"Failed to decode message {request_in}")

    request_in = request_in_f
    request_in.msg = request_in.msg.strip('"').lstrip()
    log.info(request_in.msg)

    try:
        return call_method(request, background_tasks, db_session, current_user, request_in)
    except IntegrityError as exc:
        log.error(f"IntegrityError: {exc}\nURL: {request.url}\nHeaders: {request.headers}")

        # Extract duplicate key information
        error_detail = str(exc.orig)  # Access the underlying database exception
        match = re_search(r'duplicate key value violates unique constraint "(.*?)"', error_detail)
        duplicate_key = match.group(1) if match else "unknown"

        return JSONResponse(
            status_code=status.HTTP_200_OK,  # Return HTTP 200 to tell TBM trigger to move on
            content={
                "code": 400,
                "data": {
                    "tip": f"Duplicate key error on '{duplicate_key}', please check your input.",
                    "details": "message has been received but error occurred: " + error_detail,
                },
                "message": "fail",
            },
        )
    except Exception as e:
        request_info = {
            "method": request.method,
            "url": str(request.url),
            "headers": dict(request.headers),
            "client": request.client.host,
        }

        # 判断请求是否有 body
        request_body = None
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                # 缓存请求体以防止多次读取
                if not hasattr(request, "_body"):
                    request._body = request.body()

                content_type = request.headers.get("Content-Type", "")

                if "application/json" in content_type:
                    request_body = json.loads(request._body.decode("utf-8"))
                elif "application/x-www-form-urlencoded" in content_type:
                    request_body = parse_qs(request._body.decode("utf-8"))
                else:
                    request_body = request._body.decode("utf-8")
            except Exception as e:
                request_body = f"Failed to read request body: {str(e)}"

        err = (
            f"Unknown error: request: {request_info}\n"
            f"Request body: {request_body}\n"
            f"Error Details: {str(e)}\n"
            f"Traceback: {traceback.format_exc()}"
        )
        log.error(err)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "code": 400,
                "data": {
                    "tip": str(e),
                    "details": err,
                },
                "message": "fail",
            },
        )


@router.post("/push_message/pc_7xxx/repeat", response_model=PushMessage7xxxDataRead)
def push_message_7xxx_repeat(data: dict, db_session: Session = Depends(get_db)):
    try:
        from dispatch.contrib.message_admin.message_server.message_strategy import Message7xxxService
        message_7xxx_service = Message7xxxService(content=data)
        message_7xxx_service.process_message(db_session=db_session, is_repeat=1)
        return PushMessage7xxxDataRead(**{
            "status": 200,
            "detail": "Import Success!",
        })
    except ImportError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )