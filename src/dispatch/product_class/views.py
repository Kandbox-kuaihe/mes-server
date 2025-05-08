from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from dispatch.system_admin.auth.models import DispatchUser
from dispatch.system_admin.auth.service import get_current_user
from dispatch.database import get_db
from .models import ProductClassCreate, ProductClassPagination, ProductClassRead, ProductClassUpdate
from .service import create, delete, get, update, get_codes
from dispatch.database_util.service import common_parameters, search_filter_sort_paginate
from dispatch.system_admin.auth.service import get as user_get

router = APIRouter()


@router.get("/", response_model=ProductClassPagination)
def get_product_classes(*, common: dict = Depends(common_parameters)):
    return search_filter_sort_paginate(model="ProductClass", **common)


@router.get("/{id}", response_model=ProductClassRead)
def get_product_class_by_id(*, db_session: Session = Depends(get_db), id: int):
    """
    Get a product class by ID.
    """
    product_class = get(db_session=db_session, id=id)
    if not product_class:
        raise HTTPException(status_code=400, detail="The product class with this id does not exist.")
    return product_class


@router.post("/create", response_model=ProductClassRead)
def create_product_class(*, db_session: Session = Depends(get_db), product_class_in: ProductClassCreate,
                         current_user: DispatchUser = Depends(get_current_user)):
    """
    Create a new product class.
    """
    product_class_in.created_by = current_user.email
    product_class = create(db_session=db_session, product_class_in=product_class_in)
    return product_class


@router.put("/update/{id}", response_model=ProductClassRead)
def update_product_class(*, db_session: Session = Depends(get_db), id: int, product_class_in: ProductClassUpdate,
                         current_user: DispatchUser = Depends(get_current_user)):
    """
    Update a product class.
    """
    product_class = get(db_session=db_session, id=id)
    if not product_class:
        raise HTTPException(status_code=400, detail="The product class with this id does not exist.")

    product_class_in.updated_by = current_user.email
    product_class = update(db_session=db_session, product_class=product_class, product_class_in=product_class_in)
    return product_class


@router.delete("/{id}", response_model=ProductClassRead)
def delete_product_class(*, db_session: Session = Depends(get_db), id: int):
    """
    Delete a product class.
    """
    product_class = get(db_session=db_session, id=id)
    if not product_class:
        raise HTTPException(status_code=400, detail="The product class with this id does not exist.")
    delete(db_session=db_session, id=id)

    return ProductClassRead(id=id)


@router.get("/item/codes")
def get_product_class_codes(db_session: Session = Depends(get_db), current_user: DispatchUser = Depends(get_current_user)):
    """
    Get all product class codes.
    """
    # user = user_get(db_session=db_session, user_id=current_user.id)
    codes = get_codes(db_session=db_session, mill_id=current_user.current_mill_id)
    return codes
