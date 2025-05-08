from sqlalchemy.orm import Session
from sqlalchemy import and_
from sqlalchemy.sql import and_
from fastapi import Depends, HTTPException
from typing import List, Type, Optional
from dispatch.product_class.models import ProductClass
from dispatch.product_category.models import ProductCategory
from dispatch.product_type.models import ProductTypeCreate, ProductTypeUpdate, ProductTypeRead, ProductType
from dispatch.database import get_db
from dispatch.mill.models import Mill
from fastapi.encoders import jsonable_encoder
from dispatch.spec_admin.tolerance.models import Tolerance

# 创建 ProductType
def create_product_type(product_data: ProductTypeCreate, db: Session = Depends(get_db)) -> ProductType:
    product_type = ProductType(
        mill_id=product_data.mill_id,
        code=product_data.code,
        type=product_data.type,
        desc=product_data.desc,
        longitude=product_data.longitude,
        latitude=product_data.latitude,
        dim1=product_data.dim1,
        dim2=product_data.dim2,
        dim3=product_data.dim3,
        dim4=product_data.dim4,
    )
    db.add(product_type)
    db.commit()
    db.refresh(product_type)
    return product_type


def create_product_type_by_mill_code(product_data: ProductTypeCreate, db: Session = Depends(get_db)) -> ProductType:
    product_class_id = None
    product_category_id = None
    tolerance_id = None
    m_id = db.query(Mill).filter(Mill.code == product_data.mill_code).first().id
    if m_id is None:
        raise HTTPException(status_code=400, detail='Mill code not found')
    product_category = db.query(ProductCategory).filter(and_(ProductCategory.code == product_data.product_category_code, ProductCategory.mill_id == (product_data.mill_id or m_id))).first()
    if product_category:
        product_category_id = product_category.id

    product_class = db.query(ProductClass).filter(and_(ProductClass.code == product_data.product_class_code, ProductClass.mill_id == (product_data.mill_id or m_id))).first()
    if product_class:
        product_class_id = product_class.id
    tolerance = db.query(Tolerance).filter(and_(Tolerance.code == product_data.tolerance_code, Tolerance.mill_id == (product_data.mill_id or m_id))).first()
    if tolerance:
        tolerance_id = tolerance.id

    product_type = ProductType(
        **product_data.model_dump(exclude={"mill", "tolerance", "product_category", "product_class","mill_id","product_category_id","product_class_id","tolerance_id",
                                           "mill_code","product_category_code","product_class_code","tolerance_code"}),
        mill_id=product_data.mill_id if product_data.mill_id else m_id,
        product_category_id=product_data.product_category_id if product_data.product_category_id else product_category_id,
        tolerance_id=tolerance_id,
        product_class_id=product_class_id
    )
    db.add(product_type)
    db.commit()
    db.refresh(product_type)
    return product_type


# 获取所有 ProductType
def get_product_types(db: Session = Depends(get_db), skip: int = 0, limit: int = 100) -> list[Type[ProductType]]:
    return db.query(ProductType).offset(skip).limit(limit).all()


def get(db_session: Session, product_type_id: int) -> ProductType:
    return db_session.query(ProductType).filter(ProductType.id == product_type_id).one_or_none()

def get_all(*, db_session) -> List[ProductType]:
    """Returns all specs."""
    return db_session.query(ProductType).all()


def get_by_mill(*, db_session, mill_id) -> List[Optional[ProductType]]:
    """Returns all specs."""
    return db_session.query(ProductType).filter(ProductType.mill_id == mill_id).all()


def get_by_code(db_session: Session, code: str) -> ProductType:
    return db_session.query(ProductType).filter(ProductType.code == code).one_or_none()


# 根据 ID 获取单个 ProductType
def get_product_type(db: Session, product_type_id: int) -> ProductType:
    return db.query(ProductType).filter(ProductType.id == product_type_id).first()

def get_id(*, db_session, product_type_id: int) -> ProductType:
    return db_session.query(ProductType).filter(ProductType.id == product_type_id).first()

def get_by_code(db: Session, code: str) -> ProductType:
    return db.query(ProductType).filter(ProductType.code == code).first()
## 用于product_type 的create sql接口(SRSM)/(TBM)
def get_id_by_code(db: Session, code: str) -> Optional[int]:
    product_type=db.query(ProductType).filter(and_(ProductType.code == code,ProductType.mill_id == 410)).one_or_none()
    if product_type:
        return product_type.id
    else:
        return None

def get_by_code_and_mill_id(db: Session, code: str, mill_id: int) -> ProductType:
    return db.query(ProductType).filter(and_(ProductType.code == code, ProductType.mill_id == mill_id)).first()

# get ID from dimensions
def get_product_type_id_by_dimensions(
    *, db_session, dim1: Optional[float] = None, dim2: Optional[float] = None, dim3: Optional[float] = None
) -> Optional[int]:
    """
    Returns the product type ID based on dimensional filters.
    """
    query = db_session.query(ProductType.id)

    if dim1 is not None:
        query = query.filter(ProductType.dim1 == dim1)
    if dim2 is not None:
        query = query.filter(ProductType.dim2 == dim2)
    if dim3 is not None:
        query = query.filter(ProductType.dim3 == dim3)
    # if dim4 is not None:
    #     query = query.filter(ProductType.dim4 == dim4)

    return query.scalar()

# 更新 ProductType
def update_product_type(db: Session, product_type_id: int, product_data: ProductTypeUpdate) -> ProductType:
    product_class_id = None
    product_category_id = None
    tolerance_id = None
    m_id = db.query(Mill).filter(Mill.code == product_data.mill_code).first().id
    if m_id is None:
        raise HTTPException(status_code=400, detail='Mill code not found')
    product_category = db.query(ProductCategory).filter(
        ProductCategory.code == product_data.product_category_code).first()
    if product_category:
        product_category_id = product_category.id

    product_type = db.query(ProductType).filter(ProductType.id == product_type_id).first()
    if not product_type:
        return None

    product_class = db.query(ProductClass).filter(ProductClass.code == product_data.product_class_code).first()
    if product_class:
        product_class_id = product_class.id
    tolerance = db.query(Tolerance).filter(Tolerance.code == product_data.tolerance_code).first()
    if tolerance:
        tolerance_id = tolerance.id

    # 将 product_type 转换为字典形式
    product_type_data = jsonable_encoder(product_type)
    product_data.mill_id = m_id
    product_data.product_category_id = product_category_id
    product_data.product_class_id = product_class_id
    product_data.tolerance_id = tolerance_id
    # 获取更新的数据，排除未设置的字段
    update_data = product_data.dict(exclude_unset=True)

    # 遍历现有字段并更新
    for field in product_type_data:
        if field in update_data:
            setattr(product_type, field, update_data[field])

    # 更新 updated_by 字段
    if product_data.updated_by is not None:  # 确保有值
        product_type.updated_by = product_data.updated_by

    db.add(product_type)
    db.commit()
    db.refresh(product_type)  # 刷新以获取最新的数据
    return product_type


# 删除 ProductType
def delete_product_type(db: Session, product_type_id: int) -> bool:
    product_type = db.query(ProductType).filter(ProductType.id == product_type_id).first()
    if product_type:
        db.delete(product_type)
        db.commit()
        return True
    return False


def get_dim3(db: Session):
    dim3_list = db.query(ProductType.dim3).all()
    return [dim3 for dim3, in dim3_list if dim3 != -1]  # 返回去除值为 -1 的 dim3 值列表


def get_codes(*, db_session: Session):
    codes = []
    result = db_session.query(ProductType.code).all()
    if not result:
        return codes
    for i in result:
        codes.append(i[0])
    return codes


####################### 区分mill的product type service #######################
def get_by_code_m(db: Session, code: str, mill_id: int):
    return db.query(ProductType).filter(and_(ProductType.code == code, ProductType.mill_id == mill_id)).first()
