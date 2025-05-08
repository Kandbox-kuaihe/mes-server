import uuid
import re
from dispatch.database import get_db

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from dispatch.system_admin.auth.models import DispatchUser
from dispatch.system_admin.auth.service import get_current_user

from dispatch.database_util.service import common_parameters, search_filter_sort_paginate
from .models import (
    RoleCreate,
    RolePagination,
    RoleRead,
    RoleSelect,
    RoleSelectRespone,
    RoleUpdate,
)
from dispatch.system_admin.menu.models import TreeSelectMenuResponse, TreeSelectMenuRead, TreeMenuRead
from dispatch.system_admin.menu.service import build_tree, create, delete, get, get_all_active, get_by_name, update
from dispatch.system_admin.role import service as role_service
from dispatch.system_admin.role.service import get as get_search, sync_role_from_odoo_data, delete_role_from_odoo
from dispatch.system_admin.menu import service as menu_service
from dispatch.system_admin.menu_button import service as menu_button_service
from dispatch.system_admin.menu.models_secondary import role_menu_table as role_menu
from dispatch.system_admin.menu.models_secondary import role_menu_button_table as role_menu_button

from dispatch.mill import service as mill_service
from sqlalchemy.exc import IntegrityError


from .service import create, delete, get, get_all_select, get_by_name, update, search_in_children, get_all_children
from dispatch.system_admin.auth.service import update_user_permission_cache
router = APIRouter()


@router.get("/", response_model=RolePagination)
def get_Role(*, common: dict = Depends(common_parameters)):

    return search_filter_sort_paginate(model="Role", **common)


@router.post("/", response_model=RoleRead)
def create_Role(*, db_session: Session = Depends(get_db), Role_in: RoleCreate,
                 current_user: DispatchUser = Depends(get_current_user)):
    """
    Create a new Role contact.
    """
    
    Role = get_by_name(db_session=db_session,name=Role_in.name)
    
    if Role:
        raise HTTPException(status_code=400, detail="The Role with this code already exists.")
    permission_ids = [i['id'] for i in Role_in.menuPermissions if i.get('type') =='button']
    menu_ids = [i['id'] for i in Role_in.menuPermissions if i.get('type') !='button']
    if permission_ids:
        permission = menu_button_service.get_by_ids(db_session=db_session, id_list=permission_ids)
        Role_in.permission = permission
    if menu_ids:
        menu = menu_service.get_by_ids(db_session=db_session, id_list=menu_ids)
        Role_in.menu = menu
    if Role_in.homepage_id:
        homepage = menu_service.get(db_session=db_session, id=Role_in.homepage_id)
        Role_in.homepage_path = homepage.web_path

 
    Role_in.created_by = current_user.email
    Role_in.updated_by = current_user.email
    

    try:
        Role = create(db_session=db_session, Role_in=Role_in)
    except IntegrityError:
        raise HTTPException(
            status_code=400, detail="The key field cannot be empty.")

    return Role


@router.get("/{Role_id}", response_model=RoleRead)
def get_Role(*, db_session: Session = Depends(get_db), Role_id: int):
    """
    Get a Role contact.
    """
    Role = get(db_session=db_session, id=Role_id)
    if not Role:
        raise HTTPException(status_code=400, detail="The Role with this id does not exist.")
    return Role

@router.get("/search/role/{Role_id}", response_model=RoleRead)
def get_search_role(*, db_session: Session = Depends(get_db), Role_id: int):
    Role = get_search(db_session=db_session, id=Role_id)
    if not Role:
        raise HTTPException(status_code=400, detail="The Role with this id does not exist.")
    return Role

@router.get("/search/{Role_id}", response_model=TreeSelectMenuResponse)
def get_search_role(*, db_session: Session = Depends(get_db), common: dict = Depends(common_parameters), Role_id: int,
                    search_role: str):
    menu_list = [TreeSelectMenuRead(
        id=None,
        title="Root",
        hasChild=False,
        children=[],
    )]
    Menu = get_all_active(db_session=db_session)
    if not Menu:
        return TreeSelectMenuResponse(options=menu_list)

    role_data = role_service.get(db_session=db_session, id=Role_id)
    if not role_data:
        return TreeSelectMenuResponse(options=menu_list)

    permission_ids = [i.id for i in role_data.permission]
    menu_ids = [i.id for i in role_data.menu]
    origin_data = {}
    menu_list = []

    for menu in Menu:
        origin_data[menu.id] = menu
        menu_list.append(
            TreeMenuRead(
                id=menu.id,
                label=menu.name,
                children=[],
                parent=menu.parent_id
            )
        )

    tree_data = build_tree(menu_list)
    result_list = []

    search_pattern = re.compile(f"^{re.escape(search_role.lower())}.*")

    for first_menu in tree_data:
        first_data = TreeSelectMenuRead(
            id=first_menu.id,
            title=first_menu.label,
            hasChild=False,
            children=[],
            checkbox={"state": "checked"} if first_menu.id in menu_ids else None,
        )

        if len(first_menu.children) > 0:
            first_data.hasChild = True
            matching_children = search_in_children(first_menu, search_pattern)
            for second_menu in matching_children:
                second_data = TreeSelectMenuRead(
                    id=second_menu.id,
                    title=second_menu.label,
                    hasChild=False,
                    children=[],
                    checkbox={"state": "checked"} if second_menu.id in menu_ids else None,
                )

                if len(origin_data[second_menu.id].menu_button_to_menu) > 0:
                    second_data.hasChild = True
                    for menu_button in origin_data[second_menu.id].menu_button_to_menu:
                        if menu_button.is_deleted == 0:
                            second_data.children.append(
                                TreeSelectMenuRead(
                                    id=menu_button.id,
                                    title=menu_button.name,
                                    hasChild=False,
                                    children=[],
                                    checkbox={"state": "checked"} if menu_button.id in permission_ids else None,
                                    type="button",
                                )
                            )
                else:
                    second_data.hasChild = False

                first_data.children.append(second_data)

        if search_role:
            if search_pattern.match(first_menu.label.lower()) or matching_children:
                result_list.append(first_data)

        else:
            result_list.append(first_data)

    if len(result_list) == 1:
        first_data = result_list[0]
        if len(first_data.children) == 0 and first_data.hasChild == True:
            all_children = get_all_children(first_data, Menu, menu_ids)  # 根据你的逻辑获取子菜单
            first_data.children.extend(all_children)

    return TreeSelectMenuResponse(options=result_list)

@router.put("/{Role_id}", response_model=RoleRead)
def update_Role(
    *,
    db_session: Session = Depends(get_db),
    Role_id: int,
    Role_in: RoleUpdate, current_user: DispatchUser = Depends(get_current_user)
):
    """
    Update a Role contact.
    """
    Role = get(db_session=db_session, id=Role_id)
    if not Role:
        raise HTTPException(status_code=400, detail="The Role with this id does not exist.")
    permission_ids = [i['id'] for i in Role_in.menuPermissions if i.get('type') =='button']
    menu_ids = [i['id'] for i in Role_in.menuPermissions if i.get('type') !='button']
    if permission_ids:
        permission = menu_button_service.get_by_ids(db_session=db_session, id_list=permission_ids)
        Role_in.permission = permission
    else:
        Role_in.permission = Role.permission
    if menu_ids:
        menu = menu_service.get_by_ids(db_session=db_session, id_list=menu_ids)
        Role_in.menu = menu
    else:
        Role_in.menu = Role.menu
    if Role_in.homepage_id:
        homepage = menu_service.get(db_session=db_session, id=Role_in.homepage_id)
        Role_in.homepage_path = homepage.web_path
    else :
        Role_in.homepage_path = Role.homepage_path
 
    Role = update(
        db_session=db_session,
        Role=Role,
        Role_in=Role_in,
    )
    update_user_permission_cache(email=current_user.email)
    return Role


@router.put("/role_name/{role_name}", response_model=RoleRead)
def update_Role_by_name(
    *,
    db_session: Session = Depends(get_db),
    role_name: str,
    Role_in: RoleUpdate, current_user: DispatchUser = Depends(get_current_user)
):
    """
    Update a Role contact.
    """
    Role = get_by_name(db_session=db_session, name=role_name)
    if not Role:
        raise HTTPException(status_code=400, detail="The Role with this id does not exist.")

    Role_in.updated_by = current_user.email
    Role = update(
        db_session=db_session,
        Role=Role,
        Role_in=Role_in,
    )

    return Role


@router.delete("/{Role_id}")
def delete_Role(*, db_session: Session = Depends(get_db), Role_id: int):
    """
    Delete a Role contact.
    """
    Role = get(db_session=db_session, id=Role_id)
    if not Role:
        raise HTTPException(status_code=400, detail="The Role with this id does not exist.")
    
    try:
        return delete(db_session=db_session, id=Role_id)
    except IntegrityError:
        raise HTTPException(
            status_code=400, detail="There are associated records that cannot be deleted.")

    


@router.get("/data/roleSelect", response_model=RoleSelectRespone)
def getRoleSelect(*, db_session: Session = Depends(get_db)):
    """
    """
    data_list = get_all_select(db_session=db_session )
    
    result_list = []
    for row in data_list:
        result_list.append( RoleSelect( id = row.id,  name = row.name  ) )
    result_list.sort(key=lambda role: role.name[0].lower() if role.name else "")
 
    return RoleSelectRespone(options=result_list)

@router.post("/copy/{role_id}", response_model=RoleRead)
def copy_role(
    *,
    db_session: Session = Depends(get_db),
    role_in: RoleCreate,
    role_id: int,
    current_user: DispatchUser = Depends(get_current_user)
    ):
    role_in.created_by = current_user.email
    role_in.updated_by = current_user.email
    role_in.key = role_in.name
    try:
            Role = create(db_session=db_session, Role_in=role_in)
    except IntegrityError as err:
            print(err)
            raise HTTPException(
                status_code=400, detail="This name already exists.")
    if Role.id:
        try:
            # 通过ORM查询原角色关联菜单
            menus=db_session.query(role_menu).filter(role_menu.c.role_id==role_id).all()
            menu_buttons=db_session.query(role_menu_button).filter(role_menu_button.c.role_id==role_id).all()
            new_menu_records = []
            new_menu_button_records = []
            for menu in menus:
                # 构建新的菜单记录，将 role_id 替换为新角色的 id
                new_menu = {
                    'role_id': Role.id,
                    'menu_id': menu.menu_id
                }
                new_menu_records.append(new_menu)

            for menu_button in menu_buttons:
                new_menu_button = {
                    'role_id': Role.id,
                    'menu_button_id': menu_button.menu_button_id
                }
                new_menu_button_records.append(new_menu_button)
            if new_menu_records:
                db_session.execute(role_menu.insert(), new_menu_records)
            if new_menu_button_records:
                db_session.execute(role_menu_button.insert(), new_menu_button_records)
            db_session.commit()
        except IntegrityError as e:
            db_session.rollback()
            raise HTTPException(status_code=400, detail=f"Menu association failed: {str(e.orig)}")

    return Role



@router.post("/sync_role_from_odoo")
def sync_role_from_odoo(
        *,
        db_session: Session = Depends(get_db),
        role_in: dict,
        current_user: DispatchUser = Depends(get_current_user)
):
    """
    Sync role from odoo.
    """
    result = sync_role_from_odoo_data(session=db_session, role_in=role_in)

    return result

@router.post("/delete_role_from_odoo")
def delete_from_odoo(
        *,
        db_session: Session = Depends(get_db),
        role_in: dict,
        current_user: DispatchUser = Depends(get_current_user)
):
    result = delete_role_from_odoo(session=db_session, role_in=role_in)

    return result