from sqlalchemy.orm import Session
from sqlalchemy.sql.functions import func
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional
from .models import CastSpec, CastSpecCreate, CastSpecUpdate, CastSpecCreate
from sqlalchemy.schema import Sequence, CreateSequence, DropSequence


def get(*, db_session, id: int) -> Optional[CastSpec]:
    """Returns an cast_spec given an cast_spec id."""
    return db_session.query(CastSpec).filter(CastSpec.id == id).one_or_none()


def get_by_code(*, db_session, code: str) -> Optional[CastSpec]:
    """Returns an cast_spec given an cast_spec code address."""
    return db_session.query(CastSpec).filter(CastSpec.code == code).one_or_none()


def get_default_cast_spec(*, db_session ) -> Optional[CastSpec]:
    """Returns an cast_spec given an cast_spec code address."""
    return db_session.query(CastSpec).first()


def get_all(*, db_session) -> List[Optional[CastSpec]]:
    """Returns all cast_specs."""
    return db_session.query(CastSpec)

def get_one_by_cast_id_and_spec_id(*, db_session, cast_id: int, spec_id: int, product_type_id: int) -> CastSpec:

    return db_session.query(CastSpec).filter(CastSpec.cast_id == cast_id).filter(CastSpec.spec_id==spec_id).filter(CastSpec.product_type_id==product_type_id).one_or_none()

def get_by_spec_ids(*, db_session, spec_ids: List[int]) -> List[int]:
    """Returns all cast_specs by spec_ids."""
    return db_session.query(CastSpec).filter(CastSpec.spec_id.in_(spec_ids)).all()


def get_unique_cast_ids_by_spec_ids(*, db_session: Session, spec_ids: List[int]) -> List[int]:
    """Returns unique cast_ids by spec_ids."""
    result = db_session.query(CastSpec.cast_id).filter(CastSpec.spec_id.in_(spec_ids)).distinct().all()
    return [row[0] for row in result]


def get_unique_spec_ids_by_cast_ids(*, db_session: Session, cast_ids: List[int]) -> List[int]:
    """Returns unique cast_ids by spec_ids."""
    result = db_session.query(CastSpec.spec_id).filter(CastSpec.cast_id.in_(cast_ids)).distinct().all()
    return [row[0] for row in result]


def get_by_cast_ids(*, db_session, cast_ids: List[int]) -> List[int]:
    """Returns all cast_specs by spec_ids."""
    return db_session.query(CastSpec).filter(CastSpec.cast_id.in_(cast_ids)).all()
    

def create(*, db_session, cast_id: int, spec_id: int, product_type_id: int) -> CastSpec:
    """Creates an cast_spec."""

    # contact = CastSpec(**cast_spec_in.dict(exclude={"flex_form_data"}),
    #                 flex_form_data=cast_spec_in.flex_form_data)
    contact = CastSpec(cast_id=cast_id, spec_id=spec_id, product_type_id=product_type_id)

    db_session.add(contact)
    db_session.commit()
    return contact


def batch_insert_cast_spec(*, db_session: Session, cast_spec_ins: List[dict]) -> Optional[int]:
    try:
        db_session.bulk_insert_mappings(CastSpec, cast_spec_ins)
        db_session.commit()
    except SQLAlchemyError as e:
        db_session.rollback()
        print(f"Batch insertion failed: {e}")


def update(
    *,
    db_session,
    cast_spec: CastSpec,
    cast_spec_in: CastSpecUpdate,
) -> CastSpec:

    update_data = cast_spec_in.dict(
        exclude={"flex_form_data"},
    )
    for field, field_value in update_data.items():
        setattr(cast_spec, field, field_value)

    cast_spec.flex_form_data = cast_spec_in.flex_form_data
    db_session.add(cast_spec)
    db_session.commit()
    return cast_spec


def delete(*, db_session, id: int):
    cast_spec = db_session.query(CastSpec).filter(CastSpec.id == id).one_or_none()
    
    if cast_spec:
        cast_spec.is_deleted = 1
    db_session.add(cast_spec)
    db_session.commit()

    return cast_spec


def get_max_cast_id(*, db_session) -> Optional[int]:
    cast_id = db_session.query(func.max(CastSpec.cast_id)).scalar()
    return cast_id if cast_id else -1


def get_distinct_cast_ids(*, db_session) -> Optional[List[int]]:
    cast_ids = db_session.query(CastSpec.cast_id).distinct().all()
    if cast_ids:
        return [cast_id[0] for cast_id in cast_ids]
    return None


def delete_by_cast_id(*, db_session, cast_id: int):
    try:
        # 构建删除查询
        delete_query = db_session.query(CastSpec).filter(CastSpec.cast_id == cast_id)
        # 执行删除操作
        delete_count = delete_query.delete(synchronize_session=False)
        # 提交事务
        db_session.commit()
        print(f"Successfully deleted {delete_count} records.")
    except Exception as e:
        # 回滚事务
        db_session.rollback()
        print(f"An error occurred while deleting records: {e}")


def reset_sequence_to_max_id(db_session: Session):
    try:
        # 获取最大 id
        max_id = db_session.query(func.max(CastSpec.id)).scalar()

        # 如果表为空，max_id 会是 None，设置为 0 或 1（根据你的需求）
        max_id = max_id if max_id is not None else 0

        # 构造 ALTER SEQUENCE 语句
        seq_name = 'cast_spec_id_seq'
        seq = Sequence(seq_name, start=max_id + 1)
        db_session.execute(seq)

        db_session.commit()
    except SQLAlchemyError as e:
        db_session.rollback()
        print(f"Error resetting sequence: {e}")