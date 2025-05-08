
from typing import List, Optional

from dispatch.site import service as site_service
from .models import SemiLoad, SemiLoadCreate, SemiLoadRead, SemiLoadUpdate, SemiLoadCreate
from dispatch.mill import service as mill_service
from ..semi.models import Semi
from sqlalchemy import select, func


def get(*, db_session, id: int) -> Optional[SemiLoad]:
    """Returns an semi given an semi id."""
    return db_session.query(SemiLoad).filter(SemiLoad.id == id).one_or_none()


def get_by_code(*, db_session, code: str) -> Optional[SemiLoad]:
    """Returns an semi given an semi code address."""
    return db_session.query(SemiLoad).filter(SemiLoad.semi_load_code == code).one_or_none()


def get_default_semi(*, db_session ) -> Optional[SemiLoad]:
    """Returns an semi given an semi code address."""
    return db_session.query(SemiLoad).first()


def get_all(*, db_session) -> List[Optional[SemiLoad]]:
    """Returns all semis."""
    return db_session.query(SemiLoad)

   
def create(*, db_session, semi_load_in: SemiLoadCreate) -> SemiLoad:
    """Creates an semi.""" 
 
    site= None
 
    if semi_load_in.site:
        site = site_service.get( db_session=db_session, id=semi_load_in.site.id) 

    semi_ids = semi_load_in.semi_ids

    contact = SemiLoad(**semi_load_in.dict(exclude={"flex_form_data","site","semi_ids", "mill"}),
                    flex_form_data=semi_load_in.flex_form_data,
                    site=site
                    )
    
    db_session.add(contact)
    db_session.commit()

    if semi_ids:
        for semi_id in semi_ids:
            semi_get = db_session.get(Semi, semi_id)
            semi_get.semi_load_id = contact.id
        db_session.commit()
    return contact


def update(
    *,
    db_session,
    semi: SemiLoad,
    semi_load_in: SemiLoadUpdate,
) -> SemiLoad:

    mill = None
  
    if semi_load_in.site and ( semi_load_in.site.id != semi.site.id):
        site = site_service.get( db_session=db_session, id=semi_load_in.site.id)
        semi.site = site 

    if semi_load_in.mill_id:
        mill = mill_service.get(db_session=db_session, mill_id=semi_load_in.mill_id)
    semi_ids = semi_load_in.semi_ids

    update_data = semi_load_in.dict(
        exclude={"flex_form_data","site","semi_ids", "mill"},
    )
    for field, field_value in update_data.items():
        setattr(semi, field, field_value)

    semi.flex_form_data = semi_load_in.flex_form_data
    semi.mill = mill
    db_session.add(semi)
    db_session.commit()

    if semi_ids:
        stmt = select(Semi).where(Semi.semi_load_id == semi.id)
        for bound_semi in db_session.scalars(stmt):
            bound_semi.semi_load_id = None
        db_session.commit()
        for semi_id in semi_ids:
            semi_get = db_session.get(Semi, semi_id)
            semi_get.semi_load_id = semi.id
        db_session.commit()
    return semi


def insert_json_semi_load(*, db_session, semi_body):
    try:
        db_session.add(semi_body)
        db_session.commit()  # 提交事务
        return semi_body
    except Exception as e:
        db_session.rollback()
        raise e


def delete(*, db_session, id: int):
    
    semi = db_session.query(SemiLoad).filter(SemiLoad.id == id).one_or_none()
    if semi:
        semi.is_deleted = 1
    db_session.add(semi)
    db_session.commit()

    return semi

def update_semi_to_semi_load(*, db_session, semi_load_in: SemiLoadRead, semi_id: int):
    db_session.query(Semi).filter(Semi.id == semi_id).update({
        "updated_at": semi_load_in.updated_at,
        "updated_by": semi_load_in.updated_by,
        "semi_load_id": semi_load_in.id,
    })
    db_session.commit()
    return True


def update_semi_by_move(db_session, semi_load_body):
    try:
        db_session.bulk_update_mappings(SemiLoad, semi_load_body)
        db_session.commit()
        return True
    except Exception as e:
        db_session.rollback()  # 如果更新失败，回滚事务
        raise e

def get_by_wagon(db_session, wagon):
    return db_session.query(SemiLoad).filter(SemiLoad.vehicle_code == wagon).order_by(SemiLoad.id.desc()).first()


def get_max_semi_load_id(db_session):
    max_id = db_session.query(func.max(SemiLoad.id)).scalar()
    return max_id  # 如果表为空，返回 None

