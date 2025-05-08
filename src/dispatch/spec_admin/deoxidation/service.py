
from datetime import datetime
from typing import List, Optional
from sqlalchemy.sql.functions import func
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

from .models import (SpecDeoxidation, SpecDeoxidationBase, SpecDeoxidationCreate,
                     SpecDeoxidationRead, SpecDeoxidationUpdate)

from dispatch.cast.models import Cast
from dispatch.spec_admin.spec.models import Spec

def get(*, db_session, id: int) -> Optional[SpecDeoxidation]:
    """Returns an DeoxidationBase given an DeoxidationBase id."""
    return db_session.query(SpecDeoxidation).filter(SpecDeoxidation.id == id).one_or_none()


def get_all(*, db_session) -> List[Optional[SpecDeoxidation]]:
    """Returns all Deoxidation."""
    return db_session.query(SpecDeoxidation)

def create(*, db_session, deoxidation_in: SpecDeoxidationCreate) -> SpecDeoxidation:
    """Creates an spec."""

    if deoxidation_in.spec_id:
        spec = db_session.query(Spec).filter(Spec.id == deoxidation_in.spec_id).one_or_none()

    contact = SpecDeoxidation(**deoxidation_in.dict(exclude={"flex_form_data", "spec"}),
                           spec=spec,
                           flex_form_data=deoxidation_in.flex_form_data)
    try:
        db_session.add(contact)
        db_session.commit()
    except IntegrityError:
        raise HTTPException(status_code=400, detail="The deoxidation version with this code already exists.")

    return contact


def update(
    *,
    db_session,
    deoxidation: SpecDeoxidation,
    deoxidation_in: SpecDeoxidationUpdate
    ) -> SpecDeoxidation:

    if deoxidation_in.spec_id:
        deoxidation.spec = db_session.query(Spec).filter(Spec.id == deoxidation_in.spec_id).one_or_none()

    update_data = deoxidation_in.dict(
        exclude={"flex_form_data", "spec"},
    )
    for field, field_value in update_data.items():
        setattr(deoxidation, field, field_value)

    deoxidation.flex_form_data = deoxidation_in.flex_form_data
    db_session.add(deoxidation)
    db_session.commit()
    return deoxidation


def delete(*, db_session, id: int):

    deoxidation = db_session.query(SpecDeoxidation).filter(SpecDeoxidation.id == id).one_or_none()

    if deoxidation:
        deoxidation.is_deleted = 1
    db_session.add(deoxidation)
    db_session.commit()
    return deoxidation