

# import random
from datetime import datetime
from typing import List, Optional
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder

from dispatch.system_admin.menu_button.models import MenuButton
from sqlalchemy.exc import SQLAlchemyError





from .models import Menu, MenuCreate, MenuRead, MenuUpdate, MenuCreate, TreeMenuRead


def get(*, db_session, id: int) -> Optional[Menu]:
    """Returns an Menu given an Menu id."""
    return db_session.query(Menu).filter(Menu.id == id).one_or_none()

def get_by_ids(*, db_session, id_list: list) -> List[Optional[Menu]]:
    """Returns an MenuButton given an MenuButton id."""
    return db_session.query(Menu).filter(Menu.id.in_(id_list)).all()

def get_by_name(*, db_session, name: str) -> Optional[Menu]:
    """Returns an Menu given an Menu code address."""
    return db_session.query(Menu).filter(Menu.name == name).one_or_none()


def get_default_Menu(*, db_session ) -> Optional[Menu]:
    """Returns an Menu given an Menu code address."""
    return db_session.query(Menu).first()


def get_all(*, db_session) -> List[Optional[Menu]]:
    """Returns all Menus."""
    return db_session.query(Menu)

def get_all_active(*, db_session) -> List[Optional[Menu]]:
    """Returns all Menus."""
    return db_session.query(Menu).filter(Menu.status == True,Menu.is_deleted != 1).all()

def create(*, db_session, Menu_in: MenuCreate) -> Menu:
    """Creates an Menu.""" 


    parent = None
    if Menu_in.parent_id is not None and Menu_in.parent_id != -1:
        parent = get(db_session= db_session,id = Menu_in.parent_id) 
    contact = Menu(**Menu_in.model_dump(exclude={"flex_form_data","parent"}),
                    flex_form_data=Menu_in.flex_form_data,
                    parent = parent
                    )

    db_session.add(contact)
    db_session.commit()
    return contact


def update(
    *,
    db_session,
    Menu: Menu,
    Menu_in: MenuUpdate,
) -> Menu:

    update_data = Menu_in.dict(
        exclude={"flex_form_data","parent"},
    )
    for field, field_value in update_data.items():
        setattr(Menu, field, field_value)

    parent = None
    if Menu_in.parent_id is not None and Menu_in.parent_id != -1:
        parent = get(db_session= db_session,id = Menu_in.parent_id) 
    Menu.parent = parent
    Menu.flex_form_data = Menu_in.flex_form_data
    Menu.updated_at = datetime.utcnow()
    db_session.add(Menu)
    db_session.commit()
    return Menu


def delete(*, db_session, id: int):
    db_session.query(Menu).filter(Menu.id == id).delete()
    db_session.commit()
    return MenuRead(id=id) 


def build_tree(nodes, parent=None) -> TreeMenuRead:
    tree = []
    for node in nodes:
        if node.parent == parent:
            children = build_tree(nodes, node.id)
            node.children = children
            tree.append(node)
    return tree


def create_menu_and_button(*, session, menu_in: dict):
    """
    menu_in = {
        "menu": {
            
            "is_catalog": false,
            "web_path":"/123456"
        },
        "menu_buttons": [
            {
                "name": "Create123",
                "value": "Create123",
                "api": "",
                "method": 1

            },
            {
                "name": "Create456",
                "value": "Create456",
                "api": "",
                "method": 1
            }
        
        ]
    }
    """
    if not menu_in or not menu_in.get('menu') or not menu_in.get('menu_buttons'):
        raise HTTPException(f"input order info must have 'order' and 'order_items' fields")

    menu_data = menu_in["menu"]
    buttons_data = menu_in["menu_buttons"]

    try:
        result = {}
        if menu_data.get("parent_name"):
            parent = get_by_name(db_session=session, name=menu_data["parent_name"])
            if parent:
                menu_data["parent_id"] = parent.id
        del menu_data["parent_name"]
        menu = Menu(**menu_data)
        session.add(menu)
        session.flush()
        result["menu"] = jsonable_encoder(menu)

        result["menu_buttons"] = []
        for item_data in buttons_data:
            item_data['menu_id'] = menu.id
            button_item = MenuButton(**item_data)
            session.add(button_item)
            result["menu_buttons"].append(jsonable_encoder(button_item))

        session.commit()
        return result

    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(f"创建订单失败: {str(e)}")


def update_menu_and_button(*, session, menu_in: dict):

    menu = get_by_name(db_session=session, name=menu_in["name"])


    if 'add_button' in menu_in:
        for add_item in menu_in['add_button']:
            add_item['menu_id'] = menu.id
            button_item = MenuButton(**add_item)
            session.add(button_item)

    if 'delete_button' in menu_in:
        for delete_item in menu_in['delete_button']:
            button_item = session.query(MenuButton).filter(MenuButton.menu_id == menu.id, MenuButton.name == delete_item).one_or_none()
            if button_item:
                session.delete(button_item)
    
    if 'update_button' in menu_in:
        for update_item in menu_in['update_button']:
            button_item = session.query(MenuButton).filter(MenuButton.menu_id == menu.id, MenuButton.name == update_item['name']).one_or_none()
            if button_item:
                for field, field_value in update_item.items():
                    setattr(button_item,field, field_value)

    
    keys_to_remove = ["add_button","delete_button","update_button"]

    for key in keys_to_remove:
        if key in menu_in:
            del menu_in[key]


    for field, field_value in menu_in.items():
        setattr(menu, field, field_value)

    session.add(menu)
    session.commit()
    return menu


def delete_menu_and_button(*, session, menu_in: dict):
    menu = session.query(Menu).filter(Menu.name == menu_in["name"], Menu.web_path == menu_in["web_path"]).one_or_none()
    if not menu:
        return True
    
    menu_button = session.query(MenuButton).filter(MenuButton.menu_id == menu.id).all()
    if menu_button:
        for button in menu_button:
            session.delete(button)
    # 删除菜单
    session.delete(menu)
    session.commit()
    return True

