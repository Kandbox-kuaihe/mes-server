from typing import List, Optional
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from sqlalchemy import and_
from fastapi import  HTTPException
from dispatch.mill.models import Mill
from .models import ProductCategory, ProductCategoryCreate, ProductCategoryUpdate
import logging

from dispatch.log import getLogger
log = getLogger(__name__)


def get(*, db_session: Session, id: int) -> Optional[ProductCategory]:
    return db_session.query(ProductCategory).filter(ProductCategory.id == id).one_or_none()


def get_by_code(*, db_session: Session, code: str) -> Optional[ProductCategory]:
    return db_session.query(ProductCategory).filter(ProductCategory.code == code).one_or_none()

def get_by_code_SRSM(*, db_session: Session, code: str) -> Optional[ProductCategory]:
    return db_session.query(ProductCategory).filter(and_(ProductCategory.code == code,ProductCategory.mill_id==1)).one_or_none()
def get_all(*, db_session: Session) -> List[ProductCategory]:
    return db_session.query(ProductCategory).all()


def create(*, db_session: Session, category_in: ProductCategoryCreate) -> ProductCategory:

    m_id = db_session.query(Mill).filter(Mill.code == category_in.mill_code).first().id
    if m_id is None:
        raise HTTPException(status_code=400, detail='Mill code not found')
    category = ProductCategory(
        code=category_in.code,
        type=category_in.type,
        desc=category_in.desc,
        mill_id=category_in.mill_id if category_in.mill_id else m_id,
        dim1=category_in.dim1,
        dim2=category_in.dim2,
        dim3=category_in.dim3,
        dim4=category_in.dim4,
        created_at=category_in.created_at,
        created_by=category_in.created_by,
        updated_at=category_in.updated_at,
        updated_by=category_in.updated_by,
    )
    db_session.add(category)
    db_session.commit()
    # db_session.refresh(category)
    return category


def update(*, db_session: Session, category: ProductCategory, category_in: ProductCategoryUpdate) -> ProductCategory:
    m_id = db_session.query(Mill).filter(Mill.code == category_in.mill_code).first().id
    if m_id is None:
        raise HTTPException(status_code=400, detail='Mill code not found')

    category_data = jsonable_encoder(category)
    category_in.mill_id = category_in.mill_id if category_in.mill_id else m_id
    update_data = category_in.dict()

    for field in category_data:
        if field in update_data:
            setattr(category, field, update_data[field])

    db_session.add(category)
    db_session.commit()
    return category


def delete(*, db_session: Session, id: int):
    category = db_session.query(ProductCategory).filter(ProductCategory.id == id).first()
    if category:
        db_session.delete(category)
        db_session.commit()


def get_codes(*, db_session: Session, mill_id: int):
    codes = []
    result = db_session.query(ProductCategory.code).filter(ProductCategory.mill_id == mill_id).all()
    if not result:
        return codes
    for i in result:
        codes.append(i[0])
    return codes