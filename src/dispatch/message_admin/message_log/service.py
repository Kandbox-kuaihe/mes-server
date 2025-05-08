import json
from typing import List, Optional
import requests
from .models import MessageLogCreate, MessageLog
from dispatch.mill import service as mill_service
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
from fastapi import BackgroundTasks

from dispatch.log import getLogger


log = getLogger(__name__)


def create(*, db_session, message_log_in: MessageLogCreate) -> MessageLog:
    mill = None
    if message_log_in.mill_id is not None and message_log_in.mill_id != -1:
        mill = mill_service.get(db_session=db_session, mill_id=message_log_in.mill_id)
    message_log_in.created_at = datetime.now()
    message_log_in.updated_at = datetime.now()
    message_log = MessageLog(**message_log_in.dict(exclude={"mill"}),
                             mill=mill)
    db_session.add(message_log)
    try:
        db_session.commit()
    except Exception as e:
        db_session.rollback()
        raise e
    return message_log


# def create_message_log(*, db_session, message_log_in: MessageLogCreate,
#                           current_user: DispatchUser = Depends(get_current_user), ):
#     message_log_in.updated_by = current_user.email
#     message_log_in.created_by = current_user.email
#     message_log = create(db_session=db_session, operation_log_in=message_log_in)
#     return message_log


def get(*, db_session, id: int) -> Optional[MessageLog]:
    return db_session.query(MessageLog).filter(
        MessageLog.id == id).one_or_none()


def get_by_days(*, db_session, interact_types=None, message_ids=None, start_time=None, end_time=None) -> List[
    Optional[MessageLog]]:
    """
    Get message logs within a specified time range
    Args:
        db_session: Database session
        interact_types: List of interaction types to filter
        message_ids: List of message IDs to filter
        start_time: Start time for the query (datetime)
        end_time: End time for the query (datetime)
    """
    query = db_session.query(MessageLog).filter(
        MessageLog.type == 'pc'
    )

    # Add time range filter
    if start_time and end_time:
        query = query.filter(
            MessageLog.created_at >= start_time,
            MessageLog.created_at <= end_time
        )
    else:
        # Default to last 7 days if no specific time range provided
        query = query.filter(
            MessageLog.created_at >= datetime.now() - timedelta(days=7)
        )

    # Add interaction type filter
    if interact_types:
        query = query.filter(MessageLog.interact.in_(interact_types))

    # Add message ID filter
    if message_ids:
        query = query.filter(MessageLog.message_id.in_(message_ids))

    return query.order_by(MessageLog.created_at.desc()).all()


def get_or_create_by_code(*, db_session, massage_log_in) -> MessageLog:
    if massage_log_in.id:
        q = db_session.query(MessageLog).filter(
            MessageLog.id == massage_log_in.id)
    else:
        # return None
        raise Exception("The MassageLog.id can not be None.")

    instance = q.first()

    if instance:
        return instance

    return create(db_session=db_session, operation_log_in=massage_log_in)


def get_all(*, db_session) -> List[Optional[MessageLog]]:
    return db_session.query(MessageLog)

def get_all_360_receive(
    *,
    db_session,
    start_time: datetime,
    end_time: datetime
) -> List[Optional[MessageLog]]:
    return (
        db_session.query(MessageLog)
        .filter(
            MessageLog.interact.in_(['Recieve']),
            MessageLog.message_id.in_([360]),
            MessageLog.type.in_(['pc']),
            MessageLog.msg.like('%"%'),
            MessageLog.created_at >= start_time,
            MessageLog.created_at <= end_time
        )
        .all()
    )

def create_all(*, db_session,
               operation_log_in: List[MessageLogCreate]) -> List[MessageLog]:
    operation_log = [MessageLog(id=d.id) for d in operation_log_in]
    db_session.bulk_save_insert(operation_log)
    db_session.commit()
    db_session.refresh()
    return operation_log


def delete(*, db_session, id: int):
    message_log = db_session.query(MessageLog).filter(
        MessageLog.id == id).first()

    db_session.delete(message_log)
    db_session.commit()


def advice_tip_repeat(*, request, msg):

    root = ET.fromstring(msg)
    pconno_element = root.find('.//PConNo')
    if pconno_element is None:
        raise ValueError("PConNo element not found in the XML message")

    pconno_value = pconno_element.text
    # 去掉前缀 'T'
    if pconno_value.startswith('T'):
        advice_id = pconno_value[1:]
    else:
        advice_id = pconno_value

    host_url = f"http://{request.client.host}:{request.url.port}"
    api_url = f"{host_url}/api/v1/advice/tip/{advice_id}"
    auth_header = request.headers.get('Authorization')

    # 发送 GET 请求
    headers = {
        'Authorization': auth_header,
        'Content-Type': "application/json"
    }
    requests.get(api_url, headers=headers)


def advice_sap_despatch_repeat(*, request, msg):

    host_url = f"http://{request.client.host}:{request.url.port}"
    api_url = f"{host_url}/api/v1/message_server/push_message/sap_900_auth"
    auth_header = request.headers.get('Authorization')

    headers = {
        'Authorization': auth_header,
        'Content-Type': "application/xml"
    }
    # 发送 POST 请求
    requests.post(api_url, headers=headers, data=msg)

try:
    from dispatch.contrib.message_admin.message.lims import (encrypt_message121, encrypt_message122, encrypt_message123, encrypt_message124,
                                                             encrypt_message127, encrypt_message140, encrypt_message141, encrypt_message143,
                                                             encrypt_message150)
    def lims_repeat(*, request, msg, message_id):

        encrypt_functions = {
            121: encrypt_message121,
            122: encrypt_message122,
            123: encrypt_message123,
            124: encrypt_message124,
            127: encrypt_message127,
            140: encrypt_message140,
            141: encrypt_message141,
            143: encrypt_message143,
            150: encrypt_message150,
        }

        # # 处理外层可能的JSON字符串
        # if isinstance(msg, str):
        #     try:
        #         # 尝试解析外层JSON（例如，处理双引号包裹的情况）
        #         msg = json.loads(msg)
        #     except json.JSONDecodeError:
        #         pass  # 外层解析失败，继续处理
        #
        # # 如果data仍是字符串，尝试解析内部结构
        # if isinstance(msg, str):
        #     # 尝试使用ast安全解析Python格式的字典字符串
        #     try:
        #         msg = ast.literal_eval(msg)
        #     except:
        #         # 替换单引号为双引号后重试JSON解析
        #         try:
        #             msg = json.loads(msg.replace("'", '"'))
        #         except json.JSONDecodeError as e:
        #             raise ValueError("无法解析数据为字典") from e
        #
        # encrypt_msg = encrypt_functions[message_id](json.dumps(msg))
        # msg = str(encrypt_msg)
        data = {"messages": [msg]}
        print(data)
        host_url = f"http://{request.client.host}:{request.url.port}"
        api_url = f"{host_url}/api/v1/message/test_receive_from_lims"
        auth_header = request.headers.get('Authorization')

        headers = {
            'Authorization': auth_header,
            'Content-Type': "application/json"
        }
        # 发送 POST 请求
        requests.post(api_url, headers=headers, data=json.dumps(data))
except ImportError as e:
    def lims_repeat():
        raise NotImplementedError("lims_repeat is not available because required modules are missing.")

def SlabYard_repeat(*, request, msg):

    host_url = f"http://{request.client.host}:{request.url.port}"
    api_url = f"{host_url}/api/v1/message_server/push_message/pc_7xxx"
    auth_header = request.headers.get('Authorization')
    headers = {
        'Authorization': auth_header,
        'Content-Type': "application/json"
    }
    # 发送 POST 请求
    requests.post(api_url, headers=headers, data=msg)


def trigger_message_sap_repeat(*, msg, db_session, background_tasks: BackgroundTasks ):
    try:
        from dispatch.contrib.message_admin.message_server.trigger_sap_message import send_request

        result = {"type": msg.type, "msg": msg.msg, "id": msg.message_id}
        # sap消息发送
        background_tasks.add_task(send_request, db_session=db_session, result=result)
    except ImportError as e:
        pass