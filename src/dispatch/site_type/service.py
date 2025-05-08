from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from .models import SiteType, SiteTypeCreate, SiteTypeUpdate
from dispatch.mill.service import get_by_code as get_by_code_mill


def get_site_type(*, db_session: Session, id: int) -> Optional[SiteType]:
    """Returns a SiteType by its id."""
    return db_session.query(SiteType).filter(SiteType.id == id).one_or_none()


def get_site_type_by_code(*, db_session: Session, code: str) -> Optional[SiteType]:
    """Returns a SiteType by its code."""
    return db_session.query(SiteType).filter(SiteType.code == code).one_or_none()


def get_or_create_site_type(*, db_session: Session, code: str, **kwargs) -> SiteType:
    """Gets or creates a SiteType."""
    site_type = get_site_type_by_code(db_session=db_session, code=code)
    if not site_type:
        site_type_in = SiteTypeCreate(**kwargs)
        site_type = create_site_type(db_session=db_session, site_type_in=site_type_in)
    return site_type


def create_site_type(*, db_session: Session, site_type_in: SiteTypeCreate) -> SiteType:
    """Creates a new SiteType."""
    mill = None
    if site_type_in.mill_code:
        mill = get_by_code_mill(db_session=db_session, code=site_type_in.mill_code)
    if mill:
        site_type_in.mill_id = mill.id
    site_type = SiteType(**site_type_in.dict(exclude={"mill_code", "mill"}))
    db_session.add(site_type)
    db_session.commit()
    return site_type


def update_site_type(*, db_session: Session, site_type: SiteType, site_type_in: SiteTypeUpdate) -> SiteType:
    """Updates an existing SiteType."""
    mill = None
    if site_type_in.mill_code:
        mill = get_by_code_mill(db_session=db_session, code=site_type_in.mill_code)
    if mill:
        site_type_in.mill_id = mill.id
    update_data = site_type_in.dict(exclude={"flex_form_data", "mill_code", "mill"})
    for field, value in update_data.items():
        setattr(site_type, field, value)

    site_type.flex_form_data = site_type_in.flex_form_data
    db_session.add(site_type)
    db_session.commit()
    return site_type


def delete_site_type(*, db_session: Session, id: int) -> bool:
    """Deletes a SiteType by its id."""
    site_type = db_session.query(SiteType).filter(SiteType.id == id).first()
    if site_type:
        db_session.query(SiteType).filter(SiteType.id == id).update({"is_deleted": 1})
        db_session.commit()
        return True
    return False


def get_all_site_types(*, db_session: Session) -> List[SiteType]:
    """Returns all SiteTypes."""
    return db_session.query(SiteType).all()


def get_site_type_codes(*, db_session: Session) -> List[str]:
    """Returns all site type codes."""
    codes = [site_type.code for site_type in db_session.query(SiteType.code).all()]
    return codes


def get_site_types_by_mill_id(*, db_session: Session, mill_id: int) -> List[SiteType]:
    """Returns SiteTypes by mill id."""
    return db_session.query(SiteType).filter(SiteType.mill_id == mill_id).all()


def get_site_type_codes_list(*, db_session):
    return [code for code, in db_session.query(SiteType.code).all()]


def get_site_types_by_mill_code(*, db_session: Session, mill_code: str) -> List[SiteType]:
    """Returns SiteTypes by mill code."""
    mill_id = get_by_code_mill(db_session=db_session, code=mill_code).id
    site_types = db_session.query(SiteType).filter(SiteType.mill_id == mill_id).all()
    return site_types