
from typing import List, Optional

from sqlalchemy import and_

from dispatch.mill.models import Mill
from dispatch.spec_admin.spec.models import Spec
from .models import Quality,QualityCreate, QualityUpdate
from sqlalchemy_filters import apply_pagination
from ..quality_element.models import QualityElement

def get(*, db_session, id: int) -> Optional[Quality]:
    """Returns an spmainel given an spmainel id."""
    return db_session.query(Quality).filter(Quality.id == id).one_or_none()


def create(*, db_session, quality_in: QualityCreate) -> Quality:
    """Creates an Quality with multiple child records."""

    # spec = None
    # mill = None
    # if quality_in.spec_id:
    #     spec = db_session.query(Spec).filter(Spec.id == quality_in.spec_id).one_or_none()

    # if quality_in.mill_id:
    #     mill = db_session.query(Mill).filter(Mill.id == quality_in.mill_id).one_or_none()

    main_record = Quality(
        # **quality_in.dict(exclude={"other_element", "spec", "mill", "flex_form_data"}),
        **quality_in.dict(exclude={"flex_form_data"}),
        # mill=mill,
        # spec=spec,
        flex_form_data=quality_in.flex_form_data,
    )
    db_session.add(main_record)
    db_session.flush()
    # if quality_in.other_element:
    #     child_records = [
    #         QualityElement(
    #             **detail.dict(exclude={"spmainel_id"}),
    #             spmainel=main_record
    #         )
    #         for detail in quality_in.other_element
    #     ]
        # db_session.add_all(child_records)

    db_session.commit()
    db_session.refresh(main_record)

    return main_record


def update(
    *,
    db_session,
    spmainel: Quality,
    spmainel_in: QualityUpdate,
) -> Quality:
    
    if spmainel_in.mill_id:
        spmainel.mill = db_session.query(Mill).filter(Mill.id == spmainel_in.mill_id).one_or_none()


    update_data = spmainel_in.dict(
        # exclude={"flex_form_data", "spec", "mill"},
        exclude={"flex_form_data", "created_at"},
    )
    for field, field_value in update_data.items():
        setattr(spmainel, field, field_value)

    spmainel.flex_form_data = spmainel_in.flex_form_data
    db_session.add(spmainel)
    db_session.commit()
    return spmainel



def delete(*, db_session, id: int):
    spmainel = db_session.query(Quality).filter(Quality.id == id).one_or_none()
    
    if spmainel:
        spmainel.is_deleted = 1
    db_session.add(spmainel)
    db_session.commit()

    return spmainel


def get_by_code_and_mill(db_session, code: str, mill_id: int):
    return db_session.query(Quality).filter(and_(
        Quality.code == code,
        Quality.mill_id == mill_id,
    )).first()



