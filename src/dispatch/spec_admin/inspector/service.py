from typing import Optional, List
from .models import Inspector, InspectorCreate, InspectorUpdate
from dispatch.mill.models import Mill, MillRead


def get(*, db_session, id: int) -> Optional[Inspector]:
    return db_session.query(Inspector).filter(Inspector.id == id).one_or_none()

def get_by_code(*, db_session, code: str) -> Optional[Inspector]:
    return db_session.query(Inspector).filter(Inspector.code == code).one_or_none()

def get_by_ids(*, db_session, ids: list) ->  List[Optional[Inspector]]:
    """Returns an MenuButton given an MenuButton id."""
    return db_session.query(Inspector).filter(Inspector.id.in_(ids)).all()

def create(*, db_session, inspector_in: InspectorCreate) -> Inspector:

    mill = db_session.query(Mill).filter(Mill.id == inspector_in.mill_id).one_or_none()
    inspector = Inspector(**inspector_in.dict(
        exclude={"flex_form_data", "mill", "spec"}
    ),mill=mill)
    db_session.add(inspector)
    db_session.commit()
    return inspector

def update(
    db_session,
    item: Inspector,
    item_in: InspectorUpdate,
) -> Inspector:
    update_data = item_in.dict(
        exclude={"flex_form_data", "mill", "spec", "created_at"},
    )
    for field, field_value in update_data.items():
        setattr(item, field, field_value)
    
    db_session.add(item)
    db_session.commit()
    return item

def delete(*, db_session, id: int):
    item = db_session.query(Inspector).filter(Inspector.id == id).update({"is_deleted": 1})
    db_session.commit()
    return item


def get_all_select(*, db_session) -> List[Optional[Inspector]]:
    """Returns all Inspectors."""
    return db_session.query(Inspector.id,Inspector.code,Inspector.name).all()


def get_inspectors_by_mill_id(*, db_session, mill_id: int) -> List[Inspector]:
    query = db_session.query(Inspector)
    if mill_id:
        query = query.filter(Inspector.mill_id == mill_id)
    return query.all()
