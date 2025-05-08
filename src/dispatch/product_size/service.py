from typing import List, Optional
from fastapi.encoders import jsonable_encoder
from fastapi import HTTPException
from sqlalchemy.orm import Session
from dispatch.mill.models import Mill
from .models import ProductSize, ProductSizeCreate, ProductSizeUpdate
import logging
from sqlalchemy import and_

from dispatch.log import getLogger
log = getLogger(__name__)


def get(*, db_session: Session, id: int) -> Optional[ProductSize]:
    return db_session.query(ProductSize).filter(ProductSize.id == id).one_or_none()


def get_by_code(*, db_session: Session, code: str) -> Optional[ProductSize]:
    return db_session.query(ProductSize).filter(ProductSize.code == code).one_or_none()

def get_by_mill_and_code(*, db_session: Session, mill_id: int, code: str) -> Optional[ProductSize]:
    if not mill_id or not code: return None
    return db_session.query(ProductSize).filter(ProductSize.mill_id==mill_id, ProductSize.code == code).one_or_none()


def get_all(*, db_session: Session) -> List[ProductSize]:
    return db_session.query(ProductSize).all()


def create(*, db_session: Session, product_size_in: ProductSizeCreate) -> ProductSize:
    # m_id = db_session.query(Mill).filter(Mill.code == product_size_in.mill_code).first().id
    # if m_id is None:
    #     raise HTTPException(status_code=400, detail='Mill code not found')
    # product_size = ProductSize(
    #     code=product_size_in.code,
    #     type=product_size_in.type,
    #     desc=product_size_in.desc,
    #     mill_id=m_id,
    #     created_at=product_size_in.created_at,
    #     created_by=product_size_in.created_by,
    #     updated_at=product_size_in.updated_at,
    #     updated_by=product_size_in.updated_by,
    # )
    product_size = ProductSize(**product_size_in.dict(exclude={"flex_form_data","mill","mill_code","product_category","product_class"}),
                    flex_form_data=product_size_in.flex_form_data)
    db_session.add(product_size)
    db_session.commit()
    return product_size


def update(*, db_session: Session, product_size: ProductSize, product_size_in: ProductSizeUpdate) -> ProductSize:
    m_id = db_session.query(Mill).filter(Mill.code == product_size_in.mill_code).first().id
    if m_id is None:
        raise HTTPException(status_code=400, detail='Mill code not found')
    product_size_data = jsonable_encoder(product_size)
    product_size_in.mill_id = m_id
    update_data = product_size_in.dict()

    for field in product_size_data:
        if field in update_data:
            setattr(product_size, field, update_data[field])

    db_session.add(product_size)
    db_session.commit()
    return product_size


def delete(*, db_session: Session, id: int):
    product_size = db_session.query(ProductSize).filter(ProductSize.id == id).first()
    try:
        if product_size:
            product_size.is_deleted = 1
            # db_session.delete(product_size)
            db_session.commit()
    except Exception as e:
        raise HTTPException(status_code=400, detail=e)


def get_codes(*, db_session: Session) -> List[str]:
    codes = []
    result = db_session.query(ProductSize.code).all()
    if result:
        codes = [i[0] for i in result]
    return codes


def get_by_roll_ref_code_m(db_session: Session, roll_ref_code: str, mill_id: int):
    return db_session.query(ProductSize).filter(and_(ProductSize.code == roll_ref_code, ProductSize.mill_id == mill_id)).first()

def get_by_roll_ref_code_mill(db_session: Session, roll_ref_code: str, mill_id: int):
    return db_session.query(ProductSize).filter(and_(ProductSize.roll_ref_code == roll_ref_code, ProductSize.mill_id == mill_id)).first()


# 将来可能要用这个逻辑， 暂时别删
# def get_roll_ref_code_by_dim1_dim2_product_code(db_session: Session, dim1, dim2, product_code, mill_id):
#     return db_session.query(ProductSize).filter(and_(
#         ProductSize.code == f"{product_code}-{dim1}-{dim2}",
#         ProductSize.mill_id == mill_id,
#     )).first()

def get_roll_ref_code_by_dim1_dim2_product_code(db_session: Session, dim1, dim2, product_code, mill_id):

    if dim1.isdigit() and dim2.isdigit():
        return db_session.query(ProductSize).filter(and_(
            ProductSize.code == f"{product_code}-{dim1}-{dim2}",
            ProductSize.mill_id == mill_id,
        )).first()
    else:
        result = db_session.query(ProductSize).all()
        for i in result:
            if i.desc is None:
                continue
            special_code = "".join(i.desc.split()).replace("-","")
            if special_code[:len(dim1)] == dim1 and special_code[len(dim1):len(dim1)+len(dim2)] == dim2 and product_code == i.product_code:
                # print(special_code)
                return i
        return None

def get_by_cat_class_mill(db_session: Session, category_id: int, class_id: int, mill_id: int):
    return db_session.query(ProductSize).filter(and_(ProductSize.product_category_id == category_id, ProductSize.product_class_id == class_id, ProductSize.mill_id == mill_id)).first()
