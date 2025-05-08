from typing import List, Optional
from sqlalchemy.sql.functions import func
from .models import SemiSizeDetail, SemiSizeDetailCreate, SemiSizeDetailUpdate
from dispatch.mill import service as mill_service
from dispatch.semi_admin.semi_size import service as semi_size_service
 

def get(*, db_session, id: int) -> Optional[SemiSizeDetail]:
    return db_session.query(SemiSizeDetail).filter(SemiSizeDetail.id == id).one_or_none()


def create(*, db_session, semi_size_detail_in: SemiSizeDetailCreate) -> SemiSizeDetail:
    # exclude={"flex_form_data", "location"}
    mill = None
    if semi_size_detail_in.mill_id:
        mill = mill_service.get(db_session=db_session, mill_id=semi_size_detail_in.mill_id)
    semi_size = None
    if semi_size_detail_in.semi_size_id:
        semi_size = semi_size_service.get(db_session=db_session, id=semi_size_detail_in.semi_size_id)
    semi_size_detail = SemiSizeDetail(**semi_size_detail_in.dict(exclude={"flex_form_data", "mill", "semi_size"}), mill=mill)
    db_session.add(semi_size_detail)
    db_session.commit()
    return semi_size_detail

def update(
    db_session,
    item: SemiSizeDetail,
    semi_size_detail_in: SemiSizeDetailUpdate,
) -> SemiSizeDetail:
    
    mill = None
    if semi_size_detail_in.mill_id:
        mill = mill_service.get(db_session=db_session, mill_id=semi_size_detail_in.mill_id)
    semi_size = None
    if semi_size_detail_in.semi_size_id:
        semi_size = semi_size_service.get(db_session=db_session, id=semi_size_detail_in.semi_size_id)

    update_data = semi_size_detail_in.dict(
        exclude={"flex_form_data", "mill", "semi_size"},
    )
    for field, field_value in update_data.items():
        setattr(item, field, field_value)
    
    item.mill = mill
    item.semi_size = semi_size

    db_session.add(item)
    db_session.commit()
    return item

def delete(*, db_session, id: int):
    # db_session.query(SemiSizeDetail).filter(SemiSizeDetail.id == id).delete()
    db_session.query(SemiSizeDetail).filter(SemiSizeDetail.id == id).update({"is_deleted": 1})
    db_session.commit()


def get_length_by_size_id(*, db_session):
    id_length = []
    result = db_session.query(SemiSizeDetail.semi_size_id,SemiSizeDetail.length_mm).all()
    if not result:
        return id_length
    for id,length in result:
        id_length.append({"id":id,"length":length})
    print(id_length)
    return id_length

