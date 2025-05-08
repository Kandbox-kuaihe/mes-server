from typing import List, Optional
from .models import DefectArea, DefectAreaCreate, DefectAreaUpdate


def get(*, db_session, id: int) -> Optional[DefectArea]:
    """Returns an depot given an depot id."""
    return db_session.query(DefectArea).filter(DefectArea.id == id).one_or_none()


def get_by_code(*, db_session, code: str) -> Optional[DefectArea]:
    """Returns an depot given an depot code address."""
    return db_session.query(DefectArea).filter(DefectArea.code == code).one_or_none()


def get_or_create(*, db_session, code: str, **kwargs) -> DefectArea:
    """Gets or creates an depot."""
    contact = get_by_code(db_session=db_session, code=code)
    if not contact:
        DefectArea_in = DefectAreaCreate(**kwargs)
        contact = create(db_session=db_session, DefectArea_in=DefectArea_in)

    return contact


def message_create(*, db_session, **kwargs) -> DefectArea:
    DefectArea_in = DefectAreaCreate(**kwargs)
    contact = create(db_session=db_session, DefectArea_in=DefectArea_in)
    return contact


def create(*, db_session, DefectArea_in: DefectAreaCreate) -> DefectArea:
    """Creates an depot."""
    # exclude={"flex_form_data", "location"}
    contact = DefectArea(**DefectArea_in.dict(exclude={"flex_form_data", "mill"}, ))
    db_session.add(contact)
    db_session.commit()
    return contact


# def update(
#     *,
#     db_session,
#     depot: DefectArea,
#     depot_in: DepotUpdate,
# ) -> DefectArea:

#     update_data = depot_in.dict(
#        
#         exclude={"flex_form_data", "location"},
#     )
#     if depot_in.location and (not depot.location or depot_in.location.code != depot.location.code):
#         location_obj = location_service.get_or_create_by_code(
#             db_session=db_session, location_in=depot_in.location)
#         depot.location = location_obj

#     for field, field_value in update_data.items():
#         setattr(depot, field, field_value)

#     depot.flex_form_data = depot_in.flex_form_data
#     db_session.add(depot)
#     db_session.commit()
#     return depot


def update(
        db_session,
        item: DefectArea,
        item_in: DefectAreaUpdate,
) -> DefectArea:
    update_data = item_in.dict(
        #
        exclude={"flex_form_data"},
    )
    for field, field_value in update_data.items():
        setattr(item, field, field_value)

    item.flex_form_data = item_in.flex_form_data
    db_session.add(item)
    db_session.commit()
    return item


def delete(*, db_session, id: int):
    db_session.query(DefectArea).filter(DefectArea.id == id).delete()
    db_session.commit()
