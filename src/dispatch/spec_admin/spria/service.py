from typing import List, Optional

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from dispatch.spec_admin.spec.models import Spec
from .models import Spria, SpriaCopyToCode, SpriaUpdate, SpriaCreate
from ...mill.models import Mill


def get(*, db_session, id: int) -> Optional[Spria]:
    """Returns an spria given an spria id."""
    return db_session.query(Spria).filter(Spria.id == id).one_or_none()

def get_by_spec_id(*, db_session, spec_id: int) ->List[Optional[Spria]]:
    return db_session.query(Spria).filter(
        Spria.spec_id == spec_id).all()

def get_by_code(*, db_session, code: str) -> Optional[Spria]:
    """Returns an spria given an spria code address."""
    return db_session.query(Spria).filter(Spria.code == code).one_or_none()


def get_default_spria(*, db_session) -> Optional[Spria]:
    """Returns an spria given an spria code address."""
    return db_session.query(Spria).first()


def get_all(*, db_session) -> List[Optional[Spria]]:
    """Returns all sprias."""
    return db_session.query(Spria)


def create(*, db_session, spria_in: SpriaCreate) -> Spria:
    """Creates an spria."""
    spec = None
    mill = None
    if spria_in.spec_id:
        spec = db_session.query(Spec).filter(Spec.id == spria_in.spec_id).one_or_none()
    if spria_in.mill_id:
        mill = db_session.query(Mill).filter(Mill.id == spria_in.mill_id).one_or_none()

    contact = Spria(**spria_in.model_dump( exclude={"mill","spec", "flex_form_data"}), flex_form_data=spria_in.flex_form_data, spec=spec, mill=mill)
    db_session.add(contact)
    db_session.commit()
    return contact


def update(
    *,
    db_session,
    spria: Spria,
    spria_in: SpriaUpdate,
) -> Spria:

    update_data = spria_in.model_dump(
        exclude={"mill","spec","flex_form_data"},
    )
    for field, field_value in update_data.items():
        setattr(spria, field, field_value)
    db_session.add(spria)
    db_session.commit()
    return spria


def delete(*, db_session, id: int):
    spria = db_session.query(Spria).filter(Spria.id == id).one_or_none()

    if spria:
        spria.is_deleted = 1
    db_session.add(spria)
    db_session.commit()

    return spria


def create_by_copy_spec_code(*, db_session, copy_dict: SpriaCopyToCode, current_user):
    # 通过复制前的spec_code 查询数据
    copy_before_values = db_session.query(Spria).join(Spec).filter(Spec.spec_code == copy_dict.before_code).all()

    if not copy_before_values:
        raise HTTPException(status_code=400, detail="The spria with this spec_code does not exist.")

    # 查询copy to 的spec记录
    copy_to_spec = (
        db_session.query(Spec).filter(Spec.spec_code == copy_dict.after_code).order_by(Spec.id.desc()).first()
    )
    if not copy_to_spec:
        raise HTTPException(status_code=400, detail="The spria with this spec_code does not exist.")

    after_list = []
    try:
        for cbv in copy_before_values:

            is_cunzai = (
                db_session.query(Spria)
                .filter(
                    Spria.spec_id == copy_to_spec.id, Spria.thick_from == cbv.thick_from, Spria.thick_to == cbv.thick_to
                )
                .first()
            )

            if is_cunzai:
                continue

            cbv_value = SpriaCreate(**cbv.__dict__)
            cbv_value.created_by = current_user.email
            after_list.append(Spria(**cbv_value.model_dump(exclude={"flex_form_data", "spec", "mill"}), spec=copy_to_spec, mill=cbv.mill))

        if len(after_list) > 0:
            db_session.add_all(after_list)
            db_session.commit()
        else:
            raise HTTPException(status_code=400, detail="There are no replicable objects.")

    except IntegrityError:
        db_session.rollback()
        raise HTTPException(status_code=400, detail="Insertion failed, the same record already exists.")

    return True


def get_all_data(*, db_session) -> List[Optional[Spria]]:
    return db_session.query(Spria).all()


def get_all_data_dict_of_spec_id(*, db_session) -> dict:
    data = get_all_data(db_session=db_session)
    dic = {}
    for d in data:
        if d.spec_id not in dic:
            dic[d.spec_id] = []
        dic[d.spec_id].append(d)
    return dic
