
from typing import List, Optional
from .models import Sprem, SpremCreate, SpremUpdate, SpremCreate

def get(*, db_session, id: int) -> Optional[Sprem]:
    """Returns an sprem given an sprem id."""
    return db_session.query(Sprem).filter(Sprem.id == id).one_or_none()


def get_by_code(*, db_session, code: str) -> Optional[Sprem]:
    """Returns an sprem given an sprem code address."""
    return db_session.query(Sprem).filter(Sprem.code == code).one_or_none()


def get_default_sprem(*, db_session ) -> Optional[Sprem]:
    """Returns an sprem given an sprem code address."""
    return db_session.query(Sprem).first()


def get_all(*, db_session) -> List[Optional[Sprem]]:
    """Returns all sprems."""
    return db_session.query(Sprem)


def create(*, db_session, sprem_in: SpremCreate) -> Sprem:
    """Creates an sprem."""

    contact = Sprem(**sprem_in.dict(exclude={"flex_form_data"}),
                    flex_form_data=sprem_in.flex_form_data)
    
    db_session.add(contact)
    db_session.commit()
    return contact


def update(
    *,
    db_session,
    sprem: Sprem,
    sprem_in: SpremUpdate,
) -> Sprem:

    update_data = sprem_in.dict(
        exclude={"flex_form_data"},
    )
    for field, field_value in update_data.items():
        setattr(sprem, field, field_value)

    sprem.flex_form_data = sprem_in.flex_form_data
    db_session.add(sprem)
    db_session.commit()
    return sprem


def delete(*, db_session, id: int):
    sprem = db_session.query(Sprem).filter(Sprem.id == id).one_or_none()
    
    if sprem:
        sprem.is_deleted = 1
    db_session.add(sprem)
    db_session.commit()

    return sprem