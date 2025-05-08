from typing import List, Optional
from sqlalchemy import select, cast, Integer, distinct, and_
from sqlalchemy.exc import NoResultFound
from sqlalchemy.sql import desc
from sqlalchemy.sql.functions import func
import re
from sqlalchemy.orm import joinedload
from .models import (
    OrderGroup,
    OrderGroupCreate,
    OrderGroupUpdate,
    OrderGroupBase,
    OrderSpecGroup,
    OrderSpecGroupBase,
    OrderSpecGroupUpdate,
    OrderSpecGroupCreate,
    OrderGroupListBase,
    OrderSpecGroupUpdateBase,
)
from dispatch.semi_admin.semi.models import Semi
from decimal import Decimal
from dispatch.site import service as siteservice
from dispatch.product_type.models import ProductType
from dispatch.rolling.rolling_list.models import Rolling
from dispatch.semi_admin.alternative_semi_size.models import AlternativeSemiSize
from dispatch.plugin import service as plugin_service
from dispatch.spec_admin.spec.models import Spec
from dispatch.order_admin.order_item.models import OrderItem
from dispatch.order_admin.order_item import service as order_item_service
from dispatch.rolling.rolling_list import service as rolling_service
from dispatch.product_type import service as product_type_service
from dispatch.spec_admin.spec import service as spec_service
from dispatch.mill import service as mill_service
from collections import defaultdict

from ...config import MILLEnum


def get(*, db_session, id: int) -> Optional[OrderGroup]:
    """Returns an orderGroup given an orderGroup id."""

    item = db_session.query(OrderGroup).filter(OrderGroup.id == id).one_or_none()
    if not item: return None
    spec_group_query = select(OrderSpecGroup).where(OrderSpecGroup.order_group_id == item.id)
    spec_group_info = db_session.execute(spec_group_query).scalars().all()
    item.order_spec_group = spec_group_info
    return item


def get_by_rolling_spec_id(*, db_session, rolling_id: int):  # spec_id) -> Optional[OrderGroup]:
    """Returns an orderGroup given an orderGroup id."""
    return (
        db_session.query(OrderGroup).filter(OrderGroup.rolling_id == rolling_id)
        # .filter(OrderGroup.spec_id == spec_id)
        .one_or_none()
    )


def get_by_rolling_spec_id_first(*, db_session, rolling_id: int):  # spec_id) -> Optional[OrderGroup]:
    """Returns an orderGroup given an orderGroup id."""
    return (
        db_session.query(OrderGroup).filter(OrderGroup.rolling_id == rolling_id)
        # .filter(OrderGroup.spec_id == spec_id)
        .first()
    )


def check_unique_key_exists(*, db_session, rolling_id: int, group_charge_seq: int) -> bool:
    try:
        db_session.query(OrderGroup).filter(
            OrderGroup.rolling_id == rolling_id, OrderGroup.group_charge_seq == group_charge_seq
        ).one()  # 使用one方法，如果不存在会抛出NoResultFound异常，如果存在则返回对应记录，这里不需要获取记录内容所以直接用one方法来验证存在性
        return True
    except NoResultFound:
        return False


def get_by_code(*, db_session, code: str) -> Optional[OrderGroup]:
    """Returns an orderGroup given an orderGroup code address."""
    return db_session.query(OrderGroup).filter(OrderGroup.group_code == code).one_or_none()


def get_default_orderGroup(*, db_session) -> Optional[OrderGroup]:
    """Returns an orderGroup given an orderGroup code address."""
    return db_session.query(OrderGroup).first()


def get_all(*, db_session) -> List[Optional[OrderGroup]]:
    """Returns all orderGroups."""
    return db_session.query(OrderGroup)


def get_by_code_org_id(*, db_session, code: str, org_id: int) -> Optional[OrderGroup]:
    """Returns an worker given an worker code address."""
    return db_session.query(OrderGroup).filter(OrderGroup.code == code, OrderGroup.org_id == org_id).one_or_none()


def get_by_team(*, team_id: int, db_session) -> List[Optional[OrderGroup]]:
    """Returns all orderGroups."""
    return db_session.query(OrderGroup).filter(OrderGroup.team_id == team_id).all()


def get_by_org_id_count(*, db_session, org_id: int) -> Optional[int]:
    """Returns an job based on the given code."""
    return db_session.query(func.count(OrderGroup.id)).filter(OrderGroup.org_id == org_id).scalar()


def get_by_rolling_id(*, db_session, rolling_id: int) -> List[Optional[OrderGroup]]:
    """Returns order groups by rolling code"""
    return db_session.query(OrderGroup).filter(OrderGroup.rolling_id == rolling_id).all()


def get_or_create(*, db_session, code: str, **kwargs) -> OrderGroup:
    """Gets or creates an orderGroup."""
    contact = get_by_code(db_session=db_session, code=code)

    if not contact:
        contact_plugin = plugin_service.get_active(db_session=db_session, plugin_type="contact")
        orderGroup_info = contact_plugin.instance.get(code, db_session=db_session)
        kwargs["code"] = orderGroup_info.get("code", code)
        kwargs["name"] = orderGroup_info.get("fullname", "Unknown")
        kwargs["weblink"] = orderGroup_info.get("weblink", "Unknown")
        orderGroup_in = OrderGroupCreate(**kwargs)
        contact = create(db_session=db_session, orderGroup_in=orderGroup_in)

    return contact


def get_max_group_charge_seq(*, db_session, rolling_id) -> int:
    return db_session.query(func.max(OrderGroup.group_charge_seq)).filter(OrderGroup.rolling_id == rolling_id).scalar()


def update_group_code(group_code):
    # 正则表达式：匹配结尾的数字部分
    match = re.search(r"(\D+)(\d+)$", group_code)  # (\D+) 匹配非数字部分，(\d+)$ 匹配结尾的数字部分
    if match:
        # 如果以数字结尾，提取数字部分
        prefix = match.group(1)  # 字符部分
        number = int(match.group(2))  # 数字部分
        return f"{prefix}{number + 1}"  # 拼接字符部分和数字部分加 1
    else:
        # 如果没有数字结尾，直接加 '1'
        return f"{group_code}1"


def get_order_group_list(*, db_session, section_type=None, rolling_no=None, kg=None, current_user=None) -> Optional[OrderGroup]:
    SEMI_STATUS_LOCATION_MAP = {
        'FURNACE': 'FURN',
        'DROPOUT': 'COGG',
        'SHEAR': 'SHEAR',
        'REFMILL': 'REFML',
        'ROLLED': 'SAW',  # 可能需要调整
        'SAWN': 'BANKS'
    }
    rolling_no = rolling_no
    query = select(OrderGroup)

    if rolling_no is not None:
        query = query.join(OrderGroup.rolling).where(Rolling.rolling_code == rolling_no)
    product_type_joined = False

    if section_type is not None:
        product_type_value = section_type.split("-")
        product_type_dim1_value = int(product_type_value[0])
        product_type_dim2_value = int(product_type_value[1])
        if not product_type_joined:
            query = query.join(OrderGroup.product_type)
            product_type_joined = True
        query = query.where(
            cast(ProductType.dim1, Integer) == product_type_dim1_value,
            cast(ProductType.dim2, Integer) == product_type_dim2_value,
        )

    if kg is not None:
        product_type_dim3_value = int(kg)
        if not product_type_joined:
            query = query.join(OrderGroup.product_type)
            product_type_joined = True
        query = query.where(cast(ProductType.dim3, Integer) == product_type_dim3_value)

    info = db_session.execute(query).scalars().all()
    for item in info:
        spec_group_query = select(OrderSpecGroup).outerjoin(Spec, OrderSpecGroup.spec_id==Spec.id).where(OrderSpecGroup.order_group_id == item.id).order_by(
            Spec.fecc_qual_category.asc(),Spec.spec_code.asc())
        # order_item_query = select(OrderItem).where(OrderItem.order_group_id == item.id)
        spec_group_info = db_session.execute(spec_group_query).scalars().all()
        # order_item_info = db_session.execute(order_item_query).scalars().all()
        item.order_spec_group = spec_group_info
        # item.order_item = order_item_info

        if not item.alternative_semi_size:
            alternative_semi_size_query = select(AlternativeSemiSize).where(
                AlternativeSemiSize.product_type_id == item.product_id,
                AlternativeSemiSize.mill_id == current_user.current_mill_id
                ).order_by(AlternativeSemiSize.rank_seq.asc())
            alternative_semi_size_info = db_session.execute(alternative_semi_size_query).scalars().first()
            item.alternative_semi_size = alternative_semi_size_info
            item.alternative_semi_size_id = alternative_semi_size_info.id if alternative_semi_size_info else None

        semi_query = select(Semi).where(Semi.order_group_id == item.id)
        semi_tonnes = db_session.execute(semi_query).scalars().all()
        item.blocked_semi_tonnes = 0
        item.charged_tonnes = 0
        item.quality_kg = []
        quality_map = {}
        for semi in semi_tonnes:
            # 处理 quality_kg
            # print(f"quality code: {semi.quality_code},  kg: {semi.estimated_weight_kg}")
            if semi.quality_code in quality_map:
                quality_map[semi.quality_code]["kg"] =float(quality_map[semi.quality_code]["kg"]) + float((semi.estimated_weight_kg or 0) / 1000)
            else:
                quality_map[semi.quality_code] = {"quality_code": semi.quality_code, "kg": (semi.estimated_weight_kg or 0) / 1000}

            item.charged_tonnes += semi.estimated_weight_kg if semi.estimated_weight_kg and semi.semi_status in SEMI_STATUS_LOCATION_MAP and semi.location == SEMI_STATUS_LOCATION_MAP[semi.semi_status] else 0
            item.blocked_semi_tonnes += semi.estimated_weight_kg if semi.estimated_weight_kg else 0
        item.blocked_semi_tonnes = item.blocked_semi_tonnes / 1000
        item.charged_tonnes = item.charged_tonnes / 1000
        item.quality_kg = list(quality_map.values())
        # print(item.blocked_semi_tonnes)
    # print(sorted(info, key=lambda x: x.group_charge_seq if x.group_charge_seq is not None else 0)[0].__dict__) 如果返回列表为空，此处报错
    return sorted(info, key=lambda x: x.group_charge_seq if x.group_charge_seq is not None else 0)


def get_order_spec_group_list_by_id(*, db_session, id) -> Optional[OrderSpecGroup]:
    return db_session.query(OrderSpecGroup).filter(OrderSpecGroup.id == id).one_or_none()


def get_order_spec_group_spec_ids(*, db_session, mill_id=MILLEnum.MILL410) -> Optional[OrderSpecGroup]:
    result = db_session.query(distinct(OrderSpecGroup.spec_id)).filter(OrderSpecGroup.mill_id == mill_id).all()
    return result

def get_order_spec_group_spec_ids_sct(*, db_session, mill_id=7) -> Optional[OrderSpecGroup]:
    result = db_session.query(distinct(OrderSpecGroup.spec_id)).filter(OrderSpecGroup.mill_id == mill_id).all()
    return result


def get_order_spec_group_by_order_group(*, db_session, order_group_id) -> Optional[OrderSpecGroup]:
    result = db_session.query(OrderSpecGroup).filter(OrderSpecGroup.order_group_id == order_group_id).all()
    return result


def get_order_spec_group_spec_id(*, db_session, spec_id):
    result = db_session.query(OrderSpecGroup).filter(OrderSpecGroup.spec_id == spec_id).first()
    return result


def updete_order_spec_group_id(*, db_session, spec_group: OrderSpecGroupBase, order_group_id):
    spec_group.order_group_id = order_group_id
    db_session.commit()
    return spec_group

def update_order_spec_group_project_tonnes(*, db_session, spec_group: OrderSpecGroupUpdateBase, order_spec_group_id):
    order_spec_group_info = db_session.query(OrderSpecGroup).filter(OrderSpecGroup.id == order_spec_group_id).first()
    try:
        if order_spec_group_info:
            order_spec_group_info.project_tonnes = spec_group.project_tonnes
            db_session.commit()
            return order_spec_group_info
    except:
        raise Exception("OrderSpecGroup not found")


def create_spec_group(*, db_session, order_spec_group_in: OrderSpecGroupCreate) -> OrderSpecGroup:
    """Creates an order spec group."""
    spec_group_data = order_spec_group_in.dict(exclude={"flex_form_data"})
    print(spec_group_data)
    contact = OrderSpecGroup(
        **order_spec_group_in.dict(exclude={"flex_form_data"}), flex_form_data=order_spec_group_in.flex_form_data
    )
    print(contact.spec_id)
    db_session.add(contact)
    db_session.commit()
    db_session.refresh(contact)
    created_contact = db_session.query(OrderSpecGroup).filter(OrderSpecGroup.id == contact.id).first()
    return contact


def create(*, db_session, orderGroup_in: OrderGroupCreate) -> OrderGroup:
    """Creates an orderGroup."""

    contact = OrderGroup(**orderGroup_in.dict(exclude={"flex_form_data", "mill", "rolling", "product_type"}), flex_form_data=orderGroup_in.flex_form_data)
    db_session.add(contact)
    db_session.commit()
    return contact


def batch_update(db_session, body):
    try:
        # 过滤 body，去掉值为 None 的字段
        cleaned_body = []
        for item in (body or []):
            filtered_item = {k: v for k, v in item.items() if v is not None}  # ✅ 过滤 None
            cleaned_body.append(filtered_item)

        # 处理 requested_tonnes 和 galvanisation
        for item in cleaned_body:
            if "requested_tonnes" in item:
                order_spec_group = db_session.query(OrderSpecGroup).filter(
                    OrderSpecGroup.order_group_id == item["id"]
                ).first()
                if order_spec_group:
                    order_spec_group.requested_tonnes = item["requested_tonnes"]

            if "galvanisation" in item:
                order_group = db_session.query(OrderGroup).filter(
                    OrderGroup.id == item["id"]
                ).first()
                if order_group:
                    order_group.galvanisation = item["galvanisation"]

        # 只更新去掉 None 值后的 body
        if len(cleaned_body):
            db_session.bulk_update_mappings(OrderGroup, cleaned_body)  # ✅ 只更新非 None 值
            db_session.commit()
            return True
        return False
    except Exception as e:
        db_session.rollback()  # 如果更新失败，回滚事务
        raise e


def update(
        *,
        db_session,
        orderGroup: OrderGroup,
        orderGroup_in: OrderGroupUpdate,
) -> OrderGroup:
    update_data = orderGroup_in.dict(
        #
        exclude={"flex_form_data", "location", "rolling", "product_type", "mill"},
    )
    for field, field_value in update_data.items():
        setattr(orderGroup, field, field_value)

    orderGroup.flex_form_data = orderGroup_in.flex_form_data
    if orderGroup_in.rolling_id:
        rolling_obj = rolling_service.get_by_id(db_session=db_session, id=orderGroup_in.rolling_id)
        orderGroup.rolling = rolling_obj or None 
    if orderGroup_in.mill_id:
        orderGroup.mill_id = orderGroup_in.mill_id or None
        mill_obj = mill_service.get(db_session=db_session, mill_id=orderGroup_in.mill_id)
        orderGroup.mill = mill_obj
    if orderGroup_in.product_id:
        product_obj = product_type_service.get(db_session=db_session, product_type_id=orderGroup_in.product_id)
        orderGroup.product_type = product_obj or None

    db_session.add(orderGroup)
    db_session.commit()
    return orderGroup


def get_spec_group_fields(db_session):
    spec_group_dict_list = []
    spec_group_query = db_session.query(OrderSpecGroup).all()
    for i in spec_group_query:
        spec_group_dict_list.append({
            "id": i.id,
            "order_group_id": i.order_group_id,
            "spec_id": i.spec_id,
        })
    return spec_group_dict_list


def find_max_length(db_session, spec_group_dict_list=None, order_items=None):
    result = []
    if not spec_group_dict_list:
        # 取出spec_group中 id order_group_id spec_id
        spec_group_dict_list = get_spec_group_fields(db_session=db_session)
    # 获取order_item order_group_id spec_id
    if not order_items:
        order_items = db_session.query(OrderItem).all()
    for spec_group in spec_group_dict_list:
        collection_eq_length_mm = []
        for order_item in order_items:
            if order_item["spec_id"] == spec_group["spec_id"] and order_item["order_group_id"] == spec_group[
                "order_group_id"]:
                collection_eq_length_mm.append(order_item['length_mm'])
        find_max = max(collection_eq_length_mm or [0])
        if not spec_group['length'] or spec_group['length'] != find_max:
            result.append({
                "id": spec_group["order_spec_group_id"],
                "length": find_max
            })
    db_session.bulk_update_mappings(OrderSpecGroup, result)
    db_session.commit()



def find_max_length_v2(db_session, spec_group_dict_list=None, order_items=None):
    result = []

    if not spec_group_dict_list:
        # 取出spec_group中 id, order_group_id, spec_id
        spec_group_dict_list = get_spec_group_fields(db_session=db_session)

    # 获取所有订单项数据，使用字典进行分组，以提高查询速度
    if not order_items:
        order_items = db_session.query(OrderItem).all()

    # 使用 defaultdict 将 order_items 按 spec_id 和 order_group_id 分组
    order_item_dict = defaultdict(list)
    for order_item in order_items:
        order_item_dict[(order_item["spec_id"], order_item["order_group_id"])].append(order_item['length_mm'])

    # 遍历每个 spec_group 来查找最大值
    for spec_group in spec_group_dict_list:
        spec_id = spec_group["spec_id"]
        order_group_id = spec_group["order_group_id"]

        # 根据 spec_id 和 order_group_id 查找对应的所有 lengths
        collection_eq_length_mm = order_item_dict.get((spec_id, order_group_id), [])

        # 找到最大长度，如果 collection_eq_length_mm 为空则返回0
        find_max = max(collection_eq_length_mm or [0])

        # 如果 spec_group 没有长度，或者当前长度不是最大值，则进行更新
        if not spec_group['length'] or spec_group['length'] != find_max:
            result.append({
                "id": spec_group["order_spec_group_id"],
                "length": find_max or 0
            })

    # 批量更新结果
    if result:
        db_session.bulk_update_mappings(OrderSpecGroup, result)
        db_session.commit()


def semi_ton_spec_group(*, db_session):
    semi_dict_list = []

    spec_group_dict_list = get_spec_group_fields(db_session=db_session)
    product_type_dict_list = []
    product_type_query = db_session.query(ProductType).all()
    for i in product_type_query:
        product_type_dict_list.append({
            "id": i.id,
            "dim3": int(i.dim3 or 0)
        })

    def get_dim3_by_id(target_id):
        for item in product_type_dict_list:
            if item["id"] == target_id:
                return item.get("dim3")  # 获取dim3的值
        return None  # 如果没有找到对应的id，返回None

    semi_query = db_session.query(Semi).all()
    for i in semi_query:
        if i.spec_id is None or i.order_group_id is None or i.product_type_id is None:
            continue
        semi_dict_list.append({
            "id": i.id,
            "spec_id": i.spec_id,
            "order_group_id": i.order_group_id or None,
            "product_type_id": i.product_type_id or None,
        })
    result = []
    for spec_group in spec_group_dict_list:
        kg_sum = 0
        # print()
        for semi_one in semi_dict_list:

            if semi_one["spec_id"] == spec_group["spec_id"] and semi_one["order_group_id"] == spec_group[
                "order_group_id"]:
                # print(semi_one["spec_id"] , spec_group["spec_id"] , semi_one["order_group_id"] , spec_group["order_group_id"])
                semi_dim3 = get_dim3_by_id(semi_one["product_type_id"])
                print(semi_dim3)
                kg_sum += Decimal(semi_dim3)
        result.append({
            "id": spec_group["id"],
            "allocation_tonnes": kg_sum / 1000
        })
    # print(result)
    db_session.bulk_update_mappings(OrderSpecGroup, result)
    db_session.commit()
    return 1


def computer_weight_spec_group(*, db_session, spec_group_list=None):
    if not spec_group_list:
        spec_group_list = get_spec_group_fields(db_session)
    order_group_id_list = [i['order_group_id'] for i in spec_group_list]
    order_item_list = order_item_service.get_order_item_by_order_group(db_session=db_session, order_group_id=order_group_id_list)
    order_item_dict_list = [
        {
            "id": order_item.id,
            "order_group_id": order_item.order_group_id,
            "spec_id": order_item.spec_id,
            "tonnage": float(order_item.tonnage),
        } for order_item in order_item_list
    ]

    update_spec_group_data = []
    for spec_group in spec_group_list:
        spec_group_id = spec_group["order_spec_group_id"]
        weight_total = 0
        for order_item in order_item_dict_list:
            if spec_group["order_group_id"] == order_item["order_group_id"] and spec_group["spec_id"] == order_item["spec_id"]:
                weight_total += order_item["tonnage"]
        update_spec_group_data.append(
            {
                "id": spec_group_id,
                "weight": weight_total * 1000
            }
        )
    db_session.bulk_update_mappings(OrderSpecGroup, update_spec_group_data)
    db_session.commit()

def computer_weight_spec_group_v2(*, db_session, spec_group_list=None):
    if not spec_group_list:
        spec_group_list = get_spec_group_fields(db_session)

    # 提取所有的 order_group_id 并批量查询 order_items
    order_group_id_list = [i['order_group_id'] for i in spec_group_list]

    # 批量获取 order_items，避免逐个查询
    order_item_list = order_item_service.get_order_item_by_order_group(
        db_session=db_session, order_group_id=order_group_id_list
    )

    # 使用字典来缓存 order_items，按 (order_group_id, spec_id) 组合作为键
    order_item_dict = {}
    for order_item in order_item_list:
        key = (order_item.order_group_id, order_item.spec_id)
        if key not in order_item_dict:
            order_item_dict[key] = 0
        order_item_dict[key] += Decimal(str(order_item.tonnage)).quantize(Decimal('0.0001'))

    # 更新 spec_group 的权重数据
    update_spec_group_data = [
        {
            "id": spec_group["order_spec_group_id"],
            "weight": order_item_dict.get(
                (spec_group["order_group_id"], spec_group["spec_id"]), 0
            ) * 1000 # 按照千克计算
        }
        for spec_group in spec_group_list
    ]

    # 批量更新 spec_group 数据
    db_session.bulk_update_mappings(OrderSpecGroup, update_spec_group_data)
    db_session.commit()




def delete(*, db_session, id: int):
    orderGroup = db_session.query(OrderGroup).filter(OrderGroup.id == id).one_or_none()

    db_session.delete(orderGroup)
    db_session.commit()

    return orderGroup


def get_order_group_ids_by_code(*, db_session, q: str) -> List[int]:
    return db_session.query(OrderGroup.id).filter(OrderGroup.group_code.contains(q)).all()


def update_order_spec_group(*, db_session, order_spec_group: OrderSpecGroup, order_spec_group_in: OrderSpecGroupUpdate):
    update_data = order_spec_group_in.dict(
        exclude={"flex_form_data", "mill"},
    )
    for field, field_value in update_data.items():
        if field_value:
            setattr(order_spec_group, field, field_value)
    
    db_session.add(order_spec_group)
    db_session.commit()
    return order_spec_group


def get_by_code_m(*, db_session, code: str, mill_id: int) -> Optional[OrderGroup]:
    """Returns an orderGroup given an orderGroup code address."""
    return db_session.query(OrderGroup).filter(and_(OrderGroup.group_code == code, OrderGroup.mill_id == mill_id)).first()


def get_order_group_codes(*, rolling_id: int, mill_id: int, db_session):
    return db_session.query(OrderGroup).filter(OrderGroup.rolling_id == rolling_id, OrderGroup.mill_id == mill_id).order_by(OrderGroup.id.desc()).all()
