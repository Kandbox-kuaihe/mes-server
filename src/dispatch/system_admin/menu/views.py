from collections import defaultdict
import copy
import json
# from dispatch.common.utils.read_menu_js import get_menu
from dispatch.common.utils.read_menu_js import get_menu
from dispatch.database import get_db
from typing import List
from sqlalchemy import delete, text
from sqlalchemy.exc import IntegrityError

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from dispatch.system_admin.auth.models import DispatchUser
from dispatch.system_admin.auth.service import get_current_user

from dispatch.database_util.service import common_parameters, search_filter_sort_paginate
from dispatch.system_admin.menu_button.models import MenuButtonCreate, MenuButton
from dispatch.system_admin.menu.models import (
    Menu,
    MenuBase,
    MenuCreate,
    MenuInitRespone,
    MenuPagination,
    MenuRead,
    MenuUpdate,
    TreeMenuRead,
    TreeSelectMenuRead,
    TreeSelectMenuResponse,
    TreeTopMenuRead,
)

from dispatch.system_admin.menu.service import build_tree, create, delete, get, get_all_active, get_by_name, update,get_all, create_menu_and_button, update_menu_and_button, delete_menu_and_button

from dispatch.system_admin.role import service as role_service
from dispatch.system_admin.menu_button import service as menu_button_service
from dispatch.system_admin.menu.models_secondary import role_menu_table, role_menu_button_table
from dispatch.system_admin.role.models import Role
from dispatch.system_admin.import_menu_button import import_menu_button
from dispatch.system_admin.menu.utils import InitMenuButtonSettings

router = APIRouter()

@router.get("/get_by_role/{role_id}", response_model=MenuPagination)
def get_menu_by_role(role_id: int, common: dict = Depends(common_parameters), db_session: Session = Depends(get_db)):
    """
    根据角色 ID 获取菜单列表，支持搜索、过滤、排序和分页
    """
    # 根据角色 ID 获取菜单 ID 列表
    menus_roles = db_session.query(role_menu_table).filter(role_menu_table.c.role_id == role_id).all()
    menu_ids = [item.menu_id for item in menus_roles]
    if menu_ids:
        # 如果有菜单 ID，添加到通用参数中
        common["filter_type"] = "and"
        common["fields"] = ["id"]
        common["ops"] = ["in"]
        common["values"] = [menu_ids]

    common["fields"].append("title")
    common["ops"].append("!=")
    common["values"].append("")
    return search_filter_sort_paginate(model="Menu", **common)


@router.get("/", response_model=MenuPagination)
def get_Menu(*, common: dict = Depends(common_parameters)):

    if common["query_str"]:
        common["filter_type"]  = "or"
        common["fields"] = ["name","title","web_path"]
        common["ops"] = ["like","like","like"]
        common["values"] = [f"%{common['query_str']}%",f"%{common['query_str']}%",f"%{common['query_str']}%"]

        common["query_str"] = ''

    return search_filter_sort_paginate(model="Menu", **common)


@router.post("/", response_model=MenuRead)
def create_Menu(*, db_session: Session = Depends(get_db), Menu_in: MenuCreate,
                 current_user: DispatchUser = Depends(get_current_user)):
    """
    Create a new Menu contact.
    """
    
    Menu = get_by_name(db_session=db_session,name=Menu_in.name)
    
    if Menu:
        raise HTTPException(status_code=400, detail="The Menu with this code already exists.")
    
    Menu_in.created_by = current_user.email
    Menu_in.updated_by = current_user.email
    Menu = create(db_session=db_session, Menu_in=Menu_in)
    return Menu


@router.get("/{Menu_id}", response_model=MenuRead)
def get_Menu(*, db_session: Session = Depends(get_db), Menu_id: int):
    """
    Get a Menu contact.
    """
    Menu = get(db_session=db_session, id=Menu_id)
    if not Menu:
        raise HTTPException(status_code=400, detail="The Menu with this id does not exist.")
    return Menu


@router.put("/{Menu_id}", response_model=MenuRead)
def update_Menu(
    *,
    db_session: Session = Depends(get_db),
    Menu_id: int,
    Menu_in: MenuUpdate, current_user: DispatchUser = Depends(get_current_user)
):
    """
    Update a Menu contact.
    """
    Menu = get(db_session=db_session, id=Menu_id)
    if not Menu:
        raise HTTPException(status_code=400, detail="The Menu with this id does not exist.")

    Menu = update(
        db_session=db_session,
        Menu=Menu,
        Menu_in=Menu_in,
    )
    return Menu


@router.put("/menu_name/{menu_name}", response_model=MenuRead)
def update_Menu_by_code(
    *,
    db_session: Session = Depends(get_db),
    menu_name: str,
    Menu_in: MenuUpdate, current_user: DispatchUser = Depends(get_current_user)
):
    """
    Update a Menu contact.
    """
    Menu = get_by_name(db_session=db_session, name=menu_name)
    if not Menu:
        raise HTTPException(status_code=400, detail="The Menu with this id does not exist.")

    Menu_in.updated_by = current_user.email
    Menu = update(
        db_session=db_session,
        Menu=Menu,
        Menu_in=Menu_in,
    )

    return Menu


@router.delete("/{id}")
def delete_Menu(*, db_session: Session = Depends(get_db), id: int):
    """
    Delete a Menu contact.
    """
    Menu = get(db_session=db_session, id=id)
    if not Menu:
        raise HTTPException(status_code=400, detail="The Menu with this id does not exist.")
    
    try:
        return delete(db_session=db_session, id=id)
    except IntegrityError:
        raise HTTPException(
            status_code=400, detail="There are associated records that cannot be deleted.")


@router.get("/data/treeSelect", response_model=TreeMenuRead)
def get_treeSelect(*, db_session: Session = Depends(get_db)):
    """
    Get a Menu contact.
    """
    Menu = get_all(db_session=db_session )
    if not Menu:
        raise HTTPException(status_code=400, detail="The Menu with this id does not exist.")
    
    menu_list = []
    for menu in Menu:
        menu_list.append(
            TreeMenuRead(
                id = menu.id,
                label = menu.name,
                children = [],
                parent= menu.parent_id
            )
        )
    tree_data  = build_tree(menu_list)

    tree_root = TreeMenuRead(id =-1, label =  "Root", children = tree_data)
 
    return tree_root


@router.get("/data/treeTop", response_model=TreeTopMenuRead)
def getTreeTopSelect(*, db_session: Session = Depends(get_db)):
    """
     
    """
    Menu = get_all_active(db_session=db_session )
    if not Menu:
        raise HTTPException(status_code=400, detail="The Menu with this id does not exist.")
    
    menu_list = [TreeMenuRead(
                id = None,
                label = "Root",
                children = [],
                parent= None
            )]
    for menu in Menu:
        if menu.parent_id is not None:
            continue
        menu_list.append(
            TreeMenuRead(
                id = menu.id,
                label = menu.name,
                children = [],
                parent= menu.parent_id
            )
        ) 

 
    return TreeTopMenuRead(options=menu_list)


@router.get("/data/menuTreeSelect/{role_id}", response_model=TreeSelectMenuResponse)
def get_menuTreeSelect(*, db_session: Session = Depends(get_db),role_id:int):
    """
    Get a Menu contact.
    """
    menu_list = [TreeSelectMenuRead(
            id = None,
            title = "Root",
            hasChild= False,
            children = [],
        )]
    Menu = get_all_active(db_session=db_session )
    if not Menu:
        return TreeSelectMenuResponse(options=menu_list)
    role_data = role_service.get(db_session=db_session, id=role_id)
    if not role_data:
        return TreeSelectMenuResponse(options=menu_list)
    permission_ids = [i.id for i in role_data.permission]
    menu_ids =[i.id for i in role_data.menu]
    origin_data = {}
    menu_list = []
    for menu in Menu:
        origin_data[menu.id] = menu
        menu_list.append(
            TreeMenuRead(
                id = menu.id,
                label = menu.name,
                children = [],
                parent= menu.parent_id
            )
        )
    tree_data  = build_tree(menu_list)
    result_list = []
    for fitst_menu in tree_data:
        
        first_data = TreeSelectMenuRead(
            id = fitst_menu.id,
            title =  fitst_menu.label,
            hasChild= False,
            children = [],
            checkbox =  { "state": "checked"} if fitst_menu.id in menu_ids else None ,
        )
        if len(fitst_menu.children) > 0:
            first_data.hasChild = True
            for second_menu in fitst_menu.children:

                second_data = TreeSelectMenuRead(
                    id = second_menu.id,
                    title =  second_menu.label,
                    hasChild= False,
                    children = [],
                    checkbox =  { "state": "checked"} if second_menu.id in menu_ids else None ,
                )
                        
                if len(origin_data[second_menu.id].menu_button_to_menu) > 0:
                    second_data.hasChild = True
                    for menu_button in origin_data[second_menu.id].menu_button_to_menu:
                        if menu_button.is_deleted == 0:
                            second_data.children.append(
                                TreeSelectMenuRead(
                                    id = menu_button.id,
                                    title =  menu_button.name,
                                    hasChild= False,
                                    children = [],
                                    checkbox =  { "state": "checked"} if menu_button.id in permission_ids else None ,
                                    type = "button",
                                )
                            )
                else:
                    second_data.hasChild = False

                first_data.children.append(second_data)
        else:
            first_data.hasChild = False
        result_list.append(first_data)
    result_list = [item for item in result_list if item.children]
    first_item = next((item for item in result_list if item.title == "Order"), None)
    last_second_item = next((item for item in result_list if item.title == "Master Data"), None)

    result_list = [item for item in result_list if item.title not in ["Order", "Master Data"]]

    if first_item:
        result_list.insert(0, first_item)
    if last_second_item:
        result_list.insert(-1 if len(result_list) > 0 else 0, last_second_item)
    return TreeSelectMenuResponse(options=result_list)



@router.post("/data/init_menu", response_model=MenuInitRespone)
def init_menu(*, db_session: Session = Depends(get_db)):
    """
    Create a new Menu contact.
    """
      
    try:

        data_list = get_menu()
        for row in data_list:
            first_data = get_by_name(db_session=db_session, name=row["name"])
            if first_data is None:
                first_data = create(db_session=db_session, Menu_in=MenuCreate(**row))
            for second_menu in row["children"]:
                second_menu['parent_id'] = first_data.id
                second_menu_icon = second_menu.get("icon")
                second_menu_desc = second_menu.get("desc")
                second_menu_data = get_by_name(db_session=db_session, name=second_menu["name"])
                if second_menu_data is None:
                    second_menu_data = create(db_session=db_session, Menu_in=MenuCreate(**second_menu))
                else:
                    second_menu_data.icon = second_menu_icon
                    second_menu_data.desc = second_menu_desc
                    Menu_in = MenuUpdate(**second_menu_data.__dict__)
                    second_menu_data = update(db_session=db_session, Menu=second_menu_data, Menu_in=Menu_in)
                second_menu_button_list = [i.name for i in second_menu_data.menu_button_to_menu ]
                for menu_button in second_menu["menu_button"]:
                    if menu_button['name']  in second_menu_button_list:
                        continue
                    menu_button['menu'] = second_menu_data
                    menu_button_service.create(db_session=db_session, MenuButton_in=MenuButtonCreate(**menu_button))
    except Exception as e:
        return MenuInitRespone(status="Fail")

 
    return MenuInitRespone(status="OK")



@router.post("/data/chongzhi_menu", response_model=MenuInitRespone)
def chongzhi_menu(*, db_session: Session = Depends(get_db), current_user: DispatchUser = Depends(get_current_user)):
    """
    Create a new Menu contact.
    """
      
    try:

        # 清空表并重置序列
        db_session.execute(role_menu_table.delete())
        db_session.execute(role_menu_button_table.delete())
        
        db_session.execute(text(f"DELETE FROM dispatch_organization_{current_user.org_code}.menu_button;"))
        db_session.execute(text(f"DELETE FROM dispatch_organization_{current_user.org_code}.menu;"))

        db_session.execute(text(f"ALTER SEQUENCE dispatch_organization_{current_user.org_code}.menu_button_id_seq RESTART WITH 1;"))
        db_session.execute(text(f"ALTER SEQUENCE dispatch_organization_{current_user.org_code}.menu_id_seq RESTART WITH 1;"))
        
        db_session.commit()
        
        
        data_list = get_menu()
        for row in data_list:
            first_data = get_by_name(db_session=db_session, name=row["name"])
            if first_data is None:
                first_data = create(db_session=db_session, Menu_in=MenuCreate(**row))
            for second_menu in row["children"]:
                second_menu['parent_id'] = first_data.id
                second_menu_data = get_by_name(db_session=db_session, name=second_menu["name"])
                if second_menu_data is None:
                    second_menu_data = create(db_session=db_session, Menu_in=MenuCreate(**second_menu))
                second_menu_button_list = [i.name for i in second_menu_data.menu_button_to_menu ]
                for menu_button in second_menu["menu_button"]:
                    if menu_button['name']  in second_menu_button_list:
                        continue
                    menu_button['menu'] = second_menu_data
                    menu_button_service.create(db_session=db_session, MenuButton_in=MenuButtonCreate(**menu_button))
    except Exception as e:
        return MenuInitRespone(status="Fail")

 
    return MenuInitRespone(status="OK")


@router.post("/data/init_menu_role_button", response_model=MenuInitRespone)
def init_menu_role_button(*, db_session: Session = Depends(get_db)):
    """
    Create  role_menu_table role_menu_button_table
    """

    try:
        role = db_session.query(Role).filter(Role.name == 'sys').first()

        menus = db_session.query(Menu).all()

        buttons = db_session.query(MenuButton).all()

        role_menu = []
        menu_button = []
        for menu in menus:

            is_menu = (
                db_session.query(role_menu_table)
                .filter(
                    role_menu_table.c.menu_id == menu.id,
                    role_menu_table.c.role_id == role.id,
                )
                .first()
            )

            if not is_menu:
                role_menu.append({
                    "menu_id": menu.id,
                    "role_id": role.id
                })


        for button in buttons:

            is_button = (
                db_session.query(role_menu_button_table)
                .filter(
                    role_menu_button_table.c.menu_button_id == button.id,
                    role_menu_button_table.c.role_id == role.id,
                )
                .first()
            )

            if not is_button:
                menu_button.append({
                    "menu_button_id": button.id,
                    "role_id": role.id
                })

        db_session.execute(role_menu_table.insert(), role_menu)
        db_session.execute(role_menu_button_table.insert(), menu_button)
        db_session.commit()
    except Exception as e:
        return MenuInitRespone(status="Fail")

    return MenuInitRespone(status="OK")


@router.post("/data/import_menu_button", response_model=MenuInitRespone)
def import_buttons(*, db_session: Session = Depends(get_db)):
    try:
        import_menu_button(db_session)
    except Exception as e:
        return MenuInitRespone(status="Fail")

    return MenuInitRespone(status="OK")


@router.post("/data/init_menu_button_settings", response_model=MenuInitRespone)
def init_all_static_data(*, db_session: Session = Depends(get_db), current_user: DispatchUser = Depends(get_current_user)):
    res = InitMenuButtonSettings.init_menu_button_settings(db_session, current_user)
    return res



@router.post("/create_menu_from_odoo")
def create_from_odoo(
        *,
        db_session: Session = Depends(get_db),
        menu_in: dict,
        current_user: DispatchUser = Depends(get_current_user)
):
    """
    Create a new menu and menu button from Odoo.
    """
    result = create_menu_and_button(session=db_session, menu_in=menu_in)

    return result


@router.post("/update_menu_from_odoo")
def update_from_odoo(
        *,
        db_session: Session = Depends(get_db),
        menu_in: dict,
        current_user: DispatchUser = Depends(get_current_user)
):
    result = update_menu_and_button(session=db_session, menu_in=menu_in)

    return result


@router.post("/delete_menu_from_odoo")
def delete_from_odoo(
        *,
        db_session: Session = Depends(get_db),
        menu_in: dict,
        current_user: DispatchUser = Depends(get_current_user)
):
    result = delete_menu_and_button(session=db_session, menu_in=menu_in)

    return result