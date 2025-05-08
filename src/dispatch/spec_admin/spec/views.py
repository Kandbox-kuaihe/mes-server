from sqlalchemy import desc
from dispatch.database import get_db, get_class_by_tablename

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from dispatch.spec_admin.spbend.models import Spbend, SpbendCreate
from dispatch.spec_admin.spcev.models import Spcev, SpcevCreate
from dispatch.spec_admin.spcevan.models import Spcevan, SpcevanCreate
from dispatch.spec_admin.spcombel.models import Spcombel, SpComBelCreate
from dispatch.spec_admin.spelong.models import Spelong, SpeLongCreate
from dispatch.spec_admin.spimpact.models import Spimpact, SpImpactCreate
from dispatch.spec_admin.spjominy.models import Spjominy, SpecJominyCreate
from dispatch.spec_admin.spmainel.models import SpMainElUpdate, Spmainel
from dispatch.spec_admin.spmillref.models import Spmillref, SpmillrefCreate
from dispatch.spec_admin.spprodan.models import Spprodan, SpprodanCreate
from dispatch.spec_admin.spscond.models import Spscond, SpscondCreate
from dispatch.spec_admin.spsource.models import Spsource, SpsourceCreate
from dispatch.spec_admin.sptcert.models import Sptcert, SptcertCreate
from dispatch.spec_admin.sptensil.models import Sptensil, SptensilCreate
from dispatch.spec_admin.spyield.models import Spyield, SpyieldCreate
from dispatch.system_admin.auth.models import DispatchUser
from dispatch.system_admin.auth.service import get_current_user
from dispatch.spec_admin.spprodan_other_element.models import SpprodanOtherElement
from dispatch.spec_admin.spmainel_other_element.models import SpmainelOtherElement
from dispatch.spec_admin.spprodan_other_element.service import get_by_spprodan_id
from dispatch.spec_admin.spmainel_other_element.service import get_by_spmainel_id
from sqlalchemy.exc import SQLAlchemyError

from dispatch.database_util.service import common_parameters, search_filter_sort_paginate
from .models import (
    Spec,
    SpecCreate,
    SpecPagination,
    SpecRead,
    SpecUpdate,
    SpecUpdateNew,
    SpecByCode,
    SpecVersion,
    ChildrenSelectRespone,
    ChildrenSelect
)
from .service import create, delete, get, get_by_code, update, update_new, get_by_code_short_full, spec_version_update, \
    archive_spec_version_update
from datetime import datetime, timezone
from dispatch.spec_admin.inspector import service as inspector_service
from ...config import get_mill_ops, MILLEnum
# from ...contrib.message_admin.message_server import message_strategy

router = APIRouter()

from dispatch.spec_admin.spec import service as spec_service


@router.get("/import_spec_data_to_mes/")
def import_spec_data_to_mes(
    *,
    db_session: Session = Depends(get_db),
    current_user: DispatchUser = Depends(get_current_user)
):
    schema = f"dispatch_organization_{current_user.org_code}"
    try:
        from ...contrib.script.yinggang_to_mes_sql import import_data_to_mes
        import_data_to_mes.import_data_to_mes(schema=schema)
    except ImportError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/validate_spec_id_by_cast/{cast_id}")
def validate_spec_id_by_cast(
    *,
    db_session: Session = Depends(get_db),
    cast_id: int,
    current_user: DispatchUser = Depends(get_current_user)
):
    try:
        from dispatch.contrib.cover.get_spec_service.utils import get_spec_list
        return get_spec_list(db_session=db_session, cast_id=cast_id)
    except ImportError as e:
        raise HTTPException(status_code=400, detail=str(e))
   

@router.get("/", response_model=SpecPagination)
def get_specs(*, db_session: Session = Depends(get_db), common: dict = Depends(common_parameters), version_status:str = Query(None), spec_code: str = Query(None)):
    if common["sort_by"] and common["sort_by"][0] == "mill_code":
        common["sort_by"][0] = "mill.code"

    if version_status  and version_status != "All":
        query = db_session.query(Spec).filter(Spec.version_status == version_status)
        common["query"] = query


    if common["query_str"]:
        common["filter_type"]  = "or"
        common["fields"] = ["spec_code", "short_name", "full_name"]
        common["ops"] = ["ilike", "ilike","ilike"]
        common["values"] = [f"%{common['query_str']}%",f"%{common['query_str']}%", f"%{common['query_str']}%"]
        common["query_str"] = ''

    if spec_code:
        common['query'] = db_session.query(Spec).filter(Spec.spec_code.ilike(f"%{spec_code}%"))


    return search_filter_sort_paginate(model="Spec", **common)

@router.get("/spec_code/{code}/{mill}/{version_status}", response_model=SpecRead)
def get_spec_by_code(*, db_session: Session = Depends(get_db), code: str, mill: int, version_status: str):

    spec = get_by_code(db_session=db_session, code=code, mill=mill, version_status=version_status)
    if not spec:
        raise HTTPException(status_code=400, detail="The spec with this id does not exist.")
    return spec


@router.post("/", response_model=SpecRead)
def create_spec(
    *,
    db_session: Session = Depends(get_db),
    spec_in: SpecCreate,
    current_user: DispatchUser = Depends(get_current_user)
):
    """
    Create a new spec contact.
    """

    # spec = get_by_code(db_session=db_session, code=spec_in.spec_code)

    # if spec:
    #     raise HTTPException(status_code=400, detail="The spec with this code already exists.")
    
    spec_in.created_by = current_user.email
    spec_in.updated_by = current_user.email
    spec_in.mill_id = current_user.current_mill_id
    spec = create(db_session=db_session, spec_in=spec_in)

    inspectors = inspector_service.get_by_ids(db_session=db_session, ids=spec_in.inspector)
    spec.inspector = inspectors

    children_specs = spec_service.get_by_ids(db_session=db_session, ids=spec_in.children_specs)
    spec.children_specs = children_specs

    db_session.add(spec)
    db_session.commit()   
    return spec


@router.get("/{spec_id}", response_model=SpecRead)
def get_spec(*, db_session: Session = Depends(get_db), spec_id: int):
    """
    Get a spec contact.
    """
    spec = get(db_session=db_session, id=spec_id)
    if not spec:
        raise HTTPException(status_code=400, detail="The spec with this id does not exist.")
    return spec


@router.put("/{spec_id}", response_model=SpecRead)
def update_spec(
    *,
    db_session: Session = Depends(get_db),
    spec_id: int,
    spec_in: SpecUpdate,
    background_tasks: BackgroundTasks,
    current_user: DispatchUser = Depends(get_current_user),
):
    """
    Update a spec contact.
    """
    spec = get(db_session=db_session, id=spec_id)
    if not spec:
        raise HTTPException(status_code=400, detail="The spec with this id does not exist.")
    
    
    inspectors = inspector_service.get_by_ids(db_session=db_session, ids=spec_in.inspector)
    children_specs = spec_service.get_by_ids(db_session=db_session, ids=spec_in.children_specs)
    spec = update(
        db_session=db_session,
        spec=spec,
        spec_in=spec_in,
        inspectors=inspectors,
        children_specs=children_specs
    )

    # Check SRSM
    if get_mill_ops(spec.mill_id) == MILLEnum.MILL1:
        background_tasks.add_task(send_srsm_spec_msg, db_session, spec)

    return spec

def send_srsm_spec_msg(db_session, spec):
    try:
        from ...contrib.message_admin.message_server import message_strategy
        srsmxspe_a = message_strategy.MessageStrategyXSPE_A()
        srsmxspe_b = message_strategy.MessageStrategyXSPE_B()
        if spec.type == "rail":
            srsmxspe_a.handle(db_session=db_session, spec=spec, rspe=True)
            srsmxspe_b.handle(db_session=db_session, spec=spec)
        elif spec.type == "srsm_section":
            srsmxspe_a.handle(db_session=db_session, spec=spec, rspe=False)
        del srsmxspe_a
        del srsmxspe_b
    except ImportError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/update/", response_model=SpecRead)
def update_spec_new(
    *, 
    db_session: Session = Depends(get_db), 
    spec_in: SpecUpdateNew, 
    current_user: DispatchUser = Depends(get_current_user)
):
    spec_id = spec_in.id
    spec = get(db_session=db_session, id=spec_id)
    if not spec:
        raise HTTPException(status_code=400, detail="The spec with this id does not exist.")
    spec_in.data["updated_at"] = datetime.now(timezone.utc)
    spec_in.data["updated_by"] = current_user.email
    spec = update_new(
        db_session=db_session,
        spec=spec,
        spec_in=spec_in.data,
    )
    return spec


@router.put("/spec_code/{spec_code}", response_model=SpecRead)
def update_spec_by_code(
    *,
    db_session: Session = Depends(get_db),
    spec_code: str,
    spec_in: SpecUpdate,
    current_user: DispatchUser = Depends(get_current_user)
):
    """
    Update a spec contact.
    """
    spec = get_by_code(db_session=db_session, code=spec_code)
    if not spec:
        raise HTTPException(status_code=400, detail="The spec with this id does not exist.")

    spec_in.updated_by = current_user.email
    spec = update(
        db_session=db_session,
        spec=spec,
        spec_in=spec_in,
    )

    return spec


@router.delete("/{spec_id}", response_model=SpecRead)
def delete_spec(*, db_session: Session = Depends(get_db), spec_id: int):
    """
    Delete a spec contact.
    """
    spec = get(db_session=db_session, id=spec_id)
    if not spec:
        raise HTTPException(status_code=400, detail="The spec with this id does not exist.")

    return delete(db_session=db_session, spec_id=spec_id)


@router.post("/copy/{spec_id}", response_model=SpecRead)
def copy_spec(
    *,
    db_session: Session = Depends(get_db),
    spec_in: SpecCreate,
    spec_id: int,
    current_user: DispatchUser = Depends(get_current_user)
    ):
    spec_in.created_by = current_user.email
    spec_in.updated_by = current_user.email
    original_spec = get(db_session=db_session, id=spec_id)
    if not original_spec:
        raise HTTPException(status_code=400, detail="Spec not found")
    page_tables = [
        'Spimpact','Sptensil', 'Spyield', 'Spelong', 'Spmainel', 'Spcombel', 'Spprodan', 'Spcev', 'Spcevan', 'Spsource', 'Spjominy', 'Spscond', 'Sptcert','Spmillref', 'Spbend'
    ]
    pages = {
        'Spimpact':SpImpactCreate,
        'Sptensil':SptensilCreate,
        'Spyield':SpyieldCreate,
        'Spelong':SpeLongCreate,
        'Spmainel':SpMainElUpdate,
        'Spcombel':SpComBelCreate,
        'Spprodan':SpprodanCreate,
        'Spcev':SpcevCreate,
        'Spcevan':SpcevanCreate,
        'Spsource':SpsourceCreate,
        'Spjominy':SpecJominyCreate,
        'Spscond':SpscondCreate,
        'Sptcert':SptcertCreate ,
        'Spmillref': SpmillrefCreate,
        'Spbend': SpbendCreate
    }
    pages_2 = {
        'Spimpact':Spimpact,
        'Sptensil':Sptensil,
        'Spyield':Spyield,
        'Spelong':Spelong,
        'Spmainel':Spmainel,
        'Spcombel':Spcombel,
        'Spprodan':Spprodan,
        'Spcev':Spcev,
        'Spcevan':Spcevan,
        'Spsource':Spsource,
        'Spjominy':Spjominy,
        'Spscond':Spscond,
        'Sptcert':Sptcert,
        'Spmillref': Spmillref,
        "Spbend": Spbend
    }
    try:
        # with db_session.begin():  # 开始一个事务
            new_record = insert_record(db_session=db_session,spec_code=spec_in.spec_code)
            spec_in.version = new_record
            spec_in.version_status = "D"
            spec_in.release_date = None
            spec_in.archive_date = None
            if spec_in.redio_type == "spec":
                if spec_in.spec_code is None:
                    existing_spec = db_session.query(Spec).filter(False)
                else:
                    existing_spec = db_session.query(Spec).filter(Spec.spec_code == spec_in.spec_code, Spec.is_deleted == 0).first()
                existing_spec = db_session.query(Spec).filter(Spec.spec_code == spec_in.spec_code).first()
                if existing_spec:
                    raise HTTPException(status_code=400, detail="The spec with this code already exists.")
            elif spec_in.redio_type == "version":
                spec_code_version_status = db_session.query(Spec).filter(Spec.spec_code == spec_in.spec_code, Spec.version_status == spec_in.version_status, Spec.is_deleted == 0).first()
                if spec_code_version_status:
                    raise HTTPException(status_code=400, detail="The spec with this code and version status already exists.")
            new_spec = create(db_session=db_session, spec_in=spec_in)
            for page_table in page_tables:
                model_cls = get_class_by_tablename(page_table)
                original_page = db_session.query(model_cls).filter(model_cls.spec_id == original_spec.id).order_by(desc(model_cls.created_at)).all()
                if original_page:
                    other_element_list= []
                    for original in original_page:
                        new_page_data = pages[page_table](**original.__dict__)
                        if page_table == 'Spmillref':
                            new_data = pages_2[page_table](**new_page_data.dict(exclude={"flex_form_data", "spec","other_element","mill","other_mill"}), spec=new_spec,mill=original.mill,other_mill=original.other_mill)
                        else:
                            new_data = pages_2[page_table](**new_page_data.dict(exclude={"flex_form_data", "spec","other_element","mill"}), spec=new_spec,mill=original.mill)

                        if page_table == "Spprodan":
                            other_elements = get_by_spprodan_id(db_session=db_session, id=original.id)
                            if len(other_elements) > 0:
                                for other_element in other_elements:
                                    other_value = {
                                        "code": other_element.code,
                                        "min_value": other_element.min_value,
                                        "max_value": other_element.max_value,
                                        "precision": other_element.precision,
                                        "created_by":current_user.email,
                                        "spprodan":new_data
                                    }
                                    other_element_list.append(SpprodanOtherElement(**other_value))
                        if page_table == "Spmainel":
                            other_elements = get_by_spmainel_id(db_session=db_session, id=original.id)
                            if len(other_elements) > 0:
                                for other_element in other_elements:
                                    other_value = {
                                        "code": other_element.code,
                                        "min_value": other_element.min_value,
                                        "max_value": other_element.max_value,
                                        "precision": other_element.precision,
                                        "element_abbr": other_element.element_abbr,
                                        "uom": other_element.uom,
                                        "created_by":current_user.email,
                                        "spmainel":new_data
                                    }
                                    other_element_list.append(SpmainelOtherElement(**other_value))
                        db_session.add(new_data)
            db_session.commit()
        
    except SQLAlchemyError as e:  # 捕获 SQLAlchemy 异常
        db_session.rollback()  # 手动回滚事务
        raise HTTPException(status_code=400, detail=f"Table insertion failure, {str(e)}")

    except Exception as e:  # 捕获其他异常
        db_session.rollback()  # 手动回滚事务
        raise HTTPException(status_code=400, detail=f"Unexpected error, {str(e)}")

    return new_spec


def insert_record(*, db_session, spec_code):
    # 查询当前spec_code下已有的最大编号记录
    last_record = db_session.query(Spec).filter(Spec.spec_code == spec_code).order_by(Spec.version.desc()).first()
    if last_record and last_record.version:
        new_number = last_record.version + 1
    else:
        new_number = 1

    new_record = new_number
    return new_record


@router.post("/spec_page_search/", response_model=SpecPagination)
def get_spec_by_code(*, db_session: Session = Depends(get_db), search_dict: SpecByCode):
    spcombel = get_by_code_short_full(db_session=db_session,search_dict=search_dict)
    return spcombel



@router.post("/spec_version", response_model=SpecRead)
def spec_version(*, db_session: Session = Depends(get_db), spec_in: SpecVersion):
    """
    Update spec version.
    """
    spec = get(db_session=db_session, id=spec_in.id)
    if not spec:
        raise HTTPException(status_code=400, detail="The spec with this id does not exist.")
    
    spec = spec_version_update(db_session=db_session,spec=spec)
    return spec


@router.post("/data/childrenspec", response_model=ChildrenSelectRespone)
def getChildrenSpecSelect(*, db_session: Session = Depends(get_db), current_user: DispatchUser = Depends(get_current_user), spec_in: dict):
    """
    """

    query = db_session.query(Spec).filter(Spec.spec_code.like(f'S%'))

    if "id" in spec_in:
        query = query.filter(Spec.id != spec_in.get("id"))

    if "spec_code" in spec_in and spec_in["spec_code"]:
        query = query.filter(Spec.spec_code.like(f"%{spec_in['spec_code']}%"))

    data_list = query.all()

    # if "id" in spec_in:
    #     data_list = db_session.query(Spec).filter(Spec.id != spec_in.get("id"), Spec.spec_code.like(f'S%')).all()
    # else:
    #     data_list = db_session.query(Spec).filter(Spec.spec_code.like(f'S%')).all()
    
    result_list = []
    for row in data_list:
        result_list.append( ChildrenSelect( id = row.id,  code = row.spec_code, name = row.short_name if row.short_name else ''  ) ) 
 
    return ChildrenSelectRespone(options=result_list)


@router.post("/data/srsmspeccode", response_model=ChildrenSelectRespone)
def getSrsmSpecCodeSelect(*, db_session: Session = Depends(get_db), current_user: DispatchUser = Depends(get_current_user), spec_in: dict):
    """
    """

    query = db_session.query(Spec).filter(Spec.version_status == 'R')

    if "id" in spec_in:
        query = query.filter(Spec.id != spec_in.get("id"))

    if "spec_code" in spec_in and spec_in["spec_code"]:
        query = query.filter(Spec.spec_code.ilike(f"%{spec_in['spec_code']}%"))

    data_list = query.all()

    # if "id" in spec_in:
    #     data_list = db_session.query(Spec).filter(Spec.id != spec_in.get("id"), Spec.version_status == 'R').all()
    # else:
    #     data_list = db_session.query(Spec).filter(Spec.version_status == 'R').all()
    
    result_list = []
    for row in data_list:
        name = str(row.version) + '-' + row.version_status
        result_list.append( ChildrenSelect( id = row.id,  code = row.spec_code, name = name  ) ) 
 
    return ChildrenSelectRespone(options=result_list)


@router.post("/archive_spec_version", response_model=SpecRead)
def archive_spec_version(*, db_session: Session = Depends(get_db), spec_in: SpecVersion):
    """
    Update spec version.
    """
    spec = get(db_session=db_session, id=spec_in.id)
    if not spec:
        raise HTTPException(status_code=400, detail="The spec with this id does not exist.")
    
    spec = archive_spec_version_update(db_session=db_session,spec=spec)
    return spec


@router.get("/update_suspended/{spec_id}", response_model=SpecRead)
def update_suspended(*, db_session: Session = Depends(get_db), spec_id: int):
    """
    Update spec suspended.
    """
    spec = get(db_session=db_session, id=spec_id)
    if not spec:
        raise HTTPException(status_code=400, detail="The spec with this id does not exist.")
    spec.suspended = not spec.suspended
    db_session.commit()
    return spec