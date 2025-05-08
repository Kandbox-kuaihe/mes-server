import re
from functools import wraps
from datetime import datetime, timedelta
from typing import Optional
from uuid import uuid1
from contextvars import ContextVar
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError
import redis
import json

from sqlalchemy.exc import IntegrityError
from starlette.routing import compile_path

from sqlalchemy.orm import scoped_session
from sqlalchemy import inspect
from dispatch.database_util.service import get_schema_session
from dispatch.message_admin.message.ibmmq.mq_tools import read_mq,EnablePymqi
from dispatch.message_admin.operation_log.models import OperationLog
from dispatch.org.models import Organization

# from dispatch.planner_env.planner_service import get_active_planner, planners_dict, planners_dict_lock
import time
import logging
from tabulate import tabulate
from os import path
import asyncio
# from dispatch.cloudmarket.instance.schduler import init_scheduler

# from starlette.middleware.gzip import GZipMiddleware
from fastapi import FastAPI, Depends
# from sentry_asgi import SentryMiddleware
from starlette.applications import Starlette
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import FileResponse, Response, StreamingResponse
from starlette.staticfiles import StaticFiles
import httpx

from dispatch.plugins.base import plugins
# from dispatch.zulip_server.core import unsubcribe_stream_by_days
from .config import DISPATCH_AUTHENTICATION_PROVIDER_SLUG, redis_pool, BASE_ENV, DISPATCH_VERSION, DEV_DATABASE_SCHEMA
from dispatch import config
import threading
import time
import asyncio
from .api import unauth_view_routers, view_routers
from .common.utils.cli import install_plugins, install_plugin_events
# from .config import STATIC_DIR
# from .extensions import configure_extensions
from dispatch.log import getLogger
# from .metrics import provider as metric_provider
from dispatch.plugins.kandbox_planner.env.env_enums import (
    JobPlanningStatus,
    ActionScoringResultType,
)

from .database import engine, sessionmaker, get_auth_db
from fastapi.middleware.cors import CORSMiddleware
from .config import DISPATCH_UI_URL




from dispatch.log import getLogger
log = getLogger(__name__)
    
# 性能统计
_startup_times = {}

def record_startup_time(name: str):
    """记录启动阶段的耗时"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            result = await func(*args, **kwargs)
            _startup_times[name] = time.time() - start_time
            return result
        return wrapper
    return decorator

# we configure the extensions such as Sentry
# configure_extensions()



def include_routers(api_router_param, routers, prefix=None,dependencies = None):
    for route in routers:
        api_router_param.include_router(route[1], prefix=f"{prefix}/{route[0]}", tags=[f"{route[0]}"],**dependencies)

def create_app() -> FastAPI:
    app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

    # Configure CORS
    origins = [DISPATCH_UI_URL]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add routes
    
    if BASE_ENV:
        app_api_path = f"/{BASE_ENV.replace("/","")}/api"
    else:
        app_api_path = f"/api"


    from dispatch.system_admin.auth.service import get_current_user, check_permission
    d = {
        "dependencies":[Depends(get_current_user), Depends(check_permission)],
    }
    include_routers(app, view_routers,prefix=f"{app_api_path}/v1",dependencies=d)
    include_routers(app, unauth_view_routers,prefix=f"{app_api_path}/v1",dependencies={})
    log.info(f"Dispatch_Version: {DISPATCH_VERSION}, Env: {BASE_ENV}, api path: {app_api_path}, API Document: {app_api_path}/v1/docs")

    return app

app = create_app()

async def init_mq_connection():
    """异步初始化 MQ 连接"""
    start_time = time.time()
    try:
        # 使用异步方式启动 MQ 读取任务
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, read_mq)
        _startup_times['mq_connection'] = time.time() - start_time
        log.info(f"MQ connection initialized in {_startup_times['mq_connection']:.2f} seconds")
    except Exception as e:
        _startup_times['mq_connection'] = time.time() - start_time
        log.error(f"Failed to initialize MQ connection in {_startup_times['mq_connection']:.2f} seconds: {str(e)}")

@app.on_event("startup")
@record_startup_time("total_startup")
async def startup_event():
    global _startup_start_time
    _startup_start_time = time.time()
    
    # log.info(f'MQ configuration read: {config.MQ_LIMIS_ENDPOINTS_READ}')
    # log.info(f'MQ configuration write: {config.MQ_LIMIS_ENDPOINTS_WRITE}')
    if EnablePymqi:
        if config.MQ_LIMIS_ENDPOINTS_READ['ON_OFF']:
            # 使用 create_task 启动异步任务
            start_time = time.time()
            asyncio.create_task(init_mq_connection())
            _startup_times['mq_task_creation'] = time.time() - start_time
            log.info(f"MQ task creation took {_startup_times['mq_task_creation']:.2f} seconds")
        else:
            log.info("MQ LIMIS READ is off")
    else:
        log.warning("Not install pymqi, Please install the MQ client according to README.mq and then execute pip install pymqi")

    startup_time = time.time() - _startup_start_time
    log.info(f"Application startup completed in {startup_time:.2f} seconds")

@app.on_event("shutdown")
async def shutdown_event():
    shutdown_start = time.time()
    log.info("Application shutting down...")
    # 执行清理操作
    shutdown_time = time.time() - shutdown_start
    log.info(f"Application shutdown completed in {shutdown_time:.2f} seconds")

OVER_CURRENT_USER = None


def get_path_template(request: Request) -> str:
    if hasattr(request, "path"):
        return ",".join(request.path.split("/")[1:4])
    return ".".join(request.url.path.split("/")[1:4])



REQUEST_ID_CTX_KEY = "request_id"
_request_id_ctx_var: ContextVar[Optional[str]] = ContextVar(REQUEST_ID_CTX_KEY, default=None)


def get_request_id() -> Optional[str]:
    return _request_id_ctx_var.get()


def get_path_params_from_request(request: Request) -> str:
    path_params = {}
    for r in api_router.routes:
        path_regex, path_format, param_converters = compile_path(r.path)
        # remove the /api/v1 for matching
        path = f"/{request['path'].strip('/api/v1')}"
        match = path_regex.match(path)
        if match:
            path_params = match.groupdict()
    return path_params


@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    request_id = str(uuid1())

    # we create a per-request id such that we can ensure that our session is scoped for a particular request.
    # see: https://github.com/tiangolo/fastapi/issues/726
    ctx_token = _request_id_ctx_var.set(request_id)
    # path_params = get_path_params_from_request(request)

    # if this call is organization specific set the correct search path
    # organization_slug = path_params.get("organization")
    # install_plugins()

    auth_plugin = plugins.get(DISPATCH_AUTHENTICATION_PROVIDER_SLUG)
    login_info = None
    try:
        login_info = auth_plugin.get_current_user_data(request)
    except Exception as e:
        _path = request.url.path
        if all(
            [
                i not in _path
                for i in [
                    "/register",
                    "/login",
                    "/register_eng",
                    "/register_customer",
                    "/edit_job",
                    "/job_edit_4_worker",
                ]
            ]
        ):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": [{"msg": "Signature has expired"}]},
            )

    organization_slug = login_info.get("org_code") if login_info else None
    if organization_slug and organization_slug != "-1":
        # request.state.organization = organization_slug
        schema = f"dispatch_organization_{organization_slug}"
        # TODO, move this to be module global variable. It should not be fetched everytime.
        # validate schema name
        schema_names = inspect(engine).get_schema_names()
        if schema in schema_names:
            # add correct schema mapping depending on the request
            schema_engine = engine.execution_options(
                schema_translate_map={
                    None: schema,
                }
            )
        else:
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"detail": [{"msg": "Forbidden, wrong organization"}]},
            )
    else:
        # add correct schema mapping depending on the request
        # can we set some default here?
        request.state.organization = "default"
        schema_engine = engine.execution_options(
            schema_translate_map={
                None: DEV_DATABASE_SCHEMA,
            }
        )
    try:
        session = scoped_session(sessionmaker(bind=schema_engine), scopefunc=get_request_id)
        request.state.auth_db = session()
        # request.state.auth_db.autocommit = True
        response = await call_next(request)
    finally:
        request.state.auth_db.close()

    _request_id_ctx_var.reset(ctx_token)
    return response





@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Strict-Transport-Security"] = "max-age=31536000 ; includeSubDomains"
    return response


class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        path_template = get_path_template(request)

        # exclude non api requests e.g. static content
        if "api" not in path_template:
            return await call_next(request)

        method = request.method
        tags = {"method": method, "endpoint": path_template}

        try:
            start = time.perf_counter()
            response = await call_next(request)
            elapsed_time = time.perf_counter() - start
        except Exception as e:
            # metric_provider.counter("server.call.exception.counter", tags=tags)
            raise e from None
        else:
            tags.update({"status_code": response.status_code})
            # metric_provider.timer("server.call.elapsed", value=elapsed_time, tags=tags)
            # metric_provider.counter("server.call.counter", tags=tags)

        return response


# we add a middleware class for logging exceptions to Sentry
# app.add_middleware(SentryMiddleware)

# we add a middleware class for capturing metrics using Dispatch's metrics provider
# app.add_middleware(MetricsMiddleware)

def get_client_ip(request:Request):
    if "X-Forwarded-For" in request.headers:
        # 可能存在多个IP地址，通常第一个是客户端的真实IP
        client_ip = request.headers["X-Forwarded-For"].split(',')[0]
    elif "X-Real-IP" in request.headers:
        client_ip = request.headers["X-Real-IP"]
    else:
        client_ip = request.client.host
    return client_ip

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        body_dict = {}
        #  如果发送消息是"application/json" 就转为json 
        if request.headers.get("content-type") =="application/json" and request.method in ["POST","PUT"]:
            body_dict = await request.json()
            if 'password' in body_dict:
                body_dict['password'] = '******'
                # 记录响应内容   
            log.info(f"LoggingMiddleware_for_all:{body_dict}")
        
        # if 'password' in body_dict:
        #     body_dict['password'] = '******'
        #         # 记录响应内容


        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        if process_time >0.5:
            log.info(f"Request: {request.method} {request.url} - Status: {response.status_code} - Time: {process_time:.2f}s")
        client_host = get_client_ip(request)
        response_json = {}
        # if isinstance(response, StreamingResponse) :
        #     # 记录流式响应的内容
        #     body_chunks = []
        #     async for chunk in response.body_iterator:
        #         body_chunks.append(chunk)
        #     body = b''.join(body_chunks).decode('utf-8')  # 假设编码为 utf-8 
        #     response_json = json.loads(body)

        # 保存日志到数据库
        # if request.method not in ["GET", "OPTIONS"] : # and "/message_server/push_message" not in request.url.path

        if request.method not in ["GET", "OPTIONS"] and all(path not in request.url.path for path in
                                                            ["/message_server/push_message","/message_log/"]):
           
            try:
                db = request.state.auth_db
            
                log_data = OperationLog( 
                    request_modular="",
                    request_path=request.url.path,
                    request_body=json.dumps(body_dict,ensure_ascii=False),
                    request_method=request.method,
                    request_msg=json.dumps(request.query_params._dict,ensure_ascii=False),
                    request_ip=client_host,
                    response_code="",
                    response_json_result=response_json,
                    response_status=response.status_code, 
                    updated_by="", 
                )
                db.add(log_data)
                db.commit()
                db.close()
            except Exception as e:
                print(e)
                log.info('Confirm if the account has been logged in.')
        
        return response

app.add_middleware(LoggingMiddleware)
 

# we install all the plugins
install_plugins()

# we add all the plugin event API routes to the API router
# install_plugin_events(api_router)

# ed_daily ed_pre ed_prod 
# we add all API routes to the Web API framework




# we print all the registered API routes to the console
# table = []
# for r in api_router.routes:
#     auth = False
#     for d in r.dependencies:
#         if d.dependency.__name__ == "get_current_user":  # TODO this is fragile
#             auth = True
#     table.append([r.path, auth, ",".join(r.methods)])

# log.debug("Available Endpoints \n" + tabulate(table, headers=["Path", "Authenticated", "Methods"]))





# https://fastapi.tiangolo.com/advanced/events/


redis_conn = redis.Redis(connection_pool=redis_pool)


from fastapi.responses import JSONResponse
from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
import traceback



# 捕获唯一键冲突错误转为400，以抛出页面提示
@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    log.error(f"IntegrityError: {exc}\nURL: {request.url}\nHeaders: {request.headers}")

    # Extract the duplicated key information from the exception message
    error_detail = str(exc.orig)  # Access the underlying database exception
    match = re.search(r"value violates unique constraint \"(.+)\"", error_detail)
    duplicate_key = match.group(1) if match else "unknown"

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "code": 400,  # Still indicate the error code in the response body
            "data": {
                "tip": f"Duplicate key error on '{duplicate_key}', please check your input.",
                "details": "message has been received but error occur: " + error_detail
            },
            "message": "fail",
        }
    )

# 捕获全部异常
@app.exception_handler(Exception)
async def all_exception_handler(request: Request, exc: Exception):
    log.error(f"Global 500 ERROR, URL:{request.url}\nHeaders:{request.headers}\n{traceback.format_exc()}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"code": 500, "data": {"tip": "Server error"}, "message": "fail"},
    )

@app.get("/healthcheck", include_in_schema=False)
def healthcheck():
    return {"status": "ok"}