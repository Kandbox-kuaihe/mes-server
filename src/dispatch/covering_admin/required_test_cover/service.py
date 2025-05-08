from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.sql.functions import func

from .models import RequiredTestCover, RequiredTestCoverCreate, RequiredTestCoverUpdate, RequiredTestCoverRead, \
    RequiredTestCoverPagination


def get(*, db_session, id: int) -> Optional[RequiredTestCover]:
    return db_session.get(RequiredTestCover, id)


def create(*, db_session, required_test_cover_in: RequiredTestCoverCreate) -> RequiredTestCover:
    created = RequiredTestCover(**required_test_cover_in.model_dump())
    db_session.add(created)
    db_session.commit()
    return created


def update(
        *,
        db_session,
        required_test_cover: RequiredTestCover,
        required_test_cover_in: RequiredTestCoverUpdate,
) -> RequiredTestCover:
    update_data = required_test_cover_in.model_dump()
    for field, field_value in update_data.items():
        setattr(required_test_cover, field, field_value)

    db_session.add(required_test_cover)
    db_session.commit()
    return required_test_cover


def delete(*, db_session, required_test_cover: RequiredTestCover, required_test_cover_id: int):
    required_test_cover.is_deleted = 1

    db_session.commit()


def create_dict(db_session, required_test_cover_in: dict) -> RequiredTestCover:
    created = RequiredTestCover(**required_test_cover_in)
    created = create(db_session=db_session, required_test_cover_in=created)
    return created