
from datetime import datetime
from typing import List, Optional
from sqlalchemy.sql.functions import func

from .models import Runout, RunoutCreate, RunoutUpdate, RunoutCreate
from dispatch.mill import service as mill_service
from dispatch.product_type import service as product_type_service

def get(*, db_session, runout_id: int) -> Optional[Runout]:
    """Returns an runout given an runout id."""
    return db_session.query(Runout).filter(Runout.id == runout_id).one_or_none()


def get_by_list_code(*, db_session, list_code: List[str]) -> List[Optional[Runout]]:
    """Returns an runout given an runout code address."""
    return db_session.query(Runout).filter(Runout.runout_code.in_(list_code)).all()

def get_by_code(*, db_session, code: str) -> Optional[Runout]:
    """Returns an runout given an runout code address."""
    return db_session.query(Runout).filter(Runout.runout_code == code).one_or_none()

def get_by_semi_code(*, db_session, code: str) -> Optional[Runout]:
    """Returns an runout given an runout code address."""
    return db_session.query(Runout).filter(Runout.semi_code == code).one_or_none()

def get_default_runout(*, db_session ) -> Optional[Runout]:
    """Returns an runout given an runout code address."""
    return db_session.query(Runout).first()


def get_all(*, db_session) -> List[Optional[Runout]]:
    """Returns all runouts."""
    return db_session.query(Runout)


def get_by_code_org_id(*, db_session, code: str, org_id: int) -> Optional[Runout]:
    """Returns an worker given an worker code address."""
    return db_session.query(Runout).filter(Runout.runout_code == code, Runout.org_id == org_id).one_or_none()


def get_by_team(*, team_id: int, db_session) -> List[Optional[Runout]]:
    """Returns all runouts."""
    return db_session.query(Runout).filter(Runout.team_id == team_id).all()

def get_by_concast_code(*, db_session, concast_code: str) -> List[Optional[Runout]]:
    """Returns all runouts ordered by date created in descending order."""
    return (
        db_session.query(Runout)
        .filter(Runout.concast_code == concast_code)
        .order_by(Runout.created_at.desc())
        .all()
    )



def get_by_org_id_count(*, db_session, org_id: int) -> Optional[int]:
    """Returns an job based on the given code."""
    return db_session.query(func.count(Runout.id)).filter(Runout.org_id == org_id).scalar()

def get_runout_id_by_filters(*, db_session,cast_id: int, product_type_id: int, rolling_id: int) -> Optional[int]:
    query = db_session.query(Runout.id).filter(Runout.cast_id == cast_id, Runout.product_type_id == product_type_id, Runout.rolling_id == rolling_id).first()
    return query[0] if query else None

def create(*, db_session, runout_in: RunoutCreate) -> Runout:
    """Creates an runout."""
    mill = None
    product_type = None

    if runout_in.mill_id:
        mill = mill_service.get(db_session=db_session, mill_id=runout_in.mill_id)
    
    if runout_in.product_type_id:
        product_type = product_type_service.get(db_session=db_session, product_type_id=runout_in.product_type_id)

    contact = Runout(**runout_in.model_dump(
        exclude={"mill", "product_type", "rolling", "cast", "semi"}
    ), mill=mill, product_type=product_type)
    contact.product_code = product_type.code if product_type else None
    db_session.add(contact)
    db_session.commit()
    return contact


def update(
    *,
    db_session,
    runout: Runout,
    runout_in: RunoutUpdate,
) -> Runout:

    update_data = runout_in.model_dump(
        exclude={
            "runout_code",
            "created_at",
            "created_by",
            "is_deleted",
            "flex_form_data",
            "mill",
            "product_type",
            "rolling",
            "cast",
            "semi"
        }
    )
    for field, field_value in update_data.items():
        setattr(runout, field, field_value)

    db_session.add(runout)
    db_session.commit()
    return runout


def delete(*, db_session, runout_id: int):
    db_session.query(Runout).filter(Runout.id == runout_id).update({"is_deleted": 1})
    
    db_session.commit()


def get_by_rolling_cast(*, db_session, rolling_id: int, cast_id: int) -> list[Runout]:
    """Returns an job based on the given code."""
    return db_session.query(Runout).filter(Runout.rolling_id == rolling_id, Runout.cast_id == cast_id).all()

def get_by_rolling_id(*, db_session, rolling_id: int) -> list[Runout]:
    runout_list = db_session.query(Runout).filter(Runout.rolling_id == rolling_id).all()
    return runout_list


def get_runout_code_min(*, db_session, rolling_id) -> Optional[str]:
    """Returns the minimum runout_code."""
    min_runout_code = db_session.query(func.min(Runout.runout_code)).filter(Runout.rolling_id == rolling_id).scalar()
    return min_runout_code

def get_runout_code_max(*, db_session, rolling_id) -> Optional[str]:
    max_runout_code = db_session.query(func.max(Runout.runout_code)).filter(Runout.rolling_id == rolling_id).scalar()
    return max_runout_code