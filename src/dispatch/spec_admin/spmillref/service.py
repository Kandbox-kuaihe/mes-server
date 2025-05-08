
from typing import List, Optional
from fastapi import HTTPException
from dispatch.mill.models import Mill
from dispatch.spec_admin.spec.models import Spec
from .models import Spmillref, SpmillrefCreate, SpmillrefUpdate, SpmillrefCreate, SpmillrefBySpecCode, SpmillrefCopyToCode
from sqlalchemy_filters import apply_pagination
from sqlalchemy.exc import IntegrityError

from dispatch.log import getLogger
logger = getLogger(__name__)

def get(*, db_session, id: int) -> Optional[Spmillref]:
    """Returns an spmillref given an spmillref id."""
    return db_session.query(Spmillref).filter(Spmillref.id == id).one_or_none()


def get_by_code(*, db_session, code: str) -> Optional[Spmillref]:
    """Returns an spmillref given an spmillref code address."""
    return db_session.query(Spmillref).filter(Spmillref.code == code).one_or_none()


def get_default_spmillref(*, db_session ) -> Optional[Spmillref]:
    """Returns an spmillref given an spmillref code address."""
    return db_session.query(Spmillref).first()


def get_all(*, db_session) -> List[Optional[Spmillref]]:
    """Returns all spmillrefs."""
    return db_session.query(Spmillref)

def get_by_code_from_specid(*, db_session, spec_id: int, spec_code: str):
    """Returns an spmillref given an spmillref id."""
    return db_session.query(Spmillref).filter(Spmillref.spec_id == spec_id, Spmillref.spec_code == spec_code).one_or_none()

def create(*, db_session, spmillref_in: SpmillrefCreate) -> Spmillref:
    """Creates an spmillref."""

    spec = None
    mill = None
    if spmillref_in.spec_id:
        spec = db_session.query(Spec).filter(Spec.id == spmillref_in.spec_id).one_or_none()

    if spmillref_in.mill_id:
        mill = db_session.query(Mill).filter(Mill.id == spmillref_in.mill_id).one_or_none()

    if spmillref_in.other_mill_id:
        other_mill = db_session.query(Mill).filter(Mill.id == spmillref_in.other_mill_id).one_or_none()

    contact = Spmillref(**spmillref_in.dict(exclude={"flex_form_data", "spec", "mill", "other_mill"}),
                    mill=mill,
                    spec=spec,
                    other_mill=other_mill,
                    flex_form_data=spmillref_in.flex_form_data)

    db_session.add(contact)
    db_session.commit()
    return contact


def update(
    *,
    db_session,
    spmillref: Spmillref,
    spmillref_in: SpmillrefUpdate,
) -> Spmillref:

    if spmillref_in.mill_id:
        spmillref.mill = db_session.query(Mill).filter(Mill.id == spmillref_in.mill_id).one_or_none()

    if spmillref_in.other_mill_id:
        spmillref.other_mill = db_session.query(Mill).filter(Mill.id == spmillref_in.other_mill_id).one_or_none()


    update_data = spmillref_in.dict(
        exclude={"flex_form_data", "spec", "mill", "other_mill"},
    )
    for field, field_value in update_data.items():
        setattr(spmillref, field, field_value)

    spmillref.flex_form_data = spmillref_in.flex_form_data
    db_session.add(spmillref)
    db_session.commit()
    return spmillref


def update_new(*,db_session,spmillref: Spmillref, spmillref_in:dict) -> Spmillref:
    for field, field_value in spmillref_in.items():
        setattr(spmillref, field, field_value)

    db_session.add(spmillref)
    db_session.commit()
    return spmillref


def delete(*, db_session, id: int):
    spmillref = db_session.query(Spmillref).filter(Spmillref.id == id).one_or_none()

    if spmillref:
        spmillref.is_deleted = 1
    db_session.add(spmillref)
    db_session.commit()

    return spmillref


def get_by_spec_code(*, db_session, search_dict:SpmillrefBySpecCode):

    spmillref = db_session.query(Spmillref).join(Spec).filter(Spec.spec_code==search_dict.spec_code)

    if not spmillref:
        raise HTTPException(status_code=400, detail="The spmillref with this id does not exist.")

    query, pagination = apply_pagination(spmillref, page_number=search_dict.page, page_size=search_dict.itemsPerPage)

    return {
        "items": query.all(),
        "itemsPerPage": pagination.page_size,
        "page": pagination.page_number,
        "total": pagination.total_results,

    }



def create_by_copy_spec_code(*, db_session, copy_dict: SpmillrefCopyToCode,current_user):
    # 通过复制前的spec_code 查询数据
    copy_before_values = db_session.query(Spmillref).join(Spec).filter(Spec.spec_code==copy_dict.before_code).all()

    if not copy_before_values:
        raise HTTPException(status_code=400, detail="The spmillref with this spec_code does not exist.")

    # 查询copy to 的spec记录
    copy_to_spec = db_session.query(Spec).filter(Spec.spec_code == copy_dict.after_code).order_by(Spec.id.desc()).first()

    if not copy_to_spec:
        raise HTTPException(status_code=400, detail="The spmillref with this spec_code does not exist.")

    after_list = []
    try:
        for cbv in copy_before_values:

            is_cunzai = db_session.query(Spmillref).filter(Spmillref.spec_id == copy_to_spec.id,
                                                            Spmillref.thick_from == cbv.thick_from,
                                                            Spmillref.thick_to == cbv.thick_to).first()

            if is_cunzai:
                continue

            cbv_value = SpmillrefCreate(**cbv.__dict__)
            cbv_value.created_by = current_user.email
            after_list.append(Spmillref(**cbv_value.dict(exclude={"flex_form_data", "spec", "mill", "other_mill"}), spec=copy_to_spec, mill=cbv.mill, other_mill=cbv.other_mill))

        if len(after_list) > 0:
            db_session.add_all(after_list)
            db_session.commit()
        else:
            raise HTTPException(status_code=400, detail="There are no replicable objects.")

    except Exception as err:
        db_session.rollback()
        # 输出异常信息
        logger.error(f"Failed: {str(err)}")



    return True


################ 通过TBM的spec id 映射SRSM spec code ################
def TBM_to_SRSM_by_spec(db_session, spmillref_list: list, SRSM_spec: str) -> str:


    return ""
