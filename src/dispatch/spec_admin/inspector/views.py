from fastapi import APIRouter, Depends, HTTPException
from .models import Inspector, InspectorCreate, InspectorUpdate, InspectorRead, InspectorPagination, InspectorResponse, InspectorSelectRespone, InspectorSelect
from dispatch.database_util.service import common_parameters, search_filter_sort_paginate
from sqlalchemy.orm import Session
from dispatch.database import get_db
from dispatch.system_admin.auth.models import DispatchUser
from dispatch.system_admin.auth.service import get_current_user
from .service import create, delete, get, update, get_by_code, get_all_select
from dispatch.spec_admin.inspector.models_secondary import spec_inspector_table

router = APIRouter()


@router.get("/", response_model=InspectorPagination)
def get_all(*, common: dict=Depends(common_parameters)):

    db_session = common["db_session"]
    if common['fields'] and ("combine_inspector_spec_id" in common['fields']):
        index = common['fields'].index("combine_inspector_spec_id")
        spec_id = common['values'][index]
        inspector_ids = db_session.query(spec_inspector_table.c.inspector_id).filter(spec_inspector_table.c.spec_id == spec_id).all()
        inspector_ids = [item[0] for item in inspector_ids]
        common['query'] = db_session.query(Inspector).filter(Inspector.id.in_(inspector_ids))
        common['fields'].pop(index)
        common['ops'].pop(index)
        common['values'].pop(index)
    return search_filter_sort_paginate(model="Inspector", **common)

@router.post("/", response_model=InspectorCreate)
def create_inspector(*, db_session: Session = Depends(get_db), inspector_in: InspectorResponse,
                      current_user: DispatchUser = Depends(get_current_user)):
    existed = get_by_code(db_session=db_session, code=inspector_in.code)

    if existed:
        raise HTTPException(status_code=400, detail="The Inspector with this code already exists.")
    created = create(db_session=db_session, inspector_in=inspector_in)
    return created

@router.put("/{inspector_id}", response_model=InspectorRead)
def update_inspector(
    *,
    db_session: Session = Depends(get_db),
    current_user: DispatchUser = Depends(get_current_user),
    inspector_id: int,
    inspector_in: InspectorUpdate
):
    inspector = get(db_session=db_session, id=inspector_id)
    if not inspector:
        raise HTTPException(status_code=400, detail="The Inspector with this id does not exist.")
    updated = update(db_session=db_session, item=inspector, item_in=inspector_in)
    return updated

@router.delete("/{inspector_id}")
def delete_inspector(
    *,
    db_session: Session = Depends(get_db),
    current_user: DispatchUser = Depends(get_current_user),
    inspector_id: int
):
    inspector = get(db_session=db_session, id=inspector_id)
    if not inspector:
        raise HTTPException(status_code=400, detail="The Inspector with this id does not exist.")
    deleted = delete(db_session=db_session, id=inspector_id)
    return deleted


@router.get("/data/inspectorSelect", response_model=InspectorSelectRespone)
def getInspectorSelect(*, db_session: Session = Depends(get_db), current_user: DispatchUser = Depends(get_current_user)):
    """
    """

    data_list = get_all_select(db_session=db_session )
    
    result_list = []
    for row in data_list:
        result_list.append( InspectorSelect( id = row.id,  code = row.code, name = row.name  ) ) 
 
    return InspectorSelectRespone(options=result_list)