import logging
import re
from typing import Any, List

from fastapi import Depends, Query

# from pydantic.error_wrappers import ErrorWrapper, ValidationError
from pydantic.errors import PydanticErrorCodes, PydanticInvalidForJsonSchema
from pydantic.main import BaseModel
from pydantic.types import Json, constr
from sqlalchemy import Column, ForeignKey, Integer, MetaData, String, Table, create_engine, desc, func, or_, orm
from sqlalchemy.dialects import postgresql

# from sqlalchemy.orm import declarative_base, declared_attr
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import Query, configure_mappers, object_session, sessionmaker
from sqlalchemy.sql.expression import true
from sqlalchemy_utils import get_mapper
from starlette.requests import Request
from sqlalchemy import event
from datetime import datetime, timezone

from dispatch.exceptions import InvalidFilterError, NotFoundError
from dispatch.plugins.kandbox_planner.util.cache_dict import CacheDict
from dispatch.search.fulltext import make_searchable

from .config import SQLALCHEMY_DATABASE_URI, DEV_DATABASE_SCHEMA

log = logging.getLogger(__file__)


# QueryStr = constr(regex=r"^[ -~]+$", min_length=1)

engine = create_engine(
    str(SQLALCHEMY_DATABASE_URI),
    pool_size=16,
    max_overflow=32,
    # echo=True,
)
configure_mappers() 
log.debug(f"database engine created:{engine}")

schema_engine = engine.execution_options(
        schema_translate_map={
            None: DEV_DATABASE_SCHEMA,
        }
)
SessionLocal = sessionmaker(bind=schema_engine)
engine_dict = CacheDict(cache_len=5)
session_dict = CacheDict(cache_len=5)
# sqlalchemy core
try:
    conn_core = engine.connect()
except:
    pass
metadata = MetaData(SQLALCHEMY_DATABASE_URI) # engine


def resolve_table_name(name):
    """Resolves table names to their mapped names."""
    # print("resolve_table_name", name)
    names = re.split("(?=[A-Z])", name)  # noqa
    return "_".join([x.lower() for x in names if x])


class CustomBase:
    # __table_args__ = {"schema": "duan2"}

    @declared_attr
    def __tablename__(self):
        return resolve_table_name(self.__name__)


Base = declarative_base(cls=CustomBase)

make_searchable(Base.metadata)


@event.listens_for(Base, "before_update")
def receive_before_update(mapper, connection, target):
    if hasattr(target, 'updated_at'):
        target.updated_at = datetime.now(timezone.utc)

def get_db(request: Request):
    # https://docs.sqlalchemy.org/en/13/changelog/migration_11.html
    """
    request.state.db.connection(
        execution_options={"schema_translate_map": {None: request.state.org_code}}
    )
    """
    # TODO
    return request.state.auth_db
    # return request.state.db


def get_auth_db(request: Request):
    return request.state.auth_db

def get_model_name_by_tablename(table_fullname: str) -> str:
    """Returns the model name of a given table."""
    return get_class_by_tablename(table_fullname=table_fullname).__name__

def get_class_by_tablename(table_fullname: str) -> Any:
    """Return class reference mapped to table."""

    def _find_class(name):
        # for c in  Base.registry._class_registry.values(): #
        #     if hasattr(c, "__table__"):
        #         if c.__table__.fullname.lower() == name.lower():
        #             return c
        for c in Base.registry._class_registry.values():
            if isinstance(c, type) and hasattr(c, "__table__"):
                full_table_name = c.__table__.fullname.lower()
                class_name = resolve_table_name(c.__name__)

                if name in {full_table_name, class_name}:
                    return c

    mapped_name = resolve_table_name(table_fullname)
    mapped_class = _find_class(mapped_name)

    # try looking in the 'dispatch_core' schema
    if not mapped_class:
        mapped_class = _find_class(f"dispatch_core.{mapped_name}")

    if not mapped_class:
        raise PydanticInvalidForJsonSchema(
            [
                PydanticErrorCodes(
                    NotFoundError(msg="Model not found. Check the name of your model."),
                    loc="filter",
                )
            ],
            model=BaseModel,
        )

    return mapped_class


def get_table_name_by_class_instance(class_instance: Base) -> str:
    """Returns the name of the table for a given class instance."""
    return class_instance._sa_instance_state.mapper.mapped_table.name


def ensure_unique_default_per_project(target, value, oldvalue, initiator):
    """Ensures that only one row in table is specified as the default."""
    session = object_session(target)
    if session is None:
        return

    mapped_cls = get_mapper(target)

    if value:
        previous_default = (
            session.query(mapped_cls)
            .filter(mapped_cls.columns.default == true())
            .filter(mapped_cls.columns.project_id == target.project_id)
            .one_or_none()
        )
        if previous_default:
            # we want exclude updating the current default
            if previous_default.id != target.id:
                previous_default.default = False
                session.commit()
