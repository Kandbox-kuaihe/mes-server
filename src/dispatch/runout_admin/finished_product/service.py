from collections import defaultdict
from datetime import datetime, date
from typing import Optional, List
from decimal import Decimal
import uuid
import re

from sqlalchemy import select, and_, or_, func, desc, asc, cast, Integer
from fastapi import HTTPException

from dispatch.area.models import Area
from dispatch.cast.models import Cast
from dispatch.mill.service import get as mill_get_by_id
from dispatch.defect_reason.models import DefectReason
from dispatch.label_template.service import get as label_template_get_by_id
from dispatch.rolling.rolling_list.models import Rolling
from dispatch.runout_admin.advice.models import AdviceCreate, Advice
from dispatch.runout_admin.advice.service import create as advice_create, group_by_order
from dispatch.runout_admin.finished_product_load import service as finished_product_service
from dispatch.runout_admin.finished_product_history.models import FinishedProductHistoryChangeTypeEnum
from dispatch.runout_admin.finished_product_load.models import FinishedProductLoadCreate
from dispatch.spec_admin.spec.models import Spec
from dispatch.system_admin.auth.models import DispatchUser
from dispatch.tests_admin.test_sample.models import TestSample

from .models import (
    FinishedProduct,
    FinishedProductCreate,
    FinishedProductCreateLoad,
    FinishedProductUpdate,
    FinishedProductBySearch,
    FinishedProductAllocate,
    FinishedProductMultCreate,
    FinishedProductMultResponse,
    FinishedProductRepeatCreate,
    FinishedProductReworkComplete,
    FinishedProductHoldReason,
    ReturnUpdate
)

from dispatch.product_type.models import ProductType
from dispatch.product_size.models import ProductSize
from dispatch.runout_admin.holdreason.models_secondary import finished_product_hold
from dispatch.runout_admin.finished_product.models_secondary_load import finished_product_load
from dispatch.area.service import get as area_get_by_id
from dispatch.cast.service import get as cast_get_by_id
from dispatch.order_admin.order.service import get as order_get_by_id
from dispatch.order_admin.order_item.service import get as order_item_get_by_id
from dispatch.product_type.service import get as product_type_get_by_id
from dispatch.rolling.rolling_list.service import get as rolling_get_by_id
from dispatch.runout_admin.finished_product_history.service import bulk_create_finished_product_history
from dispatch.runout_admin.runout_list.service import get as runout_get_by_id
from dispatch.spec_admin.spec.service import get as spec_get_by_id

from dispatch.area import service as area_service
from dispatch.runout_admin.finished_product.enums import FinishedProductStatusEnum
from dispatch.rolling.cut_sequence_plan.models import CutSequencePlan
from dispatch.config import LOAD_AUTO_PLAN_TONNAGE, get_mill_ops, MILLEnum
from dispatch.config import HOLD_AGED_BAR_MONTH
from dateutil.relativedelta import relativedelta
from dispatch.runout_admin.holdreason import service as hold_service
from dispatch.spec_admin.spmainel.models import Spmainel as SpMainEl

from dispatch.log import getLogger
logger = getLogger(__name__)
try:
    from ...contrib.message_admin.message_server import server as message_server, server as MessageServer
except ImportError as e:
    logger.warning(f"ERROR in import message_server:{e}")
    pass
def get(*, db_session, id: int) -> Optional[FinishedProduct]:
    return db_session.get(FinishedProduct, id)


def get_by_code(*, db_session, code: str, mill_id:Optional[int]=None) -> Optional[FinishedProduct]:
    stmt = select(FinishedProduct).where(FinishedProduct.code == code)
    if mill_id:
        stmt = stmt.where(FinishedProduct.mill_id == mill_id)
    return db_session.scalars(stmt).one_or_none()

def get_by_codes(*, db_session, codes: list):
    stmt = select(FinishedProduct).where(FinishedProduct.code.in_(codes))
    return db_session.scalars(stmt)

def get_one_by_order_item_id(*, db_session, order_item_id: int)->Optional[FinishedProduct]:
    return db_session.query(FinishedProduct).filter(FinishedProduct.order_item_id == order_item_id).first()

def get_by_runout_id(*, db_session, runout_id: int) -> List[Optional[FinishedProduct]]:
    return db_session.query(FinishedProduct).filter(FinishedProduct.runout_id == runout_id).all()

def get_one_by_runout_id(*, db_session, runout_id: int) -> List[Optional[FinishedProduct]]:
    return db_session.query(FinishedProduct).filter(FinishedProduct.runout_id == runout_id).first()

def get_by_runout_id_mult_code(*, db_session, runout_id: int, mult_code: str) -> List[Optional[FinishedProduct]]:
    return db_session.query(FinishedProduct).filter(and_(FinishedProduct.runout_id == runout_id, FinishedProduct.mult_code == mult_code)).all()

def get_by_spec_id(*, db_session, id: int) -> List[Optional[FinishedProduct]]:
    """Returns an rolledPiece given an rolledPiece id."""
    return db_session.query(FinishedProduct).filter(FinishedProduct.spec_id == id).all()

def get_by_load_id(*, db_session, id: int) -> List[Optional[FinishedProduct]]:
    """Returns an rolledPiece given an rolledPiece id."""
    return db_session.query(FinishedProduct).filter(FinishedProduct.load_id == id).all()

def get_by_rolling_id(*, db_session, rolling_id: int) -> List[Optional[FinishedProduct]]:
    return db_session.query(FinishedProduct).filter(FinishedProduct.rolling_id == rolling_id).all()

def get_parent_children_bars(*, db_session, fp: FinishedProduct) -> List[Optional[FinishedProduct]]:
    result = []
    if not fp.mult_id:
        result = [fp]
    else:
        stmt_parent = select(FinishedProduct).where(FinishedProduct.id == fp.mult_id)
        parent = db_session.scalar(stmt_parent)
        if parent:
            result = [parent]
            stmt_children = select(FinishedProduct).where(FinishedProduct.mult_id == parent.id)
            children = db_session.scalars(stmt_children).all()
            if children:
                result += children
    
    return result


def create(*, db_session, finished_product_in: FinishedProductCreate) -> FinishedProduct:
    cast = None
    sec_cast = None
    runout = None
    rolling = None
    area = None
    spec = None
    order = None
    order_item = None
    product_type = None
    mill = None
    label_template = None

    if finished_product_in.cast_id:
        cast = cast_get_by_id(db_session=db_session, id=finished_product_in.cast_id)
    
    if finished_product_in.sec_cast_id:
        sec_cast = cast_get_by_id(db_session=db_session, id=finished_product_in.sec_cast_id)
    
    if finished_product_in.runout_id:
        runout = runout_get_by_id(db_session=db_session, runout_id=finished_product_in.runout_id)

    if finished_product_in.rolling_id:
        rolling = rolling_get_by_id(db_session=db_session, id=finished_product_in.rolling_id)
    
    if finished_product_in.area_id:
        area = area_get_by_id(db_session=db_session, area_id=finished_product_in.area_id)

    if finished_product_in.spec_id:
        spec = spec_get_by_id(db_session=db_session, id=finished_product_in.spec_id)

    if finished_product_in.order_id:
        order = order_get_by_id(db_session=db_session, order_id=finished_product_in.order_id)

    if finished_product_in.order_item_id:
        order_item = order_item_get_by_id(db_session=db_session, orderItem_id=finished_product_in.order_item_id)
    if finished_product_in.product_type_id:
        product_type = product_type_get_by_id(db_session=db_session, product_type_id=finished_product_in.product_type_id)

    if finished_product_in.mill_id:
        mill = mill_get_by_id(db_session=db_session, mill_id=finished_product_in.mill_id)

    if finished_product_in.label_template_id:
        label_template = label_template_get_by_id(db_session=db_session, label_template_id=finished_product_in.label_template_id)

    created = FinishedProduct(**finished_product_in.model_dump(
        exclude={"flex_form_data", "cast","sec_cast", "runout", "rolling", "area", "mill", "spec", "order", "order_item",
                 "codes","site_type_code","site_code","area_code","is_generate_comsi","advice","advice_id","product_type", "label_template","product_size"
                   }),
                              cast=cast,
                              sec_cast=sec_cast,
                              runout=runout,
                              rolling=rolling,
                              area=area,
                              mill=mill,
                              spec=spec,
                              order=order,
                              order_item=order_item,
                              flex_form_data=finished_product_in.flex_form_data,
                              product_type=product_type,
                              label_template=label_template
                              )
    db_session.add(created)
    db_session.commit()
    
    his = {
        "change_type": FinishedProductHistoryChangeTypeEnum.CREATE,
        "created_by": created.created_by,
        "mill_id": created.mill_id,

        "code": created.code,
        "cut_code": created.cut_code,
        "sawn_by": created.sawn_by,
        "rolling_code": rolling.rolling_code if rolling else None,
        "estimated_weight_kg": created.estimated_weight_kg,
        "length_mm": created.length_mm,
        "cast_no": cast.cast_code if cast else None,
        "spec_code": spec.spec_code if spec else None,
        "pass_tests": created.pass_tests,
        "location": created.location,
        "multed_with": created.multed_with,
        "runout_code": runout.runout_code if runout else None,
        "order_num": order.order_code if order else None,
        "product_type": created.product_type.code if product_type else None,
        "order_item_num": order_item.line_item_code if order_item else None,
        "onward": created.onward,
        "bundle": created.bundle,
        "alt_spec": created.alt_spec,
    }
    bulk_create_finished_product_history(db_session=db_session, finished_product_history_in=[his])

    return created

def extract_number_and_char(rolling_code):
    match = re.search(r'(\d+)([a-zA-Z]*)$', rolling_code)
    if match:
        number = int(match.group(1))
        letters = match.group(2)
        return number, letters
    return 0, ""

def compare_rolling_codes(rolling_code_1, rolling_code_2):
    part_1 = rolling_code_1.split('-')[-1]
    part_2 = rolling_code_2.split('-')[-1]

    number_1, letters_1 = extract_number_and_char(part_1)
    number_2, letters_2 = extract_number_and_char(part_2)

    if number_1 > number_2:
        return part_1
    elif number_1 < number_2:
        return part_2

    if letters_1 and letters_2:
        if letters_1 > letters_2:
            return part_1
        elif letters_1 < letters_2:
            return part_2
    elif letters_1:
        return part_1
    elif letters_2:
        return part_2

    return part_1

def update_finished_product_data(db_session, finished_product_id, rolling_ids, temp_code):
    finished_product_data = db_session.query(FinishedProduct).filter(FinishedProduct.id == finished_product_id).first()
    article_1 = ""
    article_2 = "G"
    article_3 = ""
    article_4 = ""
    if finished_product_data:
        product_type_data = db_session.query(ProductType).filter(
            ProductType.id == finished_product_data.product_type_id).first()
        if finished_product_data.code == temp_code:
            article_1 = f"{finished_product_data.id % 10000:04d}"
            if product_type_data:
                product_type_code = product_type_data.code
                product_type_code_parts = product_type_code.split('-')[:3]
                product_size_code = '-'.join(product_type_code_parts)
                product_size_data = db_session.query(ProductSize).filter(ProductSize.code == product_size_code).first()
                if product_size_data:
                    article_3 = product_size_data.roll_ref_code
        if rolling_ids:
            rolling_codes = []
            rolling_code_ids = []
            for rolling_id in rolling_ids:
                rolling_data = db_session.query(Rolling).filter(Rolling.id == rolling_id).first()
                if rolling_data:
                    rolling_codes.append(rolling_data.rolling_code)
                    rolling_code_ids.append(rolling_data.id)
                else:
                    print(f"Rolling with ID {rolling_id} not found.")
            if len(rolling_codes) == 2:
                article_4 = compare_rolling_codes(rolling_codes[0], rolling_codes[1])
            elif len(rolling_codes) == 1:
                article_4 = rolling_codes[0].split('-')[-1]

            code_parts = [article_1, article_2, article_3, article_4]
            code_parts = [part for part in code_parts if part]

            if code_parts:
                finished_product_data.code = "-".join(code_parts)  # 拼接 code
                db_session.commit()
        return  finished_product_data

def generate_sequence(n:int):
    """ 生成 A B C ... , AA, AB, AC ... """
    result = ""
    while n > 0:
        n -= 1  # 调整为0基索引
        result = chr(n % 26 + 65) + result
        n //= 26
    return result

def create_repeat(*, db_session, finished_product_in: FinishedProductRepeatCreate, current_user: DispatchUser):
    runout = runout_get_by_id(db_session=db_session, runout_id=finished_product_in.runout_id)
    if not runout:
        raise HTTPException(status_code=400, detail="The runout with this id does not exist.")
    runout_code = runout.runout_code
    for i in range(finished_product_in.repeat_num):
        ok_code, finished_code, cut_code  = False, runout_code, None
        for j in range(1, 1001):
            cut_code = generate_sequence(i+j)
            code = runout_code + cut_code
            if not get_by_code(db_session=db_session, code=code):
                ok_code = True
                finished_code = code
                break
        if not ok_code:
            raise HTTPException(status_code=400, detail="The code generate error ")
        fin_dic = finished_product_in.model_dump(exclude={"repeat_num"})
        fin = FinishedProductCreate(**fin_dic)
        fin.code = finished_code
        fin.cut_code = cut_code
        fin.created_by = current_user.email
        fin.updated_by = current_user.email
        fin.mill_id = current_user.current_mill_id
        fin.created_at = datetime.now()
        fin.updated_at = datetime.now()
        create(db_session=db_session, finished_product_in=fin)
    return True

def create_by_truncut(*, db_session, request_in: FinishedProductCreate) -> FinishedProduct:
    
    created = FinishedProduct(**request_in.model_dump(exclude={"flex_form_data", "cast","sec_cast", "runout", "rolling", "area", "mill", "spec", "order", "order_item",
                 "codes","site_type_code","site_code","area_code","is_generate_comsi","advice","advice_id","product_type", "label_template","product_size"
                   }))
    db_session.add(created)
    db_session.commit()

    return created


def update_finished(
        *,
        db_session,
        finished_product: FinishedProduct,
        finished_product_in: FinishedProductUpdate,
) -> FinishedProduct:
    cast = None
    runout = None
    rolling = None
    area = None
    spec = None
    order = None
    order_item = None
    product_type = None
    mill = None
    # advice = []
    label_template = None
    sec_cast = None

    if finished_product_in.cast_id:
        cast = cast_get_by_id(db_session=db_session, id=finished_product_in.cast_id)
    
    if finished_product_in.sec_cast_id:
        sec_cast = cast_get_by_id(db_session=db_session, id=finished_product_in.sec_cast_id)
    
    if finished_product_in.runout_id:
        runout = runout_get_by_id(db_session=db_session, runout_id=finished_product_in.runout_id)

    if finished_product_in.rolling_id:
        rolling = rolling_get_by_id(db_session=db_session, id=finished_product_in.rolling_id)
    
    if finished_product_in.area_id:
        area = area_get_by_id(db_session=db_session, area_id=finished_product_in.area_id)

    if finished_product_in.spec_id:
        spec = spec_get_by_id(db_session=db_session, id=finished_product_in.spec_id)

    if finished_product_in.order_id:
        order = order_get_by_id(db_session=db_session, order_id=finished_product_in.order_id)

    if finished_product_in.order_item_id:
        order_item = order_item_get_by_id(db_session=db_session, orderItem_id=finished_product_in.order_item_id)

    if finished_product_in.product_type_id:
        product_type = product_type_get_by_id(db_session=db_session, product_type_id=finished_product_in.product_type_id)

    if finished_product_in.mill_id:
        mill = mill_get_by_id(db_session=db_session, mill_id=finished_product_in.mill_id)

    # if finished_product_in.advice_id:
    #     advice = advice_get_by_id(db_session=db_session, id=finished_product_in.advice_id)

    if finished_product_in.label_template_id:
        label_template = label_template_get_by_id(db_session=db_session, label_template_id=finished_product_in.label_template_id)

    update_data = finished_product_in.model_dump(
        exclude={"id", "created_at", "created_by", "is_deleted", "flex_form_data","defect_reason","cast","sec_cast","runout","rolling","area","spec","order","order_item","advice", "mill"
                "codes","site_type_code","site_code","area_code","is_generate_comsi", "product_type","order_code", "order_item_code", "label_template","loads", "hold_reason","reserved_order_item","product_size"},
    )
    
    update_data['cast'] = cast 
    update_data['sec_cast'] = sec_cast
    update_data['runout'] = runout 
    update_data['rolling'] = rolling 
    update_data['area'] = area 
    update_data['spec'] = spec 
    update_data['order'] = order 
    update_data['order_item'] = order_item
    update_data['product_type'] = product_type
    update_data['mill'] = mill
    # update_data['advice'] = advice
    update_data['label_template'] = label_template

    for field, field_value in update_data.items():
        setattr(finished_product, field, field_value)

    finished_product.flex_form_data = finished_product_in.flex_form_data
    db_session.add(finished_product)
    db_session.commit()

    his = {
        "change_type": FinishedProductHistoryChangeTypeEnum.EDIT,
        "created_by": finished_product.created_by,
        "mill_id": finished_product.mill_id,

        "code": finished_product.code,
        "quantity": finished_product.quantity,
        "cut_code": finished_product.cut_code,
        "sawn_by": finished_product.sawn_by,
        "rolling_code": finished_product.rolling.rolling_code if finished_product.rolling else None,
        "estimated_weight_kg": finished_product.estimated_weight_kg,
        "length_mm": finished_product.length_mm,
        "cast_no": finished_product.cast.cast_code if finished_product.cast else None,
        "spec_code": finished_product.spec.spec_code if finished_product.spec else None,
        "pass_tests": finished_product.pass_tests,
        "location": finished_product.location,
        "multed_with": finished_product.multed_with,
        "runout_code": finished_product.runout.runout_code if finished_product.runout else None,
        "order_num": finished_product.order.order_code if finished_product.order else None,
        "product_type": finished_product.product_type.code if finished_product.product_type else None,
        "order_item_num": finished_product.order_item.line_item_code if finished_product.order_item else None,
        "onward": finished_product.onward,
        "bundle": finished_product.bundle,
        "alt_spec": finished_product.alt_spec,
    }
    bulk_create_finished_product_history(db_session=db_session, finished_product_history_in=[his])

    return finished_product


def delete(*, db_session, finished_product: FinishedProduct):
    finished_product.is_deleted = 1
    db_session.commit()

    his = {
        "change_type": FinishedProductHistoryChangeTypeEnum.DELETE,
        "created_by": finished_product.created_by,
        "mill_id": finished_product.mill_id,

        "code": finished_product.code,
        "cut_code": finished_product.cut_code,
        "sawn_by": finished_product.sawn_by,
        "rolling_code": finished_product.rolling.rolling_code if finished_product.rolling else None,
        "estimated_weight_kg": finished_product.estimated_weight_kg,
        "length_mm": finished_product.length_mm,
        "cast_no": finished_product.cast.cast_code if finished_product.cast else None,
        "spec_code": finished_product.spec.spec_code if finished_product.spec else None,
        "pass_tests": finished_product.pass_tests,
        "location": finished_product.location,
        "multed_with": finished_product.multed_with,
        "runout_code": finished_product.runout.runout_code if finished_product.runout else None,
        "order_num": finished_product.order.order_code if finished_product.order else None,
        "product_type": finished_product.product_type.code if finished_product.product_type else None,
        "order_item_num": finished_product.order_item.line_item_code if finished_product.order_item else None,
        "onward": finished_product.onward,
        "bundle": finished_product.bundle,
        "alt_spec": finished_product.alt_spec,
    }
    bulk_create_finished_product_history(db_session=db_session, finished_product_history_in=[his])
    
    return finished_product


def get_by_search(*, db_session, search_dict: FinishedProductBySearch):
    filter_conds = []
    if search_dict.cut_code:
        filter_conds.append(getattr(FinishedProduct, "cut_code") == search_dict.cut_code)

    if search_dict.kg:
        filter_conds.append(getattr(FinishedProduct, "kg") == search_dict.kg)

    if search_dict.rolling_no:
        rolling = db_session.query(Rolling).filter(Rolling.rolling_code == search_dict.rolling_no).first()
        if rolling:
            filter_conds.append(getattr(FinishedProduct, "rolling_id") == rolling.id)

    finished = db_session.query(FinishedProduct).filter(and_(*filter_conds)).first()
    if not finished:
        raise HTTPException(status_code=400, detail="The finished product with this id does not exist.")

    return finished


def get_finish_product_codes(*, db_session):
    """Returns all site type codes."""
    codes = [finish_product.stock_type for finish_product in db_session.query(FinishedProduct.stock_type).all()]
    return codes


def get_covering(*, db_session, runout_id: int, covering):
    runout = runout_get_by_id(db_session=db_session, runout_id=runout_id)
    if covering['items']:
        for item in covering['items']:
            item.rolling = runout.rolling
            item.rolling_id = runout.rolling_id
            item.test_result = int(f"{item.tensile_score if item.tensile_score else 0}{item.impact_score if item.impact_score else 0}")

    # if sort_key:
    #     covering['items'] = sorted(covering['items'], key=lambda x: x.spec.spec_code, reverse=True)
    #     covering['items'] = sorted(covering['items'], key=lambda x: x.test_result, reverse=True)
    # covering—info runout_id , spec_id , tensile_result , impact_result     1,1,9,8
    return covering


def batch_update(db_session, body):
    try:
        db_session.bulk_update_mappings(FinishedProduct, body)
        db_session.commit()
        history_in = []
        for item in body:

            fin = db_session.query(FinishedProduct).filter(FinishedProduct.id == item["id"]).first()

            history_in.append({
                "created_by": fin.updated_by,
                "change_type": FinishedProductHistoryChangeTypeEnum.REGRADE,
                'spec_code': fin.spec.spec_code if fin.spec else None,

                'mill_id': fin.mill_id,
                'code': fin.code,
                'rolling_code': fin.rolling.rolling_code if fin.rolling else None,
                'runout_code': fin.runout.runout_code if fin.runout else None,
                'area_code': fin.area.code if fin.area else None,
                'cast_no': fin.cast.cast_code if fin.cast else None,
                'order_num': fin.order.order_code if fin.order else None,
                'order_item_num': fin.order_item.line_item_code if fin.order_item else None,
                'product_type': fin.product_type.code if fin.product_type else None,
            })
        bulk_create_finished_product_history(db_session=db_session, finished_product_history_in=history_in)
        return True
    except Exception as e:
        db_session.rollback()  # 如果更新失败，回滚事务
        raise e


def get_max_cut_code(db_session, runout_id: int):
    stmt = select(
        FinishedProduct.code
    ).where(
        FinishedProduct.runout_id == runout_id,
        or_(
            FinishedProduct.mult_type != 'M',
            FinishedProduct.mult_type.is_(None)
        )
    ).order_by(
        desc(FinishedProduct.code)
    )
    max_code = db_session.scalar(stmt)

    return (max_code[:-1], max_code[-1]) if max_code else (None, None)

def get_max_mult_code(db_session, runout_id: int):
    stmt = select(
        FinishedProduct.mult_code
    ).where(
        FinishedProduct.runout_id == runout_id,
        FinishedProduct.mult_code != None
    ).order_by(
        desc(FinishedProduct.mult_code)
    )
    max_mult_code = db_session.scalar(stmt)

    return max_mult_code[1:] if max_mult_code else '0'

def get_max_mult_code_all(db_session):
    stmt = (
        select(FinishedProduct.mult_code)
        .where(FinishedProduct.mult_code != None)
        .order_by(cast(func.substring(FinishedProduct.mult_code, 2), Integer).desc())
        .limit(1)
    )

    max_mult_code = db_session.scalar(stmt)

    return int(max_mult_code[1:]) if max_mult_code else 0

def inset_hold_reason_list(db_session, current_user: DispatchUser, finished_product, hold_code):
    ''' 构建finished product hold 数据 '''
    hold_data = {}
    hold_reason = hold_service.get_by_code_mill(db_session=db_session, code=hold_code, mill_id=finished_product.mill_id)
    if not hold_reason:
        raise HTTPException(status_code=400, detail="Can't hold. Reason Aged_Bar not found")
    
    hold_data = {
                    "finished_product_id": finished_product.id,
                    "hold_reason_id": hold_reason.id,
                    "mill_id": finished_product.mill_id if finished_product.mill_id else None,
                    "hold_by": current_user.email,
                }
    return hold_data

def spec_cast_contrast(db_session, finished_product: FinishedProduct, spec: Spec):
    ''' spec 对比 cast '''
    spec_thickness = finished_product.product_type.flange_thickness if finished_product.product_type and finished_product.product_type.flange_thickness else 0
    cast = finished_product.cast
    spmainel = db_session.query(SpMainEl).filter(SpMainEl.type=='Main',
                                                 SpMainEl.spec_id == spec.id,
                                                 SpMainEl.thick_from < spec_thickness, 
                                                 spec_thickness < SpMainEl.thick_to,
                                                 SpMainEl.mill_id == finished_product.mill_id
                                                ).first()
    
    if not spmainel:
        raise HTTPException(status_code=400, detail="spmainel not found")
    
    for key in dir(cast):
        if key.startswith("ch_"):
            cast_key = key.split("ch_")[1]
            value = getattr(cast, key, None)

            smin = getattr(spmainel,f"main_el_min_value_{cast_key}", None)
            smax = getattr(spmainel,f"main_el_max_value_{cast_key}", None)

            if value is not None and smin is not None and smax is not None:
                if not (smin <= value <= smax):
                    raise  HTTPException(status_code=400, detail=f"未通过检测元素：{cast_key}, {cast_key}的值为：{float(value)}, {cast_key}的合格区间为：[{float(smin)}, {float(smax)}]" ) 
    return True

def create_mult(*, db_session, current_user: DispatchUser, mult_in: FinishedProductMultCreate, bundles, background_tasks):
    resp = FinishedProductMultResponse()

    his = []
    uid = uuid.uuid4()

    code_list = []
    spec = None

    allocation_status = bundles[0].allocation_status

    if mult_in.is_cover == True:
        if len(mult_in.regulars) >0:
            if mult_in.regulars[0].spec_code:
                spec = db_session.query(Spec).filter(Spec.spec_code == mult_in.regulars[0].spec_code).first()
        else:
            if mult_in.mult.spec_code:
                spec = db_session.query(Spec).filter(Spec.spec_code == mult_in.mult.spec_code).first()

    skip_cut_sample = False
    allocation_status_his = defaultdict(list)

    hold_list = []

    for mult_id in mult_in.ids:

        mult_finished_product = get(db_session=db_session, id=mult_id)

        from_spec_code = None
        from_allocation_status = mult_finished_product.allocation_status
        # if not mult_finished_product.spec and mult_finished_product.mill and mult_finished_product.mill.code == "SRSM":
        #     raise HTTPException(status_code=400, detail="Spec is required")

        # 当spec 为空时 对比 cast
        if not mult_finished_product.spec and mult_finished_product.mill and get_mill_ops(mult_finished_product.mill.id) == MILLEnum.MILL1:
            if mult_in.mult.spec_code:
                order_spec = db_session.query(Spec).filter(Spec.spec_code == mult_in.mult.spec_code).first()
            else:
                raise HTTPException(status_code=400, detail="Order without Spec")
            
            if not mult_finished_product.cast:
                raise HTTPException(status_code=400, detail="Finished Product without Cast")
            
            spec_cast_contrast(db_session=db_session, finished_product=mult_finished_product, spec=order_spec)

        if mult_finished_product.spec:
            from_spec_code=mult_finished_product.spec.spec_code

        # if mult_finished_product.mill and mult_finished_product.mill.code == "TBM":
        if mult_finished_product.mill and get_mill_ops(mult_finished_product.mill.id) == MILLEnum.MILL410:
            # created_at 超过12个月 增加hold
            now = datetime.now()
            twelve_months_ago = now - relativedelta(months=int(HOLD_AGED_BAR_MONTH))
            # 判断 created_at 是否超过 12 个月
            if mult_finished_product.created_at and mult_finished_product.created_at < twelve_months_ago:

                hold_data = inset_hold_reason_list(db_session=db_session,current_user=current_user,finished_product=mult_finished_product,hold_code="AGB")
                hold_list.append(hold_data)

        
        # srsm工厂，并且长度不等时，添加cut rework
        if mult_finished_product.mill and get_mill_ops(mult_finished_product.mill.id) == MILLEnum.MILL1 and mult_in.mult.length_mm != mult_finished_product.length_mm:
            if mult_finished_product.rework_type:
                rework_type_list = mult_finished_product.rework_type.split(",")
                if "CUT" not in rework_type_list:
                    rework_type_list.append("CUT")
                    mult_finished_product.rework_type = ",".join(rework_type_list)
            else:
                mult_finished_product.rework_type = "CUT"
                mult_finished_product.rework_due_date = date.today()
                mult_finished_product.rework_status = 'Rework'
            

        if mult_in.mult.allocation_status == "allocate":
            mult_in.mult.defect_reason_id = None
            mult_in.mult.status_change_reason = None
            # mult_in.mult.stock_type = None

            # srsm auto pass flag
            if mult_finished_product.mill and get_mill_ops(mult_finished_product.mill.id) == MILLEnum.MILL1:
                try:
                    from dispatch.contrib.cover.srsm import runout_services as srsm_runout_services
                    mult_finished_product.auto_pass = srsm_runout_services.get_auto_pass(spec, order=mult_finished_product.order)
                except ImportError as e:
                    raise HTTPException(status_code=400, detail=str(e))

        if mult_in.mult.allocation_status == "free_stock":
            mult_in.mult.order_id = None
            mult_in.mult.order_item_id = None
            mult_in.mult.defect_reason_id = None
            # mult_in.mult.stock_type = None

        if mult_in.mult.allocation_status == "scrap":
            mult_in.mult.order_id = None
            mult_in.mult.order_item_id = None
            mult_in.mult.status_change_reason = None
            mult_in.mult.stock_type = "scrap"
            mult_finished_product.status = "scrapped"

            allocated_length = Decimal(mult_in.mult.length_mm)
            if allocated_length > mult_finished_product.length_mm:
                raise HTTPException(status_code=400, detail="Allocated length is greater than the available length.")
            
            mult_finished_product.length_mm = mult_finished_product.length_mm - allocated_length
            # srsm scrap时记录scrap quantity
            if mult_finished_product.mill and get_mill_ops(mult_finished_product.mill.id) == MILLEnum.MILL1:
                mult_in.mult.scrap_quantity = mult_finished_product.scrap_quantity + mult_in.mult.quantity if mult_finished_product.scrap_quantity else mult_in.mult.quantity
                if mult_in.mult.quantity > mult_finished_product.quantity:
                    raise HTTPException(status_code=400, detail="Scrap Quantity is greater than Quantity.")
                mult_in.mult.quantity = mult_finished_product.quantity - mult_in.mult.quantity

        mult_exclude_dict = {"length_mm", "defective_length", "spec_code", "advice", "compliance", "waste"}
        if (
            (mult_finished_product.mill and get_mill_ops(mult_finished_product.mill.id) == MILLEnum.MILL410 and mult_in.mult.allocation_status != "allocate") or
            (mult_finished_product.mill and get_mill_ops(mult_finished_product.mill.id) == MILLEnum.MILL1 and mult_in.mult.allocation_status not in ["allocate", "scrap"])
        ):
            mult_exclude_dict.add("quantity")

        update_data = mult_in.mult.model_dump(exclude=mult_exclude_dict)
        for field, field_value in update_data.items():
            setattr(mult_finished_product, field, field_value)

        if mult_in.mult.allocation_status == "free_stock":
            mult_finished_product.orig_length_mm = mult_finished_product.length_mm
            mult_finished_product.length_mm = mult_in.mult.length_mm
            mult_finished_product.defective_length = mult_in.mult.defective_length

        max_mult_code = get_max_mult_code(db_session,mult_finished_product.runout_id)
        
        if len(mult_in.regulars)>=1:
            mult_finished_product.mult_type = 'M'
            mult_finished_product.mult_code = f"M{int(max_mult_code)+1}"
        mult_finished_product.exist_flag = 'Y'

        mult_finished_product.updated_at = datetime.now()
        mult_finished_product.updated_by = current_user.email
        mult_finished_product.mult_datetime = datetime.now()
        if spec:
            mult_finished_product.spec = spec

        db_session.add(mult_finished_product)
        his.append({
            "allocation_status": mult_finished_product.allocation_status,
            "from_allocation_status": from_allocation_status,
            "mult_code": mult_finished_product.mult_code,
            "mult_type": mult_finished_product.mult_type,
            "exist_flag": mult_finished_product.exist_flag,
            "waste_length": mult_finished_product.waste_length,
            "status_change_reason": mult_finished_product.status_change_reason,
            "comment": mult_finished_product.comment,
            "length_mm": mult_finished_product.length_mm,
            "defect_reason": mult_finished_product.defect_reason.name if mult_finished_product.defect_reason else None,
            "allocate_reason": mult_finished_product.allocate_reason,
            "quantity": mult_finished_product.quantity,
            "estimated_weight_kg": mult_finished_product.estimated_weight_kg,

            'created_by': current_user.email,
            'mill_id': mult_finished_product.mill_id,
            'change_type': FinishedProductHistoryChangeTypeEnum.ALLOCATE,
            'uuid': uid,
            'code': mult_finished_product.code,
            'rolling_code': mult_finished_product.rolling.rolling_code if mult_finished_product.rolling else None,
            'runout_code': mult_finished_product.runout.runout_code if mult_finished_product.runout else None,
            'area_code': mult_finished_product.area.code if mult_finished_product.area else None,
            'cast_no': mult_finished_product.cast.cast_code if mult_finished_product.cast else None,
            'spec_code': mult_finished_product.spec.spec_code if mult_finished_product.spec else None,
            'order_num': mult_finished_product.order.order_code if mult_finished_product.order else None,
            'order_item_num': mult_finished_product.order_item.line_item_code if mult_finished_product.order_item else None,
            'product_type': mult_finished_product.product_type.code if mult_finished_product.product_type else None,
        })

        allocation_status_his[mult_id].append(
            dict(from_allocation_status=from_allocation_status, 
                    allocation_status=mult_in.mult.allocation_status,
                    from_spec_code=from_spec_code,
                    spec_code=mult_in.mult.spec_code,
                    )
        )
        # resp.mult = mult_finished_product
        # resp.regulars = []

        # 判读 regulars 是否有值，是否需要切多分 Mults
        if len(mult_in.regulars)>=1:
            allocation_status_his.clear()
            runout_code, max_cut_code = get_max_cut_code(db_session, mult_finished_product.runout_id)
            
            cut_number = 0
            
            for index, regular in enumerate(mult_in.regulars):
                allocation_status_his[mult_id].append(
                    dict(from_allocation_status=from_allocation_status,
                            allocation_status=regular.allocation_status
                            )
                )
                if regular.allocation_status == "scrap" or regular.allocation_status == "free_stock":
                    continue

                regular_spec = None

                cut_number += 1
                regular_finished_product_in = FinishedProductCreate(**mult_finished_product.__dict__)


                if regular.spec_code:
                    regular_spec = db_session.query(Spec).filter(Spec.spec_code == regular.spec_code).first()

                # 当为第一条的时候对原选择的finished product 进行修改
                if index == 0:
                    regular_finished_product_in.code = mult_finished_product.code
                    mult_finished_product.code = mult_finished_product.code + '-' + mult_finished_product.mult_code
                    regular_finished_product_in.cut_code = regular_finished_product_in.code[-1]
                else:
                    cut_code = chr(ord(max_cut_code) + cut_number) if max_cut_code else ''
                    regular_finished_product_in.code = runout_code + cut_code if runout_code else None
                    regular_finished_product_in.cut_code = cut_code

                

                if regular.allocation_status == "allocate":
                    regular.defect_reason_id = None
                    regular.status_change_reason = None
                    regular.stock_type = None
                
                # if regular.allocation_status == "free_stock":
                #     regular.order_id = None
                #     regular.order_item_id = None
                #     regular.defect_reason_id = None
                #     regular.stock_type = None

                # if regular.allocation_status == "scrap":
                #     regular.order_id = None
                #     regular.order_item_id = None
                #     regular.status_change_reason = None
                #     regular.stock_type = "scrap"

                update_data = regular.model_dump(exclude={"spec_code", "compliance", "waste"})
                for field, field_value in update_data.items():
                    setattr(regular_finished_product_in, field, field_value)

                
                regular_finished_product_in.mult_type = 'R'
                regular_finished_product_in.exist_flag = 'N'
                
                regular_finished_product_in.mult_id = mult_finished_product.id
                regular_finished_product_in.mult_code = None
                regular_finished_product_in.waste_length = None

                regular_finished_product_in.created_by = current_user.email
                regular_finished_product_in.updated_by = current_user.email
                regular_finished_product_in.created_at = datetime.now()
                regular_finished_product_in.updated_at = datetime.now()

                
                regular_finished_product = FinishedProduct(**regular_finished_product_in.model_dump(exclude={
                    "flex_form_data",
                    "cast",
                    "sec_cast",
                    "runout",
                    "rolling",
                    "area",
                    "spec",
                    "order",
                    "order_item",
                    "cast_code",
                    "runout_code",
                    "rolling_code",
                    "area_code",
                    "spec_code",
                    "order_code",
                    "order_item_code",
                    "codes",
                    "site_type_code",
                    "site_code",
                    "area_code",
                    "is_generate_comsi",
                    "product_type",
                    "advice",
                    "loads",
                    "label_template",
                    "defect_reason",
                    "regrade_reason",
                    "hold_reason",
                    "mill"
                },exclude_unset=True,),spec=regular_spec,advice=mult_finished_product.advice,loads=mult_finished_product.loads)

                code_list.append(regular_finished_product.code)

                
                db_session.add(regular_finished_product)
                
                # resp.regulars.append(regular_finished_product)

                his.append({
                    "allocation_status": regular_finished_product.allocation_status,
                    "mult_code": regular_finished_product.mult_code,
                    "mult_type": regular_finished_product.mult_type,
                    "exist_flag": regular_finished_product.exist_flag,
                    "waste_length": regular_finished_product.waste_length,
                    "status_change_reason": regular_finished_product.status_change_reason,
                    "comment": regular_finished_product.comment,
                    "length_mm": regular_finished_product.length_mm,
                    "defect_reason": regular_finished_product.defect_reason.name if regular_finished_product.defect_reason else None,
                    "allocate_reason": regular_finished_product.allocate_reason,
                    "quantity": regular_finished_product.quantity,
                    "estimated_weight_kg": regular_finished_product.estimated_weight_kg,

                    'created_by': current_user.email,
                    'mill_id': regular_finished_product.mill_id,
                    'change_type': FinishedProductHistoryChangeTypeEnum.MULT,
                    'uuid': uid,
                    'code': regular_finished_product.code,
                    'rolling_code': regular_finished_product.rolling.rolling_code if regular_finished_product.rolling else None,
                    'runout_code': regular_finished_product.runout.runout_code if regular_finished_product.runout else None,
                    'area_code': regular_finished_product.area.code if regular_finished_product.area else None,
                    'cast_no': regular_finished_product.cast.cast_code if regular_finished_product.cast else None,
                    'spec_code': regular_finished_product.spec.spec_code if regular_finished_product.spec else None,
                    'order_num': regular_finished_product.order.order_code if regular_finished_product.order else None,
                    'order_item_num': regular_finished_product.order_item.line_item_code if regular_finished_product.order_item else None,
                    'product_type': regular_finished_product.product_type.code if regular_finished_product.product_type else None,
                })

        is_sample = (
            db_session.query(TestSample)
            .filter(
                TestSample.runout_id == mult_finished_product.runout_id,
                # TestSample.finished_product_id == mult_finished_product.id,
                or_(TestSample.status == 'A', TestSample.status == 'C')
            )
            .first()
        )
        if is_sample:
            skip_cut_sample = True

    if len(hold_list)>0:
        db_session.execute(finished_product_hold.insert(), hold_list)
    db_session.commit()

    if mult_in.mult.cut_sample_length_mm == 500 and not skip_cut_sample:
        from dispatch.runout_admin.finished_product.views import cut_sample
        from dispatch.runout_admin.finished_product.models import CutTestSample

        cut_sample(background_tasks=background_tasks, db_session=db_session, Finished_in=CutTestSample(finished_ids=mult_in.ids), source='Allocate',current_user=current_user)

    bulk_create_finished_product_history(db_session=db_session, finished_product_history_in=his)
    #if allocation_status == "free_stock" or "scrap" or "Free Stock" or "Scrap" or None or "" and mult_finished_product.allocation_status == "allocate" or "Allocated":
    try:
        from ...contrib.message_admin.message_server import server as message_server, server as MessageServer

        if (allocation_status == "free_stock" or allocation_status == "scrap" or allocation_status == "Free Stock" or allocation_status == "Scrap" or allocation_status is None or allocation_status == "") and (mult_finished_product.allocation_status == "allocate" or mult_finished_product.allocation_status == "Allocated"):
            if get_mill_ops(mult_finished_product.mill_id) == MILLEnum.MILL1:
                try:
                    message_server = MessageServer.MessageStrategyRSVDSRSM()
                    message_server.handle(db_session=db_session, target_finished_product=mult_finished_product, target_finished_products=his, background_tasks=background_tasks, flag="A", current_mill_code=current_user.current_mill_code)
                except Exception as e:
                    logger.error(f"ERROR sending RSVDSRSM: {e}")
            else:
                try:
                    message_server = MessageServer.MessageStrategy215()
                    message_server.send_pc_215(db_session=db_session, target_finished_product=mult_finished_product, background_tasks=background_tasks, current_mill_code=current_user.current_mill_code)
                except Exception as e:
                    logger.error(f"ERROR in send_pc_215: {e}")
        #elif allocation_status == "allocate" or "Allocated" and mult_finished_product.allocation_status == "free_stock" or "scrap" or "Free Stock" or "Scrap":
        elif (allocation_status == "allocate" or allocation_status == "Allocated") and (mult_finished_product.allocation_status == "free_stock" or mult_finished_product.allocation_status == "scrap" or mult_finished_product.allocation_status == "Free Stock" or mult_finished_product.allocation_status == "Scrap"):
            if get_mill_ops(mult_finished_product.mill_id) != MILLEnum.MILL1:
                try:
                    message_server = MessageServer.MessageStrategy210()
                    message_server.send_pc_210(db_session=db_session, target_finished_product=mult_finished_product, background_tasks=background_tasks, current_mill_code=current_user.current_mill_code)
                except Exception as e:
                    logger.error(f"ERROR in send_pc_210: {e}")
    except ImportError as e:
        raise HTTPException(status_code=400, detail=str(e))
    try:
        check_and_trigger_rework(db_session, allocation_status_his, background_tasks=background_tasks, hist_uid=str(uid))
    except:
        logger.exception('Error preparing MFGI404 Rework message')
    return resp


def check_and_trigger_rework(db_session, allocation_status_his: dict, background_tasks, hist_uid: str):
    try:
        import dispatch.contrib.message_admin.message_server.trigger_sap_message as sap_strategy
        for fp_id, status_his in allocation_status_his.items():
            if len(status_his) == 1 and status_his[0]['allocation_status'] == 'allocate' and status_his[0]['from_spec_code'] != status_his[0]['spec_code']:
                sap_strategy.handle_mfgi182(db_session, finished_product_id=fp_id, action_e=sap_strategy.MFGI182_ACTION.BATCHCHARUPD, background_tasks=background_tasks, hist_uid=hist_uid)
            elif len(status_his) > 1:
                sap_strategy.handle_mfgi182(db_session, finished_product_id=fp_id, action_e=sap_strategy.MFGI182_ACTION.REWORK, background_tasks=background_tasks, hist_uid=hist_uid)
    except ImportError as e:
        raise HTTPException(status_code=400, detail=str(e))

def check_and_trigger_rework_rebundle(db_session, background_tasks, org_fp_ids=None, new_fp_ids=None):
    # One Rework message per original finished product
    try:
        import dispatch.contrib.message_admin.message_server.trigger_sap_message as sap_strategy
        for org_fp_id in org_fp_ids:
            sap_strategy.handle_mfgi182(db_session, finished_product_id=org_fp_id, action_e=sap_strategy.MFGI182_ACTION.REWORK, background_tasks=background_tasks, new_finished_product_ids=new_fp_ids)
    except ImportError as e:
        raise HTTPException(status_code=400, detail=str(e))

def allocate_change_type(*, db_session, finished_product_in: FinishedProductAllocate, current_user: DispatchUser):
    finisheds = db_session.query(FinishedProduct).filter(FinishedProduct.id.in_(finished_product_in.finished_ids))
    
    his = []
    uid = uuid.uuid4()
    if finished_product_in.select_type == 'order':
        
        if not finished_product_in.order_id or not finished_product_in.order_item_id:
            raise HTTPException(status_code=400, detail="order no and order item no is required.")
        
        order = order_get_by_id(db_session=db_session, order_id=finished_product_in.order_id)
        order_item = order_item_get_by_id(db_session=db_session, orderItem_id=finished_product_in.order_item_id)

        for finished in finisheds:
            finished.defect_reason = None
            finished.stock_type = None
            finished.status_change_reason = None
            finished.order = order
            finished.order_item = order_item
            
            his.append({
                "allocation_status": finished_product_in.select_type,
                "order_id": finished.order_id,
                "order_item_id": finished.order_item_id,

                'created_by': current_user.email,
                'mill_id': finished.mill_id,
                'change_type': FinishedProductHistoryChangeTypeEnum.ALLOCATE,
                'uuid': uid,
                'code':finished.code,
                'rolling_code': finished.rolling.rolling_code if finished.rolling else None,
                'runout_code': finished.runout.runout_code if finished.runout else None,
                'area_code': finished.area.code if finished.area else None,
                'cast_no': finished.cast.cast_code if finished.cast else None,
                'spec_code': finished.spec.spec_code if finished.spec else None,
                'order_num': finished.order.order_code if finished.order else None,
                'order_item_num': finished.order_item.line_item_code if finished.order_item else None,
                'product_type': finished.product_type.code if finished.product_type else None,
            })
            

    if finished_product_in.select_type == 'free_stock':

        if not finished_product_in.status_change_reason:
            raise HTTPException(status_code=400, detail="status change reason is required.")

        for finished in finisheds:
            finished.order = None
            finished.order_item = None
            finished.defect_reason = None
            finished.stock_type = None
            finished.status_change_reason = finished_product_in.status_change_reason
            
            his.append({
                "allocation_status": finished_product_in.select_type,
                "status_change_reason": finished_product_in.status_change_reason,

                'created_by': current_user.email,
                'mill_id': finished.mill_id,
                'change_type': FinishedProductHistoryChangeTypeEnum.ALLOCATE,
                'uuid': uid,
                'code': finished.code,
                'rolling_code': finished.rolling.rolling_code if finished.rolling else None,
                'runout_code': finished.runout.runout_code if finished.runout else None,
                'area_code': finished.area.code if finished.area else None,
                'cast_no': finished.cast.cast_code if finished.cast else None,
                'spec_code': finished.spec.spec_code if finished.spec else None,
                'order_num': finished.order.order_code if finished.order else None,
                'order_item_num': finished.order_item.line_item_code if finished.order_item else None,
                'product_type': finished.product_type.code if finished.product_type else None,
            })

    if finished_product_in.select_type == 'scrap':
        
        if not finished_product_in.scrap_reason_id:
            raise HTTPException(status_code=400, detail="scrap reason is required.")
        
        defect_reason = db_session.query(DefectReason).filter(DefectReason.id == finished_product_in.scrap_reason_id).first()
        
        for finished in finisheds:
            finished.order = None
            finished.order_item = None
            finished.status_change_reason = None
            finished.defect_reason = defect_reason
            finished.stock_type = "scrap"
            
            his.append({
                "allocation_status": finished_product_in.select_type,
                "status_change_reason": defect_reason.code,

                'created_by': current_user.email,
                'mill_id': finished.mill_id,
                'change_type': FinishedProductHistoryChangeTypeEnum.ALLOCATE,
                'uuid': uid,
                'code': finished.code,
                'rolling_code': finished.rolling.rolling_code if finished.rolling else None,
                'runout_code': finished.runout.runout_code if finished.runout else None,
                'area_code': finished.area.code if finished.area else None,
                'cast_no': finished.cast.cast_code if finished.cast else None,
                'spec_code': finished.spec.spec_code if finished.spec else None,
                'order_num': finished.order.order_code if finished.order else None,
                'order_item_num': finished.order_item.line_item_code if finished.order_item else None,
                'product_type': finished.product_type.code if finished.product_type else None,
            })

    db_session.commit()
    bulk_create_finished_product_history(db_session=db_session, finished_product_history_in=his)
    return finisheds


def process_batch_hold(
        db_session,
        finisheds: List[FinishedProduct],
        finished_in: FinishedProductHoldReason,
        current_user_email: str,
        hold_service,
        background_tasks,
        current_mill_code
):
    hold_data = []
    total_count = 0
    success_count = 0
    failure_count = 0
    # 处理 hold 和历史记录更新
    for finished in finisheds:
        total_count += 1
        for hold in finished_in.hold_list:
            hold_id = hold.get("hold_id")
            hold_comment = hold.get("comment") if hold.get("comment") else None

            # 查找 hold 是否已存在
            is_hold = (
                db_session.query(finished_product_hold)
                .filter(
                    finished_product_hold.c.finished_product_id == finished.id,
                    finished_product_hold.c.hold_reason_id == hold_id,
                )
                .first()
            )

            if is_hold:
                # 如果存在，更新 hold 的 comment
                update_hold = (
                    finished_product_hold.update()
                    .where(
                        finished_product_hold.c.finished_product_id == finished.id,
                        finished_product_hold.c.hold_reason_id == hold_id,
                    )
                    .values(comment=hold_comment)
                )
                db_session.execute(update_hold)
                success_count += 1
            else:
                hold_reason = hold_service.get(db_session=db_session, id=hold_id)
                hold_data.append(
                    {
                        "finished_product_id": finished.id,
                        "hold_reason_id": hold_reason.id,
                        "mill_id": hold_reason.mill_id if hold_reason.mill_id else None,
                        "comment": hold_comment,
                        "hold_by": current_user_email,
                    }
                )
                failure_count += 1

                if "SRSM" == current_user_email:
                    # 这里可以自定义逻辑发送通知
                    if "TEST" not in hold_reason.name.upper():
                        try:
                            from ...contrib.message_admin.message_server import server as message_server
                            srsmmtst = message_server.MessageStrategySRSMMTST()
                            srsmmtst.send_pc_mtst(db_session=db_session, bundle_=finished, releaseFlag="N",
                                                background_tasks=background_tasks, current_mill_code=current_mill_code)
                        except ImportError as e:
                            raise HTTPException(status_code=400, detail=str(e))
                        except Exception as e:
                            logger.error(f"ERROR in send_pc_mtst: {e}")

                # 插入 hold 数据到数据库
    if len(hold_data) > 0:
        db_session.execute(finished_product_hold.insert(), hold_data)
    db_session.commit()

    # 处理历史记录
    return process_history_for_batch_hold(db_session=db_session, finisheds=finisheds, background_tasks=background_tasks,
                                          current_user_email=current_user_email, current_mill_code=current_mill_code,
                                          total_count=total_count, success_count=success_count, failure_count=failure_count)


def process_history_for_batch_hold(db_session, finisheds: List[FinishedProduct], current_user_email: str, background_tasks, current_mill_code, total_count, success_count, failure_count):
    history_data = []
    uid = uuid.uuid4()

    for finished_product in finisheds:
        for hold_reason in finished_product.hold_reason:
            comment = None
            # 查询是否已存在 hold
            is_hold = (
                db_session.query(finished_product_hold)
                .filter(
                    finished_product_hold.c.finished_product_id == finished_product.id,
                    finished_product_hold.c.hold_reason_id == hold_reason.id,
                )
                .first()
            )
            if is_hold:
                comment = is_hold.comment
            history_data.append(
                {
                    "mill_id": finished_product.mill_id,
                    "change_type": FinishedProductHistoryChangeTypeEnum.HOLD,
                    "created_by": current_user_email,
                    "uuid": uid,
                    "code": finished_product.code,
                    'rolling_code': finished_product.rolling.rolling_code if finished_product.rolling else None,
                    'runout_code': finished_product.runout.runout_code if finished_product.runout else None,
                    'area_code': finished_product.area.code if finished_product.area else None,
                    'cast_no': finished_product.cast.cast_code if finished_product.cast else None,
                    'spec_code': finished_product.spec.spec_code if finished_product.spec else None,
                    'order_num': finished_product.order.order_code if finished_product.order else None,
                    'order_item_num': finished_product.order_item.line_item_code if finished_product.order_item else None,
                    'product_type': finished_product.product_type.code if finished_product.product_type else None,
                    "status_change_reason": hold_reason.code,
                    "comment": comment,
                }
            )

    # 创建历史记录
    bulk_create_finished_product_history(db_session=db_session, finished_product_history_in=history_data)
    try:
        from ...contrib.message_admin.message_server import server as message_server
        strategy = message_server.MessageStrategy320()
        strategy.send_pc_320(db_session, history_data, background_tasks, current_mill_code)
    except ImportError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"ERROR in send_pc_320: {str(e)}")

    count = {
        "id": total_count,
        "total_count": total_count,
        "success_count": success_count,
        "failure_count": failure_count,
    }
    finisheds.append(count)

    return history_data

def process_batch_unhold(
        db_session,
        finisheds: List[FinishedProduct],
        finished_in: FinishedProductHoldReason,
        current_user_email: str,
        hold_service,
        background_tasks,
        current_mill_code
):
    released_finished_products = []
    history_data = []
    uid = uuid.uuid4()
    total_count = 0
    success_count = 0
    failure_count = 0
    try:
        from ...contrib.message_admin.message_server import server as message_server
        for finished in finisheds:
            total_count += 1
            for hold in finished_in.hold_list:

                # 查找 hold 是否已存在
                is_hold = (
                    db_session.query(finished_product_hold)
                    .filter(
                        finished_product_hold.c.finished_product_id == finished.id,
                        finished_product_hold.c.hold_reason_id == hold,
                    )
                    .first()
                )

                if is_hold:
                    hold_reason = hold_service.get(db_session=db_session, id=hold)
                    history_data.append({
                        "mill_id": finished.mill_id,
                        "change_type": FinishedProductHistoryChangeTypeEnum.UNHOLD,
                        "created_by": current_user_email,
                        "uuid": uid,
                        "code": finished.code,
                        'rolling_code': finished.rolling.rolling_code if finished.rolling else None,
                        'runout_code': finished.runout.runout_code if finished.runout else None,
                        'area_code': finished.area.code if finished.area else None,
                        'cast_no': finished.cast.cast_code if finished.cast else None,
                        'spec_code': finished.spec.spec_code if finished.spec else None,
                        'order_num': finished.order.order_code if finished.order else None,
                        'order_item_num': finished.order_item.line_item_code if finished.order_item else None,
                        'product_type': finished.product_type.code if finished.product_type else None,
                        "status_change_reason": hold_reason.code,
                        "comment": is_hold.comment,
                    })
                    db_session.execute(
                        finished_product_hold.delete().where(
                            finished_product_hold.c.finished_product_id == finished.id,
                            finished_product_hold.c.hold_reason_id == hold,
                        )
                    )
                    success_count += 1
                    released_finished_products.append(finished)
                    if current_user_email == "SRSM" and "TEST" in hold_reason.name.upper():
                        try:
                            srsmmtst = message_server.MessageStrategySRSMMTST()
                            srsmmtst.send_pc_mtst(db_session=db_session, bundle_=finished, releaseFlag="Y",
                                                background_tasks=background_tasks, current_mill_code=current_mill_code)
                        except ImportError as e:
                            raise HTTPException(status_code=400, detail=str(e))
                        except Exception as e:
                            logger.error(f"ERROR in send_pc_mtst: {str(e)}")
                else:
                    failure_count += 1
                    logger.info(f"Unable to release finished_product {finished.code}, no hold found.")
                    continue

        # 发送消息和处理历史记录
        try:
            strategy = message_server.MessageStrategy325()
            strategy.send_pc_325(db_session, released_finished_products, background_tasks, current_mill_code)
        except Exception as e:
            logger.error(f"ERROR in send_pc_325: {str(e)}")
        db_session.commit()
    except ImportError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if len(history_data) > 0:
        bulk_create_finished_product_history(db_session=db_session, finished_product_history_in=history_data)
    count = {
        "id": total_count,
        "total_count": total_count,
        "success_count": success_count,
        "failure_count": failure_count,
    }
    released_finished_products.append(count)

    return released_finished_products

def get_regulars(*, db_session, mult_id: int):
    return db_session.query(FinishedProduct).filter(FinishedProduct.mult_id == mult_id).all()

def get_mult(*, db_session, id: int):
    mult_resp = FinishedProductMultResponse()
    row = get(db_session=db_session, id=id)
    if not row or row.mult_type != 'M': return mult_resp
    mult_resp.mult = row
    mult_resp.regulars = get_regulars(db_session=db_session, mult_id=id)

    return mult_resp


def confirm_mult(*, db_session, mult_confirm_in, current_user: DispatchUser):
    his = []
    uid = uuid.uuid4()
    for id in mult_confirm_in.ids:
        finished_product = get(db_session=db_session, id=id)
        finished_product.exist_flag = 'N'
        finished_product.mult_confirm_datetime = datetime.now()
        stmt = select(FinishedProduct).where(FinishedProduct.mult_id == finished_product.id)

        his.append({
            "allocation_status": finished_product.allocation_status,
            "mult_code": finished_product.mult_code,
            "mult_type": finished_product.mult_type,
            "exist_flag": 'N',
            "waste_length": finished_product.waste_length,
            "length_mm": finished_product.length_mm,

            'created_by': current_user.email,
            'mill_id': finished_product.mill_id,
            'change_type': FinishedProductHistoryChangeTypeEnum.MULT_COMPLETE,
            'uuid': uid,
            'code': finished_product.code,
            'rolling_code': finished_product.rolling.rolling_code if finished_product.rolling else None,
            'runout_code': finished_product.runout.runout_code if finished_product.runout else None,
            'area_code': finished_product.area.code if finished_product.area else None,
            'cast_no': finished_product.cast.cast_code if finished_product.cast else None,
            'spec_code': finished_product.spec.spec_code if finished_product.spec else None,
            'order_num': finished_product.order.order_code if finished_product.order else None,
            'order_item_num': finished_product.order_item.line_item_code if finished_product.order_item else None,
            'product_type': finished_product.product_type.code if finished_product.product_type else None,
        })

        for regular in db_session.execute(stmt).scalars():
            regular.exist_flag = 'Y'
            regular.mult_type = None
            regular.mult_code = None

            his.append({
                "allocation_status": regular.allocation_status,
                "mult_code": regular.mult_code,
                "mult_type": regular.mult_type,
                "exist_flag": 'Y',
                "waste_length": regular.waste_length,
                "length_mm": regular.length_mm,
                "quantity": regular.quantity,

                'created_by': current_user.email,
                'mill_id': regular.mill_id,
                'change_type': FinishedProductHistoryChangeTypeEnum.MULT_COMPLETE,
                'uuid': uid,
                'code': regular.code,
                'rolling_code': regular.rolling.rolling_code if regular.rolling else None,
                'runout_code': regular.runout.runout_code if regular.runout else None,
                'area_code': regular.area.code if regular.area else None,
                'cast_no': regular.cast.cast_code if regular.cast else None,
                'spec_code': regular.spec.spec_code if regular.spec else None,
                'order_num': regular.order.order_code if regular.order else None,
                'order_item_num': regular.order_item.line_item_code if regular.order_item else None,
                'product_type': regular.product_type.code if regular.product_type else None,
            })

    db_session.commit()
    bulk_create_finished_product_history(db_session=db_session, finished_product_history_in=his)

    return True

def update_rework(*, db_session, update_in, current_user: DispatchUser, background_tasks):
    resp = []
    history_in = []
    update_data = update_in.model_dump(exclude={'ids'})
    
    uid = uuid.uuid4()
    for id in update_in.ids:
        get_data = get(db_session=db_session, id=id)
        history_dict = {
            'created_by': current_user.email,
            'mill_id': get_data.mill_id,
            'change_type': FinishedProductHistoryChangeTypeEnum.REWORK,
            'uuid': uid,
            'code':get_data.code,
            'rolling_code': get_data.rolling.rolling_code if get_data.rolling else None,
            'runout_code': get_data.runout.runout_code if get_data.runout else None,
            'area_code': get_data.area.code if get_data.area else None,
            'cast_no': get_data.cast.cast_code if get_data.cast else None,
            'spec_code': get_data.spec.spec_code if get_data.spec else None,
            'order_num': get_data.order.order_code if get_data.order else None,
            'order_item_num': get_data.order_item.line_item_code if get_data.order_item else None,
            'product_type': get_data.product_type.code if get_data.product_type else None,
        }
        for field, field_value in update_data.items():
            if field_value:
                setattr(get_data, field, field_value)
        get_data.rework_due_date = date.today()
        get_data.rework_status = 'Rework'
        history_dict['rework_status'] = update_in.rework_type
        history_dict['rework_due_date'] = get_data.rework_due_date
        db_session.add(get_data)
        resp.append(get_data)
        history_in.append(history_dict)

    db_session.commit()
    bulk_create_finished_product_history(db_session=db_session, finished_product_history_in=history_in)
    try:
        from ...contrib.message_admin.message_server import server as MessageServer
        message_server = MessageServer.MessageStrategyRework()
        message_server.send_pc_240_265(db_session=db_session, finished_product=get_data, background_tasks=background_tasks, current_mill_code=current_user.current_mill_code)
    except ImportError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"ERROR in send_pc_240_265:{e}")
    return resp

def update_rework_complete(*, db_session, data_list, finished_product_in: FinishedProductReworkComplete, background_tasks, current_mill_code):
    history_list = []
    for get_data in data_list:
        if finished_product_in.rework_initial:
            get_data.rework_initial = finished_product_in.rework_initial
        if finished_product_in.rework_complete_comment:
            get_data.rework_complete_comment = finished_product_in.rework_complete_comment
        get_data.rework_finish_date = date.today()
        get_data.rework_type = 'Complete'
        get_data.rework_status = 'Complete'

        history_dict = {
            'created_by': get_data.updated_by,
            'mill_id': get_data.mill_id,
            'change_type': FinishedProductHistoryChangeTypeEnum.REWORK_COMPLETE,
            'code': get_data.code,
            'rolling_code': get_data.rolling.rolling_code if get_data.rolling else None,
            'runout_code': get_data.runout.runout_code if get_data.runout else None,
            'area_code': get_data.area.code if get_data.area else None,
            'cast_no': get_data.cast.cast_code if get_data.cast else None,
            'spec_code': get_data.spec.spec_code if get_data.spec else None,
            'order_num': get_data.order.order_code if get_data.order else None,
            'order_item_num': get_data.order_item.line_item_code if get_data.order_item else None,
            'product_type': get_data.product_type.code if get_data.product_type else None,

            'rework_due_date': get_data.rework_due_date,
            'rework_status': get_data.rework_status,
            'rework_initial': get_data.rework_initial,
            'rework_finish_date': get_data.rework_due_date,
        }
        history_list.append(history_dict)

        try:
            # import dispatch.contrib.message_admin.message_server.trigger_sap_message as sap_strategy
            from ...contrib.message_admin.message_server import server as MessageServer, trigger_sap_message as sap_strategy
            messageStrategy290=MessageServer.MessageStrategy290()
            messageStrategy290.send_pc_290(db_session, get_data.code, background_tasks, current_mill_code)
            del messageStrategy290
            if not get_data.defect_reason_id and not get_data.hold_reason:
                sap_strategy.handle_qmai264(db_session=db_session, finished_product_id=get_data.id,
                               action_e=sap_strategy.QMAI264_ACTION.ACCEPTED,
                               background_tasks=background_tasks)
        except ImportError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"ERROR in send_pc_290:{e}")

    db_session.commit()
    bulk_create_finished_product_history(db_session=db_session, finished_product_history_in=history_list)

    return True

def update_load(*, db_session, get_data, load_in):
    get_data.load_id = load_in.load_id

    db_session.commit()

    return get_data

def update_unload(*, db_session, get_data):
    get_data.load_id = None

    db_session.commit()

    return get_data


def move_to_product(*, db_session, data, current_user: DispatchUser, background_tasks):
    # is_generate_advice = data['is_generate_consi']
    codes_ls = data['codes']
    to_area_code = data.get('area_code', None)
    # to_site_code = data['site_code']
    # to_site_type_code = data['site_type_code']
    new_stock_type = data.get('stock_type', None)
    new_status = data.get('status', None)
    is_status_type = data.get('is_status_type', False)

    # to_area_obj = db_session.query(Area).filter_by(code=to_area_code).first()
    # generate_advice = None
    # if not to_area_obj:
    #     raise HTTPException(status_code=400, detail="Area code not found.")

    # if is_generate_advice:
    #     advice_obj_in = AdviceCreate()
    #     advice_obj_in.from_area_id = to_area_obj.id
    #     # print(advice_obj_in)
    #     generate_advice = advice_create(db_session=db_session, advice_in=advice_obj_in)
    #     # generate_advice_id = 1
    # 通过 code 查询是否存在finished_product
    finished_product_list = db_session.query(FinishedProduct).filter(FinishedProduct.code.in_(data['codes'])).all()
    # 定义选择规则
    rules = {
        "bws": ["scrap", "bws", "internal", 'service_center'],
        "roster": ["scrap", "roster", "internal", 'service_center'],
        "internal": ["scrap", "internal"],
        "scrap": ["bws", "roster", "scrap", "internal", 'service_center'],  # 不允许选择任何选项
        "service_center": ["scrap", "bws", "roster", "internal", 'service_center']
    }
    invalid_codes = []
    allowed_options = []
    bundles_before_image = []
    srsmm640_result = []
    update_dict = {
        "area_id": to_area_code,
        "updated_by": current_user.email,
        "updated_at": datetime.now()
    }
    # 获取允许的选项
    if is_status_type:
        if not new_status:
            raise HTTPException(status_code=400, detail="Status is required.")
        update_dict["status"] = new_status
        update_dict['stock_type'] = new_stock_type
        for finished in finished_product_list:
            allowed_options = rules.get(finished.stock_type, None)
            bundles_before_image.append({"id": finished.id, "area_id": finished.area_id})
            # 校验逻辑
            if allowed_options is not None:
                # raise HTTPException(status_code=400, detail="Invalid business_type provided.")
                if new_stock_type not in allowed_options:
                    invalid_codes.append(finished.code)
        if invalid_codes:
            raise HTTPException(
                status_code=400,
                detail={
                    "msg": f"Invalid selections: {invalid_codes}. Business Type Only allowed options: {allowed_options}.",
                    "invalid_codes": invalid_codes,
                    "allowed_options": allowed_options
                }
            )
    print("update_dict", update_dict)
    db_session.query(FinishedProduct).filter(FinishedProduct.code.in_(codes_ls)).update(
        update_dict
    )

    history_list = []
    change_list = []

    for finished_product in finished_product_list:
        history_list.append(
            {
                "change_type": FinishedProductHistoryChangeTypeEnum.MOVE,
                "created_by": current_user.email,
                "mill_id": finished_product.mill_id,

                "code": finished_product.code,
                "rolling_code": finished_product.rolling.rolling_code if finished_product.rolling else None,
                "cast_no": finished_product.cast.cast_code if finished_product.cast else None,
                "spec_code": finished_product.spec.spec_code if finished_product.spec else None,
                "runout_code": finished_product.runout.runout_code if finished_product.runout else None,
                "order_num": finished_product.order.order_code if finished_product.order else None,
                "product_type": finished_product.product_type.code if finished_product.product_type else None,
                "order_item_num": finished_product.order_item.line_item_code if finished_product.order_item else None,

                "area_code": data['area_code'],
                # "site_code": data['site_code'],
                # "site_type_code": data['site_type_code'],
                "stock_type": new_stock_type if new_stock_type else None
            }
        )
        
    #     change_list.append(
    #         {
    #             "id": finished_product.id,
    #             "stock_type": new_stock_type,
    #             # "advice_id": generate_advice_id,
    #             # "advice_id": None if not generate_advice else generate_advice.id,
    #             # "area_id": None if is_generate_advice else to_area_obj.id
    #             "area_id": data['area_code'],
    #             "status": new_status,
    #         }
    #     )
    # db_session.bulk_update_mappings(FinishedProduct, change_list)
    bulk_create_finished_product_history(db_session=db_session, finished_product_history_in=history_list)
    
    db_session.commit()

    messageStrategy460=MessageServer.MessageStrategy460()
    for finish_product in finished_product_list:
        if finish_product:      
            try:
                messageStrategy460.send_pc_460(db_session, finish_product.code, background_tasks, current_user.current_mill_code)
            except Exception as e:
                logger.error(f"ERROR in send_pc_460: {str(e)}")
    del messageStrategy460
    if get_mill_ops(current_user.current_mill_id) == MILLEnum.MILL1:
        srsm640 = MessageServer.MessageStrategySRSMM640()
        finished_product_list_after = db_session.query(FinishedProduct).filter(FinishedProduct.code.in_(data['codes'])).all()
        for finish_product_after in finished_product_list_after:
            for bundle_before in bundles_before_image:
                if bundle_before.get("id") == finish_product_after.id:
                    if finish_product_after.area_id != bundle_before.get("area_id"):
                        area: Area = area_service.get(db_session=db_session, area_id=bundle_before.get("area_id"))
                        try:
                            res2 = srsm640.send_pc_m640(db_session=db_session, bundles_=[finish_product_after], old_area=area.code, background_tasks=background_tasks, current_mill_code=current_user.current_mill_code)
                            srsmm640_result.append(res2)
                        except Exception as e:
                            logger.error(f"ERROR in send_pc_m640: {str(e)}")
                        break

    # print(history_list)
    # print(change_list)
    return True
    ####### 更改finished_product的stock_type #####
    # db_session.bulk_update_mappings(FinishedProduct, change_list)

    # 将改变动作插入到历史记录
    # finished_product_history_bulk_create(db_session=db_session, finished_product_move_histories_in=history_list)



def update_reserve_rework(*, db_session, id_list,current_user: DispatchUser,order_item_id):
    history_list = []
    hold_list = []
    for id in id_list:
        finished_product = db_session.query(FinishedProduct).filter(FinishedProduct.id == id).first()

        if finished_product.mill and get_mill_ops(finished_product.mill.id) == MILLEnum.MILL410:
            # created_at 超过12个月 增加hold
            now = datetime.now()
            twelve_months_ago = now - relativedelta(months=int(HOLD_AGED_BAR_MONTH))
            # 判断 created_at 是否超过 12 个月
            if finished_product.created_at and finished_product.created_at < twelve_months_ago:

                hold_data = inset_hold_reason_list(db_session=db_session,current_user=current_user,finished_product=finished_product,hold_code="AGB")
                hold_list.append(hold_data)

        if finished_product:
            finished_product.reserve_status = "reserved"
            finished_product.reserved_order_item_id = order_item_id
            db_session.add(finished_product)
            history_list.append(
                {
                    'reserve_status': finished_product.reserve_status,

                    'created_by': current_user.email,
                    'mill_id': finished_product.mill_id,
                    'change_type': FinishedProductHistoryChangeTypeEnum.RESERVE,
                    'code': finished_product.code,
                    'rolling_code': finished_product.rolling.rolling_code if finished_product.rolling else None,
                    'runout_code': finished_product.runout.runout_code if finished_product.runout else None,
                    'area_code': finished_product.area.code if finished_product.area else None,
                    'cast_no': finished_product.cast.cast_code if finished_product.cast else None,
                    'spec_code': finished_product.spec.spec_code if finished_product.spec else None,
                    'order_num': finished_product.order.order_code if finished_product.order else None,
                    'order_item_num': finished_product.order_item.line_item_code if finished_product.order_item else None,
                    'product_type': finished_product.product_type.code if finished_product.product_type else None,
                }
            )
    if len(hold_list)>0:
        db_session.execute(finished_product_hold.insert(), hold_list)
    db_session.commit()
    bulk_create_finished_product_history(db_session=db_session, finished_product_history_in=history_list)
    return True

def create_defects(*, db_session, data):
    defect_reason = data['defect_reason']
    defect_reason_id = defect_reason.get('id')
    
    downgraded = data.get('downgraded', None)
    comment = data.get('comment', None)
    defect_quantity = data.get('defect_quantity', None)
    defective_length = data.get('defective_length', None)
    
    try:
        defect_quantity = int(defect_quantity) if defect_quantity is not None else None
    except ValueError:
        raise HTTPException(status_code=400, detail="defect_quantity must be an integer.")
    
    code = data['codes']
    finish_product = db_session.query(FinishedProduct).filter(FinishedProduct.code.in_(code)).all()
    add_list = []
    
    for finish_product_list in finish_product:
        updated_quantity = finish_product_list.quantity - (defect_quantity or 0)
        add_list.append(
            {
                "id": finish_product_list.id,
                "defect_reason_id": defect_reason_id,
                "comment": comment,
                "downgraded": downgraded,
                "defect_quantity": defect_quantity,
                "defective_length": defective_length,
                # "quantity": updated_quantity,
            }
        )
    
    db_session.bulk_update_mappings(FinishedProduct, add_list)
    db_session.commit()
    return True


def create_by_load(
    *, 
    db_session, 
    finished_product_in: FinishedProductCreateLoad,
    current_user
):
    try:
        is_generate_advice = finished_product_in.is_generate_advice
        is_generate_load = finished_product_in.is_generate_load
        is_carry_out = finished_product_in.is_carry_out
        item_ids = finished_product_in.ids
        load_obj_in = None
        generate_advice = None
        if is_generate_load:
            load_obj_in = FinishedProductLoadCreate()
            load_obj_in.transport_type = finished_product_in.transport_type
            load_obj_in.transport_id = finished_product_in.transport_id
            load_obj_in.code = finished_product_in.load_no
            load_obj_in.comment = finished_product_in.comment
            load_obj_in.bind_finished_product_ids = finished_product_in.ids
            load_obj_in.created_by = finished_product_in.created_by
            load_obj_in.updated_at = finished_product_in.updated_at
            load_obj_in.updated_by = finished_product_in.updated_by
            if is_carry_out:
                load_obj_in.load_status = "Carry Out"
            load_obj_in = finished_product_service.new_create(db_session=db_session, create_in=load_obj_in, flush=True)
            if is_generate_advice:
                # 按 order_item 分组
                grouped_products = group_by_order(finished_product_in.ids, db_session)
                # 为每个分组创建对应的 advice
                for order, products in grouped_products.items():
                    # 创建每个分组对应的 advice 对象
                    advice_obj_in = AdviceCreate()
                    advice_obj_in.load_id = load_obj_in.id
                    advice_obj_in.finished_ids = [product.id for product in products]  # 获取分组中的所有产品 ID
                    advice_obj_in.order_id = order.id if order else None
                    advice_obj_in.business_type = "bws" if order and any(
                        item.bws_store for item in order.order_order_item) else "internal"

                    advice_obj_in.created_by = finished_product_in.created_by
                    advice_obj_in.updated_by = finished_product_in.updated_by
                    advice_obj_in.updated_at = finished_product_in.updated_at
                    advice_obj_in.mill_id = current_user.current_mill_id
                    advice_obj_in.transport_id = load_obj_in.transport_id if load_obj_in.transport_id else None
                    advice_obj_in.transport_type = load_obj_in.transport_type if load_obj_in.transport_type else None
                    generate_advice = advice_create(db_session=db_session, advice_in=advice_obj_in)
        db_session.commit()
        return load_obj_in
    except Exception as e:
        db_session.rollback()
        raise HTTPException(status_code=400, detail=str(e))


def return_finished(db_session, data:ReturnUpdate, current_user: DispatchUser):
    his = []
    uid = uuid.uuid4()
    finished_product = get(db_session=db_session, id=data.id)
    if data.is_generate_new:
        if get_by_code(db_session=db_session, code=data.code):
            raise HTTPException(status_code=400, detail="The finished product with this code already exists.")

        new_fin = FinishedProductCreate(**finished_product.__dict__)
        new_fin = FinishedProduct(**new_fin.model_dump(
            exclude={"flex_form_data", "cast", "runout", "rolling", "area", "mill", "spec", "order", "order_item",
                     "codes", "site_type_code", "site_code", "area_code", "is_generate_comsi", "advice",
                     "product_type", "label_template","product_size"
                     }))
        for key, value in data.model_dump(exclude={'id', 'is_generate_new'}, exclude_unset=True).items():
            setattr(new_fin, key, value)
        finished_product.exist_flag = 'N'
        new_fin.exist_flag = 'Y'
        # new_fin.estimated_weight_kg = data.kg
        # new_fin.length_mm = data.length
        new_fin.created_by = current_user.email
        new_fin.updated_by = current_user.email
        new_fin.status = FinishedProductStatusEnum.RETURNED
        # new_fin.stock_type = 'beam_mill'

        if data.advice_id:
            advice = db_session.query(Advice).filter(Advice.id == data.advice_id).first()
            new_fin.advice = [advice]
        db_session.add(new_fin)

        his.append({
            "uuid": uid,
            "mill_id": new_fin.mill_id,
            "change_type": FinishedProductHistoryChangeTypeEnum.RETURN,
            "created_by": current_user.email,
            "code": new_fin.code,
            'rolling_code': new_fin.rolling.rolling_code if new_fin.rolling else None,
            'runout_code': new_fin.runout.runout_code if new_fin.runout else None,
            'area_code': new_fin.area.code if new_fin.area else None,
            'cast_no': new_fin.cast.cast_code if new_fin.cast else None,
            'spec_code': new_fin.spec.spec_code if new_fin.spec else None,
            'order_num': new_fin.order.order_code if new_fin.order else None,
            'order_item_num': new_fin.order_item.line_item_code if new_fin.order_item else None,
            'product_type': new_fin.product_type.code if new_fin.product_type else None,
            "status": new_fin.status,
            "estimated_weight_kg": new_fin.estimated_weight_kg,
            "length_mm": new_fin.length_mm,
            "quantity": new_fin.quantity,
            "advice_no": new_fin.advice[0].advice_code if new_fin.advice else None,
            "exist_flag": new_fin.exist_flag,
            "stock_type": new_fin.stock_type,
        })
    else:
        finished_product.status = FinishedProductStatusEnum.RETURNED
        finished_product.exist_flag = 'Y'
        finished_product.stock_type = data.stock_type
        finished_product.area_id = data.area_id
    finished_product.updated_at = datetime.now()
    finished_product.updated_by = current_user.email
    db_session.commit()

    his.append({
        "uuid": uid,
        "mill_id": finished_product.mill_id,
        "change_type": FinishedProductHistoryChangeTypeEnum.RETURN,
        "created_by": current_user.email,
        "code": finished_product.code,
        'rolling_code': finished_product.rolling.rolling_code if finished_product.rolling else None,
        'runout_code': finished_product.runout.runout_code if finished_product.runout else None,
        'area_code': finished_product.area.code if finished_product.area else None,
        'cast_no': finished_product.cast.cast_code if finished_product.cast else None,
        'spec_code': finished_product.spec.spec_code if finished_product.spec else None,
        'order_num': finished_product.order.order_code if finished_product.order else None,
        'order_item_num': finished_product.order_item.line_item_code if finished_product.order_item else None,
        'product_type': finished_product.product_type.code if finished_product.product_type else None,

        "status": finished_product.status,
        "exist_flag": finished_product.exist_flag,
        "stock_type": finished_product.stock_type,
    })
    bulk_create_finished_product_history(db_session=db_session, finished_product_history_in=his)
    return True

def update_flex_form_data(db_session, finished_product_obj: FinishedProduct, flex_form_data: dict):
    finished_product_obj.flex_form_data = flex_form_data
    try:
        db_session.add(finished_product_obj)
        db_session.commit()
    except Exception as e:
        db_session.rollback()


def get_store_codes(*, db_session):
    """Returns all unique store codes."""
    store_codes = db_session.query(FinishedProduct.store_code).filter(FinishedProduct.store_code != None).distinct().all()
    return [code[0] for code in store_codes]

def get_by_code_batch(*, db_session, codes):
    finished_products = db_session.query(FinishedProduct).filter(FinishedProduct.code.in_(codes)).all()
    return finished_products

def update_fin_location(*, db_session, finished_product: FinishedProduct, finished_product_in: FinishedProductUpdate):
    for field, attr in finished_product_in.model_dump().items():
        if attr:
            setattr(finished_product, field, attr)
    
    db_session.add(finished_product)
    db_session.commit()

# 提供函数供 L190 消息创建 bundle 时绑定 load
def live_rolling_carry_oyt(*, db_session, bundle_id: int, order_item_id: int):
    cut_seq_objs = db_session.query(CutSequencePlan).filter(
        CutSequencePlan.order_item_id == order_item_id,
        CutSequencePlan.is_deleted == 0
    ).order_by(asc(CutSequencePlan.saw_route)).all()

    bundle_obj = db_session.query(FinishedProduct).filter(FinishedProduct.id == bundle_id).first()
    if not bundle_obj:
        raise HTTPException(status_code=404, detail=f"Bundle not found by bundle id: {bundle_id}")

    bundle_tons = bundle_obj.estimated_weight_kg / 1000 if bundle_obj.estimated_weight_kg else Decimal('0')
    if not bundle_tons:
        raise HTTPException(status_code=404, detail=f"Bundle: {bundle_id} has no estimated weight!")

    for cut_seq_obj in cut_seq_objs:
         # Get cut seq plan's loads
        cut_seq_loads = sorted(cut_seq_obj.cut_seq_loads, key=lambda x: x.cut_seq_load_no)
        for load in cut_seq_loads:
            if load.total_weight_ton and (load.total_weight_ton + bundle_tons <= LOAD_AUTO_PLAN_TONNAGE):
                load.total_weight_ton += bundle_tons
                db_session.add(load)
                db_session.execute(finished_product_load.insert().values(
                    finished_product_id=bundle_id,
                    finished_product_load_id=load.id
                ))
                db_session.commit()
                logger.info(f"Bundle: {bundle_id} add in load: {[load.id, load.cut_seq_load_no]}")
                return
    else:
        logger.error(f"All the loads are fully loaded.")

def rebundle_update(db_session, other_code):
    for codes in other_code:
        existing_product = db_session.query(FinishedProduct).filter(FinishedProduct.code == codes).first()
        if existing_product:
            existing_product.allocation_status = "scrap"
            db_session.commit()
    return


def get_cast_list_by_order_item(*, db_session, order_item_id: int):
    finisheds = db_session.query(FinishedProduct.cast_id.distinct().label("cast_id")).filter(FinishedProduct.order_item_id == order_item_id).filter(FinishedProduct.is_deleted == 0).all()
    casts =  [i.cast_id for i in finisheds]
    if casts:
        casts = db_session.query(Cast).filter(Cast.id.in_(casts)).all()
        return casts
    return []
