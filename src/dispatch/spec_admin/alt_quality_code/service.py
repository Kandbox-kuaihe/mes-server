from typing import List, Optional, Dict
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy_filters import apply_pagination
from sqlalchemy.exc import IntegrityError
from sqlalchemy import inspect
from .models import AltQualityCode, AltQualityCodeCreate, AltQualityCodeRead, AltQualityCodeUpdate
from datetime import datetime, date, UTC


def validate_field_lengths(data: dict, model):
    """验证字段长度"""
    mapper = inspect(model)
    errors = []
    for column in mapper.columns:
        field_name = column.name
        max_length = getattr(column.type, "length", None)
        if max_length is not None:
            value = data.get(field_name)
            if value and len(value) > max_length:
                errors.append(f"Field '{field_name}' exceeds maximum length of {max_length} characters.")
    if errors:
        raise HTTPException(status_code=400, detail=errors)

def get_all(*, db_session) -> List[Optional[AltQualityCode]]:
    """Returns all spImpacts."""
    return db_session.query(AltQualityCode)


def get(*, db_session: Session, code: str) -> Optional[AltQualityCode]:
    """Search AltQualityCodes by exact quality_code."""
    return db_session.query(AltQualityCode).filter(AltQualityCode.quality_code == code).one_or_none()


def get_id(*, db_session, id: int) -> Optional[AltQualityCode]:
    """Returns an semi given an semi id."""
    return db_session.query(AltQualityCode).filter(AltQualityCode.id == id).one_or_none()


def get_by_quality(*, db_session, code: str) -> Optional[AltQualityCode]:
    try:
        # 假设 quality 是 AltQualityCode 的一个属性，且该属性有 code 字段
        query_result = db_session.query(AltQualityCode).filter(AltQualityCode.quality.has(code=code), AltQualityCode.is_deleted != 1).all()
        return query_result
    except Exception as e:
        return None


def create(*, db_session: Session, alt_quality_code_in: AltQualityCodeCreate) -> AltQualityCode:
    """Creates a new AltQualityCode."""
    validate_field_lengths(alt_quality_code_in.dict(), AltQualityCode)
    alt_quality_code = AltQualityCode(**alt_quality_code_in.dict())
    db_session.add(alt_quality_code)
    db_session.commit()
    return alt_quality_code


def delete(*, db_session: Session, id: int):
    alt_quality_code = db_session.query(AltQualityCode).filter(AltQualityCode.id == id).delete()
    db_session.commit()

    return alt_quality_code


def update(
    *,
    db_session: Session,
    alt_quality_code: AltQualityCode,
    alt_quality_code_in: AltQualityCodeUpdate,
) -> AltQualityCode:
    """Updates an existing AltQualityCode."""
    update_data = alt_quality_code_in.dict(
        exclude={"flex_form_data"}
    )

    # Update the fields
    for field, field_value in update_data.items():
        setattr(alt_quality_code, field, field_value)

    # Update timestamps or other specific fields
    alt_quality_code.updated_at = datetime.now(UTC)
    db_session.add(alt_quality_code)
    db_session.commit()
    return alt_quality_code

