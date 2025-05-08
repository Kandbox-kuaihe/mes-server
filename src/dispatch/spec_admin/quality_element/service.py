
from typing import List, Optional
from fastapi import HTTPException
from dispatch.mill.models import Mill
from dispatch.spec_admin.spec.models import Spec
from dispatch.spec_admin.spprodan.models import Spprodan
from .models import (QualityElement,
                     QualityElementCreate,
                     QualityElementUpdate,
                     QualityElement)
from..quality_other_element.models import QualityOtherElement
from sqlalchemy_filters import apply_pagination
from sqlalchemy.exc import IntegrityError
from dispatch.spec_admin.quality_other_element.service import get_by_element_id

def get(*, db_session, id: int):
    """Returns an quality_element given an quality_element id."""
    return db_session.query(QualityElement).filter(QualityElement.id == id).one_or_none()


def create(*, db_session, quality_element_in: QualityElementCreate) -> QualityElement:
    """Creates an quality_element with multiple child records."""

    main_record = QualityElement(
        **quality_element_in.dict(exclude={"quality_other_element", "flex_form_data"}), 
        flex_form_data=quality_element_in.flex_form_data,
    )
    db_session.add(main_record)
    db_session.flush()
    if quality_element_in.quality_other_element:
        child_records = [
            QualityOtherElement(
                **detail.dict(exclude={"quality_element_id"}),
                quality_element=main_record
            )
            for detail in quality_element_in.quality_other_element
        ]
        db_session.add_all(child_records)

    db_session.commit()
    db_session.refresh(main_record)

    return main_record



def update(
    *,
    db_session,
    quality_element: QualityElement,
    quality_element_in: QualityElementUpdate,
) -> QualityElement:
    
    # if quality_element_in.mill_id:
    #     quality_element.mill = db_session.query(Mill).filter(Mill.id == quality_element_in.mill_id).one_or_none()


    update_data = quality_element_in.dict(
        exclude={"flex_form_data", "quality_other_element"},
    )
    for field, field_value in update_data.items():
        setattr(quality_element, field, field_value)

    quality_element.flex_form_data = quality_element_in.flex_form_data
    db_session.add(quality_element)
    db_session.commit()

     # 更新 QualityOtherElement 记录
    if quality_element_in.quality_other_element:
        other_elements = get_by_element_id(db_session=db_session, quality_element_id=quality_element.id)
        existing_other_elements = {elem.id: elem for elem in other_elements}

        # 遍历新的 QualityOtherElement 数据
        new_other_element_ids = []
        for detail in quality_element_in.quality_other_element:
            new_other_element_ids.append(detail.id)
            if detail.id in existing_other_elements:
                # 更新现有的记录
                existing_record = existing_other_elements.pop(detail.id)
                for field, field_value in detail.dict(exclude={"id", "quality_element_id"}).items():
                    setattr(existing_record, field, field_value)
                db_session.add(existing_record)
            else:
                # 添加新的记录
                new_record = QualityOtherElement(
                    **detail.dict(exclude={"id", "quality_element_id"}),
                    quality_element=quality_element
                )
                db_session.add(new_record)

        # 删除不再存在的 QualityOtherElement 记录
        for elem_id, elem in existing_other_elements.items():
            if elem_id not in new_other_element_ids:
                db_session.delete(elem)

    db_session.commit()
    db_session.refresh(quality_element)
    return quality_element


def delete(*, db_session, id: int):
    quality_element = db_session.query(QualityElement).filter(QualityElement.id == id).one_or_none()
    
    if quality_element:
        quality_element.is_deleted = 1
    db_session.add(quality_element)
    db_session.commit()

    return quality_element

