
import traceback
from dispatch.tests_admin.test_result_chemical import service as test_result_chemical_service
from dispatch.tests_admin.test_sample import service as test_sample_service
from dispatch.tests_admin.test_result_impact import service as test_result_impact_service
from dispatch.tests_admin.impact_test_card import service as test_impact_service
from dispatch.tests_admin.tensile_test_card import service as test_tensile_service
from dispatch.tests_admin.test_result_tensile import service as test_result_tensile_service
from dispatch.tests_admin.test_result_tensile_thickness import service as test_result_tensile_thickness_service
from dispatch.tests_admin.test_list import service as test_service

from dispatch.log import getLog
log = getLog(__name__)

def get_test_sample_id(db_session,decrypted_message):
    test_sample_id = None
    test_sample_str = decrypted_message.get('Sample ID',"")
    if test_sample_str:
        test_sample_code= test_sample_str[:-1]
        test_sample_part= test_sample_str[-1:]
        test_sample = test_sample_service.get_by_test_sample_code(db_session = db_session ,test_sample_code=test_sample_code,test_sample_part=test_sample_part)
        test_sample_id = test_sample.id
    return test_sample_id

from dispatch.tests_admin.test_list.service import update_then_get_test_status_by_tensile
from dispatch.tests_admin.test_list.service import update_then_get_test_status_by_impact
from dispatch.runout_admin.runout_list import service as runout_service
def save_message_to_mq(db_session,message_code,decrypted_message):
    from dispatch.message_admin.message.ibmmq.wirte_service import WriteMessageToMq

    flag = True
    try:
        # spec_id
        test_sample_id = None
        spec_id = None
        test_sample = None
        log.info(f'Get lims message, message_code: {message_code}, decrypted_message: {decrypted_message}')
        if message_code in ["121","122","123","124","127","340","341","140","141","143","150"]:
            test_sample = test_sample_service.create_from_mq(db_session = db_session ,testSample_in=decrypted_message, message_code=message_code)
            test_sample_id = test_sample.id
            spec_id = test_sample.spec_id
        else:
            log.info(f"message_code:{message_code}.This message is not within the scope of acceptance")
            return True
        try:
            if not test_sample_id:
                test_sample_id, spec_id = get_test_sample_id(db_session,decrypted_message)
            
            write_cls = WriteMessageToMq(db_session=db_session ,test_sample_id = test_sample_id,spec_id = spec_id)
            
            if message_code in ["140", "340"]:
                runout = runout_service.get_by_code(db_session=db_session, code=decrypted_message.get("Piece ID"))
                test = update_then_get_test_status_by_tensile(db_session=db_session, runout=runout, test_sample=test_sample, piece_sub_id=decrypted_message.get("Piece Sub ID"),sample_thickness = decrypted_message.get("Sample Thickness") )
                result1 = test_result_tensile_service.create_or_update_tensile_from_mq(db_session = db_session ,test_result_tensile_in=decrypted_message,test_sample =test_sample, test=test)
                result2 = test_tensile_service.create_or_update_tensile_from_mq(db_session = db_session ,test_result_tensile_in=decrypted_message,test_sample =test_sample, test=test)
            elif message_code in ["141", "341"]:
                runout = runout_service.get_by_code(db_session=db_session, code=decrypted_message.get("Piece ID"))
                test = update_then_get_test_status_by_impact(db_session=db_session,  runout=runout, temp_value=decrypted_message.get('Charpy Temp (C)'), test_sample=test_sample, piece_sub_id=decrypted_message.get("Piece Sub ID"))
                result1 = test_result_impact_service.create_or_update_impact_from_mq(db_session = db_session ,testResultImpactBase_in=decrypted_message,test_sample =test_sample, test=test)
                result2 = test_impact_service.create_or_update_impact_from_mq(db_session = db_session ,testResultImpactBase_in=decrypted_message,test_sample =test_sample, test=test)
            elif message_code in ["143"]:
                result = test_result_tensile_thickness_service.create_form_mq(db_session = db_session ,testResultTensile_in=decrypted_message,test_sample_id =test_sample_id)
            elif message_code in ["150"]:
                result = test_result_chemical_service.create_form_mq(db_session = db_session ,testResultChemical_in=decrypted_message,test_sample_id=test_sample_id)  
            
            # send to lims      
            if message_code in ["123","124"]:
                # send 130 131 133
                status_130, msg_130 = write_cls.write_message_to_lims(130,reply_to = int(message_code))
                status_131, msg_131 = write_cls.write_message_to_lims(131)
                status_133, msg_133 = write_cls.write_message_to_lims(133)
            elif message_code in ["122"]:
                # send 120
                status_120, msg_120 = write_cls.write_message_to_lims(120)
            if not test_sample.test_sample_code:
                # send 125
                error_reason= 'TEST_SAMPLE_ID is None'
                status_125, msg_125 = write_cls.write_message_to_lims(125,error_reason)
                log.info("test_sample_id is None")

        except ValueError as ve:
            # send 125
            error_reason= str(ve)
            status_125, msg_125 = write_cls.write_message_to_lims(125,error_reason)
            log.error(f"Validation Error: {ve}")
            db_session.commit()
        except Exception as e:
            # send 125
            error_reason= str(e)
            status_125, msg_125 = write_cls.write_message_to_lims(125,error_reason)
            log.error(f"Unexpected Error: {e}")
            db_session.commit()
            # raise RuntimeError("An error occurred while fetching the test sample.") from e
    except Exception as e:
        flag = False
        log.error(f'lims message_code: {message_code}, decrypted_message:{decrypted_message} has error: {e}')
        traceback.print_exc()

    return flag
 