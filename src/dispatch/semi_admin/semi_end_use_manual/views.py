from dispatch.cast.models import Cast
from dispatch.database import get_db
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from dispatch.product_category.models import ProductCategory
from dispatch.spec_admin.spec.models import Spec
from dispatch.system_admin.auth.models import DispatchUser
from dispatch.system_admin.auth.service import get_current_user

from dispatch.database_util.service import common_parameters, search_filter_sort_paginate
from .models import (
    SemiEndUseManual,
    SemiEndUseManualCreate,
    SemiEndUseManualPagination,
    SemiEndUseManualRead,
    SemiEndUseManualUpdate,
    SemiEndUseManualNew,
    GetByCastSpec,
    SemiEndUseManualBlukCrreate
)
from .service import create, delete, get, get_by_code, update, update_new, get_by_cast_spec, cast_spec_compare
from datetime import datetime, timezone

router = APIRouter()


@router.get("/", response_model=SemiEndUseManualPagination)
def get_filters(*, db_session: Session = Depends(get_db), common: dict = Depends(common_parameters)):
    query = db_session.query(SemiEndUseManual).outerjoin(Spec, SemiEndUseManual.spec_id == Spec.id
                                                        ).outerjoin(Cast, SemiEndUseManual.cast_id == Cast.id
                                                        ).outerjoin(ProductCategory, SemiEndUseManual.product_category_id == ProductCategory.id)
                                                         
    common['query'] = query
    return search_filter_sort_paginate(model="SemiEndUseManual", **common)


@router.post("/", response_model=SemiEndUseManualRead)
def create_obj(*, db_session: Session = Depends(get_db), request_in: SemiEndUseManualCreate,
                 current_user: DispatchUser = Depends(get_current_user)):
    """
    Create a new semi_end_use_manual contact.
    """
    
    # spyield = get_by_code(db_session=db_session,code=request_in.code)
    
    
    # if spyield:
    #     raise HTTPException(status_code=400, detail="The spyield with this code already exists.")
    
    request_in.created_by = current_user.email
    request_in.updated_by = current_user.email
    manual = create(db_session=db_session, manual_in=request_in)
    return manual


@router.post("/bulk_create")
def bulk_create(*, db_session: Session = Depends(get_db), current_user: DispatchUser = Depends(get_current_user), request_in: SemiEndUseManualBlukCrreate):
    add_list = []
    for item in request_in.items:
        item.created_by = current_user.email
        item.updated_by = current_user.email
        item.product_category_id = request_in.product_category_id
        item.cast_id = request_in.cast_id
        item.mill_id = request_in.mill_id
        if not request_in.force:
            if item.flange_min is None or item.flange_max is None:
                raise HTTPException(status_code=400, detail="Flange min and max are required.")
            msg = cast_spec_compare(db_session=db_session, cast_id=item.cast_id, spec_id=item.spec_id, thick_from=item.flange_min, thick_to=item.flange_max)
            if msg:
                raise HTTPException(status_code=400, detail="\n".join(msg))
        add_list.append(create(db_session=db_session, manual_in=item))
    return add_list


@router.get("/{manual_id}", response_model=SemiEndUseManualRead)
def get_manual(*, db_session: Session = Depends(get_db), manual_id: int):
    """
    Get a manual contact.
    """
    manual = get(db_session=db_session, id=manual_id)
    if not manual:
        raise HTTPException(status_code=400, detail="The manual with this id does not exist.")
    return manual


@router.put("/{manual_id}", response_model=SemiEndUseManualRead)
def update_manual(
    *,
    db_session: Session = Depends(get_db),
    manual_id: int,
    manual_in: SemiEndUseManualUpdate, current_user: DispatchUser = Depends(get_current_user)
):
    """
    Update a spyield contact.
    """
    manual = get(db_session=db_session, id=manual_id)
    if not manual:
        raise HTTPException(status_code=400, detail="The manual with this id does not exist.")

    manual_in.created_at = manual.created_at
    manual_in.updated_at = datetime.now()
    manual_in.created_by = manual.created_by
    manual_in.updated_by = current_user.email
    if not manual_in.force:
        if manual_in.flange_min is None or manual_in.flange_max is None:
            raise HTTPException(status_code=400, detail="Flange min and max are required.")
        msg = cast_spec_compare(db_session=db_session, cast_id=manual_in.cast_id, spec_id=manual_in.spec_id, thick_from=manual_in.flange_min, thick_to=manual_in.flange_max)
        if msg:
            raise HTTPException(status_code=400, detail="\n".join(msg))
    manual = update(
        db_session=db_session,
        manual=manual,
        manual_in=manual_in,
    )
    return manual
    

@router.post("/update/", response_model=SemiEndUseManualRead)
def update_manual_new(
    *, 
    db_session: Session = Depends(get_db), 
    manual_in: SemiEndUseManualNew, 
    current_user: DispatchUser = Depends(get_current_user)
):
    manual_id = manual_in.id
    manual = get(db_session=db_session, id=manual_id)
    if not manual:
        raise HTTPException(status_code=400, detail="The manual with this id does not exist.")
    manual_in.data["updated_at"] = datetime.now(timezone.utc)
    manual_in.data["updated_by"] = current_user.email
    manual = update_new(
        db_session=db_session,
        manual=manual,
        manual_in=manual_in.data,
    )
    return manual


@router.put("/manual_code/{manual_code}", response_model=SemiEndUseManualRead)
def update_manual_by_code(
    *,
    db_session: Session = Depends(get_db),
    manual_code: str,
    manual_in: SemiEndUseManualUpdate, current_user: DispatchUser = Depends(get_current_user)
):
    """
    Update a manual contact.
    """
    manual = get_by_code(db_session=db_session, code=manual_code)
    if not manual:
        raise HTTPException(status_code=400, detail="The manual with this id does not exist.")

    manual_in.updated_by = current_user.email
    manual = update(
        db_session=db_session,
        manual=manual,
        manual_in=manual_in,
    )

    return manual


@router.delete("/{manual_id}", response_model=SemiEndUseManualRead)
def delete_manual(*, db_session: Session = Depends(get_db), manual_id: int):
    """
    Delete a manual contact.
    """
    manual = get(db_session=db_session, id=manual_id)
    if not manual:
        raise HTTPException(status_code=400, detail="The manual with this id does not exist.")

    return delete(db_session=db_session, id=manual_id)


@router.post("/get_by_cast_spec/", response_model=SemiEndUseManualPagination)
def update_manual_new(
    *, 
    db_session: Session = Depends(get_db), 
    filters: GetByCastSpec, 
    current_user: DispatchUser = Depends(get_current_user)
):
    manual = get_by_cast_spec(db_session=db_session,filters=filters)
    return manual