from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy.sql import and_, desc
from typing import List, Optional, Dict, Any
from dispatch.spec_admin.remark.models import (
    Remark, RemarkCreate, RemarkUpdate,SpecRemarkRead, EditorNotesCreate, SpecTextRead, SpecTextCreate
)
from fastapi.encoders import jsonable_encoder


def get_remark_by_id(db: Session, remark_id: int) -> Optional[Remark]:
    """
    Retrieve a single remark by ID.
    """
    return db.query(Remark).filter(Remark.id == remark_id).first()


def get_remark_by_code(db: Session, code: str) -> Optional[Remark]:
    """
    Retrieve a single remark by its unique code.
    """
    return db.query(Remark).filter(Remark.code == code).first()


def get_all_remarks(db: Session) -> List[Remark]:
    """
    Retrieve all remarks.
    """
    return db.query(Remark).all()


def create_remark(db: Session, remark_data: RemarkCreate) -> Remark:
    """
    Create a new remark with flexible fields.
    """
    db_remark = Remark(
        **remark_data.model_dump(exclude={'mill'})
    )
    print(remark_data.model_dump())
    db.add(db_remark)
    db.commit()
    db.refresh(db_remark)
    return db_remark


def update_remark(db: Session, remark_id: int, remark_data: RemarkUpdate) -> Remark:
    remark = db.query(Remark).filter(Remark.id == remark_id).first()
    for field, value in remark_data.dict(exclude_unset=True).items():
        if field in remark.__dict__:
            setattr(remark, field, value)
    db.commit()
    db.refresh(remark)
    return remark


def delete_remark(db: Session, remark_id: int) -> bool:
    """
    Delete a remark by ID.
    """
    db_remark = get_remark_by_id(db, remark_id)
    if not db_remark:
        return False

    db.delete(db_remark)
    db.commit()
    return True


# many2many
from sqlalchemy.orm import Session
from typing import List
from fastapi import HTTPException

from dispatch.spec_admin.remark.models_secondary import spec_remark_table
from dispatch.spec_admin.spec.models import Spec  # 假设 Spec 模型已定义
from dispatch.spec_admin.remark.models import Remark  # 假设 Remark 模型已定义


# 创建关联关系
def add_spec_remark_association(db_session: Session, spec_id: int, remark_id: int):
    """
    添加 Spec 和 Remark 的关联关系。

    :param db_session: 数据库会话对象
    :param spec_id: Spec 的 ID
    :param remark_id: Remark 的 ID
    """
    stmt = spec_remark_table.insert().values(spec_id=spec_id, remark_id=remark_id, remark_type="r")
    db_session.execute(stmt)
    db_session.commit()


# 删除关联关系
def remove_spec_remark_association(db_session: Session, spec_id: int, remark_id: int):
    """
    删除 Spec 和 Remark 的关联关系。

    :param db_session: 数据库会话对象
    :param spec_id: Spec 的 ID
    :param remark_id: Remark 的 ID
    """
    stmt = spec_remark_table.delete().where(
        (spec_remark_table.c.spec_id == spec_id) &
        (spec_remark_table.c.remark_id == remark_id)
    )
    db_session.execute(stmt)
    db_session.commit()


# 查询与指定 Spec 关联的所有 Remark
def get_remarks_by_spec(db_session: Session, spec_id: int) -> List[SpecRemarkRead]:
    """
    根据 Spec ID 获取所有关联的 Remark。

    :param db_session: 数据库会话对象
    :param spec_id: Spec 的 ID
    :return: 关联的 Remark 列表
    """
    remarks = db_session.query(Remark).join(spec_remark_table).filter(
        spec_remark_table.c.spec_id == spec_id
    ).all()
    return remarks


# 查询与指定 Remark 关联的所有 Spec
def get_specs_by_remark(db_session: Session, remark_id: int) -> List[Spec]:
    """
    根据 Remark ID 获取所有关联的 Spec。

    :param db_session: 数据库会话对象
    :param remark_id: Remark 的 ID
    :return: 关联的 Spec 列表
    """
    specs = db_session.query(Spec).join(spec_remark_table).filter(
        spec_remark_table.c.remark_id == remark_id
    ).all()
    return specs


# 判断是否存在关联关系
def is_association_exists(db_session: Session, spec_id: int, remark_id: int) -> bool:
    """
    检查 Spec 和 Remark 是否已经关联。

    :param db_session: 数据库会话对象
    :param spec_id: Spec 的 ID
    :param remark_id: Remark 的 ID
    :return: True 表示已关联，False 表示未关联
    """

    # 检查 Spec 和 Remark 是否存在
    spec = db_session.query(Spec).filter(Spec.id == spec_id).first()
    if not spec:
        raise HTTPException(status_code=400, detail=f"Spec ID {spec_id} not found")

    remark = db_session.query(Remark).filter(Remark.id == remark_id).first()
    if not remark:
        raise HTTPException(status_code=400, detail=f"Remark ID {remark_id} not found")
    exists = db_session.query(spec_remark_table).filter(
        (spec_remark_table.c.spec_id == spec_id) &
        (spec_remark_table.c.remark_id == remark_id)
    ).first()
    return exists is not None


def get_spec_remark_by_id(db_session: Session, id: int) -> SpecRemarkRead:
    remark = db_session.query(spec_remark_table).filter(
        spec_remark_table.c.id == id
    ).first()
    return remark


def get_spec_editor_notes(db_session: Session, spec_id: int) -> List[SpecRemarkRead]:
    editor_notes = db_session.query(spec_remark_table).filter(
        and_(spec_remark_table.c.spec_id == spec_id, spec_remark_table.c.remark_type == 'e')
    ).order_by(spec_remark_table.c.created_at.desc()).all()
    return editor_notes


def create_editor_notes(db_session: Session, spec_remark_in: EditorNotesCreate):
    insert_editor_notes = spec_remark_table.insert().values(
        spec_id=spec_remark_in.spec_id,
        remark_id=spec_remark_in.remark_id,
        text=spec_remark_in.text,
        remark_type=spec_remark_in.remark_type,
        created_by=spec_remark_in.created_by
    )
    db_session.execute(insert_editor_notes)
    db_session.commit()


def update_notes(db_session: Session, editor_id: int, spec_remark_in: EditorNotesCreate):
    update_editor_notes = spec_remark_table.update().values(
        text=spec_remark_in.text,
        updated_at=datetime.now()
    ).where(
        (spec_remark_table.c.id == editor_id)
    )
    db_session.execute(update_editor_notes)
    db_session.commit()


def delete_notes(db_session: Session, editor_id: int):
    delete_editor_notes = spec_remark_table.delete().where(
        (spec_remark_table.c.id == editor_id)
    )
    db_session.execute(delete_editor_notes)
    db_session.commit()


def get_spec_text(db_session: Session, spec_id: int) -> List[SpecTextRead]:
    editor_notes = db_session.query(spec_remark_table).filter(
        and_(spec_remark_table.c.spec_id == spec_id, spec_remark_table.c.remark_type == 's')
    ).order_by(spec_remark_table.c.created_at.desc()).all()
    return editor_notes


def create_spec_text(db_session: Session, spec_remark_in: SpecTextCreate):
    insert_spec_text = spec_remark_table.insert().values(
        spec_id=spec_remark_in.spec_id,
        remark_id=spec_remark_in.remark_id,
        text=spec_remark_in.text,
        spec_text_type=spec_remark_in.spec_text_type,
        remark_type=spec_remark_in.remark_type,
        created_by=spec_remark_in.created_by
    )
    db_session.execute(insert_spec_text)
    db_session.commit()


def update_text(db_session: Session, spec_text_id: int, spec_remark_in: SpecTextCreate):
    update_spec_text = spec_remark_table.update().values(
        text=spec_remark_in.text,
        spec_text_type=spec_remark_in.spec_text_type,
        updated_at=datetime.now()
    ).where(
        (spec_remark_table.c.id == spec_text_id)
    )
    db_session.execute(update_spec_text)
    db_session.commit()


def delete_text(db_session: Session, spec_text_id: int):
    delete_spec_text = spec_remark_table.delete().where(
        (spec_remark_table.c.id == spec_text_id)
    )
    db_session.execute(delete_spec_text)
    db_session.commit()
