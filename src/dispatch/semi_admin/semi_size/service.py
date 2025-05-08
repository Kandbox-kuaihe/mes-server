from typing import List, Optional
from sqlalchemy.sql.functions import func
from .models import SemiSize, SemiSizeCreate, SemiSizeUpdate
from ...config import get_mill_ops, MILLEnum


def get(*, db_session, id: int) -> Optional[SemiSize]:
    return db_session.query(SemiSize).filter(SemiSize.id == id).one_or_none()

def get_by_code(*, db_session, code: str) -> Optional[SemiSize]:
    return db_session.query(SemiSize).filter(SemiSize.code == code).one_or_none()
## 用于product_type 的create sql接口 :SRSM code即width_mm+thick_mm
def get_size_id_by_code(db_session, code: str) -> Optional[int]:
    semi_size= db_session.query(SemiSize).filter(SemiSize.code == code).one_or_none()
    return semi_size.id

def create(*, db_session, semi_size_in: SemiSizeCreate) -> SemiSize:
    # exclude={"flex_form_data", "location"}
    semi_size = SemiSize(**semi_size_in.dict())
    db_session.add(semi_size)
    db_session.commit()
    return semi_size

def update(
    db_session,
    item: SemiSize,
    item_in: SemiSizeUpdate,
) -> SemiSize:

    update_data = item_in.dict(
        exclude={"flex_form_data"},
    )
    for field, field_value in update_data.items():
        setattr(item, field, field_value)

    db_session.add(item)
    db_session.commit()
    return item

def delete(*, db_session, id: int):
    # db_session.query(SemiSize).filter(SemiSize.id == id).delete()
    db_session.query(SemiSize).filter(SemiSize.id == id).update({"is_deleted": 1})
    db_session.commit()


def get_width_thick(*, db_session):
    width_thick = []
    result = db_session.query(SemiSize.width_mm,SemiSize.thick_mm).all()
    if not result:
        return width_thick
    for width,thick in result:
        width_thick.append({"width":width,"thick":thick})
    print(width_thick)
    return width_thick

def get_by_width_thick(*, db_session, width: int, thick: int) -> Optional[SemiSize]:
    return db_session.query(SemiSize).filter(SemiSize.width_mm == width, SemiSize.thick_mm == thick, get_mill_ops(SemiSize.mill_id) == MILLEnum.MILL1).one_or_none()