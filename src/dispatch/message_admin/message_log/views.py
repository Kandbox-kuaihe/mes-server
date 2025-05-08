from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks

from sqlalchemy.orm import Session
from dispatch.system_admin.auth.models import DispatchUser
from dispatch.system_admin.auth.service import get_current_user
from dispatch.database import get_db
from .models import MessageLogPagination

from dispatch.database_util.service import common_parameters, search_filter_sort_paginate
from .service import get, advice_tip_repeat, advice_sap_despatch_repeat, lims_repeat, SlabYard_repeat, \
    trigger_message_sap_repeat
from ..message.models import PushMessageData
from dispatch.message_admin.message_log.models import MessageLog
from dispatch.log import getLog
log = getLog(__name__)

router = APIRouter()


@router.get("/", response_model=MessageLogPagination)
def get_message_log(*, db_session: Session = Depends(get_db), common: dict = Depends(common_parameters), message_id: int = None):
    query = db_session.query(MessageLog)
    if message_id:
        query = query.filter(MessageLog.message_id == message_id)
    q = common["query_str"]
    if q:
        common["filter_type"] = "or"
        common["fields"] = ["type", "msg", "message_json"]
        common["ops"] = ["like"] * len(common["fields"])
        common["values"] = [f'%{q}%'] * len(common["fields"])
        common['query_str'] = ''
    common['query'] = query
    message_log = search_filter_sort_paginate(model="MessageLog", **common)
    return message_log


@router.get("/{message_id}", response_model=MessageLogPagination)
def get_message_log_by_id(*, db_session: Session = Depends(get_db), message_id: int, request: Request,
                          background_tasks: BackgroundTasks, common: dict = Depends(common_parameters),
                          current_user: DispatchUser = Depends(get_current_user)):
    """
    Get a order contact.
    """
    message_log = get(db_session=db_session, id=message_id)
    if not message_log:
        raise HTTPException(status_code=400, detail="Message log not found")
    message_data = {
        "id": message_log.message_id,
        "type": message_log.type,
        "msg": message_log.msg,
        "interact": "Recieve",
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "message_status": "Recieve",
    }
    message_log_in = PushMessageData(**message_data)
    log.info(f"repeat  message_log:------------{message_log_in}")
    key = f"{message_log.type}-{message_log.message_id}"

    # 特殊处理类型
    HANDLER_MAPPING = {
        "xml-1": lambda **kwargs: advice_tip_repeat(request=kwargs['request'], msg=kwargs['message_log'].msg),
        "xml-0": lambda **kwargs: advice_sap_despatch_repeat(request=kwargs['request'], msg=kwargs['message_log'].msg),

        "lims-121": lambda **kwargs: lims_repeat(request=kwargs['request'], msg=kwargs['message_log'].msg, message_id=121),
        "lims-122": lambda **kwargs: lims_repeat(request=kwargs['request'], msg=kwargs['message_log'].msg, message_id=122),
        "lims-123": lambda **kwargs: lims_repeat(request=kwargs['request'], msg=kwargs['message_log'].msg, message_id=123),
        "lims-124": lambda **kwargs: lims_repeat(request=kwargs['request'], msg=kwargs['message_log'].msg, message_id=124),
        "lims-127": lambda **kwargs: lims_repeat(request=kwargs['request'], msg=kwargs['message_log'].msg, message_id=127),
        "lims-140": lambda **kwargs: lims_repeat(request=kwargs['request'], msg=kwargs['message_log'].msg, message_id=140),
        "lims-141": lambda **kwargs: lims_repeat(request=kwargs['request'], msg=kwargs['message_log'].msg, message_id=141),
        "lims-143": lambda **kwargs: lims_repeat(request=kwargs['request'], msg=kwargs['message_log'].msg, message_id=143),
        "lims-150": lambda **kwargs: lims_repeat(request=kwargs['request'], msg=kwargs['message_log'].msg, message_id=150),

        "sap-182": lambda **kwargs: trigger_message_sap_repeat(msg=kwargs['message_log'], db_session=kwargs['db_session'], background_tasks=kwargs['background_tasks']),
        "sap-264": lambda **kwargs: trigger_message_sap_repeat(msg=kwargs['message_log'], db_session=kwargs['db_session'], background_tasks=kwargs['background_tasks']),
        "sap-302": lambda **kwargs: trigger_message_sap_repeat(msg=kwargs['message_log'], db_session=kwargs['db_session'], background_tasks=kwargs['background_tasks']),
        "sap-404": lambda **kwargs: trigger_message_sap_repeat(msg=kwargs['message_log'], db_session=kwargs['db_session'], background_tasks=kwargs['background_tasks']),

        "SlabYard-7001": lambda **kwargs: SlabYard_repeat(request=kwargs['request'], msg=kwargs['message_log'].message_json),
        "SlabYard-7108": lambda **kwargs: SlabYard_repeat(request=kwargs['request'], msg=kwargs['message_log'].message_json),
        "SlabYard-7118": lambda **kwargs: SlabYard_repeat(request=kwargs['request'], msg=kwargs['message_log'].message_json),
        "SlabYard-7104": lambda **kwargs: SlabYard_repeat(request=kwargs['request'], msg=kwargs['message_log'].message_json),
    }

    handler = HANDLER_MAPPING.get(key)
    if handler:
        # handler(request=request, message_log=message_log)
        try:
            handler(request=request, message_log=message_log, db_session=db_session, background_tasks=background_tasks)
        except Exception as e:
            log.error(f"Error in handler for {key}: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Error processing {key} message: {str(e)}")
        common["fields"] = ["id"]
        common["ops"] = ["eq"]
        common["values"] = [message_log.id]
        return search_filter_sort_paginate(model="MessageLog", **common)

    try:
        from dispatch.contrib.message_admin.message_server.server import call_method, call_method_toFECC, get_interact_type
        interact_from, interact_to, msg_type = get_interact_type(message_log_in)
        if msg_type == 1:
            call_method(request, background_tasks, db_session, current_user, message_log_in)
        elif msg_type == 0:
            call_method_toFECC(db_session, message_log_in, background_tasks, current_user)
        else:
            raise HTTPException(status_code=400, detail="Message msg_type not found")
    except  ImportError as e:
        raise HTTPException(status_code=400, detail=str(e))
    common["fields"] = ["id"]
    common["ops"] = ["eq"]
    common["values"] = [message_log.id]
    return search_filter_sort_paginate(model="MessageLog", **common)

@router.get('/test_repeat/{message_id}')
def test_repeat_message_log(*, message_id: int, db_session: Session = Depends(get_db), request: Request,
              background_tasks: BackgroundTasks, common: dict = Depends(common_parameters),
              current_user: DispatchUser = Depends(get_current_user)):
    message_ids = [
        1548054,1277309,1021595,1282108,951182,1463460,1071754,1266194,1546636,560933,402484,785084,1640379,607876,926242,420377,644499,1127839,685115,994127,647783,1306064,1263465,782497,1478684,1433316,616549,724309,1667383,534733,1492256,1265263,1096669,834228,439123,1532078,1436277,633264,1548557,834223,1076618,1477110,980350,1162355,1583901,906032,1479680,1507375,1578305,1265834,1608943,1613657,1482986,1621126,582077,707023,1450127,1519533,1266187,630200,576945,569358,391687,1585712,1482221,1612306,510355,1588788,1506416,627659,1546279,1576735,1149292,869396,1603022,1025126,1583902,679722,976531,633889,681227,1057842,1143720,1263872,619022,1621185,1022028,1266160,1075969,1591596,1182151,688967,1473274,414901,612182,1265984,1589178,1150220,1453678,1620046,1563299,526113,1202050,433114,1612262,1638069,909909,1634650,1487222,1580123,1407591,652705,973023,1118246,1118705,1525563,1264551,1481477,1546135,1585907,1567132,1603276,1545495,1533545,1533123,1592887,1534341,1610141,1577825,1274702,936711,935312,1161706
    ]
    success_message_ids = []
    failed_message_ids = []
    for message_id in message_ids:
        try:
            get_message_log_by_id(db_session=db_session, message_id=message_id,request=request,
                background_tasks=background_tasks, common=common,
                current_user=current_user)
            success_message_ids.append(message_id)
        except Exception as e:
            log.error(f'repeat error: message_id: {message_id}, e: {e}')
            failed_message_ids.append(message_id)
    log.info(f'Success message ids length: {len(success_message_ids)}, ids: {success_message_ids}')
    log.info(f'Failed message ids length: {len(failed_message_ids)}, ids: {failed_message_ids}')
