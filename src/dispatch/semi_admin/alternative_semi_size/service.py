from datetime import datetime
from typing import List, Optional
from sqlalchemy import func, or_, case
from sqlalchemy.orm import joinedload
from mako.parsetree import Code
from openpyxl.pivot.table import Location
from fastapi import HTTPException
from dispatch.rolling.rolling_list import service as rolling_service
from dispatch.order_admin.order_group import service as order_group_service
from dispatch.rolling.rolling_list.models import Rolling
from dispatch.site import service as site_service
from dispatch.semi_admin.semi_load import service as semi_load_service
from .models import AlternativeSemiSize, AlternativeSemiSizeCreate, AlternativeSemiSizeRead, AlternativeSemiSizeUpdate, AlternativeSemiSizeCreate
from dispatch.area.models import Area
from dispatch.site.models import Site
from dispatch.cast import service as cast_service
from dispatch.order_admin.order_group.models import OrderGroup
from dispatch.system_admin.auth.models import DispatchUser
from dispatch.database import get_class_by_tablename

def get_by_semi_code_rolling_code(*, db_session, semi_code: str, rolling_code: str, area_code: str, group_code: str) -> \
List[Optional[AlternativeSemiSize]]:
    """Returns an semi given an semi id."""
    return db_session.query(AlternativeSemiSize.id).outerjoin(
        Rolling, AlternativeSemiSize.rolling_id == Rolling.id
    ).filter(
        or_(AlternativeSemiSize.semi_code.like(f'%{semi_code}%'), Rolling.rolling_code.like(f'%{rolling_code}%'))
    ).all() or db_session.query(AlternativeSemiSize.id).outerjoin(
        Area, AlternativeSemiSize.area_id == Area.id
    ).filter(
        or_(AlternativeSemiSize.semi_code.like((f'%{semi_code}%')),
            Area.code.like(f'%{area_code}%')
            )
    ).all() or db_session.query(AlternativeSemiSize.id).outerjoin(
        OrderGroup, AlternativeSemiSize.order_group_id == OrderGroup.id
    ).filter(
        or_(AlternativeSemiSize.semi_code.like((f'%{semi_code}%')),
            OrderGroup.group_code.like(f'%{group_code}%')
            )
    )


def get(*, db_session, semi_id: int) -> Optional[AlternativeSemiSize]:
    """Returns an semi given an semi id."""
    return db_session.query(AlternativeSemiSize).filter(AlternativeSemiSize.id == semi_id).one_or_none()


def get_by_cast_id(*, db_session, cast_id: int) -> List[Optional[AlternativeSemiSize]]:
    """Returns an semi given an semi id."""
    return db_session.query(AlternativeSemiSize).filter(AlternativeSemiSize.cast_id == cast_id).all()


def get_by_spec_ids(*, db_session, spec_ids: List[int]) -> List[Optional[AlternativeSemiSize]]:
    """Returns an semi given an semi id."""
    return db_session.query(AlternativeSemiSize).filter(AlternativeSemiSize.spec_id.in_(spec_ids)).all()


def get_by_code(*, db_session, code: str) -> Optional[AlternativeSemiSize]:
    """Returns an semi given an semi code address."""
    return db_session.query(AlternativeSemiSize).filter(AlternativeSemiSize.semi_code == code).one_or_none()


def get_default_semi(*, db_session) -> Optional[AlternativeSemiSize]:
    """Returns an semi given an semi code address."""
    return db_session.query(AlternativeSemiSize).first()


def get_all(*, db_session) -> List[Optional[AlternativeSemiSize]]:
    """Returns all semis."""
    return db_session.query(AlternativeSemiSize)


def create(*, db_session, semi_in: AlternativeSemiSizeCreate) -> AlternativeSemiSize:
    """Creates an semi."""
    contact = AlternativeSemiSize(**semi_in.dict(
        exclude={"semi_size","product_type", "flex_form_data", "mill", "search_vector"}), flex_form_data=semi_in.flex_form_data)
    db_session.add(contact)
    db_session.commit()
    return contact


def update(
        *,
        db_session,
        semi: AlternativeSemiSize,
        semi_in: AlternativeSemiSizeUpdate,
) -> AlternativeSemiSize:

    update_data = semi_in.dict(
        exclude={"semi_size","product_type", "flex_form_data", "mill", "search_vector"})
    for field, field_value in update_data.items():
        setattr(semi, field, field_value)

    semi.flex_form_data = semi_in.flex_form_data
    semi.updated_at = datetime.utcnow()
    db_session.add(semi)
    db_session.commit()
    return semi


def delete(*, db_session, semi_id: int):
    semi = db_session.query(AlternativeSemiSize).filter(AlternativeSemiSize.id == semi_id).delete()
    db_session.commit()

    return semi


def bulk_get_semi(*, db_session, ids) -> List[Optional[AlternativeSemiSize]]:
    return db_session.query(AlternativeSemiSize).filter(AlternativeSemiSize.id.in_(ids)).all()


def get_area_location(*, db_session, semi_ids) -> Optional[Location]:
    res = db_session.query(AlternativeSemiSize).filter(AlternativeSemiSize.id.in_(semi_ids)).all()
    return res


def block_unblock_semi(db_session, semis_in):
    semi_body = []
    # 查询数据库中semi_charge_seq的最大值
    max_charge_seq = db_session.query(func.max(AlternativeSemiSize.semi_charge_seq)).scalar() or 0
    for semi_data in semis_in:
        semi_dict = semi_data.dict()
        semi_dict.pop("semi_code", None)
        rolling_id = getattr(semi_data, "rolling_id", None)
        order_group_id = getattr(semi_data, "order_group_id", None)
        existing_charge_seq = semi_dict.get('semi_charge_seq')
        if rolling_id is None or order_group_id is None:
            semi_dict["semi_charge_seq"] = None
        elif existing_charge_seq is not None:
            pass  # 已有semi_charge_seq值，不做任何修改
        else:
            max_charge_seq += 1
            semi_dict["semi_charge_seq"] = max_charge_seq
        semi_body.append(semi_dict)

    return update_semi_by_move(db_session=db_session, semi_body=semi_body)


def update_semi_by_move(db_session, semi_body):
    try:
        db_session.bulk_update_mappings(AlternativeSemiSize, semi_body)
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
            setattr(get_data, field, field_value)
        get_data.rework_status = 'Rework'
        db_session.add(get_data)
        resp.append(get_data)

    db_session.commit()

    return resp


def update_rework_status(*, db_session, get_data, update_in):
    update_data = update_in.model_dump()
    for field, field_value in update_data.items():
        setattr(get_data, field, field_value)

    db_session.commit()

    return get_data


# 通过semi code 获取 cast id, 再找所有cast id下的semi code
def find_max_semi_code_by_cast(db_session, semi_code):
    semi_one = get_by_code(db_session=db_session, code=semi_code)
    if not semi_one:
        raise HTTPException(status_code=400, detail="AlternativeSemiSize code not found！")
    cast_id = semi_one.cast_id
    if not cast_id:
        raise HTTPException(status_code=400, detail="Cast id code not found in AlternativeSemiSize！")
    result = db_session.query(AlternativeSemiSize.semi_code).filter(AlternativeSemiSize.cast_id == cast_id).all()
    max_semi_code = max([i[0] for i in result])
    return max_semi_code

