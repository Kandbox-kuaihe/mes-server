from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from dispatch.system_admin.auth.models import DispatchUser
from dispatch.system_admin.auth.service import get_current_user
from dispatch.database import get_db
from .models import (
    RemarkCreate, RemarkPagination, RemarkRead, RemarkUpdate, SpecRemarkRead, SpecRemarkCreate, 
    EditorNotesCreate, EditorNotesRead, SpecTextRead, SpecTextCreate
)
from .service import (
    create_remark, delete_remark, get_remark_by_id, update_remark, get_remark_by_code, 
    get_spec_editor_notes, create_editor_notes, get_spec_text, update_notes, delete_notes,
    create_spec_text, update_text, delete_text, get_spec_remark_by_id
)
from dispatch.database_util.service import common_parameters, search_filter_sort_paginate
from typing import List
from dispatch.spec_admin.spec.models import Spec
from dispatch.spec_admin.remark.models import Remark
from dispatch.spec_admin.remark.service import (
    add_spec_remark_association,
    remove_spec_remark_association,
    get_remarks_by_spec,
    get_specs_by_remark,
    is_association_exists,
)

router = APIRouter()


@router.get("/get_all/", response_model=RemarkPagination)
def get_remarks(*, common: dict = Depends(common_parameters)):
    return search_filter_sort_paginate(model="Remark", **common)


@router.get("/{id}", response_model=RemarkRead)
def get_remark_by_id_view(*, db_session: Session = Depends(get_db), id: int):
    """
    Get a remark by ID.
    """
    remark = get_remark_by_id(db=db_session, remark_id=id)
    if not remark:
        raise HTTPException(status_code=400, detail="The remark with this id does not exist.")
    return remark


@router.get("/code/{code}", response_model=RemarkRead)
def get_remark_by_code_view(*, db_session: Session = Depends(get_db), code: str):
    """
    Get a remark by code.
    """
    remark = get_remark_by_code(db=db_session, code=code)
    if not remark:
        raise HTTPException(status_code=400, detail="The remark with this code does not exist.")
    return remark


@router.post("/create", response_model=RemarkRead)
def create_remark_view(*, db_session: Session = Depends(get_db), remark_in: RemarkCreate,
                       current_user: DispatchUser = Depends(get_current_user)):
    """
    Create a new remark.
    """
    remark_in.created_by = current_user.email
    remark = create_remark(db=db_session, remark_data=remark_in)
    return remark


@router.put("/update/{id}", response_model=RemarkRead)
def update_remark_view(*, db_session: Session = Depends(get_db), id: int, remark_in: RemarkUpdate,
                       current_user: DispatchUser = Depends(get_current_user)):
    """
    Update a remark.
    """
    remark = get_remark_by_id(db=db_session, remark_id=id)
    if not remark:
        raise HTTPException(status_code=400, detail="The remark with this id does not exist.")

    remark_in.updated_by = current_user.email
    updated_remark = update_remark(db=db_session, remark_id=id, remark_data=remark_in)
    return updated_remark


@router.delete("/{id}", response_model=RemarkRead)
def delete_remark_view(*, db_session: Session = Depends(get_db), id: int):
    """
    Delete a remark.
    """
    remark = get_remark_by_id(db=db_session, remark_id=id)
    if not remark:
        raise HTTPException(status_code=400, detail="The remark with this id does not exist.")
    delete_remark(db=db_session, remark_id=id)
    return RemarkRead(id=id)


# many2many

# 添加 Spec 和 Remark 的关联关系
@router.post("/spec_remark/create")
def associate_spec_remark(spec_remark_in: SpecRemarkCreate, db: Session = Depends(get_db)):
    """
    添加 Spec 和 Remark 的关联关系。
    :param spec_id: Spec 的 ID
    :param remark_id: Remark 的 ID
    """
    if is_association_exists(db, spec_remark_in.spec_id, spec_remark_in.remark_id):
        raise HTTPException(status_code=400, detail="关联关系已存在")
    add_spec_remark_association(db, spec_remark_in.spec_id, spec_remark_in.remark_id)
    return {"status": 200, "message": "关联关系已添加"}


# 删除 Spec 和 Remark 的关联关系
@router.post("/spec_remark/delete")
def dissociate_spec_remark(spec_remark_in: SpecRemarkCreate, db: Session = Depends(get_db)):
    """
    删除 Spec 和 Remark 的关联关系。
    :param spec_id: Spec 的 ID
    :param remark_id: Remark 的 ID
    """
    if not is_association_exists(db, spec_remark_in.spec_id, spec_remark_in.remark_id):
        raise HTTPException(status_code=400, detail="关联关系不存在")
    remove_spec_remark_association(db, spec_remark_in.spec_id, spec_remark_in.remark_id)
    return {"status": 200, "message": "关联关系已解除"}


# 获取与指定 Spec 关联的所有 Remark
@router.get("/spec_remark/get_remark/{spec_id}", response_model=List[RemarkRead])
def get_remarks_for_spec(spec_id: int, db: Session = Depends(get_db)):
    """
    获取与指定 Spec 关联的所有 Remark。
    :param spec_id: Spec 的 ID
    """
    remarks = get_remarks_by_spec(db, spec_id)
    if not remarks:
        return []
    return remarks


# 获取指定 Spec 关联的editor notes
@router.get("/spec_remark/get_editor_notes/{spec_id}", response_model=List[EditorNotesRead])
def get_editor_notes(spec_id: int, db: Session = Depends(get_db)):
    """
    获取指定 Spec 关联的editor notes。
    :param spec_id: Spec 的 ID
    """
    editor_notes = get_spec_editor_notes(db, spec_id)
    if not editor_notes:
        return []
    return editor_notes


# 新增 Editor Notes
@router.post("/spec_remark/create_editor_notes")
def add_editor_notes(editor_notes_in: EditorNotesCreate, db: Session = Depends(get_db), current_user: DispatchUser = Depends(get_current_user)):
    """
    新增 Editor Notes。
    :param spec_id: Spec 的 ID
    :param editor_notes_in: editor notes 数据
    """
    editor_notes_in.created_by = current_user.email
    create_editor_notes(db_session=db, spec_remark_in=editor_notes_in)
    return {"status": 200, "message": "Editor Notes has added!"}


# 更新 Editor Notes
@router.put("/spec_remark/update_editor_notes/{id}")
def update_editor_notes(editor_notes_in: EditorNotesCreate, id: int, db: Session = Depends(get_db)):
    """
    更新 Editor Notes。
    :param spec_id: Spec 的 ID
    :param editor_notes_in: editor notes 数据
    """
    spec_remark_obj = get_spec_remark_by_id(db_session=db, id=id)
    if not spec_remark_obj:
        raise HTTPException(status_code=400, detail="The editor notes with this id does not exist.")

    update_notes(db_session=db, editor_id=id, spec_remark_in=editor_notes_in)
    return {"status": 200, "message":"Editor Notes has updated!"}


# 删除 Editor Notes
@router.delete("/spec_remark/delete_editor_notes/{id}")
def delete_editor_notes(id: int, db: Session = Depends(get_db)):
    """
    删除 Editor Notes。
    :param spec_id: Spec 的 ID
    :param editor_notes_in: editor notes 数据
    """
    spec_remark_obj = get_spec_remark_by_id(db_session=db, id=id)
    if not spec_remark_obj:
        raise HTTPException(status_code=400, detail="The editor notes with this id does not exist.")

    delete_notes(db_session=db, editor_id=id)
    return {"status": 200, "message":"Editor Notes has deleted!"}


# 获取指定 Spec 关联的Specification Text
@router.get("/spec_remark/get_spec_text/{spec_id}", response_model=List[SpecTextRead])
def get_editor_notes(spec_id: int, db: Session = Depends(get_db)):
    """
    获取指定 Spec 关联的 spec text。
    :param spec_id: Spec 的 ID
    """
    spec_text = get_spec_text(db, spec_id)
    if not spec_text:
        return []
    return spec_text


# 新增 Specification Text
@router.post("/spec_remark/create_spec_text")
def add_spec_text(spec_text_in: SpecTextCreate, db: Session = Depends(get_db), current_user: DispatchUser = Depends(get_current_user)):
    """
    新增 Specification Text。
    :param spec_id: Spec 的 ID
    :param spec_text_in: spec text 数据
    """
    spec_text_in.created_by = current_user.email
    create_spec_text(db_session=db, spec_remark_in=spec_text_in)
    return {"status": 200, "message": "Spec Text has added!"}


# 更新 Specification Text
@router.put("/spec_remark/update_spec_text/{id}")
def update_spec_text(spec_text_in: SpecTextCreate, id: int, db: Session = Depends(get_db)):
    """
    更新 Specification Text。
    :param spec_id: Spec 的 ID
    :param spec_text_in: spec text 数据
    """
    spec_remark_obj = get_spec_remark_by_id(db_session=db, id=id)
    if not spec_remark_obj:
        raise HTTPException(status_code=400, detail="The spec text with this id does not exist.")

    update_text(db_session=db, spec_text_id=id, spec_remark_in=spec_text_in)
    return {"status": 200, "message":"Spec Text has updated!"}


# 删除 Specification Text
@router.delete("/spec_remark/delete_spec_text/{id}")
def delete_spec_text(id: int, db: Session = Depends(get_db)):
    """
    删除 Specification Text。
    :param spec_id: Spec 的 ID
    :param spec_text_in: spec text 数据
    """
    spec_remark_obj = get_spec_remark_by_id(db_session=db, id=id)
    if not spec_remark_obj:
        raise HTTPException(status_code=400, detail="The spec text with this id does not exist.")

    delete_text(db_session=db, spec_text_id=id)
    return {"status": 200, "message":"Spec Text has deleted!"}
