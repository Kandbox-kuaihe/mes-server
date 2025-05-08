
from typing import List, Optional

from dispatch.system_admin.auth.models import DispatchUser
from .models import Mill, MillCreate, MillUpdate, MillCreate

def get(*, db_session, mill_id: int) -> Optional[Mill]:
    """Returns an mill given an mill id."""
    return db_session.query(Mill).filter(Mill.id == mill_id).one_or_none()


def get_by_code(*, db_session, code: str) -> Optional[Mill]:
    """Returns an mill given an mill code address."""
    return db_session.query(Mill).filter(Mill.code == code).one_or_none()


def get_by_user_id(*, db_session, user_id: id) -> List[Optional[Mill]]:
    from dispatch.system_admin.auth.models_secondary import user_mill_table
    """Returns an mill given an mill code address."""
    mill_data = db_session.query(Mill).join(user_mill_table, DispatchUser).\
            filter(DispatchUser.id == user_id).all()
    return mill_data

def get_default_mill(*, db_session ) -> Optional[Mill]:
    """Returns an mill given an mill code address."""
    return db_session.query(Mill).first()


def get_all(*, db_session) -> List[Optional[Mill]]:
    """Returns all mills."""
    return db_session.query(Mill)


def get_by_ids(*, db_session, id_list: list) -> List[Optional[Mill]]:
    """Returns an Mill given an Mill id."""
    return db_session.query(Mill).filter(Mill.id.in_(id_list)).all()






def create(*, db_session, mill_in: MillCreate) -> Mill:
    """Creates an mill."""

    contact = Mill(**mill_in.dict(exclude={"flex_form_data","user_ids","dispatch_user"}),
                    flex_form_data=mill_in.flex_form_data,
                    dispatch_user=mill_in.dispatch_user,
                    )

    db_session.add(contact)
    db_session.commit()
    return contact


def update(
    *,
    db_session,
    mill: Mill,
    mill_in: MillUpdate,
) -> Mill:

    update_data = mill_in.dict(
        exclude={"flex_form_data", "user_ids"},
    )
    for field, field_value in update_data.items():
        setattr(mill, field, field_value)

    mill.flex_form_data = mill_in.flex_form_data
    db_session.add(mill)
    db_session.commit()
    return mill


def delete(*, db_session, mill_id: int):
    mill = db_session.query(Mill).filter(Mill.id == mill_id).one_or_none()

    db_session.delete(mill)
    db_session.commit()

    return mill


def get_all_select(*, db_session) -> List[Optional[Mill]]:
    """Returns all Mills."""
    return db_session.query(Mill.id,Mill.code).filter(Mill.is_deleted != 1).all()


def get_mill_codes(*, db_session):
    result = db_session.query(Mill.code).all()
    return [code for code, in result] if result else []



def sync_mill_from_odoo_data(*, session, mill_in: dict):

    mill = session.query(Mill).filter(Mill.code == mill_in["code"]).first()
    if not mill:
        create_role = {
            "code": mill_in["code"],
            "type": mill_in["type"],
            "desc": mill_in["desc"]
        }
        mill = Mill(**create_role)
        session.add(mill)

    else:
        for field, field_value in mill_in.items():
            setattr(mill, field, field_value)

        session.add(mill)
    session.commit()
    return mill