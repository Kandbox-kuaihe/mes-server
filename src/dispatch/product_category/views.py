from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from dispatch.database_util.service import common_parameters, search_filter_sort_paginate
from dispatch.system_admin.auth.models import DispatchUser
from dispatch.system_admin.auth.service import get_current_user
from dispatch.database import get_db
from .models import ProductCategoryCreate, ProductCategoryPagination, ProductCategoryRead, ProductCategoryUpdate
from .service import create, delete, get, update, get_codes

router = APIRouter()


@router.get("/cate/get", response_model=ProductCategoryPagination)
def get_product_categories(*, common: dict = Depends(common_parameters)):
    """
    Get paginated product categories.
    """
    return search_filter_sort_paginate(model="ProductCategory", **common)


@router.get("/cate/{id}", response_model=ProductCategoryRead)
def get_product_category_by_id(*, db_session: Session = Depends(get_db), id: int):
    """
    Get a product category by ID.
    """
    category = get(db_session=db_session, id=id)
    if not category:
        raise HTTPException(status_code=400, detail="The product category with this id does not exist.")
    return category


@router.post("/create", response_model=ProductCategoryRead)
def create_product_category(*, db_session: Session = Depends(get_db), category_in: ProductCategoryCreate,
                            current_user: DispatchUser = Depends(get_current_user)):
    """
    Create a new product category.
    """
    category_in.updated_by = current_user.email
    # category_in.created_by = current_user.email
    category = create(db_session=db_session, category_in=category_in)
    return category


@router.put("/{id}", response_model=ProductCategoryRead)
def update_product_category(
        *, db_session: Session = Depends(get_db), id: int, category_in: ProductCategoryUpdate,
        current_user: DispatchUser = Depends(get_current_user),
):
    """
    Update a product category.
    """
    category = get(db_session=db_session, id=id)
    if not category:
        raise HTTPException(status_code=400, detail="The product category with this id does not exist.")

    category_in.updated_by = current_user.email
    category = update(db_session=db_session, category=category, category_in=category_in)
    return category


@router.delete("/{id}", response_model=ProductCategoryRead)
def delete_product_category(*, db_session: Session = Depends(get_db), id: int):
    """
    Delete a product category.
    """
    category = get(db_session=db_session, id=id)
    if not category:
        raise HTTPException(status_code=400, detail="The product category with this id does not exist.")
    delete(db_session=db_session, id=id)

    return ProductCategoryRead(id=id)


@router.get("/codes")
def get_code(db_session: Session = Depends(get_db), current_user: DispatchUser = Depends(get_current_user)):
    # print(id)
    ls = get_codes(db_session=db_session, mill_id=current_user.current_mill_id)
    return ls