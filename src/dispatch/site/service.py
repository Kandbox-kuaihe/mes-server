import json
from fastapi import HTTPException
from typing import List, Optional
from sqlalchemy.sql.functions import func
from .models import Site, SiteCreate, SiteUpdate
from dispatch.site_type.models import SiteType
from dispatch.site_type.service import get_site_type_by_code

def get(*, db_session, id: int) -> Optional[Site]:
    """Returns an depot given an depot id."""
    return db_session.query(Site).filter(Site.id == id).one_or_none()


def get_by_code(*, db_session, code: str) -> Optional[Site]:
    """Returns an depot given an depot code address."""
    return db_session.query(Site).filter(Site.code == code).first()


def get_or_create(*, db_session, code: str, **kwargs) -> Site:
    """Gets or creates an depot."""
    contact = get_by_code(db_session=db_session, code=code)
    if not contact:
        kwargs["code"] = code
        site_in = SiteCreate(**kwargs)
        contact = create(db_session=db_session, site_in=site_in)

    return contact


def create(*, db_session, site_in: SiteCreate) -> Site:
    """Creates an depot."""
    # exclude={"flex_form_data", "location"}
    contact = Site(**site_in.dict(exclude={"site_type_code"}))
    db_session.add(contact)
    db_session.commit()
    return contact


def new_create(*, db_session, site_in: SiteCreate) -> Site:
    """Creates an depot."""
    # exclude={"flex_form_data", "location"}
    site_type = get_site_type_by_code(db_session=db_session, code=site_in.site_type_code)
    if not site_type:
        raise HTTPException(status_code=400, detail="Site type not found")
    site_in.site_type_id = site_type.id
    contact = Site(**site_in.dict(exclude={"site_type", "site_type_code", "mill"}))
    db_session.add(contact)
    db_session.commit()
    return contact


def get_site_codes(*, db_session):
    codes = []
    result = db_session.query(Site.code).all()
    if not result:
        return codes
    for i in result:
        codes.append(i[0])
    print(codes)
    return codes


# def update(
#     *,
#     db_session,
#     depot: Site,
#     depot_in: DepotUpdate,
# ) -> Site:

#     update_data = depot_in.dict(
#        
#         exclude={"flex_form_data", "location"},
#     )
#     if depot_in.location and (not depot.location or depot_in.location.code != depot.location.code):
#         location_obj = location_service.get_or_create_by_code(
#             db_session=db_session, location_in=depot_in.location)
#         depot.location = location_obj

#     for field, field_value in update_data.items():
#         setattr(depot, field, field_value)

#     depot.flex_form_data = depot_in.flex_form_data
#     db_session.add(depot)
#     db_session.commit()
#     return depot


def update(
        db_session,
        item: Site,
        item_in: SiteUpdate,
) -> Site:
    site_type = get_site_type_by_code(db_session=db_session, code=item_in.site_type_code)
    item_in.site_type_id = site_type.id

    update_data = item_in.dict(
        #
        exclude={"flex_form_data", "site_type_code", "site_type", "mill"},
    )
    for field, field_value in update_data.items():
        setattr(item, field, field_value)

    item.flex_form_data = item_in.flex_form_data
    db_session.add(item)
    db_session.commit()
    return item


def delete(*, db_session, id: int):
    db_session.query(Site).filter(Site.id == id).update({"is_deleted": 1})
    db_session.commit()


def get_site_by_site_type(*, db_session, site_type_code: str):
    site_codes = []
    site_type = db_session.query(SiteType).filter(SiteType.code == site_type_code).one_or_none()

    if not site_type:
        return site_codes
    site_type_id = site_type.id
    result = db_session.query(Site).filter(Site.site_type_id == site_type_id).all()
    if not result:
        return site_codes
    else:
        for i in result:
            site_codes.append(i.code)
    return site_codes
