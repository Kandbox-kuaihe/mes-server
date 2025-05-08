
from typing import List, Optional
from .models import CertificateFinishedProduct, CertificateFinishedProductCreate, CertificateFinishedProductUpdate, CertificateFinishedProductCreate

def get(*, db_session, id: int) -> Optional[CertificateFinishedProduct]:
    """Returns an certificate given an certificate id."""
    return db_session.query(CertificateFinishedProduct).filter(CertificateFinishedProduct.id == id).one_or_none()


def get_by_code(*, db_session, code: str) -> Optional[CertificateFinishedProduct]:
    """Returns an certificate given an certificate code address."""
    return db_session.query(CertificateFinishedProduct).filter(CertificateFinishedProduct.certificate_code == code).one_or_none()

def get_by_finished_product_id(*, db_session, finished_product_id_list: List[int]) -> Optional[CertificateFinishedProduct]:
    return db_session.query(CertificateFinishedProduct).filter(CertificateFinishedProduct.finished_product_id.in_(finished_product_id_list)).all()

def get_default_certificate(*, db_session ) -> Optional[CertificateFinishedProduct]:
    """Returns an certificate given an certificate code address."""
    return db_session.query(CertificateFinishedProduct).first()


def get_all(*, db_session) -> List[Optional[CertificateFinishedProduct]]:
    """Returns all certificates."""
    return db_session.query(CertificateFinishedProduct)


def create(*, db_session, create_in: CertificateFinishedProductCreate) -> CertificateFinishedProduct:
    """Creates an certificate."""

    contact = CertificateFinishedProduct(**create_in.dict(exclude={"flex_form_data"})
                    )
    
    db_session.add(contact)
    db_session.commit()
    return contact


def update(
    *,
    db_session,
    obj: CertificateFinishedProduct,
    update_in: CertificateFinishedProductUpdate,
) -> CertificateFinishedProduct:

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
    certificate = db_session.query(CertificateFinishedProduct).filter(CertificateFinishedProduct.id == id).one_or_none()
    
    if certificate:
        certificate.is_deleted = 1
    db_session.add(certificate)
    db_session.commit()

    return certificate