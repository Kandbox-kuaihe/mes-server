from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from dispatch.system_admin.auth.models import DispatchUser
from dispatch.system_admin.auth.service import get_current_user
from dispatch.database import get_db
from .models import ProductSizeCreate, ProductSizePagination, ProductSizeRead, ProductSizeUpdate
from .service import create, delete, get, update, get_codes, get_roll_ref_code_by_dim1_dim2_product_code
from dispatch.database_util.service import common_parameters, search_filter_sort_paginate

router = APIRouter()


@router.get("/", response_model=ProductSizePagination)
def get_product_sizees(*, common: dict = Depends(common_parameters)):
    q = common["query_str"]
    if q:
        common["filter_type"] = "or"
        common["fields"] = ["code", "type"]
        common["ops"] = ["like"] * len(common["fields"])
        common["values"] = [f'%{q}%'] * len(common["fields"])
        common['query_str'] = ''
    product_size = search_filter_sort_paginate(model="ProductSize", **common)
    return product_size


@router.get("/options", response_model=ProductSizePagination)
def get_product_sizees(*, common: dict = Depends(common_parameters)):
    product_size = search_filter_sort_paginate(model="ProductSize", **common)
    return product_size


@router.get("/{id}", response_model=ProductSizeRead)
def get_product_size_by_id(*, db_session: Session = Depends(get_db), id: int):
    """
    Get a product size by ID.
    """
    product_size = get(db_session=db_session, id=id)
    if not product_size:
        raise HTTPException(status_code=400, detail="The product size with this id does not exist.")
    return product_size


@router.post("/create", response_model=ProductSizeRead)
def create_product_size(*, db_session: Session = Depends(get_db), product_size_in: ProductSizeCreate,
                         current_user: DispatchUser = Depends(get_current_user)):
    """
    Create a new product size.
    """
    # print(1111111111111111111111)
    # print(product_size_in)
    product_size_in.created_by = current_user.email
    product_size = create(db_session=db_session, product_size_in=product_size_in)
    return product_size


@router.put("/update/{id}", response_model=ProductSizeRead)
def update_product_size(*, db_session: Session = Depends(get_db), id: int, product_size_in: ProductSizeUpdate,
                         current_user: DispatchUser = Depends(get_current_user)):
    """
    Update a product size.
    """
    # print(1111111111111111111111)
    # print(product_size_in)
    product_size = get(db_session=db_session, id=id)
    if not product_size:
        raise HTTPException(status_code=400, detail="The product size with this id does not exist.")

    product_size_in.updated_by = current_user.email
    product_size = update(db_session=db_session, product_size=product_size, product_size_in=product_size_in)
    return product_size


@router.delete("/{id}", response_model=ProductSizeRead)
def delete_product_size(*, db_session: Session = Depends(get_db), id: int):
    """
    Delete a product size.
    """
    product_size = get(db_session=db_session, id=id)
    if not product_size:
        raise HTTPException(status_code=400, detail="The product size with this id does not exist.")
    delete(db_session=db_session, id=id)

    return product_size


@router.get("/item/codes")
def get_product_size_codes(db_session: Session = Depends(get_db)):
    """
    Get all product size codes.
    """
    codes = get_codes(db_session=db_session)
    return codes

@router.post("/roll_ref_code/print")
def get_product_size_roll_ref_code(
        data: dict,
        db_session: Session = Depends(get_db),
        current_user: DispatchUser = Depends(get_current_user)):
    dim1 = data.get("dim1", None)
    dim2 = data.get("dim2", None)
    product_code = data.get("product_code", None)
    if not product_code or not dim1 or not dim2:
        raise HTTPException(status_code=400, detail="The product size with this id does not exist.")
    result = get_roll_ref_code_by_dim1_dim2_product_code(db_session=db_session,
                                                dim1=str(dim1).lstrip('0'),
                                                dim2=str(dim2).lstrip('0'),
                                                mill_id=current_user.current_mill_id,
                                                product_code=product_code
                                                )
    if result:
        return {
            "roll_ref_code": result.roll_ref_code,
            "product_size_desc": result.desc,
        }
    return {
        "roll_ref_code": "",
        "product_size_desc": ""
    }