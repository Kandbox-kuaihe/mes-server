from dispatch.database import get_db
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from dispatch.system_admin.auth.models import DispatchUser
from dispatch.system_admin.auth.service import get_current_user

from dispatch.database_util.service import common_parameters, search_filter_sort_paginate
from .models import (
    Order,
    OrderCreate,
    OrderPagination,
    OrderRead,
    OrderUpdate,
)
from .service import (
    create,
    delete,
    get,
    get_by_code,
    like_by_search_vector,
    update,
    process_xml_order,
    amend_code_null_db,
    create_order_and_items,
)

from ..order_item.service import process_xml_order_item, create as create_item

# import xmltodict

router = APIRouter()


@router.get("/", response_model=OrderPagination)
def get_orders(*, common: dict = Depends(common_parameters)):

    if common["query_str"]: 
        order_ids = like_by_search_vector(db_session = common["db_session"], 
                                        search_vector = common['query_str'] )
        
        common["fields"] = ["id"]
        common["ops"] = ["in"]
        common["values"] = [[i[0] for i in order_ids]]
        common["query_str"] = ''
    return search_filter_sort_paginate(model="Order", **common)


@router.post("/", response_model=OrderRead)
def create_order(*, db_session: Session = Depends(get_db), order_in: OrderCreate,
                 current_user: DispatchUser = Depends(get_current_user)):
    """
    Create a new order contact.
    """

    order_in.created_by = current_user.email
    order_in.updated_by = current_user.email
    order = create(db_session=db_session, order_in=order_in)
    return order


from fastapi import  Request


@router.post("/send_message/")
async def send_message(*,request: Request, db_session: Session = Depends(get_db), 
                 current_user: DispatchUser = Depends(get_current_user)):
    """
    Create a new order contact.
    """

    raw_body = await request.body()
    xml_bytes = raw_body.strip()
    order_in = process_xml_order(xml_bytes, db_session=db_session)  # Pass cleaned bytes

    order_created = get_by_code(db_session=db_session, code=order_in.order_code)
    if order_created:
        raise HTTPException(status_code=400, detail="The order with this code already exists.")

    order_in.created_by = current_user.email
    order_in.updated_by = current_user.email
    order = create(db_session=db_session, order_in=order_in)
    order_item_in = process_xml_order_item(xml_bytes)  # Pass cleaned bytes
    print(order_item_in)
    order_item = create_item(db_session=db_session, orderItem_in=order_item_in)
    
    return order



@router.get("/{order_id}", response_model=OrderRead)
def get_order(*, db_session: Session = Depends(get_db), order_id: int):
    """
    Get a order contact.
    """
    order = get(db_session=db_session, order_id=order_id)
    if not order:
        raise HTTPException(status_code=400, detail="The order with this id does not exist.")
    return order

@router.put("/amend_code_null")
def amend_code_null(*, db_session: Session = Depends(get_db)):
    result = amend_code_null_db(db_session=db_session)
    return {"status": "ok", "result": result}

@router.put("/{order_id}", response_model=OrderRead)
def update_order(
    *,
    db_session: Session = Depends(get_db),
    order_id: int,
    order_in: OrderUpdate, current_user: DispatchUser = Depends(get_current_user)
):
    """
    Update a order contact.
    """
    order = get(db_session=db_session, order_id=order_id)
    if not order:
        raise HTTPException(status_code=400, detail="The order with this id does not exist.")

    order = update(
        db_session=db_session,
        order=order,
        order_in=order_in,
    )
    return order


@router.put("/order_code/{order_code}", response_model=OrderRead)
def update_order_by_code(
    *,
    db_session: Session = Depends(get_db),
    order_code: str,
    order_in: OrderUpdate, current_user: DispatchUser = Depends(get_current_user)
):
    """
    Update a order contact.
    """
    order = get_by_code(db_session=db_session, code=order_code)
    if not order:
        raise HTTPException(status_code=400, detail="The order with this id does not exist.")

    order_in.updated_by = current_user.email
    order = update(
        db_session=db_session,
        order=order,
        order_in=order_in,
    )

    return order


@router.delete("/{order_id}", response_model=OrderRead)
def delete_order(*, db_session: Session = Depends(get_db), order_id: int):
    """
    Delete a order contact.
    """
    order = get(db_session=db_session, order_id=order_id)
    if not order:
        raise HTTPException(status_code=400, detail="The order with this id does not exist.")

    return delete(db_session=db_session, order_id=order_id)


@router.post("/create_from_odoo")
def create_from_odoo(
        *,
        db_session: Session = Depends(get_db),
        order_info_in: dict,
        current_user: DispatchUser = Depends(get_current_user)
):
    """
    Create a new order and order items from Odoo.
    """
    result = create_order_and_items(session=db_session, order_info=order_info_in)

    return result