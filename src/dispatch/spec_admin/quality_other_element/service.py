
from typing import List, Optional
from fastapi import HTTPException
from dispatch.mill.models import Mill
from dispatch.spec_admin.spprodan.models import Spprodan
from .models import (
    QualityOtherElement,
    QualityOtherElementCreate,
    QualityOtherElementUpdate,
)
from sqlalchemy_filters import apply_pagination
from sqlalchemy.exc import IntegrityError
from ..quality.models import Quality
def get(*, db_session, id: int) -> Optional[QualityOtherElement]:
    """Returns an quality_other_element given an quality_other_element id."""
    return db_session.query(QualityOtherElement).filter(QualityOtherElement.id == id).one_or_none()


def get_by_code(*, db_session, code: str) -> Optional[QualityOtherElement]:
    """Returns an quality_other_element given an quality_other_element code address."""
    return db_session.query(QualityOtherElement).filter(QualityOtherElement.code == code).one_or_none()

def get_by_element_id(*, db_session, quality_element_id: int) -> Optional[QualityOtherElement]:
    """Returns an quality_other_element given an quality_other_element id."""
    return db_session.query(QualityOtherElement).filter(QualityOtherElement.quality_element_id == quality_element_id).all()

def create(
    *, 
    quality_other_element_id: int,
    db_session, 
    quality_other_element_in: QualityOtherElementCreate,
    current_user
) -> QualityOtherElement:                                                      
    """Creates an quality_other_element."""
    quality_other_element = None
    if quality_other_element_id:
            quality_other_element = db_session.query(Quality).filter(Quality.id == quality_other_element_id).one_or_none()
    for quality_other_element in quality_other_element_in.quality_other_element:
        
        contact = QualityOtherElement(**quality_other_element.dict(exclude={"flex_form_data", "quality"}),
                        quality_other_element=quality_other_element,
                        flex_form_data=quality_other_element.flex_form_data)
        db_session.add(contact)
    
    db_session.commit()
    return contact



def update(
    *,
    db_session,
    quality_other_element: QualityOtherElement,
    quality_other_element_in: QualityOtherElementUpdate,
) -> QualityOtherElement:

    update_data = quality_other_element_in.dict(
        exclude={"flex_form_data", "quality"},
    )
    for field, field_value in update_data.items():
        setattr(quality_other_element, field, field_value)

    quality_other_element.flex_form_data = quality_other_element_in.flex_form_data
    db_session.add(quality_other_element)
    db_session.commit()
    return quality_other_element


def delete(*, db_session, id: int):
    quality_other_element = db_session.query(QualityOtherElement).filter(QualityOtherElement.id == id).one_or_none()
    
    if quality_other_element:
        quality_other_element.is_deleted = 1
    db_session.add(quality_other_element)
    db_session.commit()

    return quality_other_element

