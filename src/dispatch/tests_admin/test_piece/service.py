from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import TestPiece

def create(*, db_session: Session, create_in: dict):
    created = TestPiece(**create_in)
    db_session.add(created)
    db_session.commit()

    return created

def get_by_test_number(*, db_session: Session, test_number: str):
    stmt = select(TestPiece).where(TestPiece.test_number == test_number).order_by(TestPiece.created_at.desc())
    row = db_session.scalar(stmt)

    return row