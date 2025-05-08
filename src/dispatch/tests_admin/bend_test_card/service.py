
from datetime import datetime
from typing import List, Optional
from sqlalchemy.sql.functions import func
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

from dispatch.tests_admin.test_sample.models import TestSample

from .models import TestBend, TestBendBase, TestBendCreate, TestBendRead, TestBendUpdate

from dispatch.tests_admin.test_list.models import Test
from dispatch.cast.models import Cast
from dispatch.spec_admin.spec.models import Spec

def get(*, db_session, id: int) -> Optional[TestBend]:
    """Returns an bendTestCardBase given an bendTestCardBase id."""
    return db_session.query(TestBend).filter(TestBend.id == id).one_or_none()


def get_all(*, db_session) -> List[Optional[TestBend]]:
    """Returns all TestBend."""
    return db_session.query(TestBend)

def create(*, db_session, bend_test_card_in: TestBendCreate) -> TestBend:
    """Creates an spec."""
    contact = TestBend(**bend_test_card_in.dict(exclude={"flex_form_data", "cast", "spec"}),
                           flex_form_data=bend_test_card_in.flex_form_data)
    try:
        db_session.add(contact)
        db_session.commit()
    except IntegrityError:
        raise HTTPException(status_code=400, detail="The bend test card version with this code already exists.")

    return contact


def update(
    *,
    db_session,
    bend_test_card: TestBend,
    bend_test_card_in: TestBendUpdate
    ) -> TestBend:

    if bend_test_card_in.cast_id:
        bend_test_card.cast = db_session.query(Cast).filter(Cast.id == bend_test_card_in.cast_id).one_or_none()

    if bend_test_card_in.test_sample_id:
        bend_test_card.test_sample = db_session.query(TestSample).filter(TestSample.id == bend_test_card_in.test_sample_id).one_or_none()


    update_data = bend_test_card_in.dict(
        exclude={"flex_form_data", "cast", "test_sample","test"},
    )
    for field, field_value in update_data.items():
        setattr(bend_test_card, field, field_value)

    bend_test_card.flex_form_data = bend_test_card_in.flex_form_data
    db_session.add(bend_test_card)
    db_session.commit()
    return bend_test_card


def delete(*, db_session, id: int):

    bend_test_card = db_session.query(TestBend).filter(TestBend.id == id).one_or_none()
    
    if bend_test_card:
        bend_test_card.is_deleted = 1
    db_session.add(bend_test_card)
    db_session.commit()
    return bend_test_card 


def get_all_by_test_id(*, db_session, test_id: int) -> Optional[TestBend]:
    """Returns an testResultImpactBase given an testResultImpactBase id."""
    query = db_session.query(TestBend).filter(TestBend.test_id == test_id)
    return query.all()


def get_by_test_sample_ids_tbm(*, db_session, test_sample_ids: List[int], inspector_code: Optional[List[str]] = None) -> List[Optional[TestBend]]:
    query = db_session.query(TestBend).join(Test, Test.id==TestBend.test_id).filter(
        Test.test_sample_id.in_(test_sample_ids))
    if inspector_code:
        query = query.filter(TestBend.insp_code.in_(inspector_code))
    return query.all()

def get_by_test_id(*, db_session, test_id: str) -> Optional[TestBend]:
    """Returns an TestBend given an TestBend test_id address."""
    if not test_id: return
    return db_session.query(TestBend).filter(TestBend.test_id == test_id).one_or_none()


def get_all_data_dict_of_spec_id_tbm(*, db_session, test_sample_ids: List[int], inspector_code: Optional[List[str]] = None) -> dict:
    data = get_by_test_sample_ids_tbm(db_session=db_session, test_sample_ids=test_sample_ids, inspector_code=inspector_code)

    dic = {}
    for d in data:
        dic.setdefault(d.test.test_sample_id, []).append(d)
    return dic

