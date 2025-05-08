
from typing import List, Optional

from .models import Order, OrderCreate, OrderUpdate, OrderCreate
from dispatch.order_admin.order_item.models import OrderItem
from dispatch.rolling.rolling_list import service as rolling_service
from dispatch.mill import  service as mill_service
from lxml import etree
from sqlalchemy import or_,select
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from fastapi.encoders import jsonable_encoder
from fastapi import HTTPException

from ...config import MILLEnum


def like_by_search_vector(*, db_session,search_vector) -> List[Optional[Order]]:
    """Returns an semi given an semi id."""
    return  db_session.query(Order.id).filter(
        or_(Order.order_code.like(f'%{search_vector}%'), 
            Order.customer_short_name.like(f'%{search_vector}%'), 
            Order.address_line_1.like(f'%{search_vector}%'), 
            Order.address_line_2.like(f'%{search_vector}%'), 
            Order.address_line_3.like(f'%{search_vector}%')
             )
        ).all()

def get(*, db_session, order_id: int) -> Optional[Order]:
    """Returns an order given an order id."""
    return db_session.query(Order).filter(Order.id == order_id).one_or_none()


def get_by_code(*, db_session, code: str) -> Optional[Order]:
    """Returns an order given an order code address."""
    return db_session.query(Order).filter(Order.order_code == code).first()

def get_by_sap_code(*, db_session, code: str) -> Optional[Order]:
    """Returns an order given an order code address."""
    return db_session.query(Order).filter(Order.sap_order_code == code).first()

def get_by_work_order_and_type(*, db_session, work_order, order_type) ->Optional[Order]:
    """Returns an order given an order code address."""
    return db_session.query(Order).filter(Order.work_order == work_order, Order.type_of_order==order_type).first()


def get_by_business_order_code(*, db_session, code: str) -> Optional[Order]:
    """Returns an order given an order code address."""
    return db_session.query(Order).filter(Order.business_order_code == code).one_or_none()

# def get_by_work_order(*, db_session, code: str) -> Optional[Order]:
#     """Returns an order given an order code address."""
#     return db_session.query(Order).filter(func.trim(Order.work_order) == code, Order.type_of_order == 274).one_or_none()

def get_by_work_order(*, db_session, code: str) -> Optional[Order]:
    """Returns an order given an order code address. If multiple orders exist, it filters by type_of_order=87."""
    query = db_session.query(Order).filter(func.trim(Order.work_order) == code)
   
    if query.count() > 1:
        query = query.filter(Order.type_of_order == 87)
   
    return query.one_or_none()

def get_default_order(*, db_session ) -> Optional[Order]:
    """Returns an order given an order code address."""
    return db_session.query(Order).first()


def get_all(*, db_session) -> List[Optional[Order]]:
    """Returns all orders."""
    return db_session.query(Order)

def get_all_where_sap_equal_bsorder(*, db_session) -> List[Optional[Order]]:
    """Returns all orders."""
    return db_session.query(Order).filter(
            or_(
                Order.sap_order_code == Order.business_order_code,
                Order.business_order_code.is_(None)
            )
        ).all()


def get_all_where_wor_order_is_empty(*, db_session) -> List[Optional[Order]]:
    """Returns all orders."""
    return db_session.query(Order).filter(
            or_(
                Order.work_order == '          ',
                Order.work_order == ' ',
                Order.work_order == '',
                Order.work_order.is_(None)
            )
        ).all()
# def get_count(*, db_session) -> int:
#     return db_session.query(Order).count()

def create(*, db_session, order_in: OrderCreate) -> Order:
    """Creates an order."""

    # rolling = None  # TODO SAP过来为空
    # if order_in.rolling_id:
    #     rolling = rolling_service.get( db_session=db_session, id=order_in.mill_id)
    # mill = None # TODO SAP过来为空
    # if order_in.mill_id :
    # mill = mill_service.get( db_session=db_session, mill_id=order_in.mill_id)

    contact = Order(**order_in.dict(exclude={"flex_form_data","rolling",'mill'}),
                    flex_form_data=order_in.flex_form_data,
                    # rolling=rolling,
                    # mill=mill
                    
                    )
    
    db_session.add(contact)
    db_session.commit()
    return contact


def update(
    *,
    db_session,
    order: Order,
    order_in: OrderUpdate,
) -> Order:

    update_data = order_in.dict(
        #
        exclude={"flex_form_data", "location"},
    )
    for field, field_value in update_data.items():
        setattr(order, field, field_value)

    order.flex_form_data = order_in.flex_form_data
    db_session.add(order)
    db_session.commit()
    return order


def delete(*, db_session, order_id: int):
    order = db_session.query(Order).filter(Order.id == order_id).one_or_none()
    
    db_session.delete(order)
    db_session.commit()

    return order

# def delete_all_force(*, db_session):
#     query_delete_force = db_session.query(Order).all().delete()

#     db_session.add(query_delete_force)
#     db_session.commit()

def get_nested_key(data, key_path, default=None):
    """从嵌套字典中获取键值，如果键不存在则返回默认值"""
    keys = key_path.split('.')
    current = data
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    return current


def get_nested_key_for_one(data, key_path, default=None):
    """从嵌套字典和列表中获取键值，包括处理列表索引，如果键不存在则返回默认值"""
    keys = key_path.split('.')
    current = data
    
    for part in keys:
        if '[' in part and ']' in part:  # 处理列表索引
            key, index_str = part[:-1].split('[')  # 分离键名和索引
            index = int(index_str)  # 将索引字符串转换为整数
            if isinstance(current, dict) and key in current and isinstance(current[key], list) and 0 <= index < len(current[key]):
                current = current[key][index]
            else:
                return default
        elif isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return default
            
    return current  


# def process_xml(dict_body):
    
#     # E1EDK01-ABRVW
#     order_dic = {
#       "order_category": get_nested_key(dict_body,"ZMFGE_ORDER05_01.IDOC.E1EDK01.ABRVW"),
#       "rolling_code": get_nested_key_for_one(dict_body,"ZMFGE_ORDER05_01.IDOC.E1EDP01[0].Z1MFG_ROLLPLANK01.ROLL_NUM"),
#       "order_code": get_nested_key(dict_body,"ZMFGE_ORDER05_01.IDOC.E1EDK01.BELNR"),
#       "order_reason": get_nested_key(dict_body,"ZMFGE_ORDER05_01.IDOC.E1EDK01.CURCY"),
#     }
    
#     # TODO 
#     return order_dic


# async def CreateOrder(request,db_session,current_user):
#     raw_body = await request.body()
#     xml_bytes = raw_body.strip()
#     order_in = process_xml_order(xml_bytes, db_session=db_session)  # Pass cleaned bytes

#     order_created = get_by_code(db_session=db_session, code=order_in.order_code)
#     if order_created:
#         raise HTTPException(status_code=400, detail="The order with this code already exists.")

#     order_in.created_by = current_user.email
#     order_in.updated_by = current_user.email
#     order = create(db_session=db_session, order_in=order_in)
#     order_item_in = process_xml_order_item(xml_bytes)  # Pass cleaned bytes
#     print(order_item_in)
#     order_item = create_item(db_session=db_session, orderItem_in=order_item_in)
    
    
def process_xml_order(xml_bytes, db_session):
    """从XML中解析出order需要的字段值"""
    root = etree.fromstring(xml_bytes)

    rolling_plan_number = root.findtext(".//Z1MFG_ROLLPLANK01/ROLL_NUM")
    mill_id = None
    rolling = None 
    
    if rolling_plan_number and rolling_plan_number.startswith("T"):
        mill = mill_service.get_by_code(db_session=db_session, code="T")
        if mill:
            mill_id = mill.id
        rolling = rolling_service.get_by_code(db_session=db_session, code=rolling_plan_number, mill_id=MILLEnum.MILL410)


        

    order_code = root.findtext(".//E1EDK01/BELNR")

    order_export_type_parvws = root.iterfind(".//E1EDKA1/PARVW")
    order_export_type = None
    for elem in order_export_type_parvws:
        if elem.text == "WE":
            order_export_type_land = elem.getparent().findtext("LAND1")
            if order_export_type_land != "GB" and order_export_type_land != "UK":
                order_export_type = "X"

    order_category = root.findtext(".//E1EDK01/ABRVW")
    address_line_1 = root.findtext(".//E1EDKA1/STRAS")
    
    address_line_2 = root.findtext(".//E1EDKA1/STRS2")
    address_line_3 = root.findtext(".//E1EDKA1/ORT01")
    address_line_4 = root.findtext(".//E1EDKA1/PSTLZ")

    address_line_5 = root.findtext(".//E1EDKA1/LAND1")
    
    customer_full_name = root.findtext(".//E1EDKA1/NAME2")
   
    
    
    

    order_create = OrderCreate(
        # mill_id = mill_id,
        rolling = rolling,
        order_code = order_code,
        order_export_type = order_export_type,
        order_category = order_category,
        business_order_code = None,
        customer_code = None,
        customer_short_name = None,
        # customer_full_name = None,
        address_line_1 = address_line_1,
        address_line_2 = address_line_2,
        address_line_3 = address_line_3,
        address_line_4 = address_line_4,
        address_line_5 = address_line_5,
        customer_full_name=customer_full_name,
        
    )


#       "order_category": get_nested_key(dict_body,"ZMFGE_ORDER05_01.IDOC.E1EDK01.ABRVW"),
#       "rolling_code": get_nested_key_for_one(dict_body,"ZMFGE_ORDER05_01.IDOC.E1EDP01[0].Z1MFG_ROLLPLANK01.ROLL_NUM"),
#       "order_code": get_nested_key(dict_body,"ZMFGE_ORDER05_01.IDOC.E1EDK01.BELNR"),
#       "order_reason": get_nested_key(dict_body,"ZMFGE_ORDER05_01.IDOC.E1EDK01.CURCY"),
    return order_create


def amend_code_null_db(db_session) -> list:
    result = []
    stmt = select(Order).where(Order.order_code == None)
    orders = db_session.execute(stmt).scalars().all()
    for order in orders:
        order.order_code = str(order.id)
        order.type_of_order = 0
        result.append(order.id)
    db_session.commit()
    return result

def create_order_and_items(*, session, order_info: dict):
    """
    order_info = {
        "order": {
            "order_code": "123456",
            "type_of_order": 1,
            "sap_order_code": "123456"
        },
        "order_items": [
            {
                "line_item_code": "三脚架",
                "plant_id": 1,
                "product_type_id": 1,
                "spec_id": 1,
                "rolling_code": "HW-200-200-A01",
                "spec_code": "Q345B",
                "quantity": 20,
                "stocked_quantity": 0
            },
            {
                "line_item_code": "",
                "plant_id": 0,
                "product_type_id": 0,
                "spec_id": 0,
                "rolling_code": "",
                "spec_code": "",
                "quantity": 0,
                "stocked_quantity": 0
            },
        ]
    }
    """
    if not order_info or not order_info.get('order') or not order_info.get('order_items'):
        raise HTTPException(f"input order info must have 'order' and 'order_items' fields")

    order_data = order_info["order"]
    items_data = order_info["order_items"]

    try:
        result = {}
        order = Order(**order_data)
        session.add(order)
        session.flush()
        result["order"] = jsonable_encoder(order)

        result["order_items"] = []
        for item_data in items_data:
            item_data['order_id'] = order.id
            order_item = OrderItem(**item_data)
            session.add(order_item)
            result["order_items"].append(jsonable_encoder(order_item))

        session.commit()
        return result

    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(f"创建订单失败: {str(e)}")
