from typing import Optional

from fastapi import Depends
from requests import Session

from dispatch.database import get_db
from .models import Cust_Attr, Customer, CustomerCreate, CustomerUpdate


def get(*, db_session, id: int) -> Optional[Customer]:
    return db_session.query(Customer).filter(Customer.id == id).one_or_none()

def get_cust_attr(*, db_session, cust_id: int) -> Optional[Cust_Attr]:
    return db_session.query(Cust_Attr).filter(Cust_Attr.cust_id == cust_id).one_or_none()

def get_cust_attr_by_id(*, db_session, id: int) -> Optional[Cust_Attr]:
    return db_session.query(Cust_Attr).filter(Cust_Attr.id == id).one_or_none()
def get_by_code(*, db_session, code: str) -> Optional[Customer]:
    return db_session.query(Customer).filter(Customer.code == code).one_or_none()

def create(*, db_session, customer_in: CustomerCreate) -> Customer:
    from dispatch.mill.models import Mill
    mill = db_session.query(Mill).filter(Mill.id == customer_in.mill_id).one_or_none()
    customer = Customer(**customer_in.dict(
        exclude={"flex_form_data", "mill", "cust_attr" }
    ),mill=mill)
    db_session.add(customer)
    db_session.flush()
    if customer_in.cust_attr:
        for attr in customer_in.cust_attr:
            cust_attr = Cust_Attr(**attr.dict(exclude={"cust_id"}), cust_id=customer.id)
            db_session.add(cust_attr)
    db_session.commit()
    return customer

def update(
    db_session,
    item: Customer,
    item_in: CustomerUpdate,
) -> Customer:
    update_data = item_in.dict(
        exclude={"flex_form_data", "mill", "cust_attr"},
    )
    for field, field_value in update_data.items():
        setattr(item, field, field_value)
    db_session.add(item)
    db_session.flush()
    if item_in.cust_attr:
        for cust_attr_item in item_in.cust_attr:
            if cust_attr_item.id:
                cust_attr = get_cust_attr_by_id(db_session=db_session, id=cust_attr_item.id)
                cust_attr.value = cust_attr_item.value
                cust_attr.code = cust_attr_item.code
            db_session.add(cust_attr)
    db_session.commit()
    return item

def delete(*, db_session, id: int):
    item = db_session.query(Customer).filter(Customer.id == id).update({"is_deleted": 1})
    db_session.commit()
    return item


def update_cust_attr(*, db_session: Session = Depends(get_db), customer_id: int, cust_attr_in: Cust_Attr):
    cust_attr = db_session.query(Cust_Attr).filter(Cust_Attr.cust_id == customer_id).first()


def sync_customer_from_odoo_data(*, session, customer_in: dict):

    customer = session.query(Customer).filter(Customer.name == customer_in["name"]).first()
    if not customer:
        create_role = {
            "name": customer_in["name"],
            "code": customer_in["code"],
            "address_line_1": customer_in["address_line_1"],
            "address_line_2": customer_in["address_line_2"],
            "address_line_3": customer_in["address_line_3"],
            "address_line_4":customer_in["address_line_4"],
            "address_line_5":customer_in["address_line_5"],
            # "customer_type":customer_in["customer_type"],
            # "group":customer_in["group"],
            # "desc":customer_in["desc"],
            # "coh_code":customer_in["coh_code"],
        }
        customer = Customer(**create_role)
        session.add(customer)

    else:
        for field, field_value in customer_in.items():
            setattr(customer, field, field_value)

        session.add(customer)
    session.commit()
    return customer