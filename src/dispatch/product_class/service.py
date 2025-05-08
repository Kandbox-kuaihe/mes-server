from typing import List, Optional
from fastapi.encoders import jsonable_encoder
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_
from dispatch.mill.models import Mill
from .models import ProductClass, ProductClassCreate, ProductClassUpdate
import logging

from dispatch.log import getLogger
log = getLogger(__name__)


def get(*, db_session: Session, id: int) -> Optional[ProductClass]:
    return db_session.query(ProductClass).filter(ProductClass.id == id).one_or_none()


def get_by_code(*, db_session: Session, code: str) -> Optional[ProductClass]:
    return db_session.query(ProductClass).filter(ProductClass.code == code).one_or_none()

def get_by_code_SRSM(*, db_session: Session, code: str) -> Optional[ProductClass]:
    return db_session.query(ProductClass).filter(and_(ProductClass.code == code, ProductClass.mill_id==1)).one_or_none()


def get_all(*, db_session: Session) -> List[ProductClass]:
    return db_session.query(ProductClass).all()


def create(*, db_session: Session, product_class_in: ProductClassCreate) -> ProductClass:
    m_id = db_session.query(Mill).filter(Mill.code == product_class_in.mill_code).first().id
    if m_id is None:
        raise HTTPException(status_code=400, detail='Mill code not found')
    product_class = ProductClass(
        code=product_class_in.code,
        type=product_class_in.type,
        desc=product_class_in.desc,
        mill_id=product_class_in.mill_id if product_class_in.mill_id else m_id,
        created_at=product_class_in.created_at,
        created_by=product_class_in.created_by,
        updated_at=product_class_in.updated_at,
        updated_by=product_class_in.updated_by,
    )
    db_session.add(product_class)
    db_session.commit()
    return product_class


def update(*, db_session: Session, product_class: ProductClass, product_class_in: ProductClassUpdate) -> ProductClass:
    m_id = db_session.query(Mill).filter(Mill.code == product_class_in.mill_code).first().id
    if m_id is None:
        raise HTTPException(status_code=400, detail='Mill code not found')
    product_class_data = jsonable_encoder(product_class)
    product_class_in.mill_id = product_class_in.mill_id if product_class_in.mill_id else m_id
    update_data = product_class_in.dict()

    for field in product_class_data:
        if field in update_data:
            setattr(product_class, field, update_data[field])

    db_session.add(product_class)
    db_session.commit()
    return product_class


def delete(*, db_session: Session, id: int):
    product_class = db_session.query(ProductClass).filter(ProductClass.id == id).first()
    try:
        if product_class:
            db_session.delete(product_class)
            db_session.commit()
    except Exception as e:
        raise HTTPException(status_code=400, detail=e)


def get_codes(*, db_session: Session, mill_id: int) -> List[str]:
    codes = []
    result = db_session.query(ProductClass.code).filter(ProductClass.mill_id == mill_id).all()
    if result:
        codes = [i[0] for i in result]
    return codes
