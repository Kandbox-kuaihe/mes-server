from dispatch.database import get_db
from typing import List, Optional
from datetime import datetime
from sqlalchemy import func
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from dispatch.message_admin.message_server.models import PushMessageData
from dispatch.system_admin.auth.models import DispatchUser
from dispatch.system_admin.auth.service import get_current_user
from fastapi import Request, BackgroundTasks

from dispatch.database_util.service import common_parameters, search_filter_sort_paginate
from .models import (
    OrderGroup,
    OrderGroupCreate,
    OrderGroupPagination,
    OrderGroupRead,
    OrderGroupUpdate,
    OrderGroupListBase,
    OrderGroupSplit,
    OrderSpecGroupBase,
    OrderSpecGroupCreate,
    OrderGroupBatchUpdate,
    OrderSpecGroupUpdateBase,
    OrderSpecGroupUpdate
)
from .service import (
    create,
    delete,
    get,
    get_by_code,
    update,
    batch_update,
    get_order_group_list,
    get_order_spec_group_list_by_id,
    updete_order_spec_group_id,
    create_spec_group,
    get_max_group_charge_seq,
    update_group_code,
    check_unique_key_exists,
    semi_ton_spec_group,
    update_order_spec_group_project_tonnes,
    get_order_group_codes
)

router = APIRouter()


@router.get("/", response_model=OrderGroupPagination)
def get_orderGroups(*, common: dict = Depends(common_parameters)):
    if common["query_str"]:
        common["fields"] = ["group_code"]
        common["ops"] = ["like"]
        common["values"] = [f"%{common['query_str']}%"]
        common["query_str"] = ''
    return search_filter_sort_paginate(model="OrderGroup", **common)


@router.post("/", response_model=OrderGroupRead)
def create_orderGroup(
    *,
    db_session: Session = Depends(get_db),
    orderGroup_in: OrderGroupCreate,
    current_user: DispatchUser = Depends(get_current_user)
):
    """
    Create a new orderGroup contact.
    """

    # orderGroup = get_by_code(db_session=db_session,code=orderGroup_in.code)

    # if orderGroup:
    #     raise HTTPException(status_code=400, detail="The orderGroup with this code already exists.")

    orderGroup_in.created_by = current_user.email
    orderGroup_in.updated_by = current_user.email
    print(orderGroup_in.rolling_id)
    print(orderGroup_in.product_id)
    orderGroup = create(db_session=db_session, orderGroup_in=orderGroup_in)
    return orderGroup


@router.get("/byid/{orderGroup_id}", response_model=OrderGroupRead)
def get_orderGroup(*, db_session: Session = Depends(get_db), orderGroup_id: int):
    """
    Get a orderGroup contact.
    """
    orderGroup = get(db_session=db_session, id=orderGroup_id)
    if not orderGroup:
        raise HTTPException(status_code=400, detail="The orderGroup with this id does not exist.")
    return orderGroup


@router.put('/update/project_tonnes', response_model=OrderSpecGroupUpdate)
def update_project_tonnes(
        *,
        db_session:Session = Depends(get_db),
        orderSpecGroup_in: OrderSpecGroupUpdateBase,
        current_user: DispatchUser = Depends(get_current_user)
):
    print("orderSpecGroup_in type:", type(orderSpecGroup_in))
    print("orderSpecGroup_in data:", orderSpecGroup_in.id)  # 打印出传递的数据
    order_spec_group = get_order_spec_group_list_by_id(db_session=db_session, id=orderSpecGroup_in.id)
    if not order_spec_group:
        raise HTTPException(status_code=400, detail="The orderSpecGroup with this id does not exist.")
    updated_order_group = update_order_spec_group_project_tonnes(
        db_session=db_session,
        spec_group=orderSpecGroup_in,
        order_spec_group_id=orderSpecGroup_in.id
    )
    return updated_order_group



@router.put("/{orderGroup_id}", response_model=OrderGroupRead)
def update_orderGroup(
    *,
    db_session: Session = Depends(get_db),
    orderGroup_id: int,
    orderGroup_in: OrderGroupUpdate,
    current_user: DispatchUser = Depends(get_current_user)
):
    """
    Update a orderGroup contact.
    """
    orderGroup = get(db_session=db_session, id=orderGroup_id)
    if not orderGroup:
        raise HTTPException(status_code=400, detail="The orderGroup with this id does not exist.")

    orderGroup = update(
        db_session=db_session,
        orderGroup=orderGroup,
        orderGroup_in=orderGroup_in,
    )
    return orderGroup


@router.put("/orderGroup_code/{orderGroup_code}", response_model=OrderGroupRead)
def update_orderGroup_by_code(
    *,
    db_session: Session = Depends(get_db),
    orderGroup_code: str,
    orderGroup_in: OrderGroupUpdate,
    current_user: DispatchUser = Depends(get_current_user)
):
    """
    Update a orderGroup contact.
    """
    orderGroup = get_by_code(db_session=db_session, code=orderGroup_code)
    if not orderGroup:
        raise HTTPException(status_code=400, detail="The orderGroup with this id does not exist.")

    orderGroup_in.updated_by = current_user.email
    orderGroup = update(
        db_session=db_session,
        orderGroup=orderGroup,
        orderGroup_in=orderGroup_in,
    )

    return orderGroup


@router.delete("/{orderGroup_id}", response_model=OrderGroupRead)
def delete_orderGroup(*, db_session: Session = Depends(get_db), orderGroup_id: int):
    """
    Delete a orderGroup contact.
    """
    orderGroup = get(db_session=db_session, id=orderGroup_id)
    if not orderGroup:
        raise HTTPException(status_code=400, detail="The orderGroup with this id does not exist.")

    return delete(db_session=db_session, id=orderGroup_id)


@router.get("/list", response_model=List[OrderGroupListBase])
def get_order_groups_list(
    *,
    db_session: Session = Depends(get_db),
    rolling_no: Optional[str] = None,
    section_type: Optional[str] = None,
    kg: Optional[int] = None,
    current_user: DispatchUser = Depends(get_current_user)
):
    """
    Get a order group list.
    """
    order = get_order_group_list(db_session=db_session, section_type=section_type, rolling_no=rolling_no, kg=kg, current_user=current_user)
    return order


@router.get("/reverse", response_model=List[OrderGroupListBase])
def get_reverse(
    *,
    db_session: Session = Depends(get_db),
    rolling_no: Optional[str] = None,
    section_type: Optional[str] = None,
    kg: Optional[int] = None,
    current_user: DispatchUser = Depends(get_current_user)
):
    """
    Get a order group list.
    """
    order = get_order_group_list(db_session=db_session, section_type=section_type, rolling_no=rolling_no, kg=kg, current_user=current_user)
    if not order:
        raise HTTPException(status_code=400, detail="The order with this id does not exist.")
    order_sorted = sorted(order, key=lambda x: x.group_charge_seq if x.group_charge_seq is not None else 0)
    new_seq_values = {record.id: -(i + 1) for i, record in enumerate(order_sorted)}
    update_mappings = [
        {'id': record.id, 'group_charge_seq': new_seq_values[record.id]}
        for record in order_sorted
    ]
    # print(update_mappings)
    db_session.bulk_update_mappings(OrderGroup, update_mappings)
    db_session.commit()

    new_seq_values = {record.id: len(order_sorted) - i - 1 for i, record in enumerate(order_sorted)}
    update_mappings = [
        {'id': record.id, 'group_charge_seq': new_seq_values[record.id]}
        for record in order_sorted
    ]
    # print(update_mappings)
    db_session.bulk_update_mappings(OrderGroup, update_mappings)
    db_session.commit()

    order = get_order_group_list(db_session=db_session, section_type=section_type, rolling_no=rolling_no, kg=kg, current_user=current_user)
    if not order:
        raise HTTPException(status_code=400, detail="The order with this id does not exist.")
    return order


@router.post("/list")
def update_batch_order_groups_list(
    *,
    request: Request, 
    background_tasks: BackgroundTasks,
    db_session: Session = Depends(get_db),
    order_group_in: List[OrderGroupBatchUpdate],
    current_user: DispatchUser = Depends(get_current_user)
):
    body = []
    updated_at = datetime.now()
    new_order_group_id_list = []
    for order_group in order_group_in:
        orderGroup = get(db_session=db_session, id=order_group.id)
        order_group.created_at = orderGroup.created_at
        order_group.created_by = orderGroup.created_by
        order_group.updated_by = orderGroup.updated_by
        order_group.updated_at = orderGroup.updated_at
        order_group.is_deleted = orderGroup.is_deleted
        order_group.flex_form_data = orderGroup.flex_form_data
        if not orderGroup: continue
        if order_group.alternative_semi_size_id and order_group.alternative_semi_size_id != orderGroup.alternative_semi_size_id:
            # 修改semi_size
            orderGroup.updated_by = order_group.updated_by = current_user.email
            orderGroup.updated_at = order_group.updated_at = updated_at
            orderGroup.alternative_semi_size_id = order_group.alternative_semi_size_id
            db_session.add(orderGroup)
            db_session.commit()
        if order_group.group_code != orderGroup.group_code or order_group.plan_tonnes != orderGroup.plan_tonnes or order_group.galvanisation != orderGroup.galvanisation:
            orderGroup.updated_by = order_group.updated_by = current_user.email
            orderGroup.updated_at = order_group.updated_at = updated_at
            new_order_group_id_list.append(orderGroup.id)
            body.append(order_group.__dict__)
            continue
        elif order_group.group_charge_seq == orderGroup.group_charge_seq:
            continue
        elif check_unique_key_exists(db_session=db_session, rolling_id=orderGroup.rolling_id, group_charge_seq=order_group.group_charge_seq):
            raise HTTPException(status_code=400, detail="The seq already exists.")
        orderGroup.updated_by = order_group.updated_by = current_user.email
        orderGroup.updated_at = order_group.updated_at = updated_at
        new_order_group_id_list.append(orderGroup.id)
        body.append(order_group.__dict__)
    # send message to SRSM
    if len(new_order_group_id_list):
        message = PushMessageData(id=240, type='srsmpc', msg=str(new_order_group_id_list))
        try:
            from dispatch.contrib.message_admin.message_server.server import call_method
            call_method(request, background_tasks, db_session=db_session, current_user=current_user, message=message)
        except ImportError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            print(f'Sending srsmpc-240 failed, reason: {e}')
    # update to db, need before send message to SRSM
    is_success = batch_update(db_session=db_session, body=body)
        
    return is_success

@router.post("/order_spec_group", response_model=OrderSpecGroupBase)
def create_order_spec_group(
    *,
    db_session: Session = Depends(get_db),
    order_spec_group_in: OrderSpecGroupCreate,
    current_user: DispatchUser = Depends(get_current_user)
):
    """
    Create a new orderGroup contact.
    """
    order_spec_group_in.created_by = current_user.email
    order_spec_group_in.updated_by = current_user.email
    orderGroup = create_spec_group(db_session=db_session, order_spec_group_in=order_spec_group_in)
    return orderGroup


@router.get("/order_spec_group/{id}", response_model=OrderSpecGroupBase)
def get_order_spec_groups_list(*, db_session: Session = Depends(get_db), id):
    """
    Get a order group list.
    """
    order = get_order_spec_group_list_by_id(db_session=db_session, id=id)
    if not order:
        raise HTTPException(status_code=400, detail="The order with this id does not exist.")
    return order


@router.post("/split", response_model=OrderGroupRead)
def create_order_group_split_spec_group(
    *,
    db_session: Session = Depends(get_db),
    orderGroup_in: OrderGroupSplit,
    current_user: DispatchUser = Depends(get_current_user)
):
    """
    Create a new orderGroup contact.
    """

    # orderGroup = get_by_code(db_session=db_session,code=orderGroup_in.code)

    # if orderGroup:
    #     raise HTTPException(status_code=400, detail="The orderGroup with this code already exists.")
    spec_group_ids = orderGroup_in.order_spec_group_ids
    del orderGroup_in.order_spec_group_ids
    orderGroup_in.mill_id = current_user.current_mill_id
    orderGroup_in.created_by = current_user.email
    orderGroup_in.updated_by = current_user.email
    orderGroup_in.group_code = update_group_code(orderGroup_in.group_code)
    group_charge_seq = get_max_group_charge_seq(db_session=db_session, rolling_id=orderGroup_in.rolling_id)

    orderGroup_in.group_charge_seq = group_charge_seq + 10 if group_charge_seq else 10
    orderGroup = create(db_session=db_session, orderGroup_in=orderGroup_in)
    for spec_group_id in spec_group_ids:
        spec_group = get_order_spec_group_list_by_id(db_session=db_session, id=spec_group_id)
        if not spec_group:
            raise HTTPException(status_code=400, detail="The order spec group with this id does not exist.")
        updete_order_spec_group_id(
            db_session=db_session,
            spec_group=spec_group,
            order_group_id=orderGroup.id,
        )

    return orderGroup


@router.get("/sum_allocation_tonnes")
def sum_allocation_tonnes(db_session: Session = Depends(get_db)):
    return semi_ton_spec_group(db_session=db_session)


@router.put("/move/{order_group_id}")
def move_to_rolling(
    order_group_move_in: OrderGroupUpdate,
    order_group_id: int = None,
    db_session: Session = Depends(get_db),
    current_user: DispatchUser = Depends(get_current_user)
):
    order_group_obj = get(db_session=db_session, id=order_group_id)
    order_group_obj.updated_by = current_user.email
    order_group_obj.mill_id = current_user.current_mill_id

    # 计算新的group_charge_seq
    current_rolling_id = order_group_move_in.rolling_id
    current_mill_id = order_group_obj.mill_id
    # 查询当前rolling_id和mill_id组合的最大序号
    max_seq = db_session.query(
        func.max(OrderGroup.group_charge_seq)
    ).filter(
        OrderGroup.rolling_id == current_rolling_id,
        OrderGroup.mill_id == current_mill_id
    ).scalar()
    
    print(f"当前最大 group_charge_seq: {max_seq}")  # 添加打印

    new_group_charge_seq = (max_seq + 1) if max_seq is not None else 0
    print(f"new_group_charge_seq: {new_group_charge_seq}")
    order_group_obj.rolling_id = order_group_move_in.rolling_id
    order_group_obj.group_charge_seq = new_group_charge_seq

    order_group_in = OrderGroupUpdate(**order_group_obj.__dict__)
    order_group = update(
        db_session=db_session, orderGroup=order_group_obj, orderGroup_in=order_group_in
    )
    return order_group


@router.get("/options")
def get_order_group_options(rolling_id: int, db_session: Session = Depends(get_db), current_user: DispatchUser = Depends(get_current_user)):
    """
    Get a order group list.
    """
    order_group_options = get_order_group_codes(rolling_id=rolling_id, mill_id=current_user.current_mill_id, db_session=db_session)
    options_dims = {
        "options": [],
        "dim3": {}
    }
    for og in order_group_options:
        options_dims["options"].append({"value": og.id, "text": og.group_code})
        options_dims["dim3"][og.id] = og.product_type.dim3 if og.product_type else None
    
    return options_dims
