import json
import logging
from datetime import datetime

# import random
from typing import List, Optional
from sqlalchemy.sql.functions import func
from dispatch.order_admin.order_group import service as order_groupservice
from dispatch.order_admin.order_group.models import OrderSpecGroup, OrderGroup

from dispatch.order_admin.order import service as orderservice
from dispatch.rolling.rolling_list import service as rolling_service
from dispatch.runout_admin.finished_product.models import FinishedProduct

from .models import OrderItem, OrderItemCreate, OrderItemUpdate, OrderItemCreate
from ...config import DEV_DATABASE_SCHEMA
from ...rolling.rolling_list.models import Rolling

from dispatch.site import service as siteservice
from dispatch.system_admin.auth.models import DispatchUser, UserRoles
from dispatch.message_admin import message_server

from sqlalchemy_filters import apply_pagination
import sqlalchemy
from sqlalchemy import insert, text, select, and_

from lxml import etree

log = logging.getLogger(__file__)


def get(*, db_session, orderItem_id: int) -> Optional[OrderItem]:
    """Returns an orderItem given an orderItem id."""
    return db_session.query(OrderItem).filter(OrderItem.id == orderItem_id).one_or_none()


def get_by_orderId(
        db_session,
        order_id: int,
        query_str: str = None,
        page: int = 1,
        items_per_page: int = 5,
        sort_by: List[str] = None,
        descending: List[bool] = None,
        fields: List[str] = None,
        ops: List[str] = None,
        values: List[str] = None,
        current_user: DispatchUser = None,
        role: UserRoles = UserRoles.CUSTOMER,
) -> List[Optional[OrderItem]]:
    """Returns an orderItem given an orderItem id."""
    query = db_session.query(OrderItem).filter(OrderItem.order_id == order_id)

    try:
        query, pagination = apply_pagination(query, page_number=page, page_size=items_per_page)
    except sqlalchemy.exc.ProgrammingError as e:
        log.error(e)
        return {
            "items": [],
            "itemsPerPage": items_per_page,
            "page": page,
            "total": 0,
        }

    return {
        "items": query.all(),
        "itemsPerPage": pagination.page_size,
        "page": pagination.page_number,
        "total": pagination.total_results,
    }


def get_by_code(*, db_session, code: str) -> Optional[OrderItem]:
    """Returns an orderItem given an orderItem code address."""
    return db_session.query(OrderItem).filter(OrderItem.line_item_code == code).one_or_none()


def get_default_orderItem(*, db_session) -> Optional[OrderItem]:
    """Returns an orderItem given an orderItem code address."""
    return db_session.query(OrderItem).first()


def get_all(*, db_session) -> List[Optional[OrderItem]]:
    """Returns all orderItems."""
    return db_session.query(OrderItem)


def get_by_code_org_id(*, db_session, code: str, org_id: int) -> Optional[OrderItem]:
    """Returns an worker given an worker code address."""
    return db_session.query(OrderItem).filter(OrderItem.code == code, OrderItem.org_id == org_id).one_or_none()

def get_by_code_order_id(*, db_session, code: str, order_id: int) -> Optional[OrderItem]:
    """Returns an worker given an worker code address."""
    return db_session.query(OrderItem).filter(OrderItem.line_item_code == code, OrderItem.order_id == order_id).one_or_none()

def get_by_code_sub_line_no(*, db_session, order_id:int, code: str, sub_item_no: str):
    stmt = select(OrderItem).where(
        OrderItem.order_id == order_id,
        OrderItem.sap_line_item_code == code,
        OrderItem.line_item_code == sub_item_no
    )
    row = db_session.scalar(stmt)

    return row


def get_by_team(*, team_id: int, db_session) -> List[Optional[OrderItem]]:
    """Returns all orderItems."""
    return db_session.query(OrderItem).filter(OrderItem.team_id == team_id).all()


def get_by_org_id_count(*, db_session, org_id: int) -> Optional[int]:
    """Returns an job based on the given code."""
    return db_session.query(func.count(OrderItem.id)).filter(OrderItem.org_id == org_id).scalar()

def get_by_rolling_id(*, db_session, rolling_id: int) -> List[Optional[OrderItem]]:
    """Returns all OrderItem objects associated with the given rolling_id."""
    # return db_session.query(OrderItem).filter(OrderItem.rolling_id == rolling_id).order_by(OrderItem.order_id).all()
    return db_session.query(OrderItem).filter(OrderItem.rolling_id == rolling_id).order_by(OrderItem.order_id, OrderItem.sub_item_code).all()


def get_by_order_group_id(*, db_session, order_group_id: int):
    return db_session.query(OrderItem).filter(OrderItem.order_group_id == order_group_id).all()

def get_by_rolling_order_group_id(*, db_session, order_group_id: int, rolling_id: int) -> List[Optional[OrderItem]]:
    order_items = db_session.query(OrderItem).filter(
        OrderItem.rolling_id == rolling_id,
        OrderItem.order_group_id == order_group_id
    ).all()
    return order_items

def create(*, db_session, orderItem_in: OrderItemCreate) -> OrderItem:
    """Creates an orderItem."""

    order_group = None
    order = None
    rolling = None
    if orderItem_in.order_group_id:
        order_group = order_groupservice.get(db_session=db_session, id=orderItem_in.order_group_id)
    if orderItem_in.order_id:
        order = orderservice.get(db_session=db_session, order_id=orderItem_in.order_id)
    if orderItem_in.rolling_id:
        rolling = rolling_service.get(db_session=db_session, id=orderItem_in.rolling_id)

    contact = OrderItem(**orderItem_in.dict(exclude={"flex_form_data", "order", "order_group", "rolling", "plant"}),
                        flex_form_data=orderItem_in.flex_form_data,
                        order_group=order_group,
                        order=order,
                        rolling=rolling
                        )

    db_session.add(contact)
    db_session.commit()
    return contact


def create_bulk(*, db_session, order_items_in):
    db_session.execute(
        insert(OrderItem),
        order_items_in
    )
    db_session.commit()

    return True


def update(
        *,
        db_session,
        orderItem: OrderItem,
        orderItem_in: OrderItemUpdate,
) -> OrderItem:
    update_data = orderItem_in.dict(
       
        exclude={"flex_form_data", "location","order", "order_group", "rolling", "plant", "product_type", "spec", "label_template"},
    )
    for field, field_value in update_data.items():
        setattr(orderItem, field, field_value)

    orderItem.flex_form_data = orderItem_in.flex_form_data
    db_session.add(orderItem)
    db_session.commit()
    return orderItem


def delete(*, db_session, orderItem_id: int):
    orderItem = db_session.query(OrderItem).filter(OrderItem.id == orderItem_id).update({"is_deleted": 1})

    # db_session.add(orderItem)
    db_session.commit()

    return orderItem

def move_to_order_item(*, db_session, data, current_user: DispatchUser, background_tasks):
    order_item_rolling_id = data["new_rolling_code"]
    order_item_ids= data['ids']
    result = []
    for item_id in order_item_ids:
        order_item_data = db_session.query(OrderItem).filter(OrderItem.id == item_id).first()
        if order_item_data:
            rolling_data = db_session.query(Rolling).filter(Rolling.id == order_item_rolling_id).first()
            if order_item_data.rolling_id:
                old_rolling_data = rolling_service.get(db_session=db_session, id=order_item_data.rolling_id)
            else:
                old_rolling_data = None
            
            new_rolling_codes = rolling_data.rolling_code
            rolling_code_parts = new_rolling_codes.split('-')
            if len(rolling_code_parts) >= 4:
                # 获取各个部分
                product_code = rolling_code_parts[0]
                product_dim1 = rolling_code_parts[1]
                product_dim2 = rolling_code_parts[2]
                rolling_codes = rolling_code_parts[-1]
            else:
                product_code = product_dim1 = product_dim2 = rolling_codes = ""
            order_group_id = order_item_data.order_group_id
            if order_group_id:
                order_item_datas = db_session.query(OrderItem).filter(OrderItem.id == item_id).all()
                if order_item_datas:
                    for item in order_item_datas:
                        item.order_group_id = None
                order_spec_group_data = db_session.query(OrderSpecGroup).filter(OrderSpecGroup.order_group_id == order_group_id).all()
                order_group_data = db_session.query(OrderGroup).filter(OrderGroup.id == order_group_id).all()
                if order_spec_group_data:
                    for spec_group in order_spec_group_data:
                        db_session.delete(spec_group)
                if order_group_data:
                    for order_group in order_group_data:
                        db_session.delete(order_group)
            order_item_data.order_group_id = None
            order_item_data.rolling_code = rolling_codes
            order_item_data.rolling_id = rolling_data.id
            order_item_data.product_code = product_code
            order_item_data.product_dim1 = product_dim1
            order_item_data.product_dim2 = product_dim2
            db_session.commit()
            try:
                message_strategy = message_server.server.MessageStrategy130()
                message_strategy.send_pc_150(db_session=db_session, rolling=rolling_data, background_tasks=background_tasks, current_mill_code=current_user.current_mill_code)
                # if old_rolling_data:
                #     message_strategy.send_pc_150(db_session=db_session, rolling=old_rolling_data, background_tasks=background_tasks, current_mill_code=current_user.current_mill_code)
            except Exception as e:
                log.error(f"ERROR in send_pc_150: {str(e)}")
            result.append({
                "id": order_item_data.id,
                "spec_id": order_item_data.spec_id,
                "order_id": order_item_data.order_id,
                "line_item_code": order_item_data.line_item_code,
                "product_code": product_code,
                "product_dim1": product_dim1,
                "product_dim2": product_dim2,
                "product_dim3": order_item_data.product_dim3,
                "spec_code": order_item_data.spec_code,
                "rolling_code": rolling_codes,
                "length_mm": order_item_data.length_mm,
                "quality_code": order_item_data.quality_code,
                "mill_id": order_item_data.plant_id,
            })
    return result

def process_xml_order_item(xml_bytes):
    """从XML中解析出order_item需要的字段值"""
    root = etree.fromstring(xml_bytes)

    destination_port = root.findtext(".//E1EDK17/QUALF")

    order_item_create = OrderItemCreate(
        destination_port=destination_port,
        # loading_port = extracted_values.get("E1EDK17/QUALF"),
    )

    return order_item_create


def order_item_group_need_fields(db_session, mill_id, rolling_id, one_rolling: bool = False):
    result = []
    query = db_session.query(
        OrderItem.id,
        OrderItem.rolling_id,
        OrderItem.product_type_id,
        OrderItem.order_id,
        OrderItem.order_group_id,
        OrderItem.line_item_code,
        OrderItem.product_code,
        OrderItem.product_dim1,
        OrderItem.product_dim2,
        OrderItem.product_dim3,
        OrderItem.spec_code,
        OrderItem.spec_id,
        OrderItem.rolling_code,
        OrderItem.length_mm,
        OrderItem.quality_code,
        OrderItem.plant_id
    )
    if not one_rolling:
        query = query.filter(OrderItem.plant_id == mill_id)
    else:
        query = query.filter(and_(OrderItem.plant_id == mill_id,
                                  OrderItem.rolling_id == rolling_id))
    for row in query.all():
        result.append({
            "id": row.id,
            "order_id": row.order_id,
            "order_group_id": row.order_group_id,
            "rolling_id": row.rolling_id,
            "product_type_id": row.product_type_id,
            "line_item_code": row.line_item_code,
            "product_code": row.product_code,
            "product_dim1": row.product_dim1,
            "product_dim2": row.product_dim2,
            "product_dim3": row.product_dim3,
            "spec_code": row.spec_code,
            "spec_id": row.spec_id,
            "rolling_code": row.rolling_code,
            "length_mm": row.length_mm,
            "quality_code": row.quality_code,
            "mill_id": row.plant_id,
        })
    return result

def amend_rolling_attach(db_session):
    db_session.execute(text(f"""update
        {DEV_DATABASE_SCHEMA}.order_item oi
        set
            rolling_id = (
                select
                    r.id
                from
                    {DEV_DATABASE_SCHEMA}.rolling r
                where
                    oi.product_code = r.product_type
                    and oi.product_dim1 = r.rolling_dim1
                    and oi.product_dim2 = r.rolling_dim2
                    and oi.rolling_code = r.short_code
                    and oi.plant_id = r.mill_id
            )
        where oi.rolling_id is null"""))
    db_session.commit()

    db_session.execute(text(f"""update
        {DEV_DATABASE_SCHEMA}.order_item oi
        set
            product_type_id = (
                select
                    pt.id
                from
                    {DEV_DATABASE_SCHEMA}.product_type pt
                where
                	pt.code = concat(oi.product_code, '-', oi.product_dim1, '-', oi.product_dim2, '-', oi.product_dim3) 
                	and pt.mill_id = oi.plant_id 
                	and pt.code is not null 
            )
        where oi.product_type_id is null"""))
    db_session.commit()

    return True

from decimal import Decimal

def get_max_bundle_weight(db_session, order_item_id):
    """获取指定 order_item_id 在 FinishedProduct 表中的最大 estimated_weight_kg 值"""
    stmt = select(func.max(FinishedProduct.estimated_weight_kg)).where(
        FinishedProduct.order_item_id == order_item_id
    )
    result = db_session.scalar(stmt)

    # 确保返回值是 Decimal 类型，防止 None 导致错误
    return float(result) if result is not None else 0


def get_order_item_by_order_group(db_session, order_group_id):
    return db_session.query(OrderItem).filter(OrderItem.order_group_id.in_(order_group_id)).all()