from collections import defaultdict
from typing import Any,List

from jose import jwt
from uuid import uuid4
from dispatch.plugins.base import plugins
from dispatch.common.utils.read_menu_js import get_menu
from dispatch.database_util.init_data import init_menu_role
from dispatch.system_admin.menu_button import service as menu_button_service
from dispatch.config import (
    DEFAULT_ORG_MAX_NBR_JOBS, DEFAULT_ORG_MAX_NBR_TEAMS, DEFAULT_ORG_MAX_NBR_WORKERS, DISPATCH_AUTHENTICATION_PROVIDER_SLUG, DISPATCH_JWT_ALG, DISPATCH_JWT_EXP, DISPATCH_JWT_SECRET, REDIS_KEY_TEMPLATE_LOGIN_EXPIRE, REDIS_KEY_TEMPLATE_USER, 
    SQLALCHEMY_DATABASE_URI, 
    redis_pool, redis, 
    # SAMPLE_DATA_GENERATOR_URL_ROOT,
    PLANNER_TEMPLATE_DICT
)
from dispatch.config import KANDBOX_DATE_FORMAT, ENABLE_REGISTER
import logging
from dispatch.database_util.org_config import (
    # DEFAULT_JOB_FLEX_FORM_DATA,
    # DEFAULT_WORKER_FLEX_FORM_DATA,
    get_flex_form_schema,
    # team_flex_form_schema,
    # worker_flex_form_schema,
    # job_flex_form_schema,
    order_flex_form_schema,
    DEFAULT_ORG_SETTING,
    DEFAULT_WORK_CALENDAR
)
from fastapi import APIRouter, Body, Depends, Request, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from dispatch.common.utils.encryption import decrypt, encrypt
from dispatch.database_util.service import common_parameters, get_schema_session, search_filter_sort_paginate
from dispatch.database import get_auth_db as get_db
from dispatch.system_admin.auth.service import get as user_get
# from dispatch.job.service import SHORTUUID
from dispatch.org.models import OrganizationBase
from dispatch.org import service as org_service
# from dispatch.worker import service as worker_service
# from dispatch.system_admin.auth import service as auth_service
from dispatch.org.enums import OrganizationType 
from dispatch.system_admin.menu.models import MenuConfig, MenuCreate,Menu
from dispatch.system_admin.menu_button.models import MenuButtonCreate
from dispatch.system_admin.role import  service as role_service
from dispatch.system_admin.menu import  service as menu_service
from dispatch.mill import service as mill_service


from time import time

from dispatch.system_admin.role.models import RoleCreate, RoleRead

# from dispatch.team import service as team_service

# from dispatch.cloudmarket.instance import service as instance_service
# from dispatch.worker.models import WorkerUpdate
from .models import (
    DispatchUser,
    LoginRespones,
    MenuButtonPermission,
    UserLogin,
    UserPermissionRead,
    UserRegister,
    UserRead,
    UserRoles,
    UserUpdate,
    UserPagination,
    UserLoginResponse,
    UserRegisterResponse,
    UserPassWordUpdate
)
from dispatch.common.utils.string_checker import check_org_str


from .service import ( 
    get,
    get_by_email,
    get_or_set_user_redis,
    get_org_user,
    init_menu,
    update,
    create,
    get_current_user,
    delete,
    update_password,
    update_user_permission_cache,
    remove_user_info_cache,
    remove_user_permission_cache
)


from datetime import datetime, timedelta

from dispatch.database_util.service import get_schema_session
from fastapi.responses import JSONResponse

# from dispatch.planner_env.planner_service import get_active_planner

auth_router = APIRouter()
user_router = APIRouter()

from dispatch.log import getLogger
log = getLogger(__name__)


@user_router.get("/", response_model=UserPagination)
def get_users(
    *,
    current_user: DispatchUser = Depends(get_current_user),
    common: dict = Depends(common_parameters),
):
    """
    Get all users.
    """
    common["fields"] = ["org_id"]
    common["ops"] = ["=="]
    common["values"] = [current_user.org_id]
    # if current_user.role != UserRoles.SYSTEM:
    #     common["fields"].append("role")
    #     common["ops"].append("!=")
    #     common["values"].append(UserRoles.SYSTEM.value)
    return search_filter_sort_paginate(model="DispatchUser", **common)

@user_router.get("/{user_id}", response_model=UserRead)
def get_user(
    *, db_session: Session = Depends(get_db), 
    user_id: int,
    current_user: DispatchUser = Depends(get_current_user),
    ):
    """
    Get a user.
    """
    if current_user.role not in (UserRoles.OWNER, UserRoles.SYSTEM):
        raise HTTPException(status_code=400)

    user = get(db_session=db_session, user_id=user_id)
    if not user:
        raise HTTPException(status_code=400, detail="The user with this id does not exist.")
    if user.org_id != current_user.org_id:
        raise HTTPException(status_code=400, detail="The user with this id does not exist in this orgnization.")

    return user

@auth_router.get("/me", response_model=UserRead)
def get_me(
    req: Request,
    db_session: Session = Depends(get_db),
    current_user: DispatchUser = Depends(get_current_user),
):
    # current_user = get_current_user(db_session=db_session, request=req)
    user = user_get(db_session = db_session,user_id = current_user.id)
    user.current_mill_id = current_user.current_mill_id
    user.current_mill_code = current_user.current_mill_code
    return user

@user_router.get("/data/get_permission", response_model=UserPermissionRead)
def get_permission(
    *,
    db_session: Session = Depends(get_db),
    current_user: DispatchUser = Depends(get_current_user),
):
    permission = []
    menu = []
    key_list = []
    user = get(db_session=db_session, user_id=current_user.id) 
    menu_mapping = defaultdict(list)
    root_menu_sorted = []
    for role in user.role:
        for p in role.permission:
            key = f"{p.id}_{p.name}"
            if key in key_list:
                continue
            permission.append(MenuButtonPermission(id = p.id ,name = p.menu.name, path = p.menu.web_path,component_name =  p.menu.component_name, permission =  p.value,remark = p.remark))
            key_list.append(key)
        
        for p in role.menu:
            if not p.is_deleted:
                key = f"{p.id}_{p.name}"
                if key in key_list:
                    continue
                header = ""
                name = ""
                title = ""
                group = ""
                icon = ""
                href = ""
                desc = ""
                flag = True
                if p.parent_id is None:
                    header = p.name
                    name = p.name
                else:
                    flag = False
                    name = p.name
                    title = p.title
                    group = p.parent.name
                    icon = p.icon
                    href = p.web_path
                    desc = p.desc
                menu_obj = MenuConfig(
                        header = header,
                        name = name,
                        title = title,
                        group =group,
                        icon = icon,
                        href =href,
                        sort =p.sort,
                        desc = desc,
                        visible= p.visible,
                )
                menu.append(menu_obj)
                key_list.append(key)
                if flag:
                    root_menu_sorted.append(menu_obj)
                    # menu_mapping[name].append(menu_obj)
                else:
                    menu_mapping[group].append(menu_obj)
            else:
                continue

    root_menu_sorted = sorted(root_menu_sorted, key=lambda x: x.sort )

    
    menu_sorted =  []
    for root_menu in root_menu_sorted:
        menu_sorted.append(root_menu)
        sec_menu_list = menu_mapping.get(root_menu.name,[])
        sorted_menu_list = sorted(sec_menu_list, key=lambda x: x.sort ) 
        menu_sorted.extend(sorted_menu_list)
        

    return UserPermissionRead(permission=permission, menu=menu_sorted)


@user_router.put("/{user_id}", response_model=UserRead)
def update_user(
    *,
    db_session: Session = Depends(get_db),
    current_user: DispatchUser = Depends(get_current_user),
    user_id: int,
    user_in: UserUpdate,
):
    """
    Update a user.
    """
    # if current_user.id != user_id:
    #     if current_user.role not in (UserRoles.SYSTEM, UserRoles.OWNER, ):
    #         raise HTTPException(status_code=400, detail="Only owner can modify other users.")

    if current_user.id != user_id:

        sys_user = get(db_session=db_session, user_id=current_user.id)

        is_sys = False
        if sys_user and len(sys_user.role) > 0:
            for ul in sys_user.role:
                if ul.name == UserRoles.SYSTEM:
                    is_sys = True
                    break
        if not is_sys:
            raise HTTPException(status_code=400, detail="Only owner can modify other users.")


    user = get(db_session=db_session, user_id=user_id)
    if not user:
        raise HTTPException(status_code=400, detail="The user with this id does not exist.")
    


    if user_in.email == current_user.email:
        if user_in.password:
            if not user_in.old_password : # and (current_user.role != UserRoles.OWNER)
                raise HTTPException(status_code=400, detail="Current password must be provided.")
            if not user.check_password(user_in.old_password):
                raise HTTPException(status_code=400, detail="Current password is wrong.")
    
 

    current_user_from_db = get(db_session=db_session, user_id=current_user.id)
    if not current_user_from_db:
        raise HTTPException(status_code=400, detail="The user with this id does not exist.")

    roles = role_service.get_by_ids(db_session=db_session, ids=user_in.role)
    mills = mill_service.get_by_ids(db_session=db_session, id_list=user_in.mill)
    user = update(
        db_session=db_session, user=user, user_in=user_in, 
        token=current_user_from_db.token,
        current_user_id = current_user_from_db.id,roles = roles,mills=mills)
    
    redis_conn = redis.Redis(connection_pool=redis_pool)
    user_redis_key = REDIS_KEY_TEMPLATE_USER.format(user_in.email) 
    redis_conn.delete(user_redis_key)

    return user


@auth_router.post("/login", response_model=LoginRespones)
def login_user(
    req: Request,
    user_in: UserLogin,
    db_session: Session = Depends(get_db),
):
    try:
        message="succeed"
        data = None
        user_in.email = user_in.email.strip()
        user = get_by_email(db_session=db_session, email=user_in.email)
        # print(user.org_code, user.is_org_owner)
        if user and user.check_password(user_in.password):

            # 先生成 token，获取 session_id
            token = user.token
            # 解码 token 获取 session_id
            token_data = jwt.decode(token, DISPATCH_JWT_SECRET, algorithms=[DISPATCH_JWT_ALG])
            session_id = token_data["session_id"]
            
            # 将 session_id 存入请求状态
            req.state.session_id = session_id

            # reload user info for redis
            get_or_set_user_redis(user_email=user_in.email, reload=True, request=req)
            update_user_permission_cache(email=user_in.email)
            # NOT for authorization purpose
            # req.state.code = user.code
            # req.state.org_code = user.org_code
            if not user.is_active:
                message = f"User {user_in.email} is not activated..."
                return LoginRespones(status=0,message=message,data=data)

            # 登录时根据org查询实例表，根据实例表的user_id查询实际用户
            is_first_login = 0
            instance_id = ""
            # 没有org则为临时用户且未绑定或新建用户
            if user.org_id == -1:
                is_first_login = 1
                # instance = instance_service.get_by_temporary_username(
                #     db_session=db_session, username=user.email
                # )
                # instance_id = instance.instance_id
            # # 为owner则根据org查询instance
            # if user.role == "Owner":
            # instance = instance_service.get_by_organization_code(
            #     db_session=db_session, organization_code=user.org_code, status=["0", "1", "2"]
            # )
            # instance存在则说明是云市场用户，且已绑定org，则不需要绑定
            # if instance:
            #     instance_id = instance.instance_id
                # # 当前用户是原临时用户，则使用后续新建或绑定的用户返回用户信息
                # if instance.fk_admin_user_id != user.id:
                #     user = get(db_session=db_session, user_id=instance.fk_admin_user_id)

            #  添加三小时 不操作推出判断所需 redis 值
            #  TODO 2024-01-11 01:54:03 为什么有这个功能，DISPATCH_JWT_EXP 本身控制就可以了。。。
            # exp_time_sceonds = 3 * 60 * 60
            # now = time()
            # redis_conn = redis.Redis(connection_pool=redis_pool)
            # exp_rds_key = REDIS_KEY_TEMPLATE_LOGIN_EXPIRE.format(data["org_code"], data["email"], )
            # redis_conn.set(exp_rds_key, now, ex=exp_time_sceonds)
            data =  {
                "token": token, 
                "session_id": session_id,
                "is_first_login": is_first_login, 
                "instance_id": instance_id,
                "org_code": user.org_code,
                "org_id": user.org_id,
                "role": user.role,
                "default_team_id": user.default_team_id,
                "current_mill_id ": user.current_mill_id ,
                "userToken": f"{user.id}"

            }
        # elif not user:
        #     message = "Invalid Email"
        else:
            message = "Invalid email or password"


        return LoginRespones(status=1 if message =='succeed' else 0,message=message,data=data)
    except Exception as e:
        print(f"An exception occurred in login: {str(e)}")
        import traceback

        log.error(traceback.format_exc())
        return LoginRespones(status=0, message="internal error",result= "fail" ,data=None)


@auth_router.post("/mes/login/{token}",response_model=LoginRespones)
def mes_login(req: Request,token: str, db_session: Session = Depends(get_db)):
    data = None
    message ='succeed'
    payload = jwt.decode(token, DISPATCH_JWT_SECRET, algorithms=[DISPATCH_JWT_ALG])
    username = payload.get("email")
    print("Username:", username)
    email = username.strip()
    user = get_by_email(db_session=db_session, email=email)
    # print(user.org_code, user.is_org_owner)
    if user:

        # 先生成 token，获取 session_id
        # 解码 token 获取 session_id
        token_data = jwt.decode(token, DISPATCH_JWT_SECRET, algorithms=[DISPATCH_JWT_ALG])
        session_id = token_data["session_id"] if "session_id" in token_data else str(uuid4())
        print("session_id:", session_id)
        
        # 将 session_id 存入请求状态
        req.state.session_id = session_id

        # reload user info for redis
        get_or_set_user_redis(user_email=email, reload=True, request=req)
        update_user_permission_cache(email=email)
        # NOT for authorization purpose
        # req.state.code = user.code
        # req.state.org_code = user.org_code
        if not user.is_active:
            message = f"User {email} is not activated..."
            return LoginRespones(status=0,message=message,data=data)

        # 登录时根据org查询实例表，根据实例表的user_id查询实际用户
        is_first_login = 0
        instance_id = ""
        # 没有org则为临时用户且未绑定或新建用户
        if user.org_id == -1:
            is_first_login = 1
 
        data =  {
            "token": token, 
            "session_id": session_id,
            "is_first_login": is_first_login, 
            "instance_id": instance_id,
            "org_code": user.org_code,
            "org_id": user.org_id,
            "role": user.role,
            "default_team_id": user.default_team_id,
            "current_mill_id ": user.current_mill_id ,
            "userToken": f"{user.id}"

        }
    # elif not user:
    #     message = "Invalid Email"
    else:
        message = "Invalid email or password"

    return LoginRespones(status=1 if message =='succeed' else 0,message=message,data=data)



@auth_router.post("/logout")
def logout_user(
    req: Request,
    current_user: DispatchUser = Depends(get_current_user),
):
    auth_plugin = plugins.get(DISPATCH_AUTHENTICATION_PROVIDER_SLUG)
    user_data = auth_plugin.get_current_user_data(req)
    remove_user_permission_cache(email=current_user.email)
    remove_user_info_cache(email=current_user.email, session_id=user_data.get("session_id",""))
    return {"status":1, "message":"logout succeed", "result": "success"}


def import_sample_data(user: UserRegister, token):
    # import london data
    if user.import_sample_data == "no_data":
        return
    

def validate_create_user_request(user_in):
    if not user_in.en_code:
        flag = check_org_str(user_in.org_code)
        if not flag:
            raise HTTPException(
                status_code=400, detail="The organization name contains special characters. Only alphanumeric is allowed"
            )
    else:
        return True
    # user_in.org_code = user_in.org_code.lower()
    
    # if user_in.planner_code not in PLANNER_TEMPLATE_DICT.keys(): # ("single_planner", "pickdrop_planner"):
    #     raise HTTPException(status_code=400, detail=f"planner_code must be one of {list(PLANNER_TEMPLATE_DICT.keys())}")      
    # if user_in.import_sample_data != "no_data": 
    #     raise HTTPException(status_code=400, detail="import_sample_data must be no_data")      
    return True

@auth_router.post("/register", response_model=UserRegisterResponse)
def register_user(
    req: Request,
    user_in: UserRegister,
    db_session: Session = Depends(get_db),  #
):
    # Block registration if not enabled. 2022-09-23 01:21:38
    if ENABLE_REGISTER != "yes":
        raise HTTPException(status_code=400, detail="Registration is forbiddened. Please use marketplace to register.")
    validate_create_user_request(user_in)
    # check if user is null
    try:
        user_in.email = user_in.email.strip()
        if user_in.email:
            # 正常新增
            user_info = get_by_email(db_session=db_session, email=user_in.email)
            if user_info:
                raise HTTPException(
                    status_code=400, detail=f"User ({user_in.email}) already exists"
                )
        else:
            raise HTTPException(status_code=400, detail="Email can not be empty")

        if user_in.org_code:

 
            return registerUserAndOrg(
                db_session=db_session, 
                user_in=user_in) 

        if user_in.en_code:
            # check org table have data
            # check org_user table have data
            # add user data
            try:

                de_code = decrypt(user_in.en_code)
            except Exception:
                raise HTTPException(
                    status_code=400, detail="Please enter the correct organization Invitation code"
                )

            user_in.id = int(de_code.split("|")[0])
            user_in.org_id = int(de_code.split("|")[1])

            org_data = org_service.get(db_session=db_session, org_id=user_in.org_id)
            if not org_data:
                raise HTTPException(status_code=401, detail="The organization does not exist.")

            org_user = get_org_user(
                db_session=db_session, user_id=user_in.id, org_id=user_in.org_id
            )
            if not org_user:
                raise HTTPException(status_code=401, detail="User is not allowed to register.")
            
           
            user_in.org_code = org_data.code
            user_in.org_id = org_data.id
            user_in.default_team_id = org_user.team_id
            user_in.role = org_user.role
            user_in.is_active = True
            user_in.is_org_owner = True if org_user.role == UserRoles.OWNER else False
            user = create(db_session=db_session, user_in=user_in)

            # Remove the record by changing id.
            org_user.organization_id = 0 - org_user.organization_id
            db_session.add(org_user)
            db_session.commit()




            return user

        else:
            raise HTTPException(
                status_code=400, detail="Please enter the correct organization Invitation code"
            )
    except HTTPException as he:
        raise he
    # except Exception as e:
    #     log.error(f"Internal Registration Error 500: {str(e)}")
    #     raise HTTPException(
    #         status_code=400, detail=f"Internal Error: {str(e)} " # {e.detail if e.detail else str(e.orig)}
    #     )



# 注册的方法抽出来，实例注册也要调用该方法
def registerUserAndOrg(
    *, db_session: Session, user_in: UserRegister  # , org_id: str = None
):
    org_data = org_service.get(db_session=db_session, org_code=user_in.org_code)
    if org_data is None:

        org_in = OrganizationBase(
            code=user_in.org_code,
            # id=org_id,
            org_type=OrganizationType.DEFAULT, # if user_in.import_sample_data == "london_fsm" else OrganizationType.POC,
            org_setting=DEFAULT_ORG_SETTING,
            work_calendar=DEFAULT_WORK_CALENDAR,
            max_nbr_jobs=DEFAULT_ORG_MAX_NBR_JOBS,
            max_nbr_workers=DEFAULT_ORG_MAX_NBR_WORKERS,
            max_nbr_teams=DEFAULT_ORG_MAX_NBR_TEAMS,
            team_flex_form_schema= get_flex_form_schema(planner_type=user_in.planner_code,schema_type="team",),#team_flex_form_schema,
            worker_flex_form_schema=get_flex_form_schema(planner_type=user_in.planner_code,schema_type="worker",),#worker_flex_form_schema,
            job_flex_form_schema=get_flex_form_schema(planner_type=user_in.planner_code,schema_type="job",),#job_flex_form_schema,
            order_flex_form_schema=order_flex_form_schema,
        )
        org_in_dict = org_in.dict()
        # org_in_dict["id"] = org_id   # 初始化 配置 信息 是在这里 
        org_db = org_service.create(
            db_session=db_session, 
            planner_code = user_in.planner_code,
            **org_in_dict)
        
        # import sample data


        org_db_session = get_schema_session(org_code=user_in.org_code)  
        # default_team = team_service.get_by_code(
        #     db_session=org_db_session, code="default_team")
        # if not default_team:
        #     log.error("Failed to find team by team_code = default_team, no user creating.")
        #     raise HTTPException(status_code=400, detail="Failed to find team by team_code = default_team, no user creating.")

        # add user
        # user_in.role = role
        user_in.is_org_owner = True
        user_in.is_active = True
        user_in.org_id = org_db.id
        user_in.default_team_id = -1
        user = create(db_session=org_db_session, user_in=user_in)

        # create org_user relationship
        org_service.add_user(
            db_session=org_db_session,
            organization_id=org_db.id,
            dispatch_user_id=user.id,
            role=user.role,
            team_id=-1,
            worker_code=-1,
        )
        reurn_data = UserRegisterResponse(email = user.email,org_code = user.org_code,default_team_id = user.default_team_id,is_org_owner = user.is_org_owner,role =None,
                                          current_mill_id = user.current_mill_id,
                                          current_mill_code = user.current_mill_code,
                                            )
        # import_sample_data(user_in, user.token)
        
        
        init_menu_role(org_db_session=org_db_session,user_email =user.email)

        org_db_session.close()

        return reurn_data
    else:
        if not org_data.public_registration:
            raise HTTPException(status_code=400, detail="This organization already exists")
        else:
            # create invitation code dynamically by the team
            user_in.org_id = org_data.id
            user = create(db_session=db_session, user_in=user_in)
            return user




# @auth_router.post("/register_user_org", summary="Create a new org.")
# def register_user_org(
#     *,
#     db_session: Session = Depends(get_db),
#     org_in: OrganizationBase,
# ):
#     """
#     register add org  , no login info
#     """
#     org = org_service.get(db_session=db_session, org_code=org_in.code)
#     if org:
#         raise HTTPException(status_code=400, detail="add user org error. user code already exists")

#     org_in_dict = org_in.dict()
#     org_in_dict["id"] = SHORTUUID.random(length=9)
#     org = org_service.create(db_session=db_session, **org_in_dict)
#     en_code = encrypt(org.id)
#     return en_code


@user_router.delete("/{user_id}", summary="Delete an user.")
def delete_user(
    *,
    db_session: Session = Depends(get_db),
    user_id: str,
    current_user: DispatchUser = Depends(get_current_user),
):
    """
    Delete an worker job.
    """
    user = get(db_session=db_session, user_id=current_user.id)
    data = [item.key for item in user.role]
    if not user:
        raise HTTPException(status_code=400, detail="The requested user does not exist.")
    if data[0] != "sys":
        raise HTTPException(status_code=400, detail="No delete permission.")
    # 判断用户是否被worker绑定时
    # ref_user = worker_service.get_by_auth(db_session=db_session, email=user.email)
    # if ref_user:
    #     raise HTTPException(status_code=400, detail="Please remove the associated worker first")
    
    
    try:
        delete(db_session=db_session, id=user_id)
    except IntegrityError:
        raise HTTPException(
            status_code=400, detail="There are associated records that cannot be deleted.")
    
    return True





@auth_router.get("/profile", response_model=UserRead)
def get_me(
    req: Request,
    db_session: Session = Depends(get_db),
):
    current_user = get_current_user(db_session=db_session, request=req)
    
    response = {}
    response["accountScenarioCode"] = ""

    response["appMenuPermissionCodeList"] = [""]
    response["defaultTeam"] = ""
    response["email"] = current_user.email
    response["role"] = current_user.role
    return JSONResponse(response)


@user_router.post("/", response_model=UserRegisterResponse)
def post_user(
    *,
    db_session: Session = Depends(get_db),
    current_user: DispatchUser = Depends(get_current_user),
    user_in: UserRegister,
):
    """
    
    create user 
    related to same worker 

    """
    try:
        user_in.email = user_in.email.strip()
        if user_in.email:
            # 正常新增
            user_info = get_by_email(db_session=db_session, email=user_in.email)
            if user_info:
                raise HTTPException(
                    status_code=400, detail=f"User ({user_in.email}) already exists"
                )
        else:
            raise HTTPException(status_code=400, detail="Email can not be empty")
 
        user_in.org_id = current_user.org_id 
        org_data = org_service.get(db_session=db_session, org_id=user_in.org_id)
        if not org_data:
            raise HTTPException(status_code=401, detail="The organization does not exist.")
        
       

        user_in.org_code = org_data.code
        user_in.org_id = org_data.id
        user_in.is_team_worker = True 
        user_in.is_active = True
        user = create(db_session=db_session, user_in=user_in)

        roles = role_service.get_by_ids(db_session=db_session, ids=user_in.role)
        user.role = roles

        mill = mill_service.get_by_ids(db_session=db_session, id_list=user_in.mill)
        user.mill = mill

        db_session.add(user)
        db_session.commit()   


        return user
 
    except HTTPException as he:
        raise he 
    return None



@user_router.post("/update_user_mill/{mill_id}", response_model=UserRegisterResponse)
def update_user_mill(
    *,
    db_session: Session = Depends(get_db),
    current_user: DispatchUser = Depends(get_current_user),
    mill_id: int,
):
    """
    
    update user current mill

    """
    try:
         
        user = get(db_session=db_session, user_id=current_user.id)
        if not user:
            raise HTTPException(status_code=401, detail="The user does not exist.")
 
        mill = mill_service.get(db_session=db_session, mill_id=mill_id)
        if not mill:
            raise HTTPException(status_code=401, detail="The mill does not exist.")
        if all([role.name !='sys' for role in  user.role]):
            user_mill_ids = [ mill.id for mill in user.mill]
            if mill_id not in user_mill_ids:
                raise HTTPException(status_code=401, detail="The mill does not in users Mills.")
        
        user.current_mill_id = mill.id
        user.current_mill_code = mill.code
        db_session.add(user)
        db_session.commit()   
        get_or_set_user_redis(user_email=current_user.email, reload=True)

        return user
 
    except HTTPException as he:
        raise he 
    return None



@user_router.post("/new_update_user_mill/{mill_id}", response_model=UserRegisterResponse)
def new_update_user_mill(
    *,
    req: Request,
    db_session: Session = Depends(get_db),
    current_user: DispatchUser = Depends(get_current_user),
    mill_id: int,
):
    """
    
    update user current mill

    """
    try:
        
        mill = mill_service.get(db_session=db_session, mill_id=mill_id)
        if not mill:
            raise HTTPException(status_code=401, detail="The mill does not exist.")
       
        user = get_or_set_user_redis(user_email=current_user.email, reload=True,mill=mill, request=req)

        return user
 
    except HTTPException as he:
        raise he 
    return None

@user_router.post("/update_user_password",response_model=UserRead)
def update_user_password(
    *,
    db_session: Session = Depends(get_db),
    current_user: DispatchUser = Depends(get_current_user),
    user_in: UserPassWordUpdate,
):
    """
    Update user password.
    """
  
    user = get(db_session=db_session, user_id=user_in.id)
    if not user:
        raise HTTPException(status_code=400, detail="The user with this id does not exist.")
    

    if user.email == current_user.email:
        if user_in.password:
            if not user_in.old_password : # and (current_user.role != UserRoles.OWNER)
                raise HTTPException(status_code=400, detail="Current password must be provided.")
            if not user.check_password(user_in.old_password):
                raise HTTPException(status_code=400, detail="Current password is wrong.")
    

    user = update_password(db_session=db_session, user=user, user_in=user_in)

    return user

@user_router.post("/main_menu/update")
def update_pref_menu(
    *,
    db_session: Session = Depends(get_db),
    user_id: int=Body(...),
    menu_id: int=Body(...),
):
    

    menu = (db_session.query(Menu).filter(Menu.id == menu_id).first())
    if not menu:
        raise HTTPException(status_code=404, detail="Menu not found")
    
    user = get(db_session=db_session, user_id=user_id) 
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    

    user.current_menu_path = menu.web_path  
    db_session.commit()
    
    return user.current_menu_path