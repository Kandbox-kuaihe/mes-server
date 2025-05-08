from datetime import datetime, timezone
from dispatch.database import get_db
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from dispatch.message_admin.message.ibmmq.mq_service import save_message_to_mq
from dispatch.message_admin.message.ibmmq.wirte_service import WriteMessageToMq
from dispatch.system_admin.auth.models import DispatchUser
from dispatch.system_admin.auth.service import get_current_user
from .models import PushMessageData, PushMessageDataRead, RequestSemiMessageData
from dispatch.semi_admin.semi_load.models import SemiLoadCreate
from dispatch.semi_admin.semi_load import service as semi_load_service 
from dispatch.semi_admin.semi import service as semi_service
from dispatch.semi_admin.semi.models import SemiCreate
from dispatch.site import service as site_service


router = APIRouter()

 
from dispatch.log import getLogger
log = getLogger(__name__)

@router.post("/push_message_lims", response_model=PushMessageDataRead, summary="push message to lims.")
async def push_message(*,   db_session: Session = Depends(get_db),  request_in: PushMessageData , current_user: DispatchUser = Depends(get_current_user)):
    '''
    
    '''
    
    write = WriteMessageToMq(db_session=db_session ,test_sample_id = request_in.tast_sample_id)
    status, msg = write.write_message_to_lims(request_in.type)
 
    return PushMessageDataRead(status=status,msg=msg)


@router.post("/semi_message", response_model=PushMessageDataRead, summary="push semi message.")
async def semi_message(*, db_session: Session = Depends(get_db),   request_in: RequestSemiMessageData , current_user: DispatchUser = Depends(get_current_user)):
    
    data_list = request_in.semi_data if request_in.semi_data else []
    if not data_list:
        return PushMessageDataRead(status="Error", msg="No semi data found")
    try:
        semi_dict = {}
        semi_load_dict = {}
        for data in data_list:
            semi_load_code = f"{data.wagon_no}-{data.consignment_code}"
            semi_code = f"{data.cast_no}-{data.slabid}{data.slabnum}"
            if semi_load_code not in semi_load_dict:
                site = site_service.get_or_create(db_session=db_session, code=data.destination_site_code)
                dispatch_date  = datetime.strptime(data.dispatch_date, "%d/%m/%Y")
                _semi_load = {
                    "site":site,
                    "semi_load_code":semi_load_code,
                    "vehicle_code":data.wagon_no,
                    "vehicle_type":"wagon",
                    "consignment_code":data.consignment_code,
                    "dispatch_date":dispatch_date,
                    "created_at": datetime.now(timezone.utc),
                    "updated_at": datetime.now(timezone.utc),
                    "updated_by":current_user.email,
                    "created_by":current_user.email
                }
                semi_load_dict[semi_load_code] = _semi_load

            
            if semi_code not in semi_dict:
                site = site_service.get_or_create(db_session=db_session, code=data.destination_site_code)
                _semi_load = {
                    "rolling":None,
                    "order_group":None, 
                    "site":site, 
                    "semi_load":None, 
                    "semi_load_code":semi_load_code, 
                    "semi_charge_seq":None, 
                    "cast_code":data.cast_no, 
                    "semi_code":semi_code, 
                    "stock_in_date":datetime.now(timezone.utc), 
                    "skelp_code":data.slabid, 
                    "semi_cut_seq":data.slabnum, 
                    "semi_code_1":None,  
                    "product_type":data.product_type, 
                    "quality_code":data.quality_code, 
                    "length_mm":data.length_mm, 
                    "width_mm":data.width_mm, 
                    "thickness_mm":data.thickness_mm, 
                    "estimated_weight_kg":data.estimated_weight_kg, 
                    "scarfed_status":data.scarfed_status, 
                    "created_at": datetime.now(timezone.utc),
                    "updated_at": datetime.now(timezone.utc),
                    "updated_by":current_user.email,
                    "created_by":current_user.email
                }
                semi_dict[semi_code] = _semi_load

        # semi load save
        for semi_load_code ,semi_load_dict in semi_load_dict.items():
            semi_load_data = semi_load_service.get_by_code(db_session=db_session, code=semi_load_code)
            if  semi_load_data:
                continue
            semi_load_obj = SemiLoadCreate(**semi_load_dict)
            semi_load_service.create(db_session=db_session, semi_load_in = semi_load_obj)

        # semi  save
        for semi_code ,semi_dict in semi_dict.items():
            semi_data = semi_service.get_by_code(db_session=db_session, code=semi_code)
            if  semi_data:
                continue
            semi_load = semi_load_service.get_by_code(db_session=db_session, code=semi_dict['semi_load_code'])
            semi_dict['semi_load'] = semi_load
            del semi_dict['semi_load_code']
            semi_obj = SemiCreate(**semi_dict)
            semi_service.create(db_session=db_session, semi_in = semi_obj)

    except Exception as e:
        print(e)
        return PushMessageDataRead(status="Error", msg=str(e))


    return PushMessageDataRead(status="ok")


from pydantic import BaseModel
class MessageRequest(BaseModel):
    messages: list[str]

@router.post("/test_receive_from_lims", summary="mocking receive message from lims.")
def push_message(*, db_session: Session = Depends(get_db), request: MessageRequest):
    log.info(f'receive test lims messages: {request.messages}')
    try:
        from dispatch.contrib.message_admin.message.lims import transform_decrypt_message

        for message in request.messages:
            message_code, decrypted_message = transform_decrypt_message(message)
            if not decrypted_message:
                log.info(f'decrypted_message: {decrypted_message}, original message: {message}')
            flag = save_message_to_mq(db_session=db_session, message_code=message_code, decrypted_message=decrypted_message)
        return flag
    except ImportError as e:
        raise HTTPException(status_code=400, detail=str(e))
