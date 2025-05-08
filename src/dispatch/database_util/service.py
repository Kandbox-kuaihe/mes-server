import copy
import json
import logging
from itertools import groupby
from typing import List

import sqlalchemy
from fastapi import Depends, Query
from pydantic import BaseModel

# from pydantic.error_wrappers import ErrorWrapper, ValidationError
from pydantic.errors import PydanticErrorCodes, PydanticInvalidForJsonSchema
from pydantic.types import Json, constr
from sqlalchemy import and_, desc, func, not_, or_, orm

# from dispatch.location.models import Location
# from dispatch.location import service as location_service
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy_filters import apply_filters, apply_pagination, apply_sort
from sqlalchemy_filters.exceptions import BadFilterFormat, FieldNotFound
from sqlalchemy_filters.filters import build_filters, get_named_models

from dispatch.database import Base, engine, get_class_by_tablename, get_db, get_model_name_by_tablename
from dispatch.exceptions import FieldNotFoundError, InvalidFilterError
from dispatch.mill.models import Mill
from dispatch.order_admin.order_item.models import OrderItem
from dispatch.runout_admin.finished_product.models import FinishedProduct
from dispatch.system_admin.auth.models import DispatchUser, UserRoles
from dispatch.system_admin.auth.service import get_current_role, get_current_user

# from pydantic.errors import PydanticErrorCodes, PydanticInvalidForJsonSchema
# from pydantic.types import Json, constr
# from sqlalchemy import and_, desc, func, not_, or_, orm



# from dispatch.enums import UserRoles, Visibility
# from dispatch.fulltext.composite_search import CompositeSearch



# from dispatch.job.models import Job
# from dispatch.team.models import Team
# from dispatch.worker.models import Worker


log = logging.getLogger(__file__)

# allows only printable characters
# QueryStr = constr(regex=r"^[ -~]+$", min_length=1)




def restricted_mill_filter(query: orm.Query, current_user: DispatchUser,
                                role: UserRoles, db_session, fields, values):
    """Adds additional incident type filters to query (usually for permissions)."""

    if current_user:
        if role == UserRoles.CUSTOMER:
            # mill_list = [i.id for i in current_user.mill]
            query = query.filter(Mill.id == current_user.current_mill_id)

    return query


def restricted_orderItem_filter(query: orm.Query, current_user: DispatchUser,
                                role: UserRoles, db_session, fields, values):
    """Adds additional incident type filters to query (usually for order_item completion_status)."""
    if "completion_status" in fields:

        # 第一步：找出每个 OrderItem.id 在 FinishedProduct.order_item_id 中出现的次数
        subquery = (
            db_session.query(
                FinishedProduct.order_item_id,
                func.count(FinishedProduct.order_item_id).label('occurrence_count')
            )
            .group_by(FinishedProduct.order_item_id)
            .subquery()
        )
        # 第二步：筛选出 OrderItem.quantity <= occurrence_count 的 OrderItem.id
        completed_order_item = (
            db_session.query(OrderItem.id)
            .join(subquery, subquery.c.order_item_id == OrderItem.id)
            .filter(and_(OrderItem.quantity <= subquery.c.occurrence_count,
                         OrderItem.quantity > 0))
        )
        # 执行查询并获取结果
        results = completed_order_item.all()
        # 将结果转换为一个包含 OrderItem.id 的列表
        result_ids = [item[0] for item in results]
        if "completed" in values:
            query = query.filter(OrderItem.id.in_(result_ids))
        if "incomplete" in values:
            query = query.filter(OrderItem.id.notin_(result_ids))

    return query


def apply_model_specific_filters(
    model: DeclarativeMeta, query: orm.Query, current_user: DispatchUser, role: UserRoles
, db_session, fields, values):
    """Applies any model specific filter as it pertains to the given user."""

    # 当前用户的mill 有值 且 model中存在mill_id字段 就过滤,,兼容字段mill_id 为空不过滤
    if current_user.current_mill_id !=-1 and "mill_id" in model._sa_class_manager.keys():
        query = query.filter(or_(model.mill_id == current_user.current_mill_id,
                                 model.mill_id == None )) 
        

    model_map = {
        # Mill: [restricted_mill_filter],
        OrderItem: [restricted_orderItem_filter],
    }

    filters = model_map.get(model, [])

    for f in filters:
        query = f(query, current_user, role, db_session, fields, values)

    return query

def get_model_map(filters: dict) -> dict:
    # this is required because by default sqlalchemy-filter's auto-join
    # knows nothing about how to join many-many relationships.
    model_map = { 
        # (Feedback, "Incident"): (Incident, False),
        # (Feedback, "Case"): (Case, False),
        # (Task, "Project"): (Incident, False),
        # (Task, "Incident"): (Incident, False),
        # (DispatchUser, "Organization"): (DispatchUser.organizations, True), 
    } 
    return model_map

def apply_filter_specific_joins(model: Base, filter_spec: dict, query: orm.query):
    """Applies any model specific implicitly joins."""
    filters = build_filters(filter_spec)
    filter_models = get_named_models(filters)

    return apply_model_specific_joins(model, filter_models, query)

def apply_model_specific_joins(model: Base, models: List[str], query: orm.query):
    model_map = get_model_map(models)
    joined_models = []

    for include_model in models:
        if model_map.get((model, include_model)):
            joined_model, is_outer = model_map[(model, include_model)]
            try:
                if joined_model not in joined_models:
                    query = query.join(joined_model, isouter=is_outer)
                    joined_models.append(joined_model)
            except Exception as e:
                log.exception(e)

    return query
     


# def composite_search(*, db_session, query_str: str, models: List[Base], current_user: DispatchUser):
#     """Perform a multi-table search based on the supplied query."""
#     s = CompositeSearch(db_session, models)
#     query = s.build_query(query_str, sort=True)

#     # TODO can we do this with composite filtering?
#     # for model in models:
#     #    query = apply_model_specific_filters(model, query, current_user)

#     return s.search(query=query)


def search(*, query_str: str, query: Query, model: str, sort=False):
    """Perform a search based on the query."""
    search_model = get_class_by_tablename(model)

    if not query_str.strip():
        return query
    
    if not hasattr(search_model, 'search_vector'):
        return query
    vector = search_model.search_vector

    # 使用lower函数处理查询字符串，实现不区分大小写的搜索
    query = query.filter(vector.op("@@")(func.tsq_parse(func.lower(query_str))))
    if sort:
        query = query.order_by(desc(func.ts_rank_cd(vector, func.tsq_parse(func.lower(query_str)))))

    return query.params(term=query_str)


def create_sort_spec(model, sort_by, descending):
    """Creates sort_spec."""
    sort_spec = []
    if sort_by and descending:
        for field, direction in zip(sort_by, descending):
            direction = "desc" if direction else "asc"

            # we have a complex field, we may need to join
            if "." in field:
                complex_model, complex_field = field.split(".")[-2:]

                sort_spec.append(
                    {
                        "model": get_model_name_by_tablename(complex_model),
                        "field": complex_field,
                        "direction": direction,
                    }
                )
            else:
                sort_spec.append({"model": model, "field": field, "direction": direction})
    log.debug(f"Sort Spec: {json.dumps(sort_spec, indent=2)}")
    return sort_spec


def get_all(*, db_session, model):
    """Fetches a query object based on the model class name."""
    return db_session.query(get_class_by_tablename(model))


def common_parameters(
    db_session: orm.Session = Depends(get_db),
    page: int = Query(1, gt=0, lt=2147483647),
    items_per_page: int = Query(5, alias="itemsPerPage", gt=-2, lt=2147483647),
    query_str: str = Query(None, alias="q"),
    sort_by: List[str] = Query([], alias="sortBy[]"),
    descending: List[bool] = Query([], alias="descending[]"),
    fields: List[str] = Query([], alias="fields[]"),
    ops: List[str] = Query([], alias="ops[]"),
    values: List[str] = Query([], alias="values[]"),
    filter_type: str = Query(None, alias="filter_type"), # and ,or 
    current_user: DispatchUser = Depends(get_current_user),
    role: UserRoles = Depends(get_current_role),
):

    # values[]: [1,2,3] 会变成 ['[1,2,3]'] 处理一下 以支持多选的in查询
    for idx, (val, op) in enumerate(zip(values, ops)):
        if op == 'in':
            try:
                values[idx] = json.loads(val)
            except json.JSONDecodeError:
                pass

    return {
        "db_session": db_session,
        "page": page,
        "items_per_page": items_per_page,
        "query_str": query_str,
        "sort_by": sort_by,
        "descending": descending,
        "current_user": current_user,
        "role": role,
        "fields": fields,
        "values": values,
        "ops": ops,
        "filter_type": filter_type,
    }

# https://github.com/juliotrigo/sqlalchemy-filters/blob/master/README.rst
def search_filter_sort_paginate(
    db_session,
    model,
    query_str: str = None,
    filter_spec: str | dict | None = None,
    include_keys: List[str] = None,
    page: int = 1,
    items_per_page: int = 5,
    sort_by: List[str] = None,
    descending: List[bool] = None,
    fields: List[str] = None,
    ops: List[str] = None,
    values: List[str] = None,
    current_user: DispatchUser = None,
    role: UserRoles = UserRoles.CUSTOMER,
    filter_type: str = None,
    query = None,
    do_auto_join: bool = False
):
    """Common functionality for searching, filtering, sorting, and pagination."""
    model_cls = get_class_by_tablename(model)
    try:
        # do_auto_join = False
        if query is None:
            query = db_session.query(model_cls) 
            do_auto_join = True

        if query_str:
            sort = False if sort_by else True
            query = search(query_str=query_str, query=query, model=model, sort=sort)
        if "is_deleted" in model_cls._sa_class_manager.keys():
            query = query.filter((model_cls.is_deleted == None)|(model_cls.is_deleted == 0))

        query = apply_model_specific_filters(model_cls, query, current_user, role, db_session, fields, values)

        if filter_spec:
            # some functions pass filter_spec as dictionary such as auth/views.py/get_users
            # but most come from API as seraialized JSON
            if isinstance(filter_spec, str):
                filter_spec = json.loads(filter_spec)
            query = apply_filter_specific_joins(model_cls, filter_spec, query)
            
            query = apply_filters(query, filter_spec, model_cls)
        else:
            # 老的处理方式
            # 兼容没有filter_spec的情况
            # orderItem completion_status特殊处理相关
            if "completion_status" in fields:
                fields = [item for item in fields if item != "completion_status"]
                values = [item for item in values if item != "completed"]
                values = [item for item in values if item != "incomplete"]

            filter_spec , filters = create_filter_spec(model, fields, ops, values)
            # filter change or  and
            if filter_type:
                filter_spec = apply_filter_type( filter_type, filters)

            query = apply_filters(query, filter_spec, do_auto_join)

        if include_keys:
            query = apply_model_specific_joins(model_cls, include_keys, query)
        if sort_by:
            sort_spec = create_sort_spec(model, sort_by, descending)
            sort_spec[0].update({'nullslast': 'True'})
            query = apply_sort(query, sort_spec)

    except FieldNotFound as e:
        import traceback
        print(
            '========='
        )
        traceback.print_exception(e)
        raise PydanticInvalidForJsonSchema(
            [
                PydanticErrorCodes(FieldNotFoundError(msg=str(e)), loc="filter"),
            ],
            model=BaseModel,
        )
    except BadFilterFormat as e:
        raise PydanticInvalidForJsonSchema(
            [PydanticErrorCodes(InvalidFilterError(msg=str(e)), loc="filter")], model=BaseModel
        )

    if items_per_page == -1:
        items_per_page = None

    # sometimes we get bad input for the search function
    # TODO investigate moving to a different way to parsing queries that won't through errors
    # e.g. websearch_to_tsquery
    # https://www.postgresql.org/docs/current/textsearch-controls.html
    try:
        query, pagination = apply_pagination(query, page_number=page, page_size=items_per_page)
    except sqlalchemy.exc.ProgrammingError as e:
        log.error(e)
        return {
            "items": [],
            "itemsPerPage": items_per_page,
            "page": page,
            "total": 0,
        }

    return {
        "items": query.all(),
        "itemsPerPage": pagination.page_size,
        "page": pagination.page_number,
        "total": pagination.total_results,
    }

def apply_filter_type(filter_type, filters):
    """
    Apply filter type with support for array-based relationship structure.
    
    Args:
        filter_type: Can be string ('and', 'or', 'custom') or array format:
                    e.g., ['and', ['or', 'or'], 'and']
        filters: List of filter conditions
        
    Example:
        filter_type = ['and', ['or', 'or'], 'and']
        filters = [4223, 26, 28, "Default Location"]
        Result: 4223 AND (26 OR 28) AND "Default Location"
    """
    # Handle string filter types
    if isinstance(filter_type, str):
        if filter_type == "or":
            return {"and": [{"or": filters}]}
        elif filter_type == "and":
            return {"and": [{"or": [f]} for f in filters]}
        elif filter_type == "custom":
            if len(filters) < 2:
                raise ValueError("The filters list must contain at least two conditions for custom type.")
            return {"and": [{"or": filters[:2]}] + [{"or": [f]} for f in filters[2:]]}
        return {}

    # Handle array-based filter type
    if not isinstance(filter_type, list):
        return {}

    filter_spec = []
    filter_index = 0

    for item in filter_type:
        if isinstance(item, list):
            # Handle OR group
            or_conditions = []
            for _ in range(len(item)):
                if filter_index < len(filters):
                    or_conditions.append(filters[filter_index])
                    filter_index += 1
            if or_conditions:
                filter_spec.append({"or": or_conditions})
        elif item in ('and', 'or'):
            # Handle single condition for and/or
            if filter_index < len(filters):
                filter_spec.append({"or": [filters[filter_index]]})
                filter_index += 1

    return {"and": filter_spec} if filter_spec else {}

def create_filter_spec(model, fields, ops, values):
    """Creates a filter spec."""
    filters = []
    if fields and ops and values:
        for field, op, value in zip(fields, ops, values):
            if "." in field:
                complex_model, complex_field = field.split(".")
                filters.append(
                    {
                        "model": get_model_name_by_tablename(complex_model),
                        "field": complex_field,
                        "op": op,
                        "value": value,
                    }
                )
            else:
                filters.append({"model": model, "field": field, "op": op, "value": value})
                
    filter_spec = []
    # group by field (or for same fields and for different fields)
    data = sorted(filters, key=lambda x: x["model"])
    for k, g in groupby(data, key=lambda x: x["model"]):
        # force 'and' for operations other than equality
        _filters = list(g)
        force_and = False
        for f in filters:
            if "eq" in f["op"] or ">" in f["op"] or "<" in f["op"] or "!=" in f["op"] or 'in' in f["op"]:
                force_and = True

        if force_and:
            filter_spec.append({"and": _filters})
        else:
            filter_spec.append({"or": _filters})

    if filter_spec:
        filter_spec = {"and": filter_spec}

    # log.debug(f"Filter Spec: {json.dumps(filter_spec, indent=2)}")
    return filter_spec ,filters


def get_schema_session(org_code):
    schema_engine = engine.execution_options(
        schema_translate_map={None: f"dispatch_organization_{org_code}"}
    )
    schema_session = sessionmaker(bind=schema_engine)()
    return schema_session
