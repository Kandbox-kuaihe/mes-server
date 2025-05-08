
from typing import List, Optional
from fastapi import HTTPException
from dispatch.mill.models import Mill
from dispatch.spec_admin.spprodan.models import Spprodan
from .models import SpprodanOtherElement
from .models import SpprodanOtherElementCreate, SpprodanOtherElementUpdate, SpprodanOtherElementCreate
from sqlalchemy_filters import apply_pagination
from sqlalchemy.exc import IntegrityError

def get(*, db_session, id: int) -> Optional[SpprodanOtherElement]:
    """Returns an spprodan_other_element given an spprodan_other_element id."""
    return db_session.query(SpprodanOtherElement).filter(SpprodanOtherElement.id == id).one_or_none()


def get_by_code(*, db_session, code: str) -> Optional[SpprodanOtherElement]:
    """Returns an spprodan_other_element given an spprodan_other_element code address."""
    return db_session.query(SpprodanOtherElement).filter(SpprodanOtherElement.code == code).one_or_none()

def get_by_spprodan_id(*, db_session, id: int) -> Optional[SpprodanOtherElement]:
    """Returns an spprodan_other_element given an spprodan id."""
    return db_session.query(SpprodanOtherElement).filter(SpprodanOtherElement.spprodan_id == id).all()


def create(
    *, 
    spprodan_id: int,
    db_session, 
    spprodan_other_element_in: SpprodanOtherElementCreate,
    current_user
) -> SpprodanOtherElement:                                                      
    """Creates an spprodan_other_element."""
    spprodan = None
    if spprodan_id:
            spprodan = db_session.query(Spprodan).filter(Spprodan.id == spprodan_id).one_or_none()

    for spprodan_other_element in spprodan_other_element_in.other_element:
        spprodan_other_element.created_by = current_user.email
        spprodan_other_element.updated_by = current_user.email
        contact = SpprodanOtherElement(**spprodan_other_element.dict(exclude={"flex_form_data", "spprodan"}),
                        spprodan=spprodan,
                        flex_form_data=spprodan_other_element.flex_form_data)
        db_session.add(contact)
    
    db_session.commit()
    return contact



def update(
    *,
    db_session,
    spprodan_other_element: SpprodanOtherElement,
    spprodan_other_element_in: SpprodanOtherElementUpdate,
) -> SpprodanOtherElement:
    

    update_data = spprodan_other_element_in.dict(
        exclude={"flex_form_data", "spprodan"},
    )
    for field, field_value in update_data.items():
        setattr(spprodan_other_element, field, field_value)

    spprodan_other_element.flex_form_data = spprodan_other_element_in.flex_form_data
    db_session.add(spprodan_other_element)
    db_session.commit()
    return spprodan_other_element


def delete(*, db_session, id: int):
    spprodan_other_element = db_session.query(SpprodanOtherElement).filter(SpprodanOtherElement.id == id).one_or_none()
    
    if spprodan_other_element:
        spprodan_other_element.is_deleted = 1
    db_session.add(spprodan_other_element)
    db_session.commit()

    return spprodan_other_element

