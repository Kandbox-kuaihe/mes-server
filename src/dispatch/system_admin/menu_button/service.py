

# import random
from datetime import datetime
from typing import List, Optional



from .models import MenuButton, MenuButtonCreate, MenuButtonRead, MenuButtonUpdate, MenuButtonCreate
from dispatch.system_admin.menu.models import Menu 

def get(*, db_session, id: int) -> Optional[MenuButton]:
    """Returns an MenuButton given an MenuButton id."""
    return db_session.query(MenuButton).filter(MenuButton.id == id).one_or_none()

def get_by_ids(*, db_session, id_list: list) ->  List[Optional[MenuButton]]:
    """Returns an MenuButton given an MenuButton id."""
    return db_session.query(MenuButton).filter(MenuButton.id.in_(id_list)).all()


def get_by_name(*, db_session, name: str) -> Optional[MenuButton]:
    """Returns an MenuButton given an MenuButton code address."""
    return db_session.query(MenuButton).filter(MenuButton.name == name).one_or_none()


def get_default_MenuButton(*, db_session ) -> Optional[MenuButton]:
    """Returns an MenuButton given an MenuButton code address."""
    return db_session.query(MenuButton).first()


def get_all(*, db_session) -> List[Optional[MenuButton]]:
    """Returns all MenuButtons."""
    return db_session.query(MenuButton)

  

def create(*, db_session, MenuButton_in: MenuButtonCreate) -> MenuButton:
    """Creates an MenuButton.""" 

    menu = db_session.query(Menu).filter(Menu.id == MenuButton_in.menu.id).one_or_none()
    if not menu:
        raise ValueError("Menu not found")
    contact = MenuButton(**MenuButton_in.model_dump(exclude={"flex_form_data","menu"}),
                    flex_form_data=MenuButton_in.flex_form_data,
                    menu=menu
                    )
    
    db_session.add(contact)
    db_session.commit()
    return contact


def update(
    *,
    db_session,
    MenuButton: MenuButton,
    MenuButton_in: MenuButtonUpdate,
) -> MenuButton:
    
    menu = db_session.query(Menu).filter(Menu.id == MenuButton_in.menu.id).one_or_none()
    if not menu:
        raise ValueError("Menu not found")
    update_data = MenuButton_in.dict(
        exclude={"flex_form_data","menu"},
    )
    for field, field_value in update_data.items():
        setattr(MenuButton, field, field_value)

    MenuButton.flex_form_data = MenuButton_in.flex_form_data
    MenuButton.updated_at = datetime.utcnow()
    MenuButton.menu = menu
    db_session.add(MenuButton)
    db_session.commit()
    return MenuButton


def delete(*, db_session, id: int):
    db_session.query(MenuButton).filter(MenuButton.id == id).delete()
    db_session.commit()
    return MenuButtonRead(id=id) 
