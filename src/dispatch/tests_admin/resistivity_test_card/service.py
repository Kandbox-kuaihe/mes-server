from typing import List, Optional
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

from .models import (
    TestResistivity,
    TestResistivityCreate,
    TestResistivityUpdate,
)

from dispatch.cast.models import Cast
from dispatch.spec_admin.spec.models import Spec


def get(*, db_session, id: int) -> Optional[TestResistivity]:
    """Returns an TestResistivityBase given an TestResistivityBase id."""
    return (
        db_session.query(TestResistivity)
        .filter(TestResistivity.id == id)
        .one_or_none()
    )


def get_all(*, db_session) -> List[Optional[TestResistivity]]:
    """Returns all TestResistivity."""
    return db_session.query(TestResistivity)

def get_by_test_id(*, db_session, test_id: str) -> Optional[TestResistivity]:
    """Returns an TestBend given an TestBend test_id address."""
    if not test_id: return
    return db_session.query(TestResistivity).filter(TestResistivity.test_id == test_id).one_or_none()


def create(
    *, db_session, resistivity_test_card_in: TestResistivityCreate
) -> TestResistivity:
    """Creates an spec."""

    contact = TestResistivity(
        **resistivity_test_card_in.dict(exclude={"flex_form_data", "cast", "spec"}),
        flex_form_data=resistivity_test_card_in.flex_form_data
    )
    try:
        db_session.add(contact)
        db_session.commit()
    except IntegrityError:
        raise HTTPException(
            status_code=400,
            detail="The decarburisation test card version with this code already exists.",
        )

    return contact


def update(
    *,
    db_session,
   resistivity_test_card: TestResistivity,
   resistivity_test_card_in: TestResistivityUpdate
) -> TestResistivity:

    update_data = resistivity_test_card_in.dict(
        exclude={"flex_form_data", "cast", "spec"},
    )
    for field, field_value in update_data.items():
        setattr(resistivity_test_card, field, field_value)

    resistivity_test_card.flex_form_data = (
        resistivity_test_card_in.flex_form_data
    )
    db_session.add(resistivity_test_card)
    db_session.commit()
    return resistivity_test_card


def delete(*, db_session, id: int):

    resistivity_test_card = (
        db_session.query(TestResistivity)
        .filter(TestResistivity.id == id)
        .one_or_none()
    )

    if resistivity_test_card:
        resistivity_test_card.is_deleted = 1
    db_session.add(resistivity_test_card)
    db_session.commit()
    return resistivity_test_card
