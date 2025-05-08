from fastapi import APIRouter, Depends, HTTPException
from .models import Customer, CustomerCreate, CustomerRead, CustomerUpdate, CustomerPagination, CustomerBase
from dispatch.database_util.service import common_parameters, search_filter_sort_paginate
from sqlalchemy.orm import Session
from dispatch.database import get_db
from dispatch.system_admin.auth.models import DispatchUser
from dispatch.system_admin.auth.service import get_current_user
from .service import create, delete, get, update, get_by_code,get_cust_attr, sync_customer_from_odoo_data

router = APIRouter()


@router.get("/", response_model=CustomerPagination)
def get_all(*, db_session: Session = Depends(get_db), common: dict=Depends(common_parameters)):
    return search_filter_sort_paginate(model="Customer", **common)


@router.post("/create", response_model=CustomerRead)
def create_customer(*, db_session: Session = Depends(get_db), customer_in: CustomerCreate,
                      current_user: DispatchUser = Depends(get_current_user)):
    customer_in.mill_id = current_user.current_mill_id
    existed = get_by_code(db_session=db_session, code=customer_in.code)
    if existed and existed.is_deleted == 1:
        db_session.query(Customer).filter(Customer.id == existed.id).update({"is_deleted": 0})
        update(db_session=db_session, item=existed, item_in=customer_in)
        db_session.commit()
        return existed
    elif existed and existed.is_deleted == 0:
        raise HTTPException(status_code=400, detail="The Customer with this code already exists.")
    else:
        coh_code = db_session.query(Customer).filter(Customer.coh_code == customer_in.coh_code).one_or_none()
        if coh_code:
            raise HTTPException(status_code=400, detail="The Customer with this coh_code already exists.")
        else:
            created = create(db_session=db_session, customer_in=customer_in)
        return created
@router.get("/detail/{customer_id}", response_model=CustomerUpdate)
def get_customer(
    *,
    db_session: Session = Depends(get_db),
    customer_id: int
):
    customer = get(db_session=db_session, id=customer_id)
    if not customer:
        raise HTTPException(status_code=400, detail="The Customer with this id does not exist.")
    cust_attr = get_cust_attr(db_session=db_session, cust_id=customer_id)
    if cust_attr:
        if not isinstance(cust_attr, list):
            cust_attr = [cust_attr]
        customer.cust_attr = cust_attr
    else:
        customer.cust_attr = []
    return customer
@router.put("/detail/{customer_id}", response_model=CustomerUpdate)
def update_customer(
    *,
    db_session: Session = Depends(get_db),
    current_user: DispatchUser = Depends(get_current_user),
    customer_id: int,
    customer_in: CustomerUpdate
):
    customer = get(db_session=db_session, id=customer_id)
    if not customer:
        raise HTTPException(status_code=400, detail="The Customer with this id does not exist.")
    
    if customer_in.coh_code != customer.coh_code:
        existing_customer_with_coh_code = db_session.query(Customer).filter(
            Customer.coh_code == customer_in.coh_code,
            Customer.id != customer_id
        ).first()
        if existing_customer_with_coh_code:
            raise HTTPException(status_code=400, detail="The Customer with this coh_code already exists.")
    
    updated = update(db_session=db_session, item=customer, item_in=customer_in)
    return updated

@router.delete("/{customer_id}")
def delete_customer(
    *,
    db_session: Session = Depends(get_db),
    current_user: DispatchUser = Depends(get_current_user),
    customer_id: int
):
    customer = get(db_session=db_session, id=customer_id)
    if not customer:
        raise HTTPException(status_code=400, detail="The Customer with this id does not exist.")
    deleted = delete(db_session=db_session, id=customer_id)
    return deleted


@router.post("/sync_customer_from_odoo")
def sync_customer_from_odoo(
        *,
        db_session: Session = Depends(get_db),
        customer_in: dict,
        current_user: DispatchUser = Depends(get_current_user)
):
    """
    Sync customer from odoo.
    """
    result = sync_customer_from_odoo_data(session=db_session, customer_in=customer_in)

    return result