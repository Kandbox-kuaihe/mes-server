
from typing import List, Optional
from fastapi import HTTPException
from dispatch.mill.models import Mill
from dispatch.spec_admin.spmainel.models import Spmainel
from .models import SpmainelOtherElement
from .models import SpmainelOtherElementCreate, SpmainelOtherElementUpdate, SpmainelOtherElementCreate
from sqlalchemy_filters import apply_pagination
from sqlalchemy.exc import IntegrityError

def get(*, db_session, id: int) -> Optional[SpmainelOtherElement]:
    """Returns an spmainel_other_element given an spmainel_other_element id."""
    return db_session.query(SpmainelOtherElement).filter(SpmainelOtherElement.id == id).one_or_none()


def get_by_code(*, db_session, code: str) -> Optional[SpmainelOtherElement]:
    """Returns an spmainel_other_element given an spmainel_other_element code address."""
    return db_session.query(SpmainelOtherElement).filter(SpmainelOtherElement.code == code).one_or_none()

def get_by_spmainel_id(*, db_session, id: int) -> Optional[SpmainelOtherElement]:
    """Returns an spmainel_other_element given an spmainel id."""
    return db_session.query(SpmainelOtherElement).filter(SpmainelOtherElement.spmainel_id == id).all()


def create(
    *, 
    spmainel_id: int,
    db_session, 
    spmainel_other_element_in: SpmainelOtherElementCreate
) -> SpmainelOtherElement:
    """Creates an spmainel_other_element."""
    spmainel = None
    if spmainel_id:
            spmainel = db_session.query(Spmainel).filter(Spmainel.id == spmainel_id).one_or_none()
    for spmainel_other_element in spmainel_other_element_in.other_element:

        contact = SpmainelOtherElement(**spmainel_other_element.dict(exclude={"flex_form_data", "spmainel"}),
                        # mill=mill,
                        spmainel=spmainel,
                        flex_form_data=spmainel_other_element.flex_form_data)
        db_session.add(contact)
    
    db_session.commit()
    return contact



def update(
    *,
    db_session,
    spmainel_other_element: SpmainelOtherElement,
    spmainel_other_element_in: SpmainelOtherElementUpdate,
) -> SpmainelOtherElement:

    update_data = spmainel_other_element_in.dict(
        exclude={"flex_form_data", "spmainel"},
    )
    for field, field_value in update_data.items():
        setattr(spmainel_other_element, field, field_value)

    spmainel_other_element.flex_form_data = spmainel_other_element_in.flex_form_data
    db_session.add(spmainel_other_element)
    db_session.commit()
    return spmainel_other_element


def delete(*, db_session, id: int):
    spmainel_other_element = db_session.query(SpmainelOtherElement).filter(SpmainelOtherElement.id == id).one_or_none()
    
    if spmainel_other_element:
        spmainel_other_element.is_deleted = 1
    db_session.add(spmainel_other_element)
    db_session.commit()

    return spmainel_other_element
