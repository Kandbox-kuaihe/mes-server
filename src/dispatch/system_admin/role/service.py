

# import random
from datetime import datetime
from typing import Any, List, Optional
from dispatch.system_admin.menu.models import Menu, TreeSelectMenuRead
from dispatch.system_admin.auth.models_secondary import role_dispatch_user_table
from dispatch.system_admin.menu_button.models import MenuButton
from sqlalchemy import or_


from .models import Role, RoleCreate, RoleRead, RoleUpdate, RoleCreate


def get(*, db_session, id: int) -> Optional[Role]:
    """Returns an Role given an Role id."""
    return db_session.query(Role).filter(Role.id == id).one_or_none()

def get_by_ids(*, db_session, ids: list) ->  List[Optional[Role]]:
    """Returns an MenuButton given an MenuButton id."""
    return db_session.query(Role).filter(Role.id.in_(ids)).all()


def get_by_name(*, db_session, name: str) -> Optional[Role]:
    """Returns an Role given an Role code address."""
    return db_session.query(Role).filter(Role.name == name).one_or_none()


def get_default_Role(*, db_session ) -> Optional[Role]:
    """Returns an Role given an Role code address."""
    return db_session.query(Role).first()


def get_all(*, db_session) -> List[Optional[Role]]:
    """Returns all Roles."""
    return db_session.query(Role)

  
def get_all_select(*, db_session) -> List[Optional[Role]]:
    """Returns all Roles."""
    return db_session.query(Role.id,Role.name).filter(Role.status == True).all()

def create(*, db_session, Role_in: RoleCreate) -> Role:
    """Creates an Role.""" 


    contact = Role(**Role_in.model_dump(exclude={"homepage_id","flex_form_data","menuPermissions"}),
                    flex_form_data=Role_in.flex_form_data)
    
    db_session.add(contact)
    db_session.commit()
    return contact


def update(
    *,
    db_session,
    Role: Role,
    Role_in: RoleUpdate,
) -> Role:

    update_data = Role_in.dict(
        exclude={"flex_form_data"},
    )
    for field, field_value in update_data.items():
        setattr(Role, field, field_value)

    Role.flex_form_data = Role_in.flex_form_data
    Role.updated_at = datetime.utcnow()
    db_session.add(Role)
    db_session.commit()
    return Role


def delete(*, db_session, id: int):
    db_session.query(role_dispatch_user_table).filter(role_dispatch_user_table.c.role_id == id).delete()
    db_session.query(Role).filter(Role.id == id).delete()
    db_session.commit()
    return RoleRead(id=id)


def search_in_children(menu, search_pattern):
    matching_children = []

    if menu.children:
        for child in menu.children:
            if search_pattern.match(child.label.lower()):
                matching_children.append(child)

            child_matches = search_in_children(child, search_pattern)
            if child_matches:
                matching_children.extend(child_matches)
    return matching_children


def get_all_children(menu_item, Menu, menu_ids):
    all_children = []

    for menu in Menu:
        if menu.parent_id == menu_item.id:
            child_menu = TreeSelectMenuRead(
                id=menu.id,
                title=menu.name,
                hasChild=False,
                children=[],
                checkbox={"state": "checked"} if menu.id in menu_ids else None,
            )
            all_children.append(child_menu)

    return all_children


# def get_all_children(menu_item, Menu, menu_ids):
#     """
#     递归获取指定菜单项的所有子菜单（直到 hasChild=False）。
#
#     :param menu_item: 当前菜单项对象，包含id和其他必要的信息
#     :param Menu: 所有菜单项的列表
#     :param menu_ids: 已选中的菜单ID列表，用于检查checkbox状态
#     :return: 当前菜单项的所有子菜单列表
#     """
#     all_children = []
#
#     # 遍历所有菜单项，查找属于当前菜单项的子菜单
#     for menu in Menu:
#         if menu.parent_id == menu_item.id:  # 如果父菜单 ID 匹配，说明是子菜单
#             child_menu = TreeSelectMenuRead(
#                 id=menu.id,
#                 title=menu.name,
#                 hasChild=False,
#                 children=[],
#                 checkbox={"state": "checked"} if menu.id in menu_ids else None,
#             )
#
#             # 如果该子菜单还有子菜单，递归调用获取更多子菜单
#             if menu.hasChild:
#                 child_menu.hasChild = True
#                 child_menu.children.extend(get_all_children(child_menu, Menu, menu_ids))
#
#             all_children.append(child_menu)
#
#     return all_children

def sync_role_from_odoo_data(*, session, role_in: dict):
    '''
    {
        "name": "test",
        "key": "test",
        "remark": "test",
        "homepage_path": 1,
        "sort":1,
        
        "menu": [
            {
                "name": 1,
                "web_path": 1,
                "menu_buttons": [
                    {
                        "name": 1,
                        "value": 1,
                        "api": 1,
                        "method": 1
                    }
                ],
            }
        ],
        
    }
    '''
    role = session.query(Role).filter(Role.name == role_in["name"]).first()
    if not role:
        create_role = {
            "name": role_in["name"],
            "key": role_in["key"],
            "remark": role_in["remark"],
            "homepage_path": role_in["homepage_path"],
            "sort": role_in["sort"],
            "admin":role_in["admin"],
        }
        role = Role(**create_role)
        session.add(role)
    menus = []
    permissions = []
    if "menu" in role_in and len(role_in["menu"]) > 0:
        for menu in role_in["menu"]:
            if not menu["web_path"]:
                menu_obj = session.query(Menu).filter(Menu.name == menu["name"], or_(Menu.web_path.is_(None), Menu.web_path== '')).first()
            else:
                menu_obj = session.query(Menu).filter(Menu.name == menu["name"], Menu.web_path == menu["web_path"]).first()
            if not menu_obj:
                continue
            menus.append(menu_obj)

            if "menu_buttons" in menu and len(menu["menu_buttons"]) > 0:
                for button in menu["menu_buttons"]:
                    button_obj = session.query(MenuButton).filter(MenuButton.name == button["name"], MenuButton.menu_id == menu_obj.id).first()
                    if button_obj:
                        permissions.append(button_obj)
    role_in["menu"] = menus
    role_in["permission"] = permissions


    for field, field_value in role_in.items():
        setattr(role, field, field_value)

    session.add(role)
    session.commit()
    return role



def delete_role_from_odoo(*, session, role_in: dict):
    role = session.query(Role).filter(Role.name == role_in["name"]).one_or_none()
    if not role:
        return True
    # 删除role
    session.delete(role)
    session.commit()
    return True

