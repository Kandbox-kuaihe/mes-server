"""
.. module: dispatch.auth.service
    :platform: Unix
    :copyright: (c) 2019 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
"""
import copy
from datetime import datetime
import re

from dispatch.common.utils.cli import import_database_models
from dispatch.database import SessionLocal
import logging
from typing import List, Optional
from fastapi import HTTPException, Depends
from fastapi.encoders import jsonable_encoder
from starlette.requests import Request
from starlette.status import HTTP_401_UNAUTHORIZED
from fastapi_permissions import Authenticated, configure_permissions
from fastapi import HTTPException, status
import dataclasses
# from dispatch.team import service as team_service
from dispatch.system_admin.role import service as role_service

from sqlalchemy.orm import Session
from dispatch.database import get_db

from dispatch.plugins.base import plugins
from dispatch.config import (
    DISPATCH_AUTHENTICATION_PROVIDER_SLUG,
    DISPATCH_AUTHENTICATION_DEFAULT_USER,
    DISPATCH_JWT_ALG,
    DISPATCH_JWT_EXP,
    DISPATCH_JWT_SECRET,
    # ENABLE_ED_JAVA_URL,
    REDIS_KEY_TEMPLATE_USER,
    REDIS_KEY_TEMPLATE_USER_PERMISSION,
    redis_pool,
)
import redis
import json

from dispatch.system_admin.role.models import Role, RoleRead
from dispatch.system_admin.auth.models_secondary import role_dispatch_user_table, user_mill_table
from dispatch.mill.models import Mill
# , UserLoginResponse
from .models import (
    DispatchUser,
    DispatchUserOrganization,
    UserRegister,
    UserRoles,
    UserUpdate,
    UserRead,
    generate_password,hash_password,
    UserPassWordUpdate
)
from jose import jwt
# from dispatch.order.external_api import  trigger_pc_logout

from dispatch.log import getLogger
log = getLogger(__name__)

credentials_exception = HTTPException(
    status_code=HTTP_401_UNAUTHORIZED, detail="Could not validate credentials"
)


def add(*, db_session: Session, dispatch_user: DispatchUser) -> DispatchUser:
    db_session.add(dispatch_user)
    # db_session.commit()
    return dispatch_user


session_local = SessionLocal()
redis_conn = redis.Redis(connection_pool=redis_pool)


def get(*, db_session, user_id: int) -> Optional[DispatchUser]:
    """Returns an user based on the given user id."""
    return db_session.query(DispatchUser).filter(DispatchUser.id == user_id).one_or_none()


def get_by_ids(*, db_session, user_id: List[int]) ->  List[Optional[DispatchUser]]:
    """Returns an user based on the given user id."""
    return db_session.query(DispatchUser).filter(DispatchUser.id.in_(user_id)).all()

def get_default_user(*, db_session ) -> Optional[DispatchUser]:
    """Returns an Menu given an Menu code address."""
    return db_session.query(DispatchUser).first()

def get_by_default_org_code(*, db_session,org_code: str ) -> Optional[DispatchUser]:
    """Returns an Menu given an Menu code address."""
    return db_session.query(DispatchUser).filter(DispatchUser.org_code == org_code).one_or_none()

def get_by_email(*, db_session, email: str) -> Optional[DispatchUser]:
    """Returns an user object based on user email."""
    return db_session.query(DispatchUser).filter(DispatchUser.email == email).one_or_none()


def get_by_org_team_role(*, db_session, org_code: str,team_id:int,role:str) -> List[Optional[DispatchUser]]:
    """Returns an user object based on user email."""
    return db_session.query(DispatchUser).filter(
        DispatchUser.org_code == org_code,
        DispatchUser.default_team_id==team_id,
        DispatchUser.role==role).all()

def get_by_email_and_org(*, db_session, email: str, org_id: int) -> Optional[DispatchUser]:
    """Returns an user object based on user email."""
    return (
        db_session.query(DispatchUser)
        .filter(DispatchUser.email == email, DispatchUser.org_id == org_id)
        .one_or_none()
    )


def get_by_org_id(*, db_session, org_id: int) -> Optional[DispatchUser]:
    """Returns an user object based on user email."""
    return db_session.query(DispatchUser).filter(DispatchUser.org_id == org_id).all()


def create(*, db_session, user_in: UserRegister) -> DispatchUser:
    """Creates a new dispatch user."""
    # pydantic forces a string password, but we really want bytes
    password = bytes(user_in.password, "utf-8")
    user = DispatchUser(**user_in.dict(exclude={
        "password", "en_code","import_sample_data","planner_code","role","mill"
        }), password=password)
    db_session.add(user)
    db_session.commit()
    return user


def get_or_create(*, db_session, user_in: UserRegister) -> DispatchUser:
    """Gets an existing user or creates a new one."""
    user = get_by_email(db_session=db_session, email=user_in.email)
    if not user:
        return create(db_session=db_session, user_in=user_in)
    return user


def update_by_org_code(*, db_session, org_id: int, org_code: str) -> DispatchUser:
    """Updates a user."""
    user_list = get_by_org_id(db_session=db_session, org_id=org_id)
    for user in user_list:
        user.org_code = org_code
        db_session.add(user)
    db_session.commit()
    return user

def update_email_password(*, db_session, user_id: int, email: str,password: str,user_data: DispatchUser = None) -> DispatchUser:
    """Updates a user."""
    # 如果传递了 user_data 就不需要在查询一边了
    if not user_data:
        user = get(db_session=db_session, user_id=user_id)
    else:
        user = user_data

    # user = get(db_session=db_session, user_id=user_id)

    user_in = UserUpdate(**user.__dict__)
    
    user.email = email
    user.password =  user_in.password_required(password)
    db_session.add(user)
    db_session.commit()
    return user

def update(*, db_session, user: DispatchUser, user_in: UserUpdate, token:str, current_user_id:int,roles:List[Role] = [],mills:List[Mill]) -> DispatchUser:
    """Updates a user."""
 
    new_managed_teams = []
    user_data = jsonable_encoder(user)
    update_data = user_in.dict(exclude ={
        "role","mill" 
        }
    )
    if "old_password" in update_data:
        update_data.pop("old_password")
    password_updated_flag = False
    if "password" in update_data:
        if update_data["password"]:
            update_data["password"] = user_in.password_required(update_data["password"])
            password_updated_flag = True
        else:
            update_data.pop("password")
    for field in user_data:
        if field in update_data:
            setattr(user, field, update_data[field])

    user.role = roles
    user.mill = mills
    user.managed_teams = new_managed_teams
    db_session.add(user)
    db_session.commit()
    if password_updated_flag:
        pass
        # if ENABLE_ED_JAVA_URL:
            # pass
            # trigger_pc_logout(token = token, 
            #     target_user_id = user.id,
            #     current_user_id = current_user_id)
        # TODO, clear login cache? 2024-01-16 21:03:24
        
    return user


def update_user_org(*, db_session, user: DispatchUser, user_in: UserUpdate) -> DispatchUser:
    user_data = jsonable_encoder(user)
    update_data = user_in.dict(skip_defaults=True)
    for field in user_data:
        if field in update_data:
            setattr(user, field, update_data[field])

    # user.managed_teams = new_managed_teams
    db_session.add(user)
    db_session.commit()
    return user

def update_user_org(*, db_session, user: DispatchUser, user_in: UserUpdate) -> DispatchUser:
    user_data = jsonable_encoder(user)
    update_data = user_in.dict(skip_defaults=True)
    for field in user_data:
        if field in update_data:
            setattr(user, field, update_data[field])

    # user.managed_teams = new_managed_teams
    db_session.add(user)
    db_session.commit()
    return user

def get_current_user(*, db_session: Session = Depends(get_db), request: Request) -> DispatchUser:
    """Attempts to get the current user depending on the configured authentication provider."""
    # redis_conn = redis.Redis(connection_pool=redis_pool)

    if DISPATCH_AUTHENTICATION_PROVIDER_SLUG:
        auth_plugin = plugins.get(DISPATCH_AUTHENTICATION_PROVIDER_SLUG)
        user_email = auth_plugin.get_current_user(request)
    else:
        log.debug("No authentication provider. Default user will be used")
        user_email = DISPATCH_AUTHENTICATION_DEFAULT_USER
    user = get_user_redis(user_email=user_email, request=request)
    if not user:
        raise HTTPException(status_code=401, detail="User Sign in expired")
    return user


def check_permission(request:Request) -> bool:
    path = request.scope['route'].path
    method = request.scope['method']
    auth_plugin = plugins.get(DISPATCH_AUTHENTICATION_PROVIDER_SLUG)
    email = auth_plugin.get_current_user(request)
    if not email :
        raise HTTPException (status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Permission denied: Missing for user {email}")
    permission = get_or_set_user_permison(email=email)
    if permission is None:
        raise HTTPException (status_code=status.HTTP_403_FORBIDDEN, detail=f"Permission denied Could not retrieve permissions for user {email}")

    curr_url = f'{method}:{path}'
    all_permissions = permission.get('all', set())
    user_permissions = permission.get('user', set())
    if curr_url in all_permissions:
        has_permission = curr_url in user_permissions
        log.debug("check_permission: result %s %s %s",email,curr_url,has_permission)
        if not has_permission:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Permission denied for user {email} on {curr_url}")
        return has_permission
    else:
        log.debug('check_permission: Route %s is not managed by the permission system.', curr_url)
        return True 


def get_or_set_user_permison(email:str) -> Optional[dict]:
    user_permission_key = REDIS_KEY_TEMPLATE_USER_PERMISSION.format(email)
    user_permission = redis_conn.get(user_permission_key)
    if user_permission:
        try:
            data = json.loads(user_permission)
            data['user'] = set(data['user'])
            data['all'] = set(data['all'])
            log.debug("%sload get_or_set_user_permison: %s user:%s, all:%s", redis_conn.client, email, len(data['user']),len(data['all']))
            return data
        except json.JSONDecodeError:
            log.warning("Failed to decode JSON permission data for key: %s", user_permission_key)
            return None
    else:
        return update_user_permission_cache(email=email)


def update_user_permission_cache(email:str):
    user_permission_key = REDIS_KEY_TEMPLATE_USER_PERMISSION.format(email)
    db_user = get_by_email(db_session=session_local, email=email)
    if not db_user:
        raise ValueError("get_or_set_user_permison error: Could not retrieve user for key %s", user_permission_key)
    user_ = set()
    for role in db_user.role:
        for p in role.permission:
            user_.add( f"{p.method.name}:{p.api.rstrip('/')}")
    
    all_ = set()
    for role in role_service.get_all(db_session=session_local):
        for p in role.permission:
            all_.add( f"{p.method.name}:{p.api.rstrip('/')}")

    redis_conn.set(user_permission_key, json.dumps({"all": list(all_), "user": list(user_)}), ex=DISPATCH_JWT_EXP)
    log.debug("set get_or_set_user_permison: %s user:%s, all:%s", email, len(user_),len(all_))
    return {"all": all_, "user": user_}


def remove_user_permission_cache(email:str):
    user_permission_key = REDIS_KEY_TEMPLATE_USER_PERMISSION.format(email)
    log.debug("remove_user_permission_cache: %s", user_permission_key)
    return redis_conn.delete(user_permission_key)


def remove_user_info_cache(email:str, session_id:str):
    user_info_key = REDIS_KEY_TEMPLATE_USER.format(f"{email}:{session_id}")
    log.debug("remove_user_info_cache: %s", user_info_key)
    return redis_conn.delete(user_info_key)


def get_user_by_id(user_id) -> DispatchUser:
    """Attempts to get the current user depending on the configured authentication provider."""
    return get_or_set_user_redis(user_id=user_id)


def get_user_redis(user_email=None, user_id=None, reload=False,mill=None, request: Request = None) -> DispatchUser:
    
    # 获取 session_id
    session_id = None
    
    # 从请求头获取 token
    auth_header = request.headers.get("Authorization") if request else None
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        try:
            # 直接从 token 解析获取 session_id
            token_data = jwt.decode(token, DISPATCH_JWT_SECRET, algorithms=[DISPATCH_JWT_ALG])
            session_id = token_data.get("session_id")
        except Exception as e:
            log.exception(f"get_or_set_user_redis error: {e}")

    # 如果还是没有 session_id，尝试从请求状态获取
    if not session_id and request and hasattr(request.state, 'session_id'):
        session_id = request.state.session_id

    if user_email is not None:
        user_redis_key = REDIS_KEY_TEMPLATE_USER.format(f"{user_email}:{session_id}" if session_id else user_email) 
    elif user_id is not None:
        user_redis_key = REDIS_KEY_TEMPLATE_USER.format(f"id:{user_id}:{session_id}" if session_id else f"id:{user_id}")
    else:
        raise ValueError("get_or_set_user_redis, no id nor email")
    if reload:
        user_json = {}
    else:
        user_json = redis_conn.get(user_redis_key)
    if user_json:
        user_loaded = json.loads(user_json)
        user_ = UserRead(**user_loaded)
        return user_
    
def get_or_set_user_redis(user_email=None, user_id=None, reload=False,mill=None, request: Request = None) -> DispatchUser:
    
    # 获取 session_id
    session_id = None
    
    # 从请求头获取 token
    auth_header = request.headers.get("Authorization") if request else None
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        try:
            # 直接从 token 解析获取 session_id
            token_data = jwt.decode(token, DISPATCH_JWT_SECRET, algorithms=[DISPATCH_JWT_ALG])
            session_id = token_data.get("session_id")
        except Exception as e:
            log.exception(f"get_or_set_user_redis error: {e}")

    # 如果还是没有 session_id，尝试从请求状态获取
    if not session_id and request and hasattr(request.state, 'session_id'):
        session_id = request.state.session_id

    if user_email is not None:
        user_redis_key = REDIS_KEY_TEMPLATE_USER.format(f"{user_email}:{session_id}" if session_id else user_email) 
    elif user_id is not None:
        user_redis_key = REDIS_KEY_TEMPLATE_USER.format(f"id:{user_id}:{session_id}" if session_id else f"id:{user_id}")
    else:
        raise ValueError("get_or_set_user_redis, no id nor email")
    if reload:
        user_json = {}
    else:
        user_json = redis_conn.get(user_redis_key)
    if user_json:
        user_loaded = json.loads(user_json)
        user_ = UserRead(**user_loaded)
        return user_
    else:
        # Not in redis, or expired. Load it and set it.
        if user_email is not None:
            db_user = get_by_email(
                db_session=session_local, email=user_email
            )  # _or_create  user_in=UserRegister(
        else:
            db_user = get(db_session=session_local, user_id=user_id)

        db_user.__dict__["is_active"] = True if db_user.__dict__["is_active"] else False
        if '_sa_instance_state' in db_user.__dict__:
            del db_user.__dict__['_sa_instance_state']

        db_user.__dict__['role'] = []
        user_ = UserRead(**db_user.__dict__) 

      
        # 去掉时间字段
        user_data = user_.dict()
        del user_data['updated_at']
        del user_data['created_at'] 
            

        if mill:
            user_data['current_mill_id'] = mill.id
            user_data['current_mill_code'] = mill.code

        redis_conn.set(user_redis_key, json.dumps(user_data), ex=DISPATCH_JWT_EXP)
        session_local.close()
        return DispatchUser(**user_data)


def get_active_principals(user: DispatchUser = Depends(get_current_user)) -> List[str]:
    """Fetches the current participants for a given user."""
    principals = [Authenticated]
    principals.extend(getattr(user, "principals", []))
    return principals


Permission = configure_permissions(get_active_principals)


def get_org_user(*, db_session, user_id=None, org_id=None) -> Optional[DispatchUserOrganization]:
    """Returns an user object based on user email."""
    if user_id and org_id:
        return (
            db_session.query(DispatchUserOrganization)
            .filter(
                DispatchUserOrganization.dispatch_user_id == user_id,
                DispatchUserOrganization.organization_id == org_id,
            )
            .one_or_none()
        )
    elif user_id:
        return (
            db_session.query(DispatchUserOrganization)
            .filter(DispatchUserOrganization.dispatch_user_id == user_id)
            .one_or_none()
        )
    elif org_id:
        return (
            db_session.query(DispatchUserOrganization)
            .filter(DispatchUserOrganization.organization_id == org_id)
            .one_or_none()
        )
    else:
        return None


def delete(*, db_session, id: int):
    # TODO: When deleting, respect referential integrity here in the code. Or add cascading deletes
    # in models.py.
    db_session.query(role_dispatch_user_table).filter(role_dispatch_user_table.c.dispatch_user_id == id).delete()
    db_session.query(DispatchUser).filter(DispatchUser.id == id).delete()
    # db_session.query(DispatchUserOrganization).filter(
    #     DispatchUserOrganization.dispatch_user_id == id
    # ).delete()
    db_session.commit()


def get_current_role(
    request: Request, current_user: DispatchUser = Depends(get_current_user)
) -> UserRoles:
    """Attempts to get the current user depending on the configured authentication provider."""
    return current_user.role


def delete_by_org_id(*, db_session, org_id: int):

    db_session.query(DispatchUser).filter(DispatchUser.org_id == org_id).delete()
    db_session.query(DispatchUserOrganization).filter(
        DispatchUserOrganization.organization_id.in_([org_id, -org_id])
    ).delete(synchronize_session=False)
    db_session.commit()


def check_str(data):
    test_str = re.search(r"\W", data)
    if test_str == None:
        return True
    else:
        return False


def init_menu(db_session):
    pass
    

def update_password(*, db_session, user: DispatchUser, user_in: UserPassWordUpdate) -> DispatchUser:
    """Updates user password."""
 
    user_data = jsonable_encoder(user)
    update_data = user_in.dict(exclude={'id'})
    if "old_password" in update_data:
        update_data.pop("old_password")
    password_updated_flag = False
    if "password" in update_data:
        if update_data["password"]:
            update_data["password"] = user_in.password_required(update_data["password"])
            password_updated_flag = True
        else:
            update_data.pop("password")
    for field in user_data:
        if field in update_data:
            setattr(user, field, update_data[field])


    db_session.add(user)
    db_session.commit()
    if password_updated_flag:
        pass
        
    return user