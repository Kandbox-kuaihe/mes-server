import os
from datetime import datetime, date, UTC
from typing import List, Optional

import pandas as pd
from sqlalchemy import case, select
from sqlalchemy.orm import Session
from openpyxl.pivot.table import Location
from fastapi import HTTPException
from dispatch.rolling.rolling_list import service as rolling_service
from dispatch.order_admin.order_group import service as order_group_service
from dispatch.rolling.rolling_list.models import Rolling
from dispatch.semi_admin.semi_load import service as semi_load_service
try:
    from dispatch.contrib.import_data.semi.import_csv import map_semi_type
except ImportError as e:
    def map_semi_type():
        raise NotImplementedError("map_semi_type is not available because required modules are missing.")
from .models import Semi, SemiUpdate, SemiCreate, ReworkComplete
from dispatch.runout_admin.runout_list.models import Runout
from sqlalchemy import or_, func, and_
from dispatch.area.service import get_by_code as get_area_by_code
from dispatch.area.models import Area
from dispatch.cast import service as cast_service
from dispatch.order_admin.order_group.models import OrderGroup
from dispatch.system_admin.auth.models import DispatchUser
from dispatch.database import get_class_by_tablename
from ..semi_load.models import SemiLoadCreate, SemiLoad
from dispatch.semi_admin.semi_hold_reason.models_secondary import semi_hold
from dispatch.mill import service as mill_service
from ...cast.models import Cast
from ...config import MILLEnum
from ...spec_admin.quality.models import Quality


def get_by_semi_code_rolling_code(*, db_session, semi_code: str, rolling_code: str, area_code: str, group_code: str) -> \
List[Optional[Semi]]:
    """Returns an semi given an semi id."""
    return db_session.query(Semi.id).outerjoin(
        Rolling, Semi.rolling_id == Rolling.id
    ).filter(
        or_(Semi.semi_code.like(f'%{semi_code}%'), Rolling.rolling_code.like(f'%{rolling_code}%'))
    ).all() or db_session.query(Semi.id).outerjoin(
        Area, Semi.area_id == Area.id
    ).filter(
        or_(Semi.semi_code.like((f'%{semi_code}%')),
            Area.code.like(f'%{area_code}%')
            )
    ).all() or db_session.query(Semi.id).outerjoin(
        OrderGroup, Semi.order_group_id == OrderGroup.id
    ).filter(
        or_(Semi.semi_code.like((f'%{semi_code}%')),
            OrderGroup.group_code.like(f'%{group_code}%')
            )
        )


def get(*, db_session, semi_id: int) -> Optional[Semi]:
    """Returns an semi given an semi id."""
    return db_session.query(Semi).filter(Semi.id == semi_id).one_or_none()


def get_by_cast_id(*, db_session, cast_id: int) -> List[Optional[Semi]]:
    """Returns an semi given an semi id."""
    return db_session.query(Semi).filter(Semi.cast_id == cast_id).all()

def get_by_cast_id_and_type(*, db_session, cast_id: int, type: str) -> List[Optional[Semi]]:
    """Returns an semi given an semi id."""
    return db_session.query(Semi).filter(Semi.cast_id == cast_id, Semi.semi_type == type).all()

def get_one_cast_id(*, db_session, cast_id: int) -> List[Optional[Semi]]:
    """Returns an semi given an semi id."""
    return db_session.query(Semi).filter(Semi.cast_id == cast_id).first()

def get_by_rolling_id(*, db_session, rolling_id: int) -> List[Optional[Semi]]:
    """Returns an semi given a rolling id."""
    return db_session.query(Semi).filter(Semi.rolling_id == rolling_id).first()


def get_by_spec_ids(*, db_session, spec_ids: List[int]) -> List[Optional[Semi]]:
    """Returns an semi given an semi id."""
    return db_session.query(Semi).filter(Semi.spec_id.in_(spec_ids)).all()


def get_by_code(*, db_session, code: str) -> Optional[Semi]:
    """Returns an semi given an semi code address."""
    return db_session.query(Semi).filter(Semi.semi_code == code).one_or_none()


def get_by_code_mill(*, db_session, code: str, mill_id: int) -> Optional[Semi]:
    """Returns an semi given an semi code address."""
    return db_session.query(Semi).filter(and_(Semi.semi_code == code, Semi.mill_id == mill_id)).one_or_none()


def get_by_code_all(*, db_session, code: str) -> Optional[Semi]:
    """Returns an semi given an semi code address."""
    return db_session.query(Semi).filter(Semi.semi_code == code).all()


def get_default_semi(*, db_session) -> Optional[Semi]:
    """Returns an semi given an semi code address."""
    return db_session.query(Semi).first()


def get_semi_query(*, db_session, result_item):
    if result_item["items"]:
        for item in result_item["items"]:
            runout = db_session.query(Runout).filter(Runout.semi_id == item.id).first()
            if runout:
                item.runout_code = runout.runout_code
                item.runout_length = runout.runout_length

    return result_item


def get_all(*, db_session) -> List[Optional[Semi]]:
    """Returns all semis."""
    return db_session.query(Semi)


def get_hold_semi(*, db_session):
    """Returns all semis."""
    return db_session.query(semi_hold).all()


def create(*, db_session, semi_in: SemiCreate) -> Semi:
    """Creates an semi."""
    if semi_in.rolling:
        semi_in.rolling_id = semi_in.rolling.id
    if semi_in.area_code:
        area = db_session.query(Area).filter_by(code=semi_in.area_code).first()
        if area:
            semi_in.area_id = area.id
    if semi_in.order_group:
        semi_in.order_group_id = semi_in.order_group.id
    if semi_in.semi_load:
        semi_in.semi_load_id = semi_in.semi_load.id
    if semi_in.cast_code:
        cast = cast_service.get_by_code(db_session=db_session, code=semi_in.cast_code)
        if cast:
            semi_in.cast_id = cast.id
    contact = Semi(**semi_in.dict(
        exclude={"cast", "flex_form_data", "cast_code", "rolling", "rolling_code", "site", "area", "area_code", "mill",
                 "order_group", "semi_load","label_template","defect_reason","semi_hold_reason","quality"}), flex_form_data=semi_in.flex_form_data)
    db_session.add(contact)
    db_session.commit()
    return contact


def update(
        *,
        db_session,
        semi: Semi,
        semi_in: SemiUpdate,
) -> Semi:
    update_data = semi_in.dict(
        exclude={"flex_form_data", "rolling", "order_group", "site", "semi_load", "cast", "area", "mill", "label_template","semi_hold_reason",
                "defect_reason","quality"})
    for field, field_value in update_data.items():
        if field_value:
            setattr(semi, field, field_value)

    if semi_in.rolling:
        rolling = rolling_service.get(db_session=db_session, id=semi_in.rolling.id)
        semi.rolling_id = rolling.id if rolling else None
    if semi_in.order_group:
        order_group = order_group_service.get(db_session=db_session, id=semi_in.order_group.id)
        semi.order_group_id = order_group.id if order_group else None
    if semi_in.area_code:
        area = db_session.query(Area).filter_by(code=semi_in.area_code).first()
        semi_in.area_id = area.id if area else None
    if semi_in.semi_load:
        semi_load = semi_load_service.get(db_session=db_session, id=semi_in.semi_load.id)
        semi.semi_load_id = semi_load.id if semi_load else None
    if semi_in.cast_code:
        cast = cast_service.get_by_code(db_session=db_session, code=semi_in.cast_code)
        semi.cast_id = cast.id if cast else None

    semi.flex_form_data = semi_in.flex_form_data
    semi.updated_at = datetime.now(UTC)
    db_session.add(semi)
    db_session.commit()
    return semi


def delete(*, db_session, semi_id: int):
    semi = db_session.query(Semi).filter(Semi.id == semi_id).delete()
    db_session.commit()

    return semi


def bulk_get_semi(*, db_session, ids) -> List[Optional[Semi]]:
    return db_session.query(Semi).filter(Semi.id.in_(ids)).all()

def bulk_get_semi_by_codes(*, db_session, codes) -> List[Optional[Semi]]:
    return db_session.query(Semi).filter(Semi.semi_code.in_(codes)).all()

def get_area_location(*, db_session, semi_ids) -> Optional[Location]:
    res = db_session.query(Semi).filter(Semi.id.in_(semi_ids)).order_by(Semi.id.desc()).all()
    return res

def block_unblock_semi(db_session, semis_in):
    semi_body = []
    updated_at = datetime.now()
    max_charge_seq = 0
    # 查询数据库中semi_charge_seq的最大值
    for semi_data in semis_in:
        rolling_id = getattr(semi_data, "rolling_id", None)
        if rolling_id:
            max_charge_seq = db_session.query(func.max(Semi.semi_charge_seq)).filter(Semi.rolling_id == rolling_id).scalar() or 0

    area_08N=get_area_by_code(db_session=db_session, code= "08N")

    for semi_data in semis_in:
        semi_dict = semi_data.dict()
        semi_dict["updated_at"] = updated_at
        semi_dict.pop("semi_code", None)
        rolling_id = getattr(semi_data, "rolling_id", None)
        order_group_id = getattr(semi_data, "order_group_id", None)
        existing_charge_seq = semi_dict.get('semi_charge_seq')
        if rolling_id is None or order_group_id is None:
            semi_dict["semi_charge_seq"] = None
            if area_08N:
                semi_dict["area_id"] = area_08N.id if area_08N.id else None
        elif existing_charge_seq is not None:
            pass  # 已有semi_charge_seq值，不做任何修改
        else:
            max_charge_seq += 1
            semi_dict["semi_charge_seq"] = max_charge_seq

        semi_body.append(semi_dict)

    return update_semi_by_move(db_session=db_session, semi_body=semi_body)


def block_semi(db_session, semis_in):
    """
    Blocks the semis by assigning a unique `semi_charge_seq` for each rolling ID.
    """
    semi_body = []
    updated_at = datetime.now()
    max_charge_seq = 0
    # Get the max semi_charge_seq for each rolling_id
    for semi_data in semis_in:
        rolling_id = getattr(semi_data, "rolling_id", None)
        if rolling_id:
            max_charge_seq = db_session.query(func.max(Semi.semi_charge_seq)).filter(Semi.rolling_id == rolling_id).scalar() or 0

    for semi_data in semis_in:
        semi_dict["updated_at"] = updated_at
        semi_dict = semi_data.dict()
        semi_dict.pop("semi_code", None)
        rolling_id = getattr(semi_data, "rolling_id", None)
        order_group_id = getattr(semi_data, "order_group_id", None)
        existing_charge_seq = semi_dict.get('semi_charge_seq')

        if rolling_id is None or order_group_id is None:
            semi_dict["semi_charge_seq"] = None
        elif existing_charge_seq is not None:
            pass  # Keep existing semi_charge_seq
        else:
            max_charge_seq += 1
            semi_dict["semi_charge_seq"] = max_charge_seq

        semi_body.append(semi_dict)

    return update_semi_by_move(db_session=db_session, semi_body=semi_body)


def unblock_semi(db_session, semis_in):
    """
    Unblocks the semis by setting `semi_charge_seq` to None.
    """
    semi_body = []
    for semi_data in semis_in:
        semi_dict = semi_data.dict()
        semi_dict.pop("semi_code", None)
        semi_dict["semi_charge_seq"] = None  # Set charge sequence to None to unblock
        semi_body.append(semi_dict)

    return update_semi_by_move(db_session=db_session, semi_body=semi_body)


def reserve_unreserve_semi(db_session, semis_in):
    semi_body = []
    for semi_data in semis_in:
        semi_dict = semi_data.dict()
        semi_dict.pop("semi_code", None)
        rolling_id = getattr(semi_data, "rolling_id", None)
        reserved_order_group_id = getattr(semi_data, "order_group_id", None)
        semi_body.append(semi_dict)

    return update_semi_by_move(db_session=db_session, semi_body=semi_body)

def reserve_semi(db_session, semis_in):
    semi_body = []
    for semi_data in semis_in:
        semi_dict = semi_data.dict()
        semi_dict.pop("semi_code", None)
        semi_body.append(semi_dict)

    return update_semi_by_move(db_session=db_session, semi_body=semi_body)

def unreserve_semi(db_session, semis_in):
    semi_body = []
    for semi_data in semis_in:
        semi_dict = semi_data.dict()
        semi_dict.pop("semi_code", None)
        semi_body.append(semi_dict)

    return update_semi_by_move(db_session=db_session, semi_body=semi_body)


def update_semi_by_move(db_session, semi_body):
    try:
        db_session.bulk_update_mappings(Semi, semi_body)
        db_session.commit()
        return True
    except Exception as e:
        db_session.rollback()  # 如果更新失败，回滚事务
        raise e


def insert_json_semi(*, db_session, semi_body):
    try:
        db_session.add(semi_body)
        db_session.commit()  # 提交事务
        return semi_body
    except Exception as e:
        db_session.rollback()
        raise e


def update_rework(*, db_session, update_in, current_user: DispatchUser):
    resp = []
    history_in = []
    update_data = update_in.model_dump(exclude={'ids'})

    for id in update_in.ids:
        get_data = get(db_session=db_session, semi_id=id)
        for field, field_value in update_data.items():
            if field_value:
                setattr(get_data, field, field_value)
        get_data.rework_due_date = date.today()
        get_data.rework_status = 'Rework'
        db_session.add(get_data)
        resp.append(get_data)

    db_session.commit()

    return resp


def update_rework_complete(*, db_session, rework_complete_in: ReworkComplete):
    # tbm_mill = mill_service.get_by_code(db_session=db_session, code='TBM')
    tbm_mill = mill_service.get(db_session=db_session, mill_id=MILLEnum.MILL410)
    tbm_mill_id = tbm_mill.id if tbm_mill else None
    stmt = select(Area).where(Area.code == '30S', Area.type == 's-semi', Area.mill_id == tbm_mill_id)
    area_30s = db_session.scalar(stmt)
    area_30s_id = area_30s.id if area_30s else None

    stmt = select(Semi).where(Semi.id.in_(rework_complete_in.ids))
    for get_data in db_session.scalars(stmt):
        get_data.rework_finish_date = date.today()
        get_data.rework_type = 'Complete'
        get_data.rework_status = 'Complete'
        if get_data.mill_id == tbm_mill_id:
            get_data.area_id = area_30s_id
        if get_data.defect_reason_id:
            defect_reason_name = get_data.defect_reason.name
            get_data.defect_reason_id = None
            get_data.comment = f"{get_data.comment} Completed {defect_reason_name}"

    db_session.commit()

    return True


# 通过semi code 获取 cast id, 再找所有cast id下的semi code
def find_max_semi_code_by_cast(db_session, semi_code):
    semi_one = get_by_code(db_session=db_session, code=semi_code)
    if not semi_one:
        raise HTTPException(status_code=400, detail="Semi code not found！")
    cast_id = semi_one.cast_id
    if not cast_id:
        raise HTTPException(status_code=400, detail="Cast id code not found in Semi！")
    result = db_session.query(Semi.semi_code).filter(Semi.cast_id == cast_id).all()
    max_semi_code = max([i[0] for i in result])
    return max_semi_code


def sort_semi(common, order_group, dim_pairs):
    query = common.get("query", None)
    model = common.get("model", "Semi")
    db_session = common.get("db_session")
    if query is None:
        model_cls = get_class_by_tablename(model)
        query = db_session.query(model_cls)

    # 处理查询中是否包含 Area 模型
    model_cls = get_class_by_tablename(model)
    if order_group.rolling_id:
        rolling_id_sort_key = case(
                [
                    (Semi.rolling_id == order_group.rolling_id, 0),
                    (Semi.reserved_order_group_id == order_group.id, 1),
                 ],  # 如果 rolling_id 匹配，则排序优先级为 0
                else_ = 2  # 否则，排序优先级为 1
        )
    else:
        rolling_id_sort_key = case([(Semi.reserved_order_group_id == order_group.id, 1)])

    if dim_pairs:
        alt_sort_key = case(
            [
                ((Semi.dim1 == dim_pair[0]) & (Semi.dim2 == dim_pair[1]), idx + 1)
                for idx, dim_pair in enumerate(dim_pairs)
            ],
            else_=len(dim_pairs) + 2  # 默认将其它记录排到后面
        )
    else:
        alt_sort_key = None
    if common["query_str"]:
        query = query.filter(
            or_(
                model_cls.quality_code.like(f'%{common["query_str"]}%')
            )
        )
        common['query_str'] = ''

    if rolling_id_sort_key is not None and alt_sort_key is not None:
        sorted_query = query.order_by(rolling_id_sort_key, alt_sort_key)
    elif rolling_id_sort_key is not None:
        sorted_query = query.order_by(rolling_id_sort_key)
    elif alt_sort_key is not None:
        sorted_query = query.order_by(alt_sort_key)
    else:
        sorted_query = query

    common["query"] = sorted_query
    common["do_auto_join"] = True
    return common

def create_defects(*, db_session, data):
    defect_reason = data['defect_reason']
    defect_reason_id = defect_reason.get('id')
    if 'comment' in data:
        comment = data['comment']
    else:
        comment = None
    if 'defect_quantity' in data:
        defect_quantity = data['defect_quantity']
        if isinstance(defect_quantity, list) and defect_quantity:
            defect_quantity = defect_quantity[0]
        try:
            defect_quantity = int(defect_quantity)
        except (ValueError, TypeError):
            raise HTTPException(status_code=400, detail="Invalid defect_quantity value")
    else:
        defect_quantity = None
    code = data['codes']
    ids = data['ids']
    semi_list = db_session.query(Semi).filter(Semi.semi_code.in_(code)).all()
    add_list = []
    for semi_test in semi_list:
        current_defect_quantity = semi_test.defect_quantity or 0
        new_defect_quantity = current_defect_quantity + defect_quantity if defect_quantity is not None else current_defect_quantity
        add_list.append(
            {
                "id": semi_test.id,
                "defect_reason_id": defect_reason_id,
                "comment": comment,
                "defect_quantity": new_defect_quantity,
            }
        )
    db_session.bulk_update_mappings(Semi, add_list)
    db_session.commit()
    return True



def get_or_create_semi(db_session, semi_code):
    target_semi = get_by_code(db_session=db_session, code=semi_code)
    if target_semi:
        return target_semi
    else:
        semi_data = SemiCreate(semi_code=semi_code)
        new_semi = create(db_session=db_session, semi_in=semi_data)
        print(f"Target semi code: {semi_code} not found. Create new semi: {semi_code}.")
        return new_semi

def update_semi_scrap(*, db_session, semi, semi_in):
    semi.semi_status = 'Scrapped'
    semi_scrap_quantity = semi.scrap_quantity if semi.scrap_quantity else 0
    semi.scrap_quantity = semi_in.scrap_quantity + semi_scrap_quantity
    semi.defect_reason_id = semi_in.defect_reason_id
    semi.comment = semi_in.comment
    quantity = semi.quantity if semi.quantity is not None else 0
    scrap_quantity = semi_in.scrap_quantity if semi_in.scrap_quantity is not None else 0

    semi.quantity = int(quantity) - int(scrap_quantity)
    db_session.commit()
    return semi

def update_semi_return(*, db_session, semi_in):
    semi_obj = SemiLoadCreate()
    semi_obj.updated_at = semi_in.updated_at
    semi_obj.updated_by = semi_in.updated_by
    semi_load = semi_load_service.create(db_session=db_session, semi_load_in=semi_obj)
    db_session.add(semi_load)
    db_session.flush()
    semi_ids = semi_in.ids
    if semi_ids:
        db_session.query(Semi).filter(Semi.id.in_(semi_ids)).update({
            "semi_status": "Returned",
            "semi_load_id": semi_load.id,
            "area_id": None,
            "updated_at": semi_in.updated_at,
            "updated_by": semi_in.updated_by
        }, synchronize_session=False)
        db_session.commit()
    return True

try:
    from dispatch.contrib.message_admin.message_server.trigger_message_service import handle_m249

    def trigger_m249(
        *,
        db_session,
        semi_id: int,
        background_tasks,
    ):

        semi_get = db_session.get(Semi, semi_id)
        msg_in = {
            "order_group_number": semi_get.order_group.group_code if semi_get.order_group else "",
            "to_from": 0,
            "grid_id": "",
            "source": "",
            "pen_wagon": "",
            "cast_number": semi_get.cast_code,
            "cast_suffix": semi_get.cast_suffix,
            "size_code": "",
            "bloom_weight": int(semi_get.estimated_weight_kg) if semi_get.estimated_weight_kg else 0.0,
            "number_of_blooms": "",
            "cast_gen": semi_get.cast.generate_code if semi_get.cast else "",
        }
        handle_m249(db_session=db_session, msg_in=msg_in, background_tasks=background_tasks)
        return True
except ImportError as e:
    def trigger_m249():
        raise NotImplementedError("trigger_m249 is not available because required modules are missing.")


def semi_codes_exist(*, db_session, codes: List[str], mill_id: int) -> bool:
    """
    Checks if all codes in the list exist in the Semi table.
    Returns True if all codes exist, False otherwise.
    """
    if not codes:  # Handle empty list
        return False

    count = db_session.query(Semi).filter(Semi.semi_code.in_(codes), Semi.mill_id == mill_id).count()
    return count == len(codes)

def bulk_semi_update(db_session, semi_in_list: list[dict]):
    db_session.bulk_update_mappings(Semi, semi_in_list)
    db_session.commit()
    return True

def bulk_semi_insert(db_session, semi_in_list: list[dict]):
    db_session.bulk_update_mappings(Semi, semi_in_list)
    db_session.commit()
    return True


def bulk_semi_bloom_move(db_session, semi_in_list: list[dict]):
    semi_header = semi_in_list.pop(0)
    # 先处理第一个semi
    semi_header_object = get(db_session=db_session, semi_id=semi_header['id'])
    if not semi_header_object:
        raise HTTPException(status_code=400, detail=f"Semi(semi_id: {semi_header['id']}) not found!")
    semi_header_object.site_id = semi_header.get('site_id')
    semi_header_object.area_id = semi_header.get('area_id')
    semi_header_object.location = semi_header.get('location')
    semi_header_object.quantity = semi_header.get('quantity')
    semi_header_object.estimated_weight_kg = semi_header.get('estimated_weight_kg')
    semi_header_object.updated_at = datetime.now()
    db_session.add(semi_header_object)
    db_session.flush()

    def increment_last_char(s, num):
        # 获取最后一位
        last_char = s[-1]
        # 判断最后一位是数字
        if last_char.isdigit():
            new_last_char = int(last_char) + num
            # 如果加1后大于9，变成 10
            if new_last_char > 9:
                return s[:-1] + "0"  # 添加0变成10
            else:
                return s[:-1] + str(new_last_char)  # 否则正常递增
        else:
            raise HTTPException(status_code=400, detail=f"Semi code({s}) last char {last_char} is not a digit.")

    semi_code_prefix = semi_header_object.semi_code[:5]
    semi_list = db_session.query(Semi).filter(Semi.semi_code.like(f"{semi_code_prefix}%")).all()
    max_semi_code = max([semi.semi_code for semi in semi_list])
    flag = 0
    for new_semi in semi_in_list:
        flag += 1
        new_semi['semi_code'] = increment_last_char(s=max_semi_code, num=flag)
        new_semi['created_at'] = datetime.now()
    db_session.bulk_insert_mappings(Semi, semi_in_list)
    db_session.commit()

    return True


def compute_bloom_total(db_session: Session, cast_id: int, mill_id: int):
    return db_session.query(Semi).filter(
        and_(
            Semi.semi_type == 'BLM',
            Semi.cast_id == cast_id,
            Semi.mill_id == mill_id,
        )
    ).count()


def export_to_excel(*, db_session, data_list):
    """
    将 Semi 数据导出到 Excel 文件。

    :param db_session: 数据库会话
    :param data_list: 查询到的 Semi 数据列表
    :return: 生成的 Excel 文件路径
    """
    # 定义需要导出的字段
    export_fields = [
        "id", "rolling_id", "order_group_id", "reserved_order_group_id", "site_id", "product_type_id", "mill_id", "area_id",
        "semi_load_id", "spec_id", "semi_type", "semi_charge_seq", "cast_id", "semi_code", "stock_in_date", "quantity",
        "charge_seq", "location", "skelp_code", "semi_cut_seq", "semi_code_1", "quality_code", "length_mm", "width_mm",
        "thickness_mm", "estimated_weight_kg", "scarfed_status", "weight", "fit", "dim1", "dim2", "semi_status", "hold_reason",
        "comment", "defect_reason_id", "rework_type", "rework_status", "rework_due_date", "rework_finish_date",
        "rework_comment", "furnace_sequence_number", "De_Hydrogenise_Flag", "defs", "bloom_size_code", "supplier_code",
        "semi_supplier_code", "label_template_id", "defect_quantity", "section_code", "return_type", "track_code", "cast_code",
        "cast_suffix", "direction", "replacement_ind", "scrap_quantity", "quality_id", "generate_code", "long_semi_code"
    ]

    # 转换数据为字典列表
    data = []
    for item in data_list:
        row = {field: getattr(item, field) for field in export_fields}
        data.append(row)

    # 创建 DataFrame
    df = pd.DataFrame(data)

    # 格式化日期字段
    date_columns = ["stock_in_date", "rework_due_date", "rework_finish_date", "created_at", "updated_at"]
    for col in date_columns:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: x.strftime("%Y-%m-%d %H:%M:%S") if x else None)

    # 生成文件名和路径
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    # file_name = f"semi_export_{timestamp}.xlsx"
    file_name = f"semi_export_{timestamp}.csv"
    file_path = os.path.join("/tmp", file_name)  # 假设文件存储在 /tmp 目录下

    # 导出到 Excel
    try:
        # df.to_excel(file_path, index=False)
        df.to_csv(file_path, index=False)
    except Exception as e:
        raise RuntimeError(f"Failed to export Excel file: {str(e)}")

    return file_path

def import_dict_to_db_new(rows: list[dict], db_session, curr_user: str):
    """
    根据 export_to_excel 导出的字段格式，导入 Semi 数据。
    """
    # 定义需要处理的字段映射
    field_mapping = {
        "id": "id",
        "semi_code": "semi_code",
        "semi_type": "semi_type",
        "semi_status": "semi_status",
        "quantity": "quantity",
        "length_mm": "length_mm",
        "width_mm": "width_mm",
        "thickness_mm": "thickness_mm",
        "estimated_weight_kg": "estimated_weight_kg",
        "scarfed_status": "scarfed_status",
        "skelp_code": "skelp_code",
        "location": "location",
        "semi_charge_seq": "semi_charge_seq",
        "semi_cut_seq": "semi_cut_seq",
        "quality_code": "quality_code",
        "cast_code": "cast_code",
        "cast_suffix": "cast_suffix",
        "generate_code": "generate_code",
        "long_semi_code": "long_semi_code",
        "mill_id": "mill_id",
        "site_id": "site_id",
        "area_id": "area_id",
        "rolling_id": "rolling_id",
        "order_group_id": "order_group_id",
        "reserved_order_group_id": "reserved_order_group_id",
        "semi_load_id": "semi_load_id",
        "spec_id": "spec_id",
        "defect_reason_id": "defect_reason_id",
        "comment": "comment",
        "rework_type": "rework_type",
        "rework_status": "rework_status",
        "rework_due_date": "rework_due_date",
        "rework_finish_date": "rework_finish_date",
        "furnace_sequence_number": "furnace_sequence_number",
        "section_code": "section_code",
        "return_type": "return_type",
        "track_code": "track_code",
        "direction": "direction",
        "scrap_quantity": "scrap_quantity",
        "created_at": "created_at",
        "updated_at": "updated_at"
    }

    # 遍历每一行数据并进行预处理
    for row in rows:
        for key, value in row.items():
            if value == "" or value is None:
                row[key] = None
            elif key in {"cast_code", "skelp_code"}:
                row[key] = str(value)
            # 对特定字段进行类型转换
            elif key in {"mill_id", "area_id", "quantity", "semi_load_id", "generate_code",
                         "semi_charge_seq", "semi_cut_seq", "site_id", "order_group_id",
                         "reserved_order_group_id", "spec_id", "defect_reason_id"}:  # 数值类型字段
                try:
                    row[key] = int(value) if value else None
                except ValueError:
                    row[key] = None

        # 处理 semi_type 字段
        row['semi_type'] = map_semi_type(row.get("semi_type", "Slab"))

        # 处理日期字段
        date_fields = ["rework_due_date", "rework_finish_date", "created_at", "updated_at"]
        for date_field in date_fields:
            if row.get(date_field) and isinstance(row[date_field], str):
                try:
                    row[date_field] = datetime.strptime(row[date_field], "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    raise HTTPException(status_code=400, detail=f"Invalid date format for {date_field}")

        # 确保 rolling_id 是整数
        if row.get("rolling_id"):
            try:
                row["rolling_id"] = int(float(row["rolling_id"]))
            except (ValueError, TypeError):
                raise HTTPException(status_code=400, detail="Invalid value for rolling_id")

    # 更新或插入数据
    updated_rows = []
    for row in rows:
        # 根据相关代码反查外键 ID
        if row.get("rolling_code"):
            rolling = (
                db_session.query(Rolling)
                .filter(
                    Rolling.rolling_code == row["rolling_code"],
                    or_(Rolling.is_deleted == 0, Rolling.is_deleted == None),
                )
                .first()
            )
            row["rolling_id"] = rolling.id if rolling else None

        if row.get("order_group_code"):
            order_group = (
                db_session.query(OrderGroup)
                .filter(
                    OrderGroup.group_code == row["order_group_code"],
                    or_(OrderGroup.is_deleted == 0, OrderGroup.is_deleted == None),
                )
                .first()
            )
            row["order_group_id"] = order_group.id if order_group else None

        if row.get("area_code"):
            area = (
                db_session.query(Area)
                .filter(
                    Area.code == row["area_code"],
                    or_(Area.is_deleted == 0, Area.is_deleted == None),
                )
                .first()
            )
            row["area_id"] = area.id if area else None

        if row.get("semi_load_code"):
            semi_load = (
                db_session.query(SemiLoad)
                .filter(
                    SemiLoad.semi_load_code == row["semi_load_code"],
                    or_(SemiLoad.is_deleted == 0, SemiLoad.is_deleted == None),
                )
                .first()
            )
            row["semi_load_id"] = semi_load.id if semi_load else None

        updated_rows.append(row)

    # 批量更新或插入
    add_cnt, update_cnt = 0, 0
    for updated_row in updated_rows:
        existing_semi = db_session.query(Semi).filter(Semi.semi_code == updated_row["semi_code"]).first()
        if existing_semi:
            # 更新现有记录
            for field, value in updated_row.items():
                if field in field_mapping:
                    setattr(existing_semi, field_mapping[field], value)
            existing_semi.updated_by = curr_user
            existing_semi.updated_at = datetime.now()
            update_cnt += 1
        else:
            # 插入新记录
            semi = Semi(
                **{field_mapping[field]: value for field, value in updated_row.items() if field in field_mapping},
                created_by=curr_user,
                updated_by=curr_user,
            )
            db_session.add(semi)
            add_cnt += 1

    db_session.commit()
    return add_cnt, update_cnt


def import_cast_data(rows: list[dict], db_session, curr_user):
    """
    导入 Cast 数据。
    """

    field_mapping = {
        "SUPPLIER_CAST_ID": "long_cast_code",
        "GENERATION_CODE": "generate_code",
        "HEAT_ID": "cast_code",
        "QUALITY": "quality_code",
        "C": "ch_c",
        "Si": "ch_si",
        "Mn": "ch_mn",
        "P": "ch_p",
        "S": "ch_s",
        "Cr": "ch_cr",
        "Mo": "ch_mo",
        "Ni": "ch_ni",
        "Al": "ch_al",
        "B": "ch_b",
        "Co": "ch_co",
        "Cu": "ch_cu",
        "Nb": "ch_nb",
        "Sn": "ch_sn",
        "Ti": "ch_ti",
        "V": "ch_v",
        "Ca": "ch_ca",
        "H": "ch_h",
        "As": "ch_as",
        "Bi": "ch_bi",
        "Ce": "ch_ce",
        "O": "ch_o",
        "Pb": "ch_pb",
        "Sb": "ch_sb",
        "W": "ch_w",
        "Zn": "ch_zn",
        "Zr": "ch_zr",
        "Te": "ch_te",
        "Rad": "ch_rad",
        "INSAL": "ch_insal",
        "quality_id": "quality_id",
    }

    analyses_import_rows = [row for row in rows if row.get('sheet_name') == 'Anlyses Import']

    cast_add_cnt, cast_update_cnt = 0, 0
    for row in analyses_import_rows:
        plant_identifier = row.get("PLANT_IDENTIFIER", "")
        generation_code = row.get("GENERATION_CODE", "")
        heat_id = row.get("HEAT_ID", "")
        row["SUPPLIER_CAST_ID"] = f"{plant_identifier}{generation_code}{heat_id}"

        for key, value in row.items():
            if value == "" or value is None:
                row[key] = None
            elif key in {"HEAT_ID", "QUALITY"}:
                try:
                    row[key] = str(value) if value else None
                except ValueError:
                    row[key] = None

        if row.get("QUALITY"):
            quality = (
                db_session.query(Quality)
                .filter(
                    Quality.code == row["QUALITY"], Quality.mill_id == curr_user.current_mill_id,
                    or_(Quality.is_deleted == 0, Quality.is_deleted == None),
                )
                .first()

            )
            if not quality:
                raise HTTPException(status_code=400, detail=f"Quality code {row['QUALITY']} not found")
            row["quality_code"] = quality.code if quality else None
            row["quality_id"] = quality.id if quality else None

        existing_cast = db_session.query(Cast).filter(Cast.cast_code == row["HEAT_ID"]).first()
        if existing_cast:
            for field, value in row.items():
                if field in field_mapping:
                    setattr(existing_cast, field_mapping[field], value)
            existing_cast.updated_by = curr_user.email
            existing_cast.updated_at = datetime.now()
            cast_update_cnt += 1
        else:
            cast = Cast(
                **{field_mapping[field]: value for field, value in row.items() if field in field_mapping},
                created_by=curr_user.email,
                updated_by=curr_user.email,
                mill_id=curr_user.current_mill_id,
            )
            db_session.add(cast)
            cast_add_cnt += 1

    db_session.commit()
    return cast_add_cnt, cast_update_cnt


def import_semi_data(rows: list[dict], db_session, curr_user):
    """
    导入 Semi 数据。
    """
    field_mapping = {
        "SUPPLIER_CAST_ID": "semi_code",
        "GENERATION_CODE": "generate_code",
        "HEAT_ID": "cast_code",
        "PIECE_ID": "skelp_code",
        "LENGTH": "length_mm",
        "NOMINAL_WIDTH": "width_mm",
        "NOMINAL_THICKNESS": "thickness_mm",
        "WEIGHT": "estimated_weight_kg",
        "QUALITY_CODE": "quality_code",
        "NUMBER_OF_PIECES": "quantity",
        "cast_id": "cast_id",
        "quality_id": "quality_id",
    }

    semi_import_rows = [row for row in rows if row.get('sheet_name') == 'Semi Import']
    semi_add_cnt, semi_update_cnt = 0, 0
    for row in semi_import_rows:
        plant_identifier = row.get("PLANT_IDENTIFIER", "")
        generation_code = row.get("GENERATION_CODE", "")
        heat_id = row.get("HEAT_ID", "")
        row["SUPPLIER_CAST_ID"] = f"{plant_identifier}{generation_code}{heat_id}"

        for key, value in row.items():
            if value == "" or value is None:
                row[key] = None
            elif key in {"SUPPLIER_CAST_ID", "QUALITY_CODE", "HEAT_ID"}:
                try:
                    row[key] = str(value) if value else None
                except ValueError:
                    row[key] = None

        if row.get("HEAT_ID"):
            cast = (
                db_session.query(Cast)
                .filter(
                    Cast.cast_code == row["HEAT_ID"],
                    or_(Cast.is_deleted == 0, Cast.is_deleted == None),
                )
                .first()
            )
            row["cast_id"] = cast.id if cast else None
            row["cast_code"] = cast.cast_code if cast else None
            if not cast:
                raise HTTPException(status_code=400, detail=f"Semi Import {row['HEAT_ID']} not found")


        if row.get("QUALITY_CODE"):
            quality = (
                db_session.query(Quality)
                .filter(
                    Quality.code == row["QUALITY_CODE"],Quality.mill_id == curr_user.current_mill_id,
                    or_(Quality.is_deleted == 0, Quality.is_deleted == None),
                )
                .first()
            )
            row["quality_code"] = quality.code if quality else None
            row["quality_id"] = quality.id if quality else None
        existing_semi = db_session.query(Semi).filter(Semi.semi_code == row["SUPPLIER_CAST_ID"]).first()
        if existing_semi:
            for field, value in row.items():
                if field in field_mapping:
                    setattr(existing_semi, field_mapping[field], value)
            existing_semi.updated_by = curr_user.email
            existing_semi.updated_at = datetime.now()
            semi_update_cnt += 1
        else:
            semi = Semi(
                **{field_mapping[field]: value for field, value in row.items() if field in field_mapping},
                created_by=curr_user.email,
                updated_by=curr_user.email,
                mill_id=curr_user.current_mill_id,
            )
            db_session.add(semi)
            semi_add_cnt += 1

    db_session.commit()
    return semi_add_cnt, semi_update_cnt


def import_cast_semi_to_db(rows: list[dict], db_session, curr_user):
    """
    先导入 Cast 数据，再导入 Semi 数据。
    """
    cast_add_cnt, cast_update_cnt = import_cast_data(rows, db_session, curr_user)
    semi_add_cnt, semi_update_cnt = import_semi_data(rows, db_session, curr_user)
    return cast_add_cnt, cast_update_cnt, semi_add_cnt, semi_update_cnt
