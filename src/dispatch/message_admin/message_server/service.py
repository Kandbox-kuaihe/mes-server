import os
import json
import time
from datetime import date, datetime
from uuid import uuid4
from typing import List, Optional

import requests
from fastapi.encoders import jsonable_encoder
from sqlalchemy import func
from lxml import etree
from lxml import etree as ET
from fastapi import HTTPException
from sqlalchemy import and_, select
from sqlalchemy import update as sqlalchemy_update
from sqlalchemy.orm import Session
from collections import defaultdict
from dispatch.enums import MillCodes
from dispatch.area.models import AreaCreate, Area
from dispatch.cast import service as cast_service
from dispatch.cast.models import CastCreate, CastUpdate, Cast
from dispatch.config import ROOT_DIR, CAST_GENERATED_CODE, MILLEnum, DEFAULT_EMAIL, \
    MESSAGE_URL_IS_SERVICE_CENTER_TRUE_START, MESSAGE_URL_IS_SERVICE_CENTER_TRUE_END, \
    MESSAGE_URL_IS_SERVICE_CENTER_FALSE_START, MESSAGE_URL_IS_SERVICE_CENTER_FALSE_END
from dispatch.common.utils.func import try_int, try_int_num, try_float, split_number_and_letters, format_float
from dispatch.mill.models import Mill
from dispatch.order_admin.order.models import OrderCreate, Order
from dispatch.order_admin.order import service as order_service
from dispatch.product_class.models import ProductClass
from dispatch.product_code_trans.models import ProductCodeTrans
from dispatch.order_admin.order_item import service as order_item_service
from dispatch.order_admin.order_item_remark.models import OrderItemRemark
from dispatch.order_admin.order_remark.models import OrderRemark
from dispatch.product_type.models import ProductType
from dispatch.order_admin.order_group.models import OrderGroup
from dispatch.message_admin.operation_log.models import OperationLog, OperationLogCreate, OperationLogUpdate
from dispatch.order_admin.order_item.models import OrderItem
from dispatch.semi_admin.semi.models import Semi
from dispatch.semi_admin.semi.service import insert_json_semi
from dispatch.semi_admin.semi.service import get_by_code as get_semi_by_code
from dispatch.site.models import SiteCreate
from dispatch.site_type.models import SiteTypeCreate
from dispatch.spec_admin.spmillref.models import Spmillref
from dispatch.order_admin.order_group.models import OrderSpecGroup
from dispatch.rolling.rolling_list.models import Rolling
from dispatch.spec_admin.spec.models import Spec
from dispatch.message_admin.message_log import service as message_log_service
from dispatch.message_admin.message_log.models import MessageLogCreate
from dispatch.area import service as area_service
from dispatch.site import service as site_service
from dispatch.site_type import service as site_type_service
from dispatch.message_admin.message_server.models import PushMessage7xxxDataRead
from dispatch.customer.models import Customer, CustomerCreate
from dispatch.customer import service as customer_service

from dispatch.log import getLogger
from ...order_admin.order_group.service import computer_weight_spec_group, find_max_length, find_max_length_v2, \
    computer_weight_spec_group_v2

log = getLogger(__name__)


def get(*, db_session, id: int) -> Optional[OperationLog]:
    return db_session.query(OperationLog).filter(
        OperationLog.id == id).one_or_none()


def get_or_create_by_code(*, db_session, operation_log_in) -> OperationLog:
    if operation_log_in.id:
        q = db_session.query(OperationLog).filter(
            OperationLog.id == operation_log_in.id)
    else:
        # return None
        raise Exception("The OperationLog.id can not be None.")

    instance = q.first()

    if instance:
        return instance

    return create(db_session=db_session, operation_log_in=operation_log_in)


def get_all(*, db_session) -> List[Optional[OperationLog]]:
    return db_session.query(OperationLog)


def create(*, db_session, operation_log_in: OperationLogCreate) -> OperationLog:
    operation_log = OperationLog(**operation_log_in.dict(exclude={}))
    db_session.add(operation_log)
    db_session.commit()
    return operation_log


def create_all(*, db_session,
               operation_log_in: List[OperationLogCreate]) -> List[OperationLog]:
    operation_log = [OperationLog(id=d.id) for d in operation_log_in]
    db_session.bulk_save_insert(operation_log)
    db_session.commit()
    db_session.refresh()
    return operation_log


def update(*, db_session, operation_log: OperationLog,
           operation_log_in: OperationLogUpdate) -> OperationLog:
    operation_log_data = jsonable_encoder(operation_log)

    update_data = operation_log_in.dict(skip_defaults=True)

    for field in operation_log_data:
        if field in update_data:
            setattr(operation_log, field, update_data[field])

    db_session.add(operation_log)
    db_session.commit()
    return operation_log


def delete(*, db_session, id: int):
    operation_log = db_session.query(OperationLog).filter(
        OperationLog.id == id).first()

    db_session.delete(operation_log)
    db_session.commit()


def get_mill_id_by_code(db_session: Session, code: str) -> int | None:
    stmt = select(Mill).where(Mill.code == code)
    mill = db_session.scalar(stmt)
    mill_id = mill.id if mill else None

    return mill_id


def get_mill_id_from_prod_form(db_session, z_prod_form_value: str, destination_port: str | None):
    mill_code = None
    match z_prod_form_value:
        case "RAILS":
            mill_code = MillCodes.SRSM
        case "SECTIONS":
            if destination_port == '8511':
                mill_code = MillCodes.TBM
            elif destination_port == '8501':
                mill_code = MillCodes.SRSM
            else:
                mill_code = MillCodes.TBM
        case "SEMI":
            if destination_port == '8511':
                mill_code = MillCodes.TBM
            elif destination_port == '8501':
                mill_code = MillCodes.SRSM
        case "RD":
            mill_code = MillCodes.SRM
        case "PROFILE" | "BILLET":
            mill_code = MillCodes.SKG
        case _:
            mill_code = None

    mill_id = get_mill_id_by_code(db_session=db_session, code=mill_code)

    return mill_id


def get_mill_id_from_rolling_code_274(db_session, rolling_code: str | None) -> int | None:
    if not rolling_code:
        return None
    mill_code = None
    if rolling_code.startswith('M'):
        mill_code = MillCodes.SRSM
    elif rolling_code.startswith('K'):
        mill_code = MillCodes.SKG

    mill_id = get_mill_id_by_code(db_session=db_session, code=mill_code)

    return mill_id

# def get_cur_coh_no(db_session: Session, product_form: str, order_export_type: str, destination_country: str) -> int:
#     order_coh_no_range = ()
#     generate_coh_no = None
#     match product_form:
#         case ProductForms.SECTIONS:
#             if order_export_type == 'X':
#                 if destination_country != 'IE':
#                     order_coh_no_range = (100000, 199999)
#                 else:
#                     order_coh_no_range = (400000, 449999)
#             else:
#                 order_coh_no_range = (200000, 399999)
#         case ProductForms.PROFILE:
#             order_coh_no_range = (550001, 599999)
#         case ProductForms.RAILS:
#             order_coh_no_range = (600001, 699999)
#         case ProductForms.RD:
#             order_coh_no_range = (600001, 699999)

#     if not order_coh_no_range:
#         raise Exception(
#             f"get cur_coh_no failed."
#             f"product_form-{product_form!r}"
#             f"order_export_type-{order_export_type!r}"
#             f"destination_country-{destination_country!r}"
#         )
#     stmt = select(func.max(Order.coh_no)).where(
#         Order.coh_no >= order_coh_no_range[0],
#         Order.coh_no <= order_coh_no_range[1],
#     )
#     get_coh_no = db_session.scalar(stmt)
#     if not get_coh_no:
#         generate_coh_no = order_coh_no_range[0]
#     elif get_coh_no == order_coh_no_range[1]:
#         generate_coh_no = order_coh_no_range[0]
#     else:
#         generate_coh_no = int(get_coh_no) + 1

#     return generate_coh_no

def delete_order(*, db_session: Session, order_delete):
    # db_session.delete(order_delete)
    order_delete.is_deleted = 1
    db_session.commit()

    return True


def CreateOrder(raw_body, db_session, type_of_order):
    xml_bytes = raw_body.strip()

    order_in = None
    if type_of_order == "087":
        order_in = parse_xml_order_087(xml_bytes, db_session)
        try:
            parse_xml_order_items_087(xml_bytes, db_session=db_session, order_id=order_in.id)
        except:
            delete_order(db_session=db_session, order_delete=order_in)
            raise
    elif type_of_order == "184":
        order_in = parse_xml_order_184(xml_bytes, db_session)
        try:
            parse_xml_order_items_184(xml_bytes, db_session=db_session, order_id=order_in.id)
        except:
            delete_order(db_session=db_session, order_delete=order_in)
            raise
    elif type_of_order == "274":
        order_in = parse_xml_order_274(xml_bytes, db_session)
        try:
            parse_xml_order_items_274(xml_bytes, db_session=db_session, order_id=order_in.id)
        except:
            delete_order(db_session=db_session, order_delete=order_in)
            raise

    msg_json_dict = {"id": order_in.id} if order_in else {}
    root = etree.fromstring(xml_bytes)
    doc_no = root.findtext(".//EDI_DC40/DOCNUM")
    saved_xml_file_name = save_xml_to_file(xml_bytes.decode('utf-8'), doc_no)
    msg_json_dict = {"id": order_in.id} if order_in else {}
    save_to_message_log_all(db_session=db_session, sap_type=type_of_order, msg=saved_xml_file_name,
                            msg_type='success', msg_json_dict=msg_json_dict)
    return True


def parse_xml_node_single(node_single, key_name_list) -> dict:
    return {key: node_single.findtext(key) for key in key_name_list}


def parse_xml_node_list(node_list, key_name_list) -> list:
    return [parse_xml_node_single(node, key_name_list) for node in node_list]



def parse_vals(root) -> dict:
    vals_dict = {}
    e1edcfgs = root.findall(".//E1CUCFG")
    for e1edcfg in e1edcfgs:
        cur_line_item_code = e1edcfg.findtext("POSEX")
        vals_dict[cur_line_item_code] = {}
        if not cur_line_item_code:
            break
        e1cuvals = e1edcfg.findall("E1CUVAL")
        vals_dict[cur_line_item_code] = {
            e1cuval.findtext("CHARC"): e1cuval.findtext("VALUE")
            for e1cuval in e1cuvals if e1cuval.findtext("INST_ID") == "00000001"
        }

    return vals_dict

def get_spec_by_code(*, db_session: Session, spec_code: str, mill_id: int):
    stmt = select(Spec).where(Spec.spec_code == spec_code, Spec.mill_id == mill_id, Spec.version_status == 'R')
    spec_get = db_session.scalar(stmt)

    if not spec_get:
        stmt = select(Spec).where(Spec.spec_code == spec_code, Spec.mill_id == mill_id, Spec.version_status == 'D')
        spec_get = db_session.scalar(stmt)

    return spec_get

def get_spec_by_code_rails(*, db_session: Session, spec_code: str, mill_id: int):
    stmt = select(Spec).where(Spec.srsm_spec_code == spec_code, Spec.mill_id == mill_id, Spec.version_status == 'R')
    spec_get = db_session.scalar(stmt)

    if not spec_get:
        stmt = select(Spec).where(Spec.srsm_spec_code == spec_code, Spec.mill_id == mill_id, Spec.version_status == 'D')
        spec_get = db_session.scalar(stmt)

    return spec_get

def get_spec_id_from_code_ref(db_session, spec_code, mill_id, product_type_id):
    stmt = select(Mill).where(Mill.code == MillCodes.TBM)
    mill_tbm = db_session.scalar(stmt)
    mill_id_tbm = mill_tbm.id if mill_tbm else None

    spec_get_tbm = get_spec_by_code(db_session=db_session, spec_code=spec_code, mill_id=mill_id_tbm)

    spec_id = None
    if spec_get_tbm and product_type_id:
        product_type = db_session.get(ProductType, product_type_id)
        if product_type and product_type.flange_thickness:
            stmt = select(Spmillref).where(Spmillref.spec_id == spec_get_tbm.id)
            for spmillref in db_session.scalars(stmt):
                if float(spmillref.thick_from) <= float(product_type.flange_thickness) <= float(spmillref.thick_to):
                    stmt = select(Spec).where(Spec.spec_code == spmillref.spec_code, Spec.mill_id == mill_id,
                                              Spec.version_status == 'R')
                    spec_get_srsm = db_session.scalar(stmt)
                    spec_id = spec_get_srsm.id if spec_get_srsm else None
                    break

    return spec_id

def get_bws_store_from_rolling_code(rolling_code: str) -> str:
    try:
        from dispatch.contrib.message_admin.message_server.enums import BwsStores
        match rolling_code:
            case '806S':
                bws_store = BwsStores.ASD
            case '826S':
                bws_store = BwsStores.AJNS
            case '824S':
                bws_store = BwsStores.MTA2
            case _:
                bws_store = None

        return bws_store
    except ImportError as e:
        raise HTTPException(status_code=400, detail=str(e))

def get_product_code_trans(db_session: Session, plant_id: int, product_code: str, product_dim1: str, product_dim2: str, product_dim3: str):
    product_code_trans = None
    if (
            plant_id and
            product_code and
            product_dim1 and
            product_dim2 and
            product_dim3
    ):
        stmt = select(ProductCodeTrans).where(
            ProductCodeTrans.sap_product_code == product_code,
            ProductCodeTrans.sap_dim_1 == str(product_dim1),
            ProductCodeTrans.sap_dim_2 == str(product_dim2),
            ProductCodeTrans.sap_dim_3 == str(product_dim3),
            ProductCodeTrans.mill_id == plant_id,
        )
        product_code_trans = db_session.scalar(stmt)

    return product_code_trans


def get_rolling_code_184(root):
    e1edka1s = root.findall(".//E1EDKA1")
    source_plant = None
    destination_plant = None
    for elem in e1edka1s:
        if elem.findtext("PARVW") == "LF":
            source_plant = elem.findtext("PARTN")
            continue
        if elem.findtext("PARVW") == "WE":
            destination_plant = elem.findtext("LIFNR")
            continue

    rolling_code = None
    if source_plant and destination_plant:
        if "8501" in source_plant and destination_plant == "8406":
            rolling_code = "824S"
        elif "8501" in source_plant and destination_plant == "8407":
            rolling_code = "824S"
        elif "8511" in source_plant and destination_plant == "8406":
            rolling_code = "821S"
        elif "8511" in source_plant and destination_plant == "8407":
            rolling_code = "821S"
        elif "8801" in source_plant and destination_plant == "8800":
            rolling_code = "442S"
        elif "8800" in source_plant and destination_plant == "8801":
            rolling_code = "442S"
        elif "8501" in source_plant and destination_plant == "8609":
            rolling_code = "580S"

    return rolling_code


def parse_vals_274(root) -> dict:
    vals_dict = {}
    e1cuvals = root.findall(".//E1CUVAL")
    vals_dict = {
        e1cuval.findtext("CHARC"): e1cuval.findtext("VALUE")
        for e1cuval in e1cuvals
    }

    return vals_dict


def increment_group_code(current_code):
    """递增 group_code，例如 A -> B, Z -> AA"""
    if current_code == 'Z':
        return 'AA'

    # 将字符转为数字，计算下一个字符
    next_code = list(current_code)
    i = len(next_code) - 1

    while i >= 0:
        if next_code[i] == 'Z':
            next_code[i] = 'A'
            if i == 0:
                next_code.insert(0, 'A')  # 增加一位
        else:
            next_code[i] = chr(ord(next_code[i]) + 1)
            break
        i -= 1

    return ''.join(next_code)


def get_numeric_value(value, default=-1):
    if value is None:
        return default
    if value.isdigit():
        return int(value)
    else:
        return default



def sort_by_dim3(db_session, mill_id):
    import random
    # 查询所有符合条件的 OrderGroup 记录
    result = db_session.query(OrderGroup).with_entities(
        OrderGroup.id, OrderGroup.product_id, OrderGroup.rolling_id
    ).filter(OrderGroup.mill_id == mill_id).all()
    try:
        # 生成所需的唯一随机数集合
        unique_numbers = random.sample(range(100000, 1000000), len(result))
        # 将唯一随机数分配给每个 `id`
        ids = [{
            "id": i.id,
            "group_charge_seq": unique_numbers[idx]  # 逐个分配
        } for idx, i in enumerate(result)]

        db_session.bulk_update_mappings(OrderGroup, ids)
        db_session.commit()
    except Exception as e:
        # 生成所需的唯一随机数集合
        unique_numbers = random.sample(range(2000000, 100000000), len(result))
        # 将唯一随机数分配给每个 `id`
        ids = [{
            "id": i.id,
            "group_charge_seq": unique_numbers[idx]  # 逐个分配
        } for idx, i in enumerate(result)]

        db_session.bulk_update_mappings(OrderGroup, ids)
        db_session.commit()

    if not result:
        return

    # 构建 pro_rol_ids 列表，包含 id、rolling_id 和 product_id
    pro_rol_ids = [
        {"id": i.id, "rolling_id": i.rolling_id, "product_id": i.product_id}
        for i in result
    ]

    # 查询所有相关的 ProductType 记录，构建 dim3 查找字典
    product_type_ids = [i['product_id'] for i in pro_rol_ids]
    product_type_dict_list = db_session.query(ProductType).filter(
        ProductType.id.in_(product_type_ids)
    ).all()

    if not product_type_dict_list:
        return

    product_type_dict = {i.id: float(i.dim3) for i in product_type_dict_list}

    # 为每个记录添加 dim3 值
    for i in pro_rol_ids:
        i['dim3'] = product_type_dict.get(i['product_id'], 0.0)

    # 按 rolling_id 和 dim3 排序
    pro_rol_ids.sort(key=lambda x: (x['rolling_id'], x['dim3']))

    # 为每个 rolling_id 分配从 0 开始的 group_charge_seq
    current_rolling_id = None
    current_seq = 0

    for item in pro_rol_ids:
        if item['rolling_id'] != current_rolling_id:
            # 如果 rolling_id 变化，重置序列号
            current_rolling_id = item['rolling_id']
            current_seq = 0
        item['group_charge_seq'] = current_seq
        current_seq += 1

    # 删除不需要的字段
    for i in pro_rol_ids:
        del i['rolling_id'], i['product_id'], i['dim3']

    # 批量更新数据库
    try:
        db_session.bulk_update_mappings(OrderGroup, pro_rol_ids)
        db_session.commit()
    except Exception as e:
        db_session.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    return {}


def query_dict_list_field(source_dict_list, query_field, target,
                          add_query_field=None, add_target=None,
                          add_query_field1=None, add_target1=None,
                          add_query_field2=None, add_target2=None):
    """
    从字典列表中查询符合条件的第一个字典。

    参数：
    - source_dict_list: List[Dict]，要查询的字典列表。
    - query_field: str，主要查询字段。
    - target: Any，主要查询字段的值。
    - add_query_field, add_target: str, Any，附加条件1。
    - add_query_field1, add_target1: str, Any，附加条件2。
    - add_query_field2, add_target2: str, Any，附加条件3。

    返回：
    - 符合条件的字典；如果未找到，则返回 None。
    """
    if not source_dict_list:  # 如果 source_dict_list 为空
        return None

    # 定义所有查询条件
    conditions = [
        (query_field, target),
        (add_query_field, add_target),
        (add_query_field1, add_target1),
        (add_query_field2, add_target2),
    ]

    # 过滤掉空条件
    conditions = [(field, value) for field, value in conditions if field is not None and value is not None]

    # 遍历字典列表，查找符合条件的第一个字典
    for item in source_dict_list:
        if all(item.get(field) == value for field, value in conditions):
            return item

    # 未找到符合条件的字典
    return None


def allocated_block(db_session, order_items, mill_id=MILLEnum.MILL410):
    log_head = "[Order Group By Order Item]"

    # log.debug(order_items)
    # 避免循环查询    把所有的rolling id code都找出来
    # 把所有需要的都找出来

    rolling_list = db_session.query(Rolling).with_entities(Rolling.id, Rolling.rolling_code).filter(Rolling.mill_id == mill_id).all()
    rolling_dict_list = [
        {"rolling_id": row[0], "rolling_code": row[1]} for row in rolling_list
    ]

    product_type_list = db_session.query(ProductType).with_entities(ProductType.id, ProductType.dim1,
                                                                    ProductType.dim2,
                                                                    ProductType.dim3,
                                                                    ProductType.product_class_id
                                                                    ).filter(ProductType.mill_id == mill_id).all()
    product_class_list = db_session.query(ProductClass).with_entities(ProductClass.id, ProductClass.code).all()

    product_class_dict_list = [
        {
            "product_class_id": row[0],
            "product_class_code": row[1]
        } for row in product_class_list
    ]

    def find_code_by_id(id):
        for i in product_class_dict_list:
            if i['product_class_id'] == id:
                return i['product_class_code']
        return None

    product_type_dict_list = [
        {"product_type_id": row[0], "product_type_dim1": row[1], "product_type_dim2": row[2],
         "product_type_dim3": row[3], "product_class_code": find_code_by_id(row[4])} for row in
        product_type_list
    ]

    spec_list = db_session.query(Spec).with_entities(Spec.id, Spec.spec_code).filter(Spec.mill_id == mill_id).all()
    spec_dict_list = [
        {"spec_id": row[0], "spec_code": row[1]} for row in spec_list
    ]

    order_group_list = db_session.query(OrderGroup).with_entities(OrderGroup.id, OrderGroup.product_id,
                                                                  OrderGroup.rolling_id).filter(OrderGroup.mill_id == mill_id).all()
    order_group_dict_list = [
        {"order_group_id": row[0], "product_type_id": row[1], "rolling_id": row[2]} for row in order_group_list
    ]

    order_spec_group_list = db_session.query(OrderSpecGroup).with_entities(OrderSpecGroup.id,
                                                                           OrderSpecGroup.spec_id,
                                                                           OrderSpecGroup.order_group_id,
                                                                           OrderSpecGroup.length,
                                                                           OrderSpecGroup.weight,
                                                                           OrderSpecGroup.quality_code
                                                                           ).filter(OrderSpecGroup.mill_id == mill_id).all()
    order_spec_group_dict_list = [
        {"order_spec_group_id": row[0], "spec_id": row[1], "order_group_id": row[2], "length": row[3], "weight": row[4], "quality_code": row[5]}
        for row in order_spec_group_list
    ]

    ##################  order group 分组  ##################
    # 过滤条件
    for order_item in order_items:

        order_group_in = OrderGroup()
        order_spec_group_in = OrderSpecGroup()
        rolling_id = None
        product_type_id = None
        new_order_group_id = None
        # log.debug(f"[{log_head}] Rolling ID: {rolling_id}")

        ##  找product type了
        order_dim1 = get_numeric_value(value=order_item['product_dim1'], default=-99999)
        order_dim2 = get_numeric_value(value=order_item['product_dim2'], default=-99999)
        order_dim3 = get_numeric_value(value=order_item['product_dim3'], default=-99999)
        log.debug(f"order_dim1: {order_dim1}, order_dim2: {order_dim2}")
        #  查询dim1  dim2  在product type 是否存在
        query_product_type = query_dict_list_field(source_dict_list=product_type_dict_list,
                                                   query_field="product_type_dim1",
                                                   target=order_dim1,
                                                   add_query_field="product_type_dim2",
                                                   add_target=order_dim2,
                                                   add_query_field1="product_type_dim3",
                                                   add_target1=order_dim3,
                                                   add_query_field2="product_class_code",
                                                   add_target2=order_item['product_code']
                                                   )
        if not query_product_type:
            log.debug(
                f"[{log_head}] product_type dim1, dim2({order_dim1}, {order_dim2}) doesn't exist, skip grouping")
            continue
        # 保存product type id
        product_type_id = query_product_type.get("product_type_id")

        # 查找是否存在
        if order_item['product_code'] is None:
            log.debug(f"[{log_head}] product class code doesn't exist, skip grouping")
            continue


        if order_item['rolling_code'] is None:
            log.debug(f"[{log_head}] rolling code doesn't exist, skip grouping")
            continue

        # 如果存在 构造完整的rolling code
        fill_rolling_code = f"{order_item['product_code']}-{order_dim1}-{order_dim2}-{order_item['rolling_code']}"
        # if fill_rolling_code == "UB-610-229-T47A":
        #     log.debug(f"*******************【{fill_rolling_code}】*******************")

        # 将存在rolling code的rolling找到
        query_rolling = query_dict_list_field(source_dict_list=rolling_dict_list,
                                              query_field="rolling_code",
                                              target=fill_rolling_code
                                              )
        # 如果通过rolling code 查询不到rolling 那就跳过
        if not query_rolling:
            log.debug(
                f"[{log_head}] The rolling_id corresponding to rolling_short_code ({order_item['rolling_code']}) does not exist, so this order group is skipped")
            continue
        # 存在的话就找到它
        rolling_id = query_rolling.get("rolling_id")



        log.debug(f"[{log_head}] Product Type ID: ({product_type_id})")
        # 查询order group 中是否存在 product type id 和 rolling_id
        query_order_group = query_dict_list_field(source_dict_list=order_group_dict_list,
                                                  query_field="rolling_id",
                                                  target=rolling_id,
                                                  add_query_field="product_type_id",
                                                  add_target=product_type_id
                                                  )
        if not query_order_group:
            # 如果不存在就新建一个order_group  然后再把id挂上
            order_group_in.rolling_id = rolling_id
            order_group_in.product_id = product_type_id

            """ 这一块主要在生成序号"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
            # 获取最大 group_charge_seq
            max_group_charge_seq = (
                db_session.query(OrderGroup.group_charge_seq)
                .filter(and_(OrderGroup.rolling_id == rolling_id, OrderGroup.mill_id == mill_id))
                .order_by(OrderGroup.group_charge_seq.desc())
                .first()
            )
            group_charge_seq = (max_group_charge_seq[0] + 1) if max_group_charge_seq else 10000

            # 检查并调整 group_charge_seq 确保唯一性
            while db_session.query(OrderGroup).filter_by(
                    rolling_id=rolling_id,
                    group_charge_seq=group_charge_seq,
                    mill_id=mill_id
            ).first():
                group_charge_seq += 1

            # 获取最大 group_code
            max_group_code = (
                db_session.query(OrderGroup.group_code)
                .filter_by(rolling_id=rolling_id, mill_id=mill_id)
                .order_by(OrderGroup.group_code.desc())
                .first()
            )

            # 如果 max_group_code 存在，直接在最大值上加 1；如果不存在，默认从 1 开始
            new_group_code = str(int(max_group_code[0]) + 1) if max_group_code else '1'

            """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
            order_group_in.group_charge_seq = group_charge_seq
            order_group_in.group_code = new_group_code
            order_group_in.mill_id = mill_id
            db_session.add(order_group_in)
            db_session.flush()  # 推送数据
            # 获取新建order_group的id
            new_order_group_id = order_group_in.id
            # 挂上group_id
            update_group_id = sqlalchemy_update(OrderItem).where(and_(
                OrderItem.line_item_code == order_item['line_item_code'],
                OrderItem.order_id == order_item['order_id'],
                OrderItem.plant_id == order_item.get('mill_id'),
            )).values(
                {"order_group_id": new_order_group_id})
            db_session.execute(update_group_id)
            db_session.commit()

            ###### 如果新建order group了 需要重新查一下表
            order_group_list = db_session.query(OrderGroup).with_entities(OrderGroup.id, OrderGroup.product_id,
                                                                          OrderGroup.rolling_id).filter(OrderGroup.mill_id == mill_id).all()
            order_group_dict_list = [
                {"order_group_id": row[0], "product_type_id": row[1], "rolling_id": row[2]} for row in order_group_list
            ]

        else:
            new_order_group_id = query_order_group.get('order_group_id')
            # log.info(f"**************************** [{mill_id}工厂更新order item调试] **************************")
            # log.info(f"1. 存在的order_group_id：{new_order_group_id}")
            # 如果存在 那直接获取order_group_id然后挂到order_item的order_group_id上即可
            update_group_id = sqlalchemy_update(OrderItem).where(
                OrderItem.id == order_item.get('id')
            ).values(
                {"order_group_id": new_order_group_id})


            # log.info(f"SQL: {update_group_id}")
            db_session.execute(update_group_id)
            # log.info(f"2. 执行完更新order item[id: {order_item['id']}]上挂order_group_id：{new_order_group_id}")
            db_session.commit()
            # log.info(f"3. order_item： {order_item['line_item_code'], order_item['order_id']} 已提交事务")
            # log.info("*****************************************************************************")
        ############## order spec group 分组 ##############

        # 没有spec code 跳过
        if not order_item["spec_id"]:
            log.debug(f"[{log_head}] Spec id doesn't exist, skip grouping")
            continue

        # query_spec = query_dict_list_field(
        #     source_dict_list=spec_dict_list,
        #     query_field="spec_code",
        #     target=order_item["spec_code"],
        # )

        # # 在spec表中找不到 就跳过
        # if not query_spec:
        #     log.debug(f"[{log_head}] spec_code ({order_item['spec_code']}) doesn't query in database, skip grouping")
        #     continue

        # 如果存在就取出来
        spec_id = order_item.get("spec_id")

        query_order_spec_group = query_dict_list_field(
            source_dict_list=order_spec_group_dict_list,
            query_field="spec_id",
            target=spec_id,
            add_query_field="order_group_id",
            add_target=new_order_group_id
        )

        if not query_order_spec_group:
            if order_item["quality_code"] is None:
                log.error(f"id: {order_item['id']}, line_item_code: {order_item['line_item_code']} : quality_code is None.")


            # 如果不存在 order spec group 就新建一个
            order_spec_group_in.spec_id = spec_id
            order_spec_group_in.order_group_id = new_order_group_id
            order_spec_group_in.spec_charge_seq = 123  # 暂时随便填的
            order_spec_group_in.spec_group_code = "A"  # 暂时随便填的
            # order_spec_group_in.length = Decimal(order_item["length_mm"] or 0)
            # dim3 = query_product_type.get("product_type_dim3")
            # order_spec_group_in.weight = Decimal(dim3 if dim3 != -1 else 0)
            order_spec_group_in.quality_code = order_item["quality_code"]  # 如果不存在就为1642
            order_spec_group_in.mill_id = mill_id
            db_session.add(order_spec_group_in)
            db_session.flush()  # 推送数据
            db_session.commit()

            # 新建 order spec group 需要重新查一下所有列表
            order_spec_group_list = db_session.query(OrderSpecGroup).with_entities(OrderSpecGroup.id,
                                                                                   OrderSpecGroup.spec_id,
                                                                                   OrderSpecGroup.order_group_id,
                                                                                   OrderSpecGroup.length,
                                                                                   OrderSpecGroup.weight,
                                                                                   OrderSpecGroup.quality_code
                                                                                   ).filter(OrderSpecGroup.mill_id == mill_id).all()
            order_spec_group_dict_list = [
                {"order_spec_group_id": row[0], "spec_id": row[1], "order_group_id": row[2], "length": row[3],
                 "weight": row[4], "quality_code": row[5]} for row in order_spec_group_list
            ]


    db_session.commit()

    computer_weight_spec_group(db_session=db_session)
    find_max_length(db_session=db_session)
    return 1




def allocated_block_v2(db_session, order_items, mill_id):
    log_head = "[Order Group By Order Item]"

    print(mill_id)
    # 避免循环查询    把所有的rolling id code都找出来
    # 把所有需要的都找出来

    order_group_list = db_session.query(OrderGroup).with_entities(OrderGroup.id, OrderGroup.product_id,
                                                                  OrderGroup.rolling_id).filter(OrderGroup.mill_id == mill_id).all()
    order_group_dict_list = [
        {"order_group_id": row[0], "product_type_id": row[1], "rolling_id": row[2]} for row in order_group_list
    ]

    order_spec_group_list = db_session.query(OrderSpecGroup).with_entities(OrderSpecGroup.id,
                                                                           OrderSpecGroup.spec_id,
                                                                           OrderSpecGroup.order_group_id,
                                                                           OrderSpecGroup.length,
                                                                           OrderSpecGroup.weight,
                                                                           OrderSpecGroup.quality_code
                                                                           ).filter(OrderSpecGroup.mill_id == mill_id).all()
    order_spec_group_dict_list = [
        {"order_spec_group_id": row[0], "spec_id": row[1], "order_group_id": row[2], "length": row[3], "weight": row[4], "quality_code": row[5]}
        for row in order_spec_group_list
    ]

    ##################  order group 分组  ##################
    temp_seq = 110 # 先使用这个字段顺序排序
    # 过滤条件
    for order_item in order_items:

        order_group_in = OrderGroup()
        order_spec_group_in = OrderSpecGroup()
        rolling_id = None
        product_type_id = None
        new_order_group_id = None
        # log.debug(f"[{log_head}] Rolling ID: {rolling_id}")

        ##  找product type了
        order_dim1 = get_numeric_value(value=order_item['product_dim1'], default=-99999)
        order_dim2 = get_numeric_value(value=order_item['product_dim2'], default=-99999)
        order_dim3 = get_numeric_value(value=order_item['product_dim3'], default=-99999)
        log.debug(f"order_dim1: {order_dim1}, order_dim2: {order_dim2}")

        # 保存product type id
        product_type_id = order_item.get("product_type_id", None)

        if not product_type_id:
            log.debug(
                f"[{log_head}] Order item not found product type id.")
            continue

        # 存在的话就找到它
        rolling_id = order_item.get("rolling_id", None)

        if not rolling_id:
            log.debug(
                f"[{log_head}] Order item not found rolling id.")
            continue


        log.debug(f"[{log_head}] Product Type ID: ({product_type_id})")
        # 查询order group 中是否存在 product type id 和 rolling_id
        query_order_group = query_dict_list_field(source_dict_list=order_group_dict_list,
                                                  query_field="rolling_id",
                                                  target=rolling_id,
                                                  add_query_field="product_type_id",
                                                  add_target=product_type_id
                                                  )
        if not query_order_group:
            # 如果不存在就新建一个order_group  然后再把id挂上
            order_group_in.rolling_id = rolling_id
            order_group_in.product_id = product_type_id

            """ 这一块主要在生成序号"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
            # 获取最大 group_charge_seq
            # max_group_charge_seq = (
            #     db_session.query(OrderGroup.group_charge_seq)
            #     .filter(and_(OrderGroup.rolling_id == rolling_id, OrderGroup.mill_id == mill_id))
            #     .order_by(OrderGroup.group_charge_seq.desc())
            #     .first()
            # )
            # group_charge_seq = (max_group_charge_seq[0] + 1) if max_group_charge_seq else 0
            #
            # # 检查并调整 group_charge_seq 确保唯一性
            # while db_session.query(OrderGroup).filter_by(
            #         rolling_id=rolling_id,
            #         group_charge_seq=group_charge_seq,
            #         mill_id=mill_id
            # ).first():
            #     group_charge_seq += 1

            # 获取最大 group_code
            max_group_code = (
                db_session.query(OrderGroup.group_code)
                .filter_by(rolling_id=rolling_id, mill_id=mill_id)
                .order_by(OrderGroup.group_code.desc())
                .first()
            )

            # 如果 max_group_code 存在，直接在最大值上加 1；如果不存在，默认从 1 开始
            new_group_code = str(int(max_group_code[0]) + 1) if max_group_code else '1'

            """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
            order_group_in.group_charge_seq = temp_seq
            temp_seq += 1
            order_group_in.group_code = new_group_code
            order_group_in.mill_id = mill_id
            db_session.add(order_group_in)
            db_session.flush()  # 推送数据
            # 获取新建order_group的id
            new_order_group_id = order_group_in.id
            # 挂上group_id
            update_group_id = sqlalchemy_update(OrderItem).where(and_(
                OrderItem.line_item_code == order_item['line_item_code'],
                OrderItem.order_id == order_item['order_id'],
                OrderItem.plant_id == order_item['mill_id'],
            )).values(
                {"order_group_id": new_order_group_id})
            db_session.execute(update_group_id)
            db_session.commit()

            ###### 如果新建order group了 需要重新查一下表
            order_group_list = db_session.query(OrderGroup).with_entities(OrderGroup.id, OrderGroup.product_id,
                                                                          OrderGroup.rolling_id).filter(OrderGroup.mill_id == mill_id).all()
            order_group_dict_list = [
                {"order_group_id": row[0], "product_type_id": row[1], "rolling_id": row[2]} for row in order_group_list
            ]

        else:
            new_order_group_id = query_order_group.get('order_group_id')
            # log.info(f"**************************** [{mill_id}工厂更新order item调试] **************************")
            # log.info(f"1. 存在的order_group_id：{new_order_group_id}")
            # 如果存在 那直接获取order_group_id然后挂到order_item的order_group_id上即可
            update_group_id = sqlalchemy_update(OrderItem).where(
                OrderItem.id == order_item['id']
            ).values(
                {"order_group_id": new_order_group_id})


            # log.info(f"SQL: {update_group_id}")
            db_session.execute(update_group_id)
            # log.info(f"2. 执行完更新order item[id: {order_item['id']}]上挂order_group_id：{new_order_group_id}")
            db_session.commit()
            # log.info(f"3. order_item： {order_item['line_item_code'], order_item['order_id']} 已提交事务")
            # log.info("*****************************************************************************")
        ############## order spec group 分组 ##############

        # 没有spec code 跳过
        if not order_item["spec_id"]:
            log.debug(f"[{log_head}] Spec id doesn't exist, skip grouping")
            continue

        # query_spec = query_dict_list_field(
        #     source_dict_list=spec_dict_list,
        #     query_field="spec_code",
        #     target=order_item["spec_code"],
        # )

        # # 在spec表中找不到 就跳过
        # if not query_spec:
        #     log.debug(f"[{log_head}] spec_code ({order_item['spec_code']}) doesn't query in database, skip grouping")
        #     continue

        # 如果存在就取出来
        spec_id = order_item.get("spec_id")

        query_order_spec_group = query_dict_list_field(
            source_dict_list=order_spec_group_dict_list,
            query_field="spec_id",
            target=spec_id,
            add_query_field="order_group_id",
            add_target=new_order_group_id
        )

        if not query_order_spec_group:
            if order_item["quality_code"] is None:
                log.info(f"id: {order_item['id']}, line_item_code: {order_item['line_item_code']} : quality_code is None.")


            # 如果不存在 order spec group 就新建一个
            order_spec_group_in.spec_id = spec_id
            order_spec_group_in.order_group_id = new_order_group_id
            order_spec_group_in.spec_charge_seq = 123  # 暂时随便填的
            order_spec_group_in.spec_group_code = "A"  # 暂时随便填的
            # order_spec_group_in.length = Decimal(order_item["length_mm"] or 0)
            # dim3 = query_product_type.get("product_type_dim3")
            # order_spec_group_in.weight = Decimal(dim3 if dim3 != -1 else 0)
            order_spec_group_in.quality_code = order_item["quality_code"]  # 如果不存在就为1642
            order_spec_group_in.mill_id = mill_id
            db_session.add(order_spec_group_in)
            db_session.flush()  # 推送数据
            db_session.commit()

            # 新建 order spec group 需要重新查一下所有列表
            order_spec_group_list = db_session.query(OrderSpecGroup).with_entities(OrderSpecGroup.id,
                                                                                   OrderSpecGroup.spec_id,
                                                                                   OrderSpecGroup.order_group_id,
                                                                                   OrderSpecGroup.length,
                                                                                   OrderSpecGroup.weight,
                                                                                   OrderSpecGroup.quality_code
                                                                                   ).filter(OrderSpecGroup.mill_id == mill_id).all()
            order_spec_group_dict_list = [
                {"order_spec_group_id": row[0], "spec_id": row[1], "order_group_id": row[2], "length": row[3],
                 "weight": row[4], "quality_code": row[5]} for row in order_spec_group_list
            ]


    db_session.commit()

    computer_weight_spec_group(db_session=db_session)
    find_max_length(db_session=db_session)
    return 1


# 稳定 大约3s
def allocated_block_v3(db_session: Session, order_items, mill_id):
    start = time.time()
    log_head = "[Order Group By Order Item]"

    # 避免循环查询    把所有的rolling id code都找出来
    # 把所有需要的都找出来

    order_group_list = db_session.query(OrderGroup).with_entities(OrderGroup.id, OrderGroup.product_id, OrderGroup.rolling_id,
                                                                  OrderGroup.group_code).filter(OrderGroup.mill_id == mill_id).all()
    order_group_dict_list = [
        {"order_group_id": row[0], "product_type_id": row[1], "rolling_id": row[2], "group_code": row[3]} for row in order_group_list
    ]
    max_order_group_id = db_session.query(func.max(OrderGroup.id)).filter(OrderGroup.id != 999999999).scalar() or 0

    order_spec_group_list = db_session.query(OrderSpecGroup).with_entities(OrderSpecGroup.id,
                                                                           OrderSpecGroup.spec_id,
                                                                           OrderSpecGroup.order_group_id,
                                                                           OrderSpecGroup.length,
                                                                           OrderSpecGroup.weight,
                                                                           OrderSpecGroup.quality_code
                                                                           ).filter(OrderSpecGroup.mill_id == mill_id).all()
    order_spec_group_dict_list = [
        {"order_spec_group_id": row[0], "spec_id": row[1], "order_group_id": row[2], "length": row[3], "weight": row[4], "quality_code": row[5]}
        for row in order_spec_group_list
    ]
    max_order_spec_group_id = db_session.query(func.max(OrderSpecGroup.id)).filter(OrderSpecGroup.id != 999999999).scalar() or 0
    max_group_charge_seq = db_session.query(func.max(OrderGroup.group_charge_seq)).filter(OrderGroup.id != 999999999).scalar()
    temp_seq = max_group_charge_seq or 110  # 先使用这个字段顺序排序
    order_group_in = []
    order_spec_group_in = []
    update_order_item_in = []
    # 过滤条件
    for order_item in order_items:
        ############################# order_group ########################
        product_type_id = order_item.get("product_type_id", None)
        if not product_type_id or product_type_id == 999999999:
            # log.debug(f"{log_head} (order item id: {order_item.get("id")}) product_type_id not exist, skip grouping")
            continue

        rolling_id = order_item.get("rolling_id", None)
        if not rolling_id or rolling_id == 999999999:
            # log.debug(f"{log_head} (order item id: {order_item.get("id")}) rolling_id not exist, skip grouping")
            continue

        query_order_group = query_dict_list_field(source_dict_list=order_group_dict_list,
                                                  query_field="rolling_id",
                                                  target=rolling_id,
                                                  add_query_field="product_type_id",
                                                  add_target=product_type_id
                                                  )
        new_order_group_id = None
        if not query_order_group:
            max_group_code = max(
                (int(item["group_code"]) for item in order_group_dict_list if item["rolling_id"] == rolling_id),
                default=0
            )
            max_group_code = str(max_group_code + 1) if max_group_code != 0 else str(max_group_code)
            new_order_group_id = max_order_group_id + 1
            temp_seq += 1
            order_group_in.append({
                "id": new_order_group_id,
                "rolling_id": rolling_id,
                "product_id": product_type_id,
                "group_charge_seq": temp_seq,
                "group_code": max_group_code,
                "mill_id": mill_id,
            })
            order_group_dict_list.append({
                "order_group_id": new_order_group_id,
                "product_type_id": product_type_id,
                "rolling_id": rolling_id,
                "group_code": max_group_code
            })
            update_order_item_in.append({
                "id": order_item.get("id"),
                "order_group_id": new_order_group_id,
            })
            max_order_group_id = new_order_group_id
        else:
            new_order_group_id = query_order_group.get("order_group_id")
            order_item_order_group_id = order_item.get("order_group_id", None)
            if not order_item_order_group_id or order_item_order_group_id != new_order_group_id:
                update_order_item_in.append({
                    "id": order_item.get("id"),
                    "order_group_id": new_order_group_id,
                })
                order_item['order_group_id'] = new_order_group_id

        ############################# order_spec_group ########################
        # 没有spec code 跳过
        spec_id = order_item.get("spec_id", None)
        if not spec_id or spec_id == 999999999:
            log.debug(f"[{log_head}] (order item id: {order_item.get("id")}) Spec id doesn't exist, skip grouping")
            continue

        query_order_spec_group = query_dict_list_field(
            source_dict_list=order_spec_group_dict_list,
            query_field="spec_id",
            target=spec_id,
            add_query_field="order_group_id",
            add_target=new_order_group_id
        )

        if not query_order_spec_group:
            quality_code = order_item.get("quality_code", None)
            if not quality_code:
                log.info(f"{log_head} (order item id: {order_item.get("id")}) quality_code is None.")
            new_order_spec_group_id = max_order_spec_group_id + 1
            order_spec_group_in.append({
                "id": new_order_spec_group_id,
                "spec_id": spec_id,
                "order_group_id": new_order_group_id,
                "quality_code": quality_code,
                "mill_id": mill_id,
                "spec_charge_seq": 123,
                "spec_group_code": "A",
            })
            order_spec_group_dict_list.append({
                "order_spec_group_id": new_order_spec_group_id,
                "spec_id": spec_id,
                "order_group_id": new_order_group_id,
                "quality_code": quality_code,
                "length": None,
                "weight": None
            })

            max_order_spec_group_id = new_order_spec_group_id


    if order_group_in:
        db_session.bulk_insert_mappings(OrderGroup, order_group_in)
    if order_spec_group_in:
        db_session.bulk_insert_mappings(OrderSpecGroup, order_spec_group_in)
    if update_order_item_in:
        db_session.bulk_update_mappings(OrderItem, update_order_item_in)

    db_session.commit()
    log.info(f"[Order group] The number of bulk inserting: {len(order_group_in)} ")
    log.info(f"[Order Spec group] The number of bulk inserting: {len(order_spec_group_in)} ")
    log.info(f"[Order Item] The number of bulk updating: {len(update_order_item_in)} ")

    end = time.time()
    log.warning(f"Generate Group spend time: {round((end - start), 3)}s")
    start = time.time()
    computer_weight_spec_group(db_session=db_session, spec_group_list=order_spec_group_dict_list)
    end = time.time()
    log.warning(f"Computer weight spend time: {round((end - start), 3)}s")

    start = time.time()
    find_max_length_v2(db_session=db_session, spec_group_dict_list=order_spec_group_dict_list, order_items=order_items)
    # find_max_length(db_session=db_session, spec_group_dict_list=order_spec_group_dict_list, order_items=order_items)
    end = time.time()
    log.warning(f"Find max length spend time:: {round((end - start), 3)}s")
    return 1


# 大约1s ~ 2s
def allocated_block_v4(db_session: Session, order_items, mill_id):
    start = time.time()
    log_head = "[Order Group By Order Item]"

    # 避免循环查询，把所有的 rolling id 和 code 都找出来
    order_group_list = db_session.query(OrderGroup).with_entities(
        OrderGroup.id, OrderGroup.product_id, OrderGroup.rolling_id, OrderGroup.group_code
    ).filter(OrderGroup.mill_id == mill_id).all()

    # 使用字典缓存，提高查找速度
    order_group_dict = {}
    for row in order_group_list:
        key = (row[2], row[1])  # (rolling_id, product_type_id)
        order_group_dict[key] = {"order_group_id": row[0], "group_code": row[3], "rolling_id": row[2]}

    order_spec_group_list = db_session.query(OrderSpecGroup).with_entities(OrderSpecGroup.id,
                                                                           OrderSpecGroup.spec_id,
                                                                           OrderSpecGroup.order_group_id,
                                                                           OrderSpecGroup.length,
                                                                           OrderSpecGroup.weight,
                                                                           OrderSpecGroup.quality_code
                                                                           ).filter(
        OrderSpecGroup.mill_id == mill_id).all()
    order_spec_group_dict_list = [
        {"order_spec_group_id": row[0], "spec_id": row[1], "order_group_id": row[2], "length": row[3], "weight": row[4],
         "quality_code": row[5]}
        for row in order_spec_group_list
    ]

    # 获取最大值并缓存
    max_order_group_id = db_session.query(func.max(OrderGroup.id)).filter(OrderGroup.id != 999999999).scalar() or 0
    max_order_spec_group_id = db_session.query(func.max(OrderSpecGroup.id)).filter(OrderSpecGroup.id != 999999999).scalar() or 0
    max_group_charge_seq = db_session.query(func.max(OrderGroup.group_charge_seq)).filter(OrderGroup.id != 999999999).scalar()
    temp_seq = max_group_charge_seq or 110

    # 数据收集列表
    order_group_in = []
    order_spec_group_in = []
    update_order_item_in = []

    # 过滤条件
    for order_item in order_items:
        product_type_id = order_item.get("product_type_id", None)
        if not product_type_id or product_type_id == 999999999:
            continue

        rolling_id = order_item.get("rolling_id", None)
        if not rolling_id or rolling_id == 999999999:
            continue

        # 使用字典查找，避免循环查询
        order_group_key = (rolling_id, product_type_id)
        order_group = order_group_dict.get(order_group_key)
        test_l = [int(item["group_code"] or 1) for item in order_group_dict.values() if int(item["rolling_id"]) == int(rolling_id)]
        # print(test_l)

        if not order_group:
            max_group_code = max(
                (int(item["group_code"]) for item in order_group_dict.values() if int(item["rolling_id"]) == int(rolling_id)),
                default=0
            )
            max_group_code = str(max_group_code + 1)
            new_order_group_id = max_order_group_id + 1
            temp_seq += 1
            order_group_in.append({
                "id": new_order_group_id,
                "rolling_id": rolling_id,
                "product_id": product_type_id,
                "group_charge_seq": temp_seq,
                "group_code": max_group_code,
                "mill_id": mill_id,
            })
            order_group_dict[(rolling_id, product_type_id)] = {
                "order_group_id": new_order_group_id,
                "group_code": max_group_code,
                "rolling_id": rolling_id  # 确保字典中包含 rolling_id
            }
            update_order_item_in.append({
                "id": order_item.get("id"),
                "order_group_id": new_order_group_id,
            })
            max_order_group_id = new_order_group_id
        else:
            new_order_group_id = order_group["order_group_id"]
            order_item_order_group_id = order_item.get("order_group_id", None)
            if not order_item_order_group_id or order_item_order_group_id != new_order_group_id:
                update_order_item_in.append({
                    "id": order_item.get("id"),
                    "order_group_id": new_order_group_id,
                })
                order_item['order_group_id'] = new_order_group_id

        ############################# order_spec_group ########################

        spec_id = order_item.get("spec_id", None)
        if not spec_id or spec_id == 999999999:
            continue

        query_order_spec_group = next(
            (item for item in order_spec_group_dict_list if item["spec_id"] == spec_id and item["order_group_id"] == new_order_group_id),
            None
        )

        if not query_order_spec_group:
            quality_code = order_item.get("quality_code", None)
            if not quality_code:
                log.info(f"{log_head} (order item id: {order_item.get('id')}) quality_code is None.")
            new_order_spec_group_id = max_order_spec_group_id + 1
            order_spec_group_in.append({
                "id": new_order_spec_group_id,
                "spec_id": spec_id,
                "order_group_id": new_order_group_id,
                "quality_code": quality_code,
                "mill_id": mill_id,
                "spec_charge_seq": 123,
                "spec_group_code": "A",
            })
            order_spec_group_dict_list.append({
                "order_spec_group_id": new_order_spec_group_id,
                "spec_id": spec_id,
                "order_group_id": new_order_group_id,
                "quality_code": quality_code,
                "length": 0,
                "weight": 0
            })
            max_order_spec_group_id = new_order_spec_group_id

    # 批量插入和更新
    order_group_ids = []
    if order_group_in:
        db_session.bulk_insert_mappings(OrderGroup, order_group_in)
        for order_group in order_group_in:
            order_group_ids.append(order_group['id']) 
    if order_spec_group_in:
        db_session.bulk_insert_mappings(OrderSpecGroup, order_spec_group_in)
    if update_order_item_in:
        db_session.bulk_update_mappings(OrderItem, update_order_item_in)

    db_session.commit()
    log.info(f"[Order group] The number of bulk inserting: {len(order_group_in)} ")
    log.info(f"[Order Spec group] The number of bulk inserting: {len(order_spec_group_in)} ")
    log.info(f"[Order Item] The number of bulk updating: {len(update_order_item_in)} ")

    end = time.time()
    log.warning(f"Generate Group spend time: {round((end - start), 3)}s")
    start = time.time()
    computer_weight_spec_group_v2(db_session=db_session, spec_group_list=order_spec_group_dict_list)
    end = time.time()
    log.warning(f"Computer weight spend time: {round((end - start), 3)}s")

    start = time.time()
    find_max_length_v2(db_session=db_session, spec_group_dict_list=order_spec_group_dict_list, order_items=order_items)
    end = time.time()
    log.warning(f"Find max length spend time: {round((end - start), 3)}s")

    return order_group_ids



def allocated_block_v2_for_message(db_session, order_items):
    log_head = "[Order Group By Order Item]"

    # log.debug(order_items)
    # 避免循环查询    把所有的rolling id code都找出来
    # 把所有需要的都找出来


    order_group_list = db_session.query(OrderGroup).with_entities(OrderGroup.id, OrderGroup.product_id,
                                                                  OrderGroup.rolling_id, OrderGroup.mill_id).filter(OrderGroup.mill_id != None).all()
    order_group_dict_list = [
        {"order_group_id": row[0], "product_type_id": row[1], "rolling_id": row[2], "mill_id": row[3]} for row in order_group_list
    ]

    order_spec_group_list = db_session.query(OrderSpecGroup).with_entities(OrderSpecGroup.id,
                                                                           OrderSpecGroup.spec_id,
                                                                           OrderSpecGroup.order_group_id,
                                                                           OrderSpecGroup.length,
                                                                           OrderSpecGroup.weight,
                                                                           OrderSpecGroup.quality_code,
                                                                           OrderSpecGroup.mill_id
                                                                           ).filter(OrderSpecGroup.mill_id != None).all()
    order_spec_group_dict_list = [
        {"order_spec_group_id": row[0], "spec_id": row[1], "order_group_id": row[2], "length": row[3], "weight": row[4], "quality_code": row[5], "mill_id": row[6]}
        for row in order_spec_group_list
    ]

    def dict_list_by_mill(dict_list, mill_id):
        temp_store = []
        for d in dict_list:
            if d['mill_id'] == mill_id:
                temp_store.append(d)
        return temp_store

    ##################  order group 分组  ##################
    # 过滤条件
    for order_item in order_items:
        order_item['order_group_id'] = None
        mill_id = order_item.get("plant_id", None)
        if not mill_id:
            continue
        order_group_dict_list = dict_list_by_mill(dict_list=order_group_dict_list, mill_id=mill_id)
        order_spec_group_dict_list = dict_list_by_mill(dict_list=order_spec_group_dict_list, mill_id=mill_id)

        order_group_in = OrderGroup()
        order_spec_group_in = OrderSpecGroup()
        rolling_id = None
        product_type_id = None
        new_order_group_id = None
        # log.debug(f"[{log_head}] Rolling ID: {rolling_id}")

        # 保存product type id
        product_type_id = order_item.get("product_type_id", None)

        if not product_type_id:
            log.debug(
                f"[{log_head}] Order item not found product type id.")
            continue

        # 存在的话就找到它
        rolling_id = order_item.get("rolling_id", None)

        if not rolling_id:
            log.debug(
                f"[{log_head}] Order item not found rolling id.")
            continue


        log.debug(f"[{log_head}] Product Type ID: ({product_type_id})")
        # 查询order group 中是否存在 product type id 和 rolling_id
        query_order_group = query_dict_list_field(source_dict_list=order_group_dict_list,
                                                  query_field="rolling_id",
                                                  target=rolling_id,
                                                  add_query_field="product_type_id",
                                                  add_target=product_type_id
                                                  )
        if not query_order_group:
            # 如果不存在就新建一个order_group  然后再把id挂上
            order_group_in.rolling_id = rolling_id
            order_group_in.product_id = product_type_id

            """ 这一块主要在生成序号"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
            # 获取最大 group_charge_seq
            max_group_charge_seq = (
                db_session.query(OrderGroup.group_charge_seq)
                .filter(and_(OrderGroup.rolling_id == rolling_id, OrderGroup.mill_id == mill_id))
                .order_by(OrderGroup.group_charge_seq.desc())
                .first()
            )
            group_charge_seq = (max_group_charge_seq[0] + 1) if max_group_charge_seq else 0

            # 检查并调整 group_charge_seq 确保唯一性
            while db_session.query(OrderGroup).filter_by(
                    rolling_id=rolling_id,
                    group_charge_seq=group_charge_seq,
                    mill_id=mill_id
            ).first():
                group_charge_seq += 1

            # 获取最大 group_code
            max_group_code = (
                db_session.query(OrderGroup.group_code)
                .filter_by(rolling_id=rolling_id, mill_id=mill_id)
                .order_by(OrderGroup.group_code.desc())
                .first()
            )

            # 如果 max_group_code 存在，直接在最大值上加 1；如果不存在，默认从 1 开始
            new_group_code = str(int(max_group_code[0]) + 1) if max_group_code else '1'

            """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
            order_group_in.group_charge_seq = group_charge_seq
            order_group_in.group_code = new_group_code
            order_group_in.mill_id = mill_id
            db_session.add(order_group_in)
            db_session.flush()  # 推送数据
            # 获取新建order_group的id
            new_order_group_id = order_group_in.id
            # 挂上group_id
            update_group_id = sqlalchemy_update(OrderItem).where(and_(
                OrderItem.line_item_code == order_item['line_item_code'],
                OrderItem.order_id == order_item['order_id'],
                OrderItem.plant_id == order_item.get("mill_id"),
            )).values(
                {"order_group_id": new_order_group_id})
            db_session.execute(update_group_id)
            db_session.commit()

            ###### 如果新建order group了 需要重新查一下表
            order_group_list = db_session.query(OrderGroup).with_entities(OrderGroup.id, OrderGroup.product_id,
                                                                          OrderGroup.rolling_id).filter(OrderGroup.mill_id == mill_id).all()
            order_group_dict_list = [
                {"order_group_id": row[0], "product_type_id": row[1], "rolling_id": row[2]} for row in order_group_list
            ]

        else:
            new_order_group_id = query_order_group.get('order_group_id')
            # log.info(f"**************************** [{mill_id}工厂更新order item调试] **************************")
            # log.info(f"1. 存在的order_group_id：{new_order_group_id}")
            # 如果存在 那直接获取order_group_id然后挂到order_item的order_group_id上即可
            update_group_id = sqlalchemy_update(OrderItem).where(
                OrderItem.id == order_item.get("id")
            ).values(
                {"order_group_id": new_order_group_id})


            # log.info(f"SQL: {update_group_id}")
            db_session.execute(update_group_id)
            # log.info(f"2. 执行完更新order item[id: {order_item['id']}]上挂order_group_id：{new_order_group_id}")
            db_session.commit()
            # log.info(f"3. order_item： {order_item['line_item_code'], order_item['order_id']} 已提交事务")
            # log.info("*****************************************************************************")
        ############## order spec group 分组 ##############
        order_item['order_group_id'] = new_order_group_id
        log.warning(order_item)
        # 没有spec code 跳过
        if not order_item["spec_id"]:
            log.debug(f"[{log_head}] Spec id doesn't exist, skip grouping")
            continue

        # query_spec = query_dict_list_field(
        #     source_dict_list=spec_dict_list,
        #     query_field="spec_code",
        #     target=order_item["spec_code"],
        # )

        # # 在spec表中找不到 就跳过
        # if not query_spec:
        #     log.debug(f"[{log_head}] spec_code ({order_item['spec_code']}) doesn't query in database, skip grouping")
        #     continue

        # 如果存在就取出来
        spec_id = order_item.get("spec_id")

        query_order_spec_group = query_dict_list_field(
            source_dict_list=order_spec_group_dict_list,
            query_field="spec_id",
            target=spec_id,
            add_query_field="order_group_id",
            add_target=new_order_group_id
        )

        if not query_order_spec_group:
            if order_item["quality_code"] is None:
                log.info(f"id: {order_item['id']}, line_item_code: {order_item['line_item_code']} : quality_code is None.")


            # 如果不存在 order spec group 就新建一个
            order_spec_group_in.spec_id = spec_id
            order_spec_group_in.order_group_id = new_order_group_id
            order_spec_group_in.spec_charge_seq = 123  # 暂时随便填的
            order_spec_group_in.spec_group_code = "A"  # 暂时随便填的
            # order_spec_group_in.length = Decimal(order_item["length_mm"] or 0)
            # dim3 = query_product_type.get("product_type_dim3")
            # order_spec_group_in.weight = Decimal(dim3 if dim3 != -1 else 0)
            order_spec_group_in.quality_code = order_item["quality_code"]  # 如果不存在就为1642
            order_spec_group_in.mill_id = mill_id
            db_session.add(order_spec_group_in)
            db_session.flush()  # 推送数据
            db_session.commit()

            # 新建 order spec group 需要重新查一下所有列表
            order_spec_group_list = db_session.query(OrderSpecGroup).with_entities(OrderSpecGroup.id,
                                                                                   OrderSpecGroup.spec_id,
                                                                                   OrderSpecGroup.order_group_id,
                                                                                   OrderSpecGroup.length,
                                                                                   OrderSpecGroup.weight,
                                                                                   OrderSpecGroup.quality_code
                                                                                   ).filter(OrderSpecGroup.mill_id == mill_id).all()
            order_spec_group_dict_list = [
                {"order_spec_group_id": row[0], "spec_id": row[1], "order_group_id": row[2], "length": row[3],
                 "weight": row[4], "quality_code": row[5]} for row in order_spec_group_list
            ]


    db_session.commit()
    # log.error(order_items)
    computer_weight_spec_group_v2(db_session=db_session, spec_group_list=order_spec_group_dict_list)
    find_max_length_v2(db_session=db_session, spec_group_dict_list=order_spec_group_dict_list, order_items=order_items)
    return 1


def order_item_group_by(db_session, order_items):
    allocated_block_v2_for_message(db_session=db_session, order_items=order_items)




def log_xml_to_file(content: str, msg_type: str):
    today = date.today()
    log_path_cur = ROOT_DIR
    log_path_hierarchy = ['.log', str(today.year), str(today.month), str(today.day)]
    for path_item in log_path_hierarchy:
        log_path_cur = os.path.join(log_path_cur, path_item)
        if not os.path.exists(log_path_cur):
            os.mkdir(log_path_cur)

    log_path_file = os.path.join(log_path_cur, datetime.now().isoformat() + '_' +  msg_type + '.xml')
    with open(log_path_file, 'w') as f:
        f.write(content)

    return True

def save_xml_to_file(xml: str, order_code: str) -> str:
    today = date.today()
    path_cur = ROOT_DIR
    path_children = ['.sap_xml', str(today.year), str(today.month), str(today.day)]
    for path_item in path_children:
        path_cur = os.path.join(path_cur, path_item)
        if not os.path.exists(path_cur):
            os.mkdir(path_cur)

    file_name = os.path.join(*path_children, order_code + '.xml')
    with open(os.path.join(ROOT_DIR, file_name), 'w') as f:
        f.write(xml)

    return file_name


def save_to_message_log_all_7001(db_session, msg, msg_status="Success", type=7001, msg_json_dict=None):
    if msg_json_dict is None:
        msg_json_dict = {}
    msg_info = {
        'message_id': type,
        'msg': msg,
        'message_status': msg_status,
        'interact': 'Slab Yard to MES',
        'message_json': json.dumps(msg_json_dict),
    }

    message_log_service.create(db_session=db_session, message_log_in=MessageLogCreate(**msg_info))

def save_to_message_log_all_7xxx(db_session, msg, msg_status="Success", type="SlabYard", message_id=None ,msg_json_dict=None, mill_id=410, is_repeat=0):
    if msg_json_dict is None:
        msg_json_dict = {}
    msg_info = {
        'message_id': message_id,
        'msg': msg,
        'message_status': msg_status,
        'interact': 'Slab Yard to MES',
        'message_json': json.dumps(msg_json_dict),
        'type': type,
        'mill_id': mill_id,
        'repeat_flag': is_repeat
    }

    message_log_service.create(db_session=db_session, message_log_in=MessageLogCreate(**msg_info))




def save_to_message_log(db_session, sap_type):
    msg_info = {
        'message_id': sap_type,
        'msg': f"{sap_type}sap message",
        'message_status': 'success',
        'interact': 'SAP to MES',
    }

    message_log_service.create(db_session=db_session, message_log_in=MessageLogCreate(**msg_info))


def save_to_message_log_all(db_session, sap_type, msg, msg_type, msg_json_dict={}):
    msg_info = {
        'message_id': sap_type,
        'msg': msg,
        'message_status': msg_type,
        'interact': 'SAP to MES',
        'message_json': json.dumps(msg_json_dict),
    }

    message_log_service.create(db_session=db_session, message_log_in=MessageLogCreate(**msg_info))


def create_advice_xml(db_session, advice, order_item, action):
    current_date = datetime.now().strftime('%Y%m%d')
    current_date_dmy = datetime.now().strftime('%d.%m.%Y')
    weight = sum(item.estimated_weight_kg or 0 for item in order_item) / 1000
    quantity = len(order_item)
    area = db_session.query(Area).filter(Area.id == advice.to_area_id).first()
    area_code = area.code if area else ""


    if advice.business_type == "service_center":
        root = ET.Element("DespatchDetails")
    else:
        root = ET.Element("MovementDetails")
    # 公共字段处理函数
    def add_common_elements(parent, elements):
        for name, text in elements:
            ET.SubElement(parent, name).text = str(text) if text is not None else ""

    if advice.business_type == "service_center":
        # Service Center 专用字段
        base_elements = [
            ("srcSys", "294TBM"), ("JourneyIdentifier", ""),
            ("SalesOrder", advice.order.order_code),  # 重要字段
            ("StockTransferOrder", ""), ("DeliveryFlag", "STO"),
            ("PlannedShippingDate", current_date), ("GIDate", current_date),
            ("PickingDate", current_date), ("LoadingDate", current_date),
            ("TransportIDName", ""), ("TransportIDNumber", ""),
            ("StartPoint", "8511RM13"), ("EndPoint", "PRAIRIE 5"),  # 固定值
            ("Location", "8407SC03"), ("ShipVesseIName", ""),
            #("SubLocation", area_code),
            ("Weight", f"{weight:.3f}"),
            ("WeightUnit", "TN"), ("ModeOfTransport", "01"),
            ("TransportOrderNo", ""), ("NoOfConsignments", "1")
        ]
        add_common_elements(root, base_elements)

        # 批次处理
        batches_group = group_batches(order_item)
        for oi_code, batches in batches_group.items():
            consignment = ET.SubElement(root, "ConsignmentDetails")
            consignment_elements = [
                ("OrderItem", oi_code),
                ("ConsignmentNo", advice.advice_code),
                ("NoOfBatches", len(batches))
            ]
            add_common_elements(consignment, consignment_elements)

            for batch in batches:
                batch_element = ET.SubElement(consignment, "BatchDetails")
                create_batch_nodes(batch_element, batch, is_service_center=True)

    else:
        # 其他业务类型处理
        ssrc = "700TBR" if advice.business_type != "BWS" else "700TBB"
        base_elements = [
            ("SSRC", ssrc), ("SalesOrder", advice.order.order_code),  # 重要字段
            ("StocktransferOrder", ""), ("Werks", advice.mill.code if advice.mill else ""),
            ("Action", action), ("ADC", ""), ("LocFrom", "MILL"),
            ("LocTo", "ROST" if advice.business_type == "Roster" else advice.business_type),
            #("AreaCode", advice.curr_area.code if advice.curr_area else ""),
            ("MVDate", current_date_dmy), ("Weight", f"{weight:.3f}"),
            ("WeightUnit", "TN"), ("TotPieces", quantity),
            ("PConNo", f"T{advice.advice_code}"),  # 重要字段
            ("ConNo", f"C{advice.advice_code}"), ("NoOfLines", quantity),
            ("Comment", advice.comment), ("SubLocn", area_code),
        ]
        add_common_elements(root, base_elements)

        # 批次处理
        batches_group = group_batches(order_item)
        order_item_node = ET.SubElement(root, "OrderItemDetails")
        for oi_code, batches in batches_group.items():
            item_elements = [
                ("OrderItem", oi_code),
                ("NoOfBatches", len(batches))
            ]
            add_common_elements(order_item_node, item_elements)

            for batch in batches:
                batch_element = ET.SubElement(order_item_node, "Batch")
                create_batch_nodes(batch_element, batch, is_service_center=False)

    # XML生成与请求
    tree = ET.ElementTree(root)
    ET.indent(tree, space="\t", level=0)  # 格式化输出
    xml = ET.tostring(root, pretty_print=True, encoding="utf-8", xml_declaration=True).decode()
    log.debug(xml)
    send_xml_request(db_session, xml, is_service_center=advice.business_type == "service_center")

    msg_info = {'message_id': 1, 'msg': xml, 'type': "xml", 'message_status': "Success", 'interact': 'MES to XML',
                'interact_from': 'MES', 'interact_to': 'XML', 'msg_type': 0}
    message_log_service.create(db_session=db_session, message_log_in=MessageLogCreate(**msg_info))
    return

# 提取的辅助函数
def group_batches(order_items):
    batches_group = defaultdict(list)
    for batch in order_items:
        if not batch.order_item:
            raise HTTPException(400, f"BatchID {batch.code} missing order_item")
        if not batch.mill:
            raise HTTPException(400, f"BatchID {batch.code} missing mill")
        batches_group[batch.order_item.line_item_code].append(batch)
    return batches_group


def create_batch_nodes(parent, batch, is_service_center):
    batch_type = "PCE" if batch.mill.code == 'TBM' else "BDL"
    elements = [
        ("BatchID", batch.code),
        ("BatchType", batch_type),
        ("Pieces", "0001"),
        #("INWeight", f"{(batch.estimated_weight_kg / 1000):.4f}" if batch.estimated_weight_kg else "0.000")
    ]

    if is_service_center:
        elements += [
            ("CastNo", batch.cast.cast_code if batch.cast_id else ""),
            ("Length", f"{batch.length_mm:.2f}" if batch.length_mm else 0),
            ("CalculatedWeight", f"{(batch.estimated_weight_kg / 1000):.4f}" if batch.estimated_weight_kg else "0.000"),
            ("WeightbridgeWeight", "0"),
            ("InlandCarriage", "0"),
            ("FOBCost", "0"),
            ("FreightCost", "0"),
            ("OnForwardCost", "0")
        ]
    else:
        elements += [
            #("SubLocn", batch.location or ""),
            ("Held", "H" if batch.hold_reason else "")
        ]

    for name, text in elements:
        ET.SubElement(parent, name).text = str(text)

def send_xml_request(db_session, xml, is_service_center=False):
    if is_service_center:
        url = f'{MESSAGE_URL_IS_SERVICE_CENTER_TRUE_START}+{uuid4()}+{MESSAGE_URL_IS_SERVICE_CENTER_TRUE_END}'
    else:
        url = f'{MESSAGE_URL_IS_SERVICE_CENTER_FALSE_START}+{uuid4()}+{MESSAGE_URL_IS_SERVICE_CENTER_FALSE_END}'
    headers = {
        'Content-Type': 'application/xml',  # 指定请求的内容类型为 XML
    }
    try:
        response = requests.post(url, data=xml, headers=headers)
        response.raise_for_status()  # 检查是否返回 HTTP 错误
        # log.info("Response:", response.text)  # 打印服务器响应
        log.info(f"Response: {response.text}")
        # log.info("Response: %s", response.text)
        # log.info("Response: {}".format(response.text))
    except requests.exceptions.RequestException as e:
        msg_info = {'message_id': 1, 'msg': xml, 'type': "xml", 'message_status': "Failed", 'interact': 'MES to XML',
                    'interact_from': 'MES', 'interact_to': 'XML', 'msg_type': 0}
        message_log_service.create(db_session=db_session, message_log_in=MessageLogCreate(**msg_info))
        raise HTTPException(status_code=400, detail="Failed to send POST request")


def push_message_data_read_dict(status="success", process=None):
    if process is None:
        process = []
    return {"status": status, "process": process}


def push_message_7001_service(db_session, data):
    """

    """

    piece = data.data["message"]["pieces"]["piece"]
    weight = float(piece.get('@actualQuantity', ""))
    # 提取需要的字段
    chars = {char["@name"]: char["value"] for char in piece.get("chars", {}).get("char", [])}

    semi_code = f"{chars.get('Cast_No', '')}-{chars.get('Strand_Number', '').lstrip('0')}{chars.get('Skelp_Letter', 'A')}{chars.get('Slab_Number', '1')}"

    dim_1 = float(chars.get('Section_Width', ''))
    dim_2 = float(chars.get('Section_Thick', ''))
    length = float(chars.get('Length', ''))
    width = float(chars.get('Width', ''))
    quality_code = chars.get('Grade_BOS_Qual', '')
    cast_code = chars.get('Cast_No', '')
    skelp_code = f"{chars.get('Strand_Number', '').lstrip('0')}{chars.get('Skelp_Letter', 'A')}{chars.get('Slab_Number', '1')}"

    message_log_dict = {
        "semi_code": semi_code,
        "dim_1": dim_1,
        "dim_2": dim_2,
        "length": length,
        "width": width,
        "quality_code": quality_code,
        "cast_code": cast_code,
        "skelp_code": skelp_code,
        'semi_type': 'Slab'
    }
    # 必填字段列表
    required_fields = [semi_code, cast_code]

    # 检查必填字段是否为空
    if any(not field for field in required_fields):
        save_to_message_log_all_7001(db_session=db_session, type=7001, msg_json_dict=message_log_dict,
                                     msg="Message semi_code and cast_code cannot be empty.", msg_status="Error")
        raise HTTPException(status_code=400, detail="semi_code and cast_code cannot be empty.")

    result = cast_service.get_by_code(db_session=db_session, code=cast_code)
    if not result:
        cast_data = {
            "updated_at": datetime.now(),
            "updated_by": f"{DEFAULT_EMAIL}",
            "created_at": datetime.now(),
            "created_by": f"{DEFAULT_EMAIL}",
            "bos_cast_code": f"6V{cast_code}",
            "cast_code": cast_code,
            "quality_code": "0218",
            "mill_id": 410,
        }
        new_cast = CastCreate(**cast_data)
        result = cast_service.create(db_session=db_session, cast_in=new_cast)

    cast_id = result.id
    semi_exist = get_semi_by_code(db_session=db_session, code=semi_code)
    # print(f"id: {id}, cast_code: {cast_code}")
    if semi_exist:
        save_to_message_log_all_7001(db_session=db_session, type=7001, msg_json_dict=message_log_dict,
                                     msg=f"semi_id: {semi_exist.id} (semi code: {semi_code}) is already exist.",
                                     msg_status="Error")
        raise HTTPException(status_code=400, detail=f"semi_id: {semi_exist.id} is already exist.")
    area_code = "SCU-Slab-Yard"
    site_code = "Slab-Yard"
    site_type_code = "MillStore"
    # 查询是否存在site type code 如果不存在那么创建一个
    site_type_one = site_type_service.get_site_type_by_code(db_session=db_session, code=site_type_code)
    if not site_type_one:
        site_type_service.create_site_type(db_session=db_session,
                                           # id 设置大一点 防止重复
                                           site_type_in=SiteTypeCreate(id=67592,
                                                                       code=site_type_code,
                                                                       type="s-semi",
                                                                       name=site_type_code,
                                                                       desc=site_type_code,
                                                                       )
                                           )
    # 获取其id
    site_type_one_id = site_type_service.get_site_type_by_code(db_session=db_session, code=site_type_code).id
    # 查询是否存在site code 如果不存在那么创建一个
    site_one = site_service.get_by_code(db_session=db_session, code=site_code)
    # print(f"site_type_one_id: {site_type_one_id}")
    if not site_one:
        site_service.create(db_session=db_session, site_in=SiteCreate(
            id=57592,
            code=site_code,
            name=site_code,
            desc=site_code,
            site_type_id=site_type_one_id,
        ))
    # 获取其id
    site_one_id = site_service.get_by_code(db_session=db_session, code=site_code).id
    # 查询是否存在area code 如果不存在 那就创建一个
    area_one = area_service.get_by_code(db_session=db_session, code=area_code)
    # print(f"site_one_id: {site_one_id}")
    if not area_one:
        area_service.create(db_session=db_session, area_in=AreaCreate(
            id=55212,
            code=area_code,
            type="s-semi",
            desc=area_code,
            site_id=site_one_id,
        ))
    # 获取其id
    area_one_id = area_service.get_by_code(db_session=db_session, code=area_code).id

    new_semi = Semi(
        semi_code=semi_code,
        dim1=dim_1,
        dim2=dim_2,
        quality_code=quality_code,
        cast_id=cast_id,
        length_mm=length,
        width_mm=width,
        estimated_weight_kg=weight,
        skelp_code=skelp_code,
        area_id=area_one_id,
        semi_type='Slab',
        thickness_mm=dim_2
    )

    insert_json_semi(db_session=db_session, semi_body=new_semi)

    update_cast_data = {
        "updated_at": datetime.now(),
        "updated_by": "sys",
        "created_at": datetime.now(),
        "created_by": "sys",
        "bos_cast_code": f"6V{cast_code}",
        "cast_code": cast_code,
        "quality_code": "0218",
        "mill_id": 410,
        "ch_c": 0.12575,
        "ch_si": 0.19075,
        "ch_mn": 1.476,
        "ch_p": 0.0165,
        "ch_s": 0.0025,
        "ch_s_p": None,
        "ch_cr": 0.01075,
        "ch_mo": 0.00325,
        "ch_ni": 0.01375,
        "ch_al": 0.0365,
        "ch_b": 0.000275,
        "ch_co": 0.00625,
        "ch_cu": 0.006,
        "ch_nb": 0.001,
        "ch_sn": 0.00175,
        "ch_ti": 0.001325,
        "ch_v": 0.09575,
        "ch_ca": 0.000125,
        "ch_n": 0.007075,
        "ch_o": None,
        "ch_h": 0.00022,
        "ch_solal": None,
        "ch_as": 0.00225,
        "ch_bi": 0.001,
        "ch_ce": None,
        "ch_pb": 0.001,
        "ch_sb": 0.0001,
        "ch_w": 0.000425,
        "ch_zn": None,
        "ch_zr": None,
        "ch_te": 0.001,
        "ch_rad": 0.02
    }

    save_to_message_log_all_7001(db_session=db_session, type=7001, msg_json_dict=message_log_dict,
                                 msg="Received a 7001 message!")

    cast_service.update(db_session=db_session, cast=result, cast_in=CastUpdate(**update_cast_data))
    return PushMessage7xxxDataRead(
        status=200,
        detail="Import Success!"
    )
    # except Exception as e:
    #     raise HTTPException(
    #         status_code=400,
    #         detail=f"Error: {str(e)}"
    #     )

def update_order_item_consignment(db_session, raw_body):
    xml_bytes = raw_body.strip()

    try:
        root = etree.fromstring(xml_bytes)
    except Exception as e:
        error_msg = "The xml can't be parsed."
        log.info(error_msg)
        log.info(xml_bytes.decode('utf-8'))
        raise Exception(e)

    sales_ord = root.findtext(".//SALES_ORD")
    if not sales_ord:
        raise Exception("sales order empty")
    elif len(sales_ord) == 6:
        sales_ord = sales_ord.rjust(10, '0')
    order_get = db_session.scalar(select(Order).where(Order.order_code == sales_ord))
    if not order_get:
        raise Exception(f"sales order {sales_ord} doesn't exist")
    order_id = order_get.id
    order_items = root.findall(".//OrderItemDetails")
    for order_item in order_items:
        line_item_code = order_item.findtext("OrderItem")
        consignment_code = order_item.findtext("Consignment")
        order_item_get = db_session.scalar(select(OrderItem).where(OrderItem.order_id == order_id).where(OrderItem.line_item_code == line_item_code))
        if order_item_get:
            order_item_get.consignment_code = consignment_code

    db_session.commit()

    return True


def update_order_item_for_sap_genesis(db_session, message_dict):
    
    ssrc = message_dict['MovementDetails']['SSRC']
    werks = message_dict['MovementDetails']['Werks']
    category = message_dict['MovementDetails']['Category']
    erdat = message_dict['MovementDetails']['Erdat']
    voyage = message_dict['MovementDetails']['VoyageNo']
    loading_port = message_dict['MovementDetails']['POL']
    destination_port = message_dict['MovementDetails']['POD']
    sales_ord = message_dict['MovementDetails']['SALES_ORD']
    delivery_date = datetime.strptime(erdat, '%Y%m%d')

    # Find sales order
    order_rec = db_session.scalar(select(Order).where(Order.order_code == sales_ord))

    if not sales_ord:
        raise Exception("sales order empty")
    elif len(sales_ord) == 6:
        sales_ord = sales_ord.rjust(10, '0')

    order_rec = db_session.scalar(select(Order).where(Order.order_code == sales_ord))
    if not order_rec:
        raise Exception(f"sales order {sales_ord} doesn't exist")
    order_id = order_rec.id

    mill_rec = db_session.scalar(select(Mill).where(Mill.code == werks))
    if not mill_rec:
        raise Exception(f"Mill {werks} doesn't exist")
    plant_id = mill_rec.id

    # Find order_items list and update
    order_items = message_dict['MovementDetails']['OrderItemDetails']
    for order_item_detail in order_items:
        line_item_code = order_item_detail['OrderItem']
        consignment_code = order_item_detail['Consignment']
        order_item_rec = db_session.scalar(select(OrderItem).where(OrderItem.order_id == order_id).where(OrderItem.line_item_code == line_item_code))
        if order_item_rec:
            order_item_rec.consignment_code = consignment_code
            order_item_rec.loading_port = loading_port
            order_item_rec.destination_port = destination_port
            order_item_rec.plant_id = plant_id
            order_item_rec.delivery_date = delivery_date
            order_item_rec.updated_at = datetime.now()
            if category == 'V':
                order_item_rec.v_voyage_no = voyage
                order_item_rec.v_port_of_loading = loading_port
                order_item_rec.v_port_of_destination = destination_port
            elif category == 'SR':
                order_item_rec.sr_voyage_no = voyage
                order_item_rec.sr_port_of_loading = loading_port
                order_item_rec.sr_port_of_destination = destination_port
            elif category == 'SP':
                order_item_rec.sp_voyage_no = voyage
                order_item_rec.sp_port_of_loading = loading_port
                order_item_rec.sp_port_of_destination = destination_port
    db_session.commit()

    return True


def parse_chars_275chm(xml_root):
    chars = xml_root.find('.//chars')
    char_dict = {}
    field_prefix = 'ch_'
    if chars is not None:
        for char in chars.iter('char'):
            name = '_'.join(char.get('name').lower().split(' '))
            char_dict[field_prefix + name] = {
                'value': try_float(str(char.findtext('value'))),
                'unit_name': char.findtext('unit_name'),
                'reporting_sequence': char.findtext('reporting_sequence'),
            }

    return char_dict



def create_cast(xml, db_session, sap_type):
    try:
        root = etree.fromstring(xml.strip())
        cast_code = root.findtext(".//header/cast_number")
        char_dict = parse_chars_275chm(root)
        if not char_dict:
            raise Exception(f"chars parsed failed.")
        cast_create_dict = {
            "cast_code": cast_code,
            "quality_code": char_dict.get("ch_aim_quality_code").get("value"),
            "generate_code": CAST_GENERATED_CODE,
            "ch_c": char_dict.get("ch_c").get("value"),
            "ch_si": char_dict.get("ch_si").get("value"),
            "ch_mn": char_dict.get("ch_mn").get("value"),
            "ch_p": char_dict.get("ch_p").get("value"),
            "ch_s": char_dict.get("ch_s").get("value"),
            "ch_cr": char_dict.get("ch_cr").get("value"),
            "ch_mo": char_dict.get("ch_mo").get("value"),
            "ch_ni": char_dict.get("ch_ni").get("value"),
            "ch_al": char_dict.get("ch_al").get("value"),
            "ch_b": char_dict.get("ch_b").get("value"),
            "ch_as": char_dict.get("ch_as").get("value"),
            "ch_co": char_dict.get("ch_co").get("value"),
            "ch_n": char_dict.get("ch_n").get("value"),
            "ch_cu": char_dict.get("ch_cu").get("value"),
            "ch_nb": char_dict.get("ch_nb").get("value"),
            "ch_sn": char_dict.get("ch_sn").get("value"),
            "ch_ti": char_dict.get("ch_ti").get("value"),
            "ch_v": char_dict.get("ch_v").get("value"),
            "ch_w": char_dict.get("ch_w").get("value"),
            "ch_bi": char_dict.get("ch_bi").get("value"),
            "ch_ca": char_dict.get("ch_ca").get("value"),
            "ch_sb": char_dict.get("ch_sb").get("value"),
            "ch_te": char_dict.get("ch_te").get("value"),
            "ch_h": char_dict.get("ch_h").get("value"),
            "ch_rad": char_dict.get("ch_rad").get("value"),
            "created_at": datetime.now(),
            "created_by": "sap_message",
            "updated_at": datetime.now(),
            "updated_by": "sap_message",
        }

        db_session.add(Cast(**cast_create_dict))
        db_session.commit()
    except Exception as e:
        error_msg = "sap 275 create cast failed."
        log.error(error_msg)
        log.error(f"error detail: {e}")
        log.error(f"xml detail: {xml.decode('utf-8')}")
        save_to_message_log_all(db_session, sap_type, error_msg, 'error')
        raise Exception(e)

    return True