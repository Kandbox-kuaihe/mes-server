
from datetime import datetime
from typing import List, Optional
from sqlalchemy.sql.functions import func
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

from .models import (TestHydrogen, TestHydrogenBase, TestHydrogenCreate,
                     TestHydrogenRead, TestHydrogenUpdate)

from dispatch.cast.models import Cast
from dispatch.spec_admin.spec.models import Spec

def get(*, db_session, id: int) -> Optional[TestHydrogen]:
    """Returns an TestHydrogenBase given an TestHydrogenBase id."""
    return db_session.query(TestHydrogen).filter(TestHydrogen.id == id).one_or_none()


def get_all(*, db_session) -> List[Optional[TestHydrogen]]:
    """Returns all TestHydrogen."""
    return db_session.query(TestHydrogen)

def create(*, db_session, product_hydrogen_test_card_in: TestHydrogenCreate) -> TestHydrogen:
    """Creates an spec."""
    contact = TestHydrogen(**product_hydrogen_test_card_in.dict(exclude={"flex_form_data", "cast", "spec"}),
                           flex_form_data=product_hydrogen_test_card_in.flex_form_data)
    try:
        db_session.add(contact)
        db_session.commit()
    except IntegrityError:
        raise HTTPException(status_code=400, detail="The product hydrogen test card version with this code already exists.")

    return contact


def update(
    *,
    db_session,
    product_hydrogen_test_card: TestHydrogen,
    product_hydrogen_test_card_in: TestHydrogenUpdate
    ) -> TestHydrogen:

    if product_hydrogen_test_card_in.cast_id:
        product_hydrogen_test_card.cast = db_session.query(Cast).filter(Cast.id == product_hydrogen_test_card_in.cast_id).one_or_none()

    if product_hydrogen_test_card_in.spec_id:
        product_hydrogen_test_card.spec = db_session.query(Spec).filter(Spec.id == product_hydrogen_test_card_in.spec_id).one_or_none()

    update_data = product_hydrogen_test_card_in.dict(
        exclude={"flex_form_data", "cast", "spec"},
    )
    for field, field_value in update_data.items():
        setattr(product_hydrogen_test_card, field, field_value)

    product_hydrogen_test_card.flex_form_data = product_hydrogen_test_card_in.flex_form_data
    db_session.add(product_hydrogen_test_card)
    db_session.commit()
    return product_hydrogen_test_card


def delete(*, db_session, id: int):

    product_hydrogen_test_card = db_session.query(TestHydrogen).filter(TestHydrogen.id == id).one_or_none()
    
    if product_hydrogen_test_card:
        product_hydrogen_test_card.is_deleted = 1
    db_session.add(product_hydrogen_test_card)
    db_session.commit()
    return product_hydrogen_test_card 


def get_by_test_id(*, db_session, test_id: int) -> TestHydrogen:
    return db_session.query(TestHydrogen).filter(TestHydrogen.test_id == test_id).one_or_none()
