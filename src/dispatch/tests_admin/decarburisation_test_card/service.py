
from datetime import datetime
from typing import List, Optional
from sqlalchemy.sql.functions import func
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

from .models import (TestDecarburisation, TestDecarburisationBase, TestDecarburisationCreate,
                     TestDecarburisationRead, TestDecarburisationUpdate)

from dispatch.cast.models import Cast
from dispatch.spec_admin.spec.models import Spec

def get(*, db_session, id: int) -> Optional[TestDecarburisation]:
    """Returns an TestDecarburisationBase given an TestDecarburisationBase id."""
    return db_session.query(TestDecarburisation).filter(TestDecarburisation.id == id).one_or_none()


def get_all(*, db_session) -> List[Optional[TestDecarburisation]]:
    """Returns all TestDecarburisation."""
    return db_session.query(TestDecarburisation)

def create(*, db_session, decarburisation_test_card_in: TestDecarburisationCreate) -> TestDecarburisation:
    """Creates an spec."""

    if decarburisation_test_card_in.cast_id:
        cast = db_session.query(Cast).filter(Cast.id == decarburisation_test_card_in.cast_id).one_or_none()

    if decarburisation_test_card_in.spec_id:
        spec = db_session.query(Spec).filter(Spec.id == decarburisation_test_card_in.spec_id).one_or_none()

    contact = TestDecarburisation(**decarburisation_test_card_in.dict(exclude={"flex_form_data", "cast", "spec"}),
                           flex_form_data=decarburisation_test_card_in.flex_form_data)
    try:
        db_session.add(contact)
        db_session.commit()
    except IntegrityError:
        raise HTTPException(status_code=400, detail="The decarburisation test card version with this code already exists.")

    return contact


def update(
    *,
    db_session,
    decarburisation_test_card: TestDecarburisation,
    decarburisation_test_card_in: TestDecarburisationUpdate
    ) -> TestDecarburisation:

    if decarburisation_test_card_in.cast_id:
        decarburisation_test_card.cast = db_session.query(Cast).filter(Cast.id == decarburisation_test_card_in.cast_id).one_or_none()

    if decarburisation_test_card_in.spec_id:
        decarburisation_test_card.spec = db_session.query(Spec).filter(Spec.id == decarburisation_test_card_in.spec_id).one_or_none()

    update_data = decarburisation_test_card_in.dict(
        exclude={"flex_form_data", "cast", "spec"},
    )
    for field, field_value in update_data.items():
        setattr(decarburisation_test_card, field, field_value)

    decarburisation_test_card.flex_form_data = decarburisation_test_card_in.flex_form_data
    db_session.add(decarburisation_test_card)
    db_session.commit()
    return decarburisation_test_card


def delete(*, db_session, id: int):

    decarburisation_test_card = db_session.query(TestDecarburisation).filter(TestDecarburisation.id == id).one_or_none()
    
    if decarburisation_test_card:
        decarburisation_test_card.is_deleted = 1
    db_session.add(decarburisation_test_card)
    db_session.commit()
    return decarburisation_test_card 


def get_by_test_id(*, db_session, test_id: int) -> TestDecarburisation:
    return db_session.query(TestDecarburisation).filter(TestDecarburisation.test_id == test_id).one_or_none()
