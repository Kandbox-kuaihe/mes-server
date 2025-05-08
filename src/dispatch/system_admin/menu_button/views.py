from dispatch.database import get_db
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from dispatch.system_admin.auth.models import DispatchUser
from dispatch.system_admin.auth.service import get_current_user

from dispatch.database_util.service import common_parameters, search_filter_sort_paginate
from .models import (
    MenuButtonBase,
    MenuButtonCreate,
    MenuButtonPagination,
    MenuButtonRead,
    MenuButtonUpdate,
)

from .service import create, delete, get, get_by_name, update

router = APIRouter()


@router.get("/", response_model=MenuButtonPagination)
def get_MenuButton(*, common: dict = Depends(common_parameters)):

    return search_filter_sort_paginate(model="MenuButton", **common)


@router.post("/", response_model=MenuButtonRead)
def create_MenuButton(*, db_session: Session = Depends(get_db), MenuButton_in: MenuButtonCreate,
                 current_user: DispatchUser = Depends(get_current_user)):
    """
    Create a new MenuButton contact.
    """
    
    MenuButton = get_by_name(db_session=db_session,name=MenuButton_in.name)
    
    if MenuButton:
        raise HTTPException(status_code=400, detail="The MenuButton with this code already exists.")
    
    MenuButton_in.created_by = current_user.email
    MenuButton_in.updated_by = current_user.email
    MenuButton = create(db_session=db_session, MenuButton_in=MenuButton_in)
    return MenuButton


@router.get("/{MenuButton_id}", response_model=MenuButtonRead)
def get_MenuButton(*, db_session: Session = Depends(get_db), MenuButton_id: int):
    """
    Get a MenuButton contact.
    """
    MenuButton = get(db_session=db_session, id=MenuButton_id)
    if not MenuButton:
        raise HTTPException(status_code=400, detail="The MenuButton with this id does not exist.")
    return MenuButton


@router.put("/{MenuButton_id}", response_model=MenuButtonRead)
def update_MenuButton(
    *,
    db_session: Session = Depends(get_db),
    MenuButton_id: int,
    MenuButton_in: MenuButtonUpdate, current_user: DispatchUser = Depends(get_current_user)
):
    """
    Update a MenuButton contact.
    """
    MenuButton = get(db_session=db_session, id=MenuButton_id)
    if not MenuButton:
        raise HTTPException(status_code=400, detail="The MenuButton with this id does not exist.")

    MenuButton = update(
        db_session=db_session,
        MenuButton=MenuButton,
        MenuButton_in=MenuButton_in,
    )
    return MenuButton


@router.put("/MenuButton_name/{MenuButton_name}", response_model=MenuButtonRead)
def update_MenuButton_by_code(
    *,
    db_session: Session = Depends(get_db),
    MenuButton_name: str,
    MenuButton_in: MenuButtonUpdate, current_user: DispatchUser = Depends(get_current_user)
):
    """
    Update a MenuButton contact.
    """
    MenuButton = get_by_name(db_session=db_session, name=MenuButton_name)
    if not MenuButton:
        raise HTTPException(status_code=400, detail="The MenuButton with this id does not exist.")

    MenuButton_in.updated_by = current_user.email
    MenuButton = update(
        db_session=db_session,
        MenuButton=MenuButton,
        MenuButton_in=MenuButton_in,
    )

    return MenuButton


@router.delete("/{id}")
def delete_MenuButton(*, db_session: Session = Depends(get_db), id: int):
    """
    Delete a MenuButton contact.
    """
    MenuButton = get(db_session=db_session, id=id)
    if not MenuButton:
        raise HTTPException(status_code=400, detail="The MenuButton with this id does not exist.")

    return delete(db_session=db_session, id=id)
