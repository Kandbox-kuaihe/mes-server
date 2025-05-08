
from typing import List, Optional
from .models import Certificate, CertificateCreate, CertificateUpdate, CertificateCreate

def get(*, db_session, id: int) -> Optional[Certificate]:
    """Returns an certificate given an certificate id."""
    return db_session.query(Certificate).filter(Certificate.id == id).one_or_none()


def get_by_code(*, db_session, code: str) -> Optional[Certificate]:
    """Returns an certificate given an certificate code address."""
    return db_session.query(Certificate).filter(Certificate.certificate_code == code).one_or_none()


def get_default_certificate(*, db_session ) -> Optional[Certificate]:
    """Returns an certificate given an certificate code address."""
    return db_session.query(Certificate).first()


def get_all(*, db_session) -> List[Optional[Certificate]]:
    """Returns all certificates."""
    return db_session.query(Certificate)


def create(*, db_session, create_in: CertificateCreate) -> Certificate:
    """Creates an certificate."""

    contact = Certificate(**create_in.dict(exclude={"flex_form_data"})
                    )
    
    db_session.add(contact)
    db_session.commit()
    return contact


def update(
    *,
    db_session,
    obj: Certificate,
    update_in: CertificateUpdate,
) -> Certificate:

    update_data = update_in.dict(
        exclude={"flex_form_data"},
    )
    for field, field_value in update_data.items():
        setattr(obj, field, field_value)

    obj.flex_form_data = update_in.flex_form_data
    db_session.add(obj)
    db_session.commit()
    return obj


def delete(*, db_session, id: int):
    certificate = db_session.query(Certificate).filter(Certificate.id == id).one_or_none()
    
    if certificate:
        certificate.is_deleted = 1
    db_session.add(certificate)
    db_session.commit()

    return certificate