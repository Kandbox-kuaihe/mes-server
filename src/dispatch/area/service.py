import json
import warnings
# import random
from typing import List, Optional, Tuple, Any
from sqlalchemy.sql.functions import func
from fastapi.encoders import jsonable_encoder
from sqlalchemy import case, and_
from dispatch.config import SQLALCHEMY_DATABASE_URI, get_mill_ops, MILLEnum
from dispatch.database import SessionLocal
from enum import Enum
from .models import Area, AreaCreate, AreaUpdate, AreaCreate
from dispatch.mill.models import Mill
from dispatch.system_admin.auth.service import get as user_get
from dispatch.site import service as siteservice
from dispatch.site.models import Site
from dispatch.site_type.models import SiteType
from dispatch.plugin import service as plugin_service


def get(*, db_session, area_id: int) -> Optional[Area]:
    """Returns an area given an area id."""
    return db_session.query(Area).filter(Area.id == area_id).one_or_none()


def get_by_code(*, db_session, code: str) -> Optional[Area]:
    """Returns an area given an area code address."""
    return db_session.query(Area).filter(Area.code == code).one_or_none()


def get_default_area(*, db_session) -> Optional[Area]:
    """Returns an area given an area code address."""
    return db_session.query(Area).first()


def get_all(*, db_session) -> List[Optional[Area]]:
    """Returns all areas."""
    return db_session.query(Area)


def get_by_code_org_id(*, db_session, code: str, org_id: int) -> Optional[Area]:
    """Returns an worker given an worker code address."""
    return db_session.query(Area).filter(Area.code == code, Area.org_id == org_id).one_or_none()


def get_by_team(*, team_id: int, db_session) -> List[Optional[Area]]:
    """Returns all areas."""
    return db_session.query(Area).filter(Area.team_id == team_id).all()


def get_by_org_id_count(*, db_session, org_id: int) -> Optional[int]:
    """Returns an job based on the given code."""
    return db_session.query(func.count(Area.id)).filter(Area.org_id == org_id).scalar()


def get_or_create(*, db_session, code: str, **kwargs) -> Area:
    """Gets or creates an area."""
    contact = get_by_code(db_session=db_session, code=code)

    if not contact:
        contact_plugin = plugin_service.get_active(db_session=db_session, plugin_type="contact")
        area_info = contact_plugin.instance.get(code, db_session=db_session)
        kwargs["code"] = area_info.get("code", code)
        kwargs["name"] = area_info.get("fullname", "Unknown")
        kwargs["weblink"] = area_info.get("weblink", "Unknown")
        area_in = AreaCreate(**kwargs)
        contact = create(db_session=db_session, area_in=area_in)

    return contact


def create(*, db_session, area_in: AreaCreate) -> Area:
    """Creates an area."""
    # location_obj = None
    # location_code = None
    # if area_in.location:
    #     location_obj = location_service.get(
    #         db_session=db_session, code=area_in.location.code)
    #     location_code = location_obj.code 
    # else:
    #     location_obj = None

    contact = Area(**area_in.dict(exclude={"flex_form_data", "site_code"}),
                   flex_form_data=area_in.flex_form_data)

    site = siteservice.get(db_session=db_session, id=area_in.site_id)
    contact.site = site

    db_session.add(contact)
    db_session.commit()
    return contact


def new_create(*, db_session, area_in: AreaCreate) -> Area:
    """Creates an area."""
    # location_obj = None
    # location_code = None
    # if area_in.location:
    #     location_obj = location_service.get(
    #         db_session=db_session, code=area_in.location.code)
    #     location_code = location_obj.code
    # else:
    #     location_obj = None

    site = siteservice.get_by_code(db_session=db_session, code=area_in.site_code)
    area_in.site_id = site.id
    contact = Area(**area_in.dict(exclude={"flex_form_data", "site_code", "site", "mill"}),
                   flex_form_data=area_in.flex_form_data)
    db_session.add(contact)
    db_session.commit()
    return contact


def update(
        *,
        db_session,
        area: Area,
        area_in: AreaUpdate,
) -> Area:
    site = siteservice.get_by_code(db_session=db_session, code=area_in.site_code)
    area_in.site_id = site.id
    update_data = area_in.dict(
        #
        exclude={"flex_form_data", "site_code", "site", "mill"},
    )
    for field, field_value in update_data.items():
        setattr(area, field, field_value)

    area.flex_form_data = area_in.flex_form_data
    db_session.add(area)
    db_session.commit()
    return area


def delete(*, db_session, area_id: int):
    db_session.query(Area).filter(Area.id == area_id).delete()
    db_session.commit()


def get_area_codes(*, db_session):
    codes = []
    result = db_session.query(Area.code).filter(Area.type == "semi").all()
    if not result:
        return codes
    for i in result:
        codes.append(i[0])
    return codes


def get_area_codes_type_all(*, db_session):
    codes = []
    result = db_session.query(Area.code, Area.type).all()
    if not result:
        return codes
    for i in result:
        codes.append({
            "code": i[0],
            "type": i[1],
        })
    return codes

def get_type_list(*, db_session):
    type_list = [t[0] for t in db_session.query(Area.type).distinct().all()]
    return type_list

def get_area_codes_type(*, db_session, s_or_f):
    codes = []
    result = db_session.query(Area.code).filter(Area.type == s_or_f).all()
    if not result:
        return codes
    for i in result:
        codes.append(i[0])
    return codes


def get_area_type_semi(db_session):
    return get_area_codes_type(db_session=db_session, s_or_f="s-semi")


def get_area_type_finished(db_session):
    return get_area_codes_type(db_session=db_session, s_or_f="f-finished")


def get_area_by_site(*, db_session, site_code: str, mill_id):
    area_codes = []
    site = db_session.query(Site).filter(and_(Site.code == site_code,
                                              Site.mill_id == mill_id)).one_or_none()

    if not site:
        return area_codes
    site_id = site.id
    result = db_session.query(Area).filter(and_(Area.site_id == site_id,
                                                Site.mill_id == mill_id)).all()
    if not result:
        return area_codes
    else:
        for i in result:
            area_codes.append(i.code)
    return area_codes


################# 新的区分 area type 代码 ####################
class MAPPING_TYPE(Enum):
    SEMI = "s-semi"
    FINISHED = "f-finished_product"


def get_area_code_by_type(*, db_session, s_or_f: str, mill_id):
    """
    通过user mill和 semi finished 区分 area code
    """
    result = db_session.query(Area.id, Area.code).filter(and_(Area.type == s_or_f, Area.mill_id == mill_id)).all()
    return [{"area_id": i.id, "area_code": i.code} for i in result]

def get_area_code_by(*, db_session, s_or_f: str, mill_id):
    """
    通过user mill和 semi finished 区分 area code
    """
    if get_mill_ops(mill_id) == MILLEnum.MILL1:
        mill_data = db_session.query(Mill).filter(Mill.id == mill_id).first()
        data = db_session.query(SiteType.id, SiteType.code).filter(
            and_(SiteType.mill_id == mill_id)).first()
        site_data = db_session.query(Site).filter(
            and_(Site.site_type_id == data.id, Site.mill_id == mill_id)).all()
        site_id_list = [site.id for site in site_data]
        result = db_session.query(Area.id, Area.code).filter(and_(Area.type == s_or_f, Area.mill_id == mill_id,
                                                                  Area.site_id.in_(site_id_list))).all()
        return [{"area_id": i.id, "area_code": i.code} for i in result]
    result = db_session.query(Area.id, Area.code).filter(and_(Area.type == s_or_f, Area.mill_id == mill_id)).all()
    return [{"area_id": i.id, "area_code": i.code} for i in result]


def get_site_code_by_type(*, db_session, s_or_f: str, mill_id):
    """
    通过user mill和 semi finished 区分 site code
    """
    result = db_session.query(Site.id, Site.code).filter(
        and_(Site.type == s_or_f, Site.mill_id == mill_id)).all()
    return sorted([{"site_id": i.id, "site_code": i.code} for i in result], key=lambda x: x["site_code"])

def get_site_code_by(*, db_session, s_or_f: str, mill_id):
    if get_mill_ops(mill_id) == MILLEnum.MILL1:
        mill_data = db_session.query(Mill).filter(Mill.id == mill_id).first()
        data = db_session.query(SiteType.id, SiteType.code).filter(
            and_(SiteType.mill_id == mill_id)).first()
        result = db_session.query(Site.id, Site.code).filter(
            and_(Site.site_type_id == data.id, Site.mill_id == mill_id)).all()
        return sorted([{"site_id": i.id, "site_code": i.code} for i in result], key=lambda x: x["site_code"])
    result = db_session.query(Site.id, Site.code).filter(
        and_(Site.type == s_or_f, Site.mill_id == mill_id)).all()
    return sorted([{"site_id": i.id, "site_code": i.code} for i in result], key=lambda x: x["site_code"])


def get_site_type_code_by_type(*, db_session, s_or_f: str, mill_id):
    """
        通过user mill和 semi finished 区分 site type code
        """
    result = db_session.query(SiteType.id, SiteType.code).filter(and_(SiteType.type == s_or_f, SiteType.mill_id == mill_id)).all()
    return sorted([{"site_type_id": i.id, "site_type_code": i.code} for i in result], key=lambda x: x["site_type_code"])

def get_site_type_code_by(*, db_session, s_or_f: str, mill_id):
    if get_mill_ops(mill_id) == MILLEnum.MILL1:
        mill_data = db_session.query(Mill).filter(Mill.id == mill_id).first()
        result = db_session.query(SiteType.id, SiteType.code).filter(
            and_(SiteType.mill_id == mill_id, SiteType.type == s_or_f)).all()
        return sorted([{"site_type_id": i.id, "site_type_code": i.code} for i in result], key=lambda x: x["site_type_code"])
    result = db_session.query(SiteType.id, SiteType.code).filter(and_(SiteType.type == s_or_f, SiteType.mill_id == mill_id)).all()
    return sorted([{"site_type_id": i.id, "site_type_code": i.code} for i in result], key=lambda x: x["site_type_code"])

def get_area_code_by_type_move(db_session, mill_id):
    return get_area_code_by(db_session=db_session, s_or_f=MAPPING_TYPE.FINISHED.value, mill_id=mill_id)


def get_area_code_by_type_semi(db_session, mill_id):
    """
    通过user mill 获取semi area code
    """
    return get_area_code_by_type(db_session=db_session, s_or_f=MAPPING_TYPE.SEMI.value, mill_id=mill_id)


def get_area_code_by_type_finished(db_session, mill_id):
    """
    通过user mill 获取finished area code
    """
    return get_area_code_by_type(db_session=db_session, s_or_f=MAPPING_TYPE.FINISHED.value, mill_id=mill_id)

